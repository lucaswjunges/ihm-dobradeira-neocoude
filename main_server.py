"""
main_server.py

WebSocket server for NEOCOUDE-HD-15 HMI.
Bridges PLC state (via state_manager) with web frontend (via WebSocket).

Features:
- WebSocket server on localhost:8080
- Sends complete state on client connect
- Pushes only deltas on state changes
- Receives JSON commands from frontend (button presses, etc.)
- Stub functions for future features (Telegram, Google Sheets)
"""

import asyncio
import json
import logging
import argparse
from typing import Set
from datetime import datetime

try:
    import websockets
    from websockets.server import WebSocketServerProtocol
    WEBSOCKETS_AVAILABLE = True
except ImportError:
    WEBSOCKETS_AVAILABLE = False
    WebSocketServerProtocol = None

from modbus_client import ModbusClient, ModbusConfig
from state_manager import StateManager
from state_machine import OperationStateMachine
from display_manager import DisplayManager

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class HMIServer:
    """
    WebSocket server for HMI frontend communication.
    """

    def __init__(self, state_manager: StateManager, host: str = 'localhost', port: int = 8080):
        """
        Initialize HMI server.

        Args:
            state_manager: StateManager instance
            host: WebSocket server host (default: localhost)
            port: WebSocket server port (default: 8080)
        """
        if not WEBSOCKETS_AVAILABLE:
            raise ImportError("websockets not installed! Install with: pip install websockets")

        self.state_manager = state_manager
        self.host = host
        self.port = port

        # Connected WebSocket clients
        self.clients: Set[WebSocketServerProtocol] = set()

        # Alert log (for "Logs e Produção" tab)
        self.alert_log = []

        # NEW: Máquina de estados e gerenciador de display
        self.operation_state = OperationStateMachine()
        self.display_manager = DisplayManager(self.operation_state)

        # Cursor blink task
        self.cursor_task = None

    async def start(self):
        """Start WebSocket server and state manager"""
        logger.info(f"Starting HMI server on ws://{self.host}:{self.port}")

        # Register state change callback
        self.state_manager.register_callback(self._on_state_change)

        # Start state manager
        await self.state_manager.start()

        # Start cursor blink task
        self.cursor_task = asyncio.create_task(self._cursor_blink_loop())

        # Start WebSocket server
        async with websockets.serve(self._handle_client, self.host, self.port):
            logger.info(f"✓ HMI server running on ws://{self.host}:{self.port}")
            await asyncio.Future()  # Run forever

    async def _handle_client(self, websocket: WebSocketServerProtocol):
        """
        Handle new WebSocket client connection.

        Args:
            websocket: WebSocket connection
        """
        client_id = f"{websocket.remote_address[0]}:{websocket.remote_address[1]}"
        logger.info(f"Client connected: {client_id}")

        # Add to clients set
        self.clients.add(websocket)

        try:
            # Send complete state on connect
            initial_state = self.state_manager.get_state()

            # Atualizar operation_state com dados do CLP
            self.operation_state.update_from_clp(initial_state)

            # Atualizar display
            self.display_manager.update_display()

            # Enviar estado completo
            await self._send_message(websocket, {
                'type': 'initial_state',
                'data': initial_state,
                'operation_state': self.operation_state.get_state_dict(),
                'display': self.display_manager.get_display_content()
            })

            # Send alert log
            await self._send_message(websocket, {
                'type': 'alert_log',
                'data': self.alert_log
            })

            # Listen for commands from client
            async for message in websocket:
                await self._handle_message(websocket, message)

        except websockets.exceptions.ConnectionClosed:
            logger.info(f"Client disconnected: {client_id}")

        except Exception as e:
            logger.error(f"Error handling client {client_id}: {e}", exc_info=True)

        finally:
            # Remove from clients set
            self.clients.discard(websocket)

    async def _handle_message(self, websocket: WebSocketServerProtocol, message: str):
        """
        Handle incoming message from client.

        Expected message format (JSON):
        {
            "action": "key_press",
            "key": "K1"
        }
        or
        {
            "action": "key_combo",
            "keys": ["K1", "K7"]
        }

        Args:
            websocket: WebSocket connection
            message: JSON message string
        """
        try:
            data = json.loads(message)
            action = data.get('action')

            logger.info(f"Received command: {data}")

            if action == 'key_press':
                key = data.get('key')
                if not key:
                    await self._send_error(websocket, "Missing key parameter")
                    return

                # Processar tecla através do display manager
                result = self.display_manager.handle_keypress(key)

                # Se precisa escrever no CLP
                if result.get('need_clp_write'):
                    clp_command = result.get('clp_command', {})
                    await self._execute_clp_command(clp_command)

                # Atualizar display e enviar para todos os clientes
                if result.get('screen_changed') or result.get('need_clp_write'):
                    await self._broadcast_display_update()

                # Send response
                await self._send_message(websocket, {
                    'type': 'key_response',
                    'success': True,
                    'key': key,
                    'message': result.get('message', '')
                })

                # Log
                if result.get('message'):
                    self._add_alert(result['message'], 'info')

            elif action == 'key_combo':
                keys = data.get('keys', [])
                if not keys or len(keys) != 2:
                    await self._send_error(websocket, "Invalid key combo")
                    return

                # Combo K1+K7 = mudar velocidade
                if set(keys) == {"K1", "K7"}:
                    if self.display_manager.show_velocity_screen():
                        await self._broadcast_display_update()
                        await self._send_message(websocket, {
                            'type': 'key_response',
                            'success': True,
                            'message': 'Tela de velocidade'
                        })
                    else:
                        await self._send_message(websocket, {
                            'type': 'key_response',
                            'success': False,
                            'message': 'Não pode trocar velocidade (modo automático?)'
                        })
                else:
                    await self._send_error(websocket, "Unknown key combo")

            elif action == 'control_button':
                control = data.get('control')
                if not control:
                    await self._send_error(websocket, "Missing control parameter")
                    return

                logger.info(f"Control button pressed: {control}")

                # Mapear controles para BITS INTERNOS (Estados livres 0x0030-0x0034)
                # SOLUÇÃO: Ladder estava sobrescrevendo S0/S1 quando E2/E4 não estavam ativos
                # Usando bits internos que o ladder pode LER e usar para controlar S0/S1
                #
                # IMPORTANTE: Ladder DEVE ser modificado para ler esses bits e ativar saídas:
                #   - Se bit 0x0030 ON → Ativa S0 (384) por tempo configurado
                #   - Se bit 0x0031 ON → Ativa S1 (385) por tempo configurado
                #   - Se bit 0x0032 ON → Desliga S0 e S1 + limpa bits 0x0030 e 0x0031
                #
                # Ver SOLUCAO_BITS_INTERNOS.md para detalhes
                control_map = {
                    'FORWARD': 48,            # Bit interno 0x0030 - TESTADO e VALIDADO
                    'BACKWARD': 49,           # Bit interno 0x0031 - TESTADO e VALIDADO
                    'STOP': 50,               # Bit interno 0x0032 - TESTADO e VALIDADO
                    'EMERGENCY_STOP': 51,     # Bit interno 0x0033 - Reservado para futuro
                    'COMMAND_ON': 52          # Bit interno 0x0034 - Reservado para futuro
                }

                # Verificar se controle está mapeado
                modbus_address = control_map.get(control)
                if modbus_address is None:
                    await self._send_error(websocket, f"Controle não mapeado: {control}")
                    return

                # Simular pulso de botão (100ms ON → OFF) para todos os comandos
                # O ladder irá ler o bit e executar a ação apropriada:
                #   - Bit 48 (FORWARD) → Ladder ativa S0
                #   - Bit 49 (BACKWARD) → Ladder ativa S1
                #   - Bit 50 (STOP) → Ladder desliga S0 e S1
                logger.info(f"Pulsing Modbus internal bit {modbus_address} (0x{modbus_address:04X}) for {control}")

                # Fase 1: Ativar coil (True)
                success_on = await asyncio.to_thread(
                    self.state_manager.client.write_coil, modbus_address, True
                )

                if not success_on:
                    logger.error(f"Falha ao ativar coil {modbus_address}")
                    await self._send_message(websocket, {
                        'type': 'control_response',
                        'success': False,
                        'control': control,
                        'message': f'Erro ao ativar {control}'
                    })
                    self._add_alert(f"Erro ao ativar {control}", 'error')
                    return

                # Fase 2: Aguardar 100ms
                await asyncio.sleep(0.1)

                # Fase 3: Desativar coil (False)
                success_off = await asyncio.to_thread(
                    self.state_manager.client.write_coil, modbus_address, False
                )

                if not success_off:
                    logger.error(f"Falha ao desativar coil {modbus_address}")

                # Enviar resposta
                await self._send_message(websocket, {
                    'type': 'control_response',
                    'success': success_on and success_off,
                    'control': control,
                    'message': f'{control} executado' if (success_on and success_off) else f'Falha parcial em {control}'
                })

                self._add_alert(f"Botão de controle acionado: {control}", 'info')

            elif action == 'ping':
                # Health check
                await self._send_message(websocket, {
                    'type': 'pong',
                    'timestamp': datetime.now().isoformat()
                })

            else:
                await self._send_error(websocket, f"Unknown action: {action}")

        except json.JSONDecodeError:
            logger.error(f"Invalid JSON received: {message}")
            await self._send_error(websocket, "Invalid JSON format")

        except Exception as e:
            logger.error(f"Error handling message: {e}", exc_info=True)
            await self._send_error(websocket, str(e))

    async def _on_state_change(self, deltas: dict):
        """
        Callback for state changes - broadcast deltas to all clients.
        Também atualiza operation_state e display.

        Args:
            deltas: Dictionary with changed state values
        """
        if not self.clients:
            return

        # Atualizar operation_state com novos dados do CLP
        full_state = self.state_manager.get_state()
        self.operation_state.update_from_clp(full_state)

        # Atualizar display
        self.display_manager.update_display()

        # Preparar mensagem completa
        message = {
            'type': 'state_update',
            'data': deltas,
            'operation_state': self.operation_state.get_state_dict(),
            'display': self.display_manager.get_display_content()
        }

        # Broadcast to all connected clients
        await asyncio.gather(
            *[self._send_message(client, message) for client in self.clients],
            return_exceptions=True
        )

    async def _execute_clp_command(self, command: dict):
        """
        Executa comando no CLP baseado no resultado do display_manager

        Args:
            command: Dicionário com comando
                {"action": "press_key", "key": "K1"}
                {"action": "write_angle", "field": "D1E", "value": 90.0}
                etc.
        """
        action = command.get('action')

        if action == 'press_key':
            key = command.get('key')
            success = await self.state_manager.press_button(key)
            logger.info(f"CLP command press_key({key}): {success}")

        elif action == 'write_angle':
            field = command.get('field')
            value = command.get('value')
            # TODO: Implementar escrita de ângulos quando mapearmos os registradores
            logger.info(f"CLP command write_angle({field}={value}): [NOT IMPLEMENTED]")

        elif action == 'set_mode':
            mode = command.get('mode')
            # TODO: Implementar mudança de modo quando mapearmos o registrador
            logger.info(f"CLP command set_mode({mode}): [NOT IMPLEMENTED]")

        elif action == 'set_velocity':
            vel_class = command.get('class')
            # TODO: Implementar mudança de velocidade quando mapearmos o registrador
            logger.info(f"CLP command set_velocity(class={vel_class}): [NOT IMPLEMENTED]")

        elif action == 'select_dobra':
            dobra = command.get('dobra')
            # TODO: Implementar seleção de dobra quando mapearmos o registrador
            logger.info(f"CLP command select_dobra({dobra}): [NOT IMPLEMENTED]")

        elif action == 'select_direction':
            direction = command.get('direction')
            # TODO: Implementar seleção de direção quando mapearmos o registrador
            logger.info(f"CLP command select_direction({direction}): [NOT IMPLEMENTED]")

        elif action == 'reset_display':
            # S2: Reset display / zerar
            success = await self.state_manager.press_button('S2')
            logger.info(f"CLP command reset_display: {success}")

        elif action == 'clear_error':
            # Limpar erro / emergência
            success = await self.state_manager.press_button('S2')
            logger.info(f"CLP command clear_error: {success}")

        else:
            logger.warning(f"Unknown CLP command: {action}")

    async def _broadcast_display_update(self):
        """
        Envia atualização do display para todos os clientes
        """
        if not self.clients:
            return

        message = {
            'type': 'display_update',
            'display': self.display_manager.get_display_content(),
            'operation_state': self.operation_state.get_state_dict()
        }

        await asyncio.gather(
            *[self._send_message(client, message) for client in self.clients],
            return_exceptions=True
        )

    async def _cursor_blink_loop(self):
        """
        Loop infinito para fazer cursor piscar a cada 500ms
        """
        while True:
            try:
                await asyncio.sleep(0.5)
                self.display_manager.toggle_cursor()

                # Se cursor mudou e está em modo edição, broadcast update
                if self.display_manager.edit_mode:
                    await self._broadcast_display_update()

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in cursor blink loop: {e}")

    async def _send_message(self, websocket: WebSocketServerProtocol, message: dict):
        """
        Send JSON message to client.

        Args:
            websocket: WebSocket connection
            message: Dictionary to send as JSON
        """
        try:
            await websocket.send(json.dumps(message))
        except Exception as e:
            logger.error(f"Error sending message: {e}")

    async def _send_error(self, websocket: WebSocketServerProtocol, error: str):
        """
        Send error message to client.

        Args:
            websocket: WebSocket connection
            error: Error message
        """
        await self._send_message(websocket, {
            'type': 'error',
            'message': error
        })

    def _add_alert(self, message: str, level: str = 'info'):
        """
        Add alert to log.

        Args:
            message: Alert message
            level: Alert level (info, warning, error)
        """
        alert = {
            'timestamp': datetime.now().isoformat(),
            'level': level,
            'message': message
        }

        self.alert_log.append(alert)

        # Keep only last 100 alerts
        if len(self.alert_log) > 100:
            self.alert_log.pop(0)

        # Broadcast alert to all clients
        asyncio.create_task(self._broadcast_alert(alert))

    async def _broadcast_alert(self, alert: dict):
        """
        Broadcast alert to all connected clients.

        Args:
            alert: Alert dictionary
        """
        if not self.clients:
            return

        message = {
            'type': 'alert',
            'data': alert
        }

        await asyncio.gather(
            *[self._send_message(client, message) for client in self.clients],
            return_exceptions=True
        )


# ============================================================================
# FUTURE FEATURES (Stubs)
# ============================================================================

async def send_telegram_alert(message: str):
    """
    Send alert via Telegram bot.

    TODO: Implement when Telegram integration is needed.

    Args:
        message: Alert message to send
    """
    logger.info(f"[STUB] Telegram alert: {message}")
    # Future: Use python-telegram-bot library
    pass


async def log_to_sheets(data: dict):
    """
    Log production data to Google Sheets.

    TODO: Implement when Google Sheets integration is needed.

    Args:
        data: Production data dictionary
    """
    logger.info(f"[STUB] Google Sheets log: {data}")
    # Future: Use gspread library
    pass


# ============================================================================
# MAIN
# ============================================================================

async def main(stub_mode: bool = True, serial_port: str = '/dev/ttyUSB0'):
    """
    Main entry point for HMI server.

    Args:
        stub_mode: Use stub mode (no PLC hardware)
        serial_port: Serial port for RS485 converter
    """
    logger.info("=" * 80)
    logger.info("NEOCOUDE-HD-15 HMI SERVER")
    logger.info("=" * 80)

    # Create Modbus client
    if stub_mode:
        logger.info("Running in STUB MODE (no PLC hardware required)")
        client = ModbusClient(stub_mode=True)
    else:
        logger.info(f"Running in LIVE MODE (PLC on {serial_port})")
        config = ModbusConfig(port=serial_port)
        client = ModbusClient(stub_mode=False, config=config)

    # Create state manager
    state_manager = StateManager(client, poll_interval=0.25)

    # Create and start HMI server
    server = HMIServer(state_manager, host='localhost', port=8080)

    try:
        await server.start()
    except KeyboardInterrupt:
        logger.info("\nShutdown requested...")
    finally:
        await state_manager.stop()
        logger.info("Server stopped")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='NEOCOUDE-HD-15 HMI Server')
    parser.add_argument(
        '--live',
        action='store_true',
        help='Run in live mode (connect to real PLC)'
    )
    parser.add_argument(
        '--port',
        type=str,
        default='/dev/ttyUSB0',
        help='Serial port for RS485 converter (default: /dev/ttyUSB0)'
    )

    args = parser.parse_args()

    try:
        asyncio.run(main(stub_mode=not args.live, serial_port=args.port))
    except KeyboardInterrupt:
        logger.info("\nShutdown complete")
