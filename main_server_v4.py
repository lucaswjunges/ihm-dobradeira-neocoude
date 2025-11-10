"""
main_server_v4.py

WebSocket server dedicado para IHM v4
Servidor simplificado focado apenas na emulação da IHM Expert Series

Arquitetura:
- Lê dados do CLP via Modbus
- Formata telas no backend (IHMv4Manager)
- Envia texto pronto via WebSocket
- Frontend é "burro" (só exibe texto)
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
from ihm_v4_manager import IHMv4Manager

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ihm_v4_server.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class IHMv4Server:
    """WebSocket server para IHM v4"""

    def __init__(self, modbus_client: ModbusClient, host: str = 'localhost', port: int = 8080):
        """
        Initialize IHM v4 server

        Args:
            modbus_client: ModbusClient instance
            host: WebSocket server host
            port: WebSocket server port
        """
        if not WEBSOCKETS_AVAILABLE:
            raise ImportError("websockets não instalado! Instale com: pip install websockets")

        self.modbus = modbus_client
        self.host = host
        self.port = port

        # IHM v4 Manager (gerencia telas e navegação)
        self.ihm_manager = IHMv4Manager(modbus_client)

        # Connected clients
        self.clients: Set[WebSocketServerProtocol] = set()

        # Polling task
        self.polling_task = None

    async def start(self):
        """Inicia servidor WebSocket e polling Modbus"""
        logger.info(f"🚀 Iniciando IHM v4 Server em ws://{self.host}:{self.port}")

        # Start Modbus polling
        self.polling_task = asyncio.create_task(self._poll_modbus_loop())

        # Start WebSocket server
        async with websockets.serve(self._handle_client, self.host, self.port):
            logger.info(f"✓ IHM v4 Server rodando em ws://{self.host}:{self.port}")
            logger.info(f"📱 Abra ihm_v4.html no navegador")
            await asyncio.Future()  # Run forever

    async def _handle_client(self, websocket: WebSocketServerProtocol):
        """Handle new WebSocket client"""
        client_addr = websocket.remote_address
        logger.info(f"Cliente conectado: {client_addr}")

        self.clients.add(websocket)

        try:
            # Enviar estado inicial
            state = await self.ihm_manager.get_display_state()
            await websocket.send(json.dumps(state))

            # Loop de mensagens do cliente
            async for message in websocket:
                await self._handle_message(websocket, message)

        except websockets.exceptions.ConnectionClosed:
            logger.info(f"Cliente desconectado: {client_addr}")
        except Exception as e:
            logger.error(f"Erro com cliente {client_addr}: {e}")
        finally:
            self.clients.discard(websocket)

    async def _handle_message(self, websocket: WebSocketServerProtocol, message: str):
        """Process message from client"""
        try:
            data = json.loads(message)
            action = data.get('action')

            if action == 'get_ihm_v4_state':
                # Cliente solicitou estado atual
                state = await self.ihm_manager.get_display_state()
                await websocket.send(json.dumps(state))

            elif action == 'press_ihm_v4_key':
                # Cliente pressionou tecla
                key_code = data.get('key_code')
                if key_code is not None:
                    new_state = await self.ihm_manager.handle_key_press(key_code)
                    # Broadcast new state to all clients
                    await self._broadcast(new_state)
                else:
                    logger.warning("press_ihm_v4_key sem key_code")

            else:
                logger.warning(f"Ação desconhecida: {action}")

        except json.JSONDecodeError:
            logger.error(f"JSON inválido recebido: {message}")
        except Exception as e:
            logger.error(f"Erro ao processar mensagem: {e}")

    async def _poll_modbus_loop(self):
        """Loop de polling Modbus (atualiza dados da máquina)"""
        logger.info("📡 Iniciando polling Modbus...")

        while True:
            try:
                # Ler dados do CLP
                machine_data = await self._read_machine_data()

                # Atualizar IHM Manager
                await self.ihm_manager.update_machine_data(machine_data)

                # Broadcast estado atualizado para todos os clientes
                if self.clients:
                    state = await self.ihm_manager.get_display_state()
                    await self._broadcast(state)

            except Exception as e:
                logger.error(f"Erro no polling Modbus: {e}")

            # Polling a cada 100ms (display atualiza rápido)
            await asyncio.sleep(0.1)

    async def _read_machine_data(self) -> dict:
        """
        Lê dados do CLP via Modbus

        Returns:
            Dictionary com dados da máquina
        """
        data = {}

        try:
            # Encoder (32-bit MSW/LSW)
            response_msw = await asyncio.to_thread(
                self.modbus.client.read_holding_registers,
                address=1238, count=1, device_id=1
            )
            response_lsw = await asyncio.to_thread(
                self.modbus.client.read_holding_registers,
                address=1239, count=1, device_id=1
            )

            if response_msw and response_lsw and not response_msw.isError() and not response_lsw.isError():
                encoder_value = (response_msw.registers[0] << 16) | response_lsw.registers[0]
                data['encoder'] = encoder_value

            # Ângulos de dobra (6 valores)
            angles_map = {
                'aj1_esq': 2112, 'aj1_dir': 2114,
                'aj2_esq': 2118, 'aj2_dir': 2120,
                'aj3_esq': 2128, 'aj3_dir': 2130
            }

            for key, addr in angles_map.items():
                response = await asyncio.to_thread(
                    self.modbus.client.read_holding_registers,
                    address=addr, count=1, device_id=1
                )
                if response and not response.isError():
                    if 'angles' not in data:
                        data['angles'] = {}
                    data['angles'][key] = response.registers[0]

            # Velocidade (bits 864-866)
            for i, bit_addr in enumerate([864, 865, 866], start=1):
                response = await asyncio.to_thread(
                    self.modbus.client.read_coils,
                    address=bit_addr, count=1, device_id=1
                )
                if response and not response.isError() and response.bits[0]:
                    data['speed_class'] = i

            # Dobra ativa (bits 248, 249)
            bit_dobra_2 = await asyncio.to_thread(
                self.modbus.client.read_coils,
                address=248, count=1, device_id=1
            )
            bit_dobra_3 = await asyncio.to_thread(
                self.modbus.client.read_coils,
                address=249, count=1, device_id=1
            )

            if bit_dobra_3 and not bit_dobra_3.isError() and bit_dobra_3.bits[0]:
                data['active_bend'] = 3
            elif bit_dobra_2 and not bit_dobra_2.isError() and bit_dobra_2.bits[0]:
                data['active_bend'] = 2
            else:
                data['active_bend'] = 1

            # Ciclo ativo (bit 247)
            response = await asyncio.to_thread(
                self.modbus.client.read_coils,
                address=247, count=1, device_id=1
            )
            if response and not response.isError():
                data['cycle_active'] = response.bits[0]

            # Carenagem (entrada E5 - endereço 261)
            response = await asyncio.to_thread(
                self.modbus.client.read_holding_registers,
                address=261, count=1, device_id=1
            )
            if response and not response.isError():
                data['carenagem_ok'] = (response.registers[0] & 0x0001) == 1

            # TODO: Adicionar leitura de:
            # - Modo AUTO/MAN
            # - Direção (K4/K5)
            # - Runtime (totalizador)
            # - Estado da máquina

        except Exception as e:
            logger.error(f"Erro ao ler dados Modbus: {e}")

        return data

    async def _broadcast(self, message: dict):
        """
        Broadcast message to all connected clients

        Args:
            message: Dictionary to send (will be JSON encoded)
        """
        if not self.clients:
            return

        message_json = json.dumps(message)
        disconnected_clients = set()

        for client in self.clients:
            try:
                await client.send(message_json)
            except websockets.exceptions.ConnectionClosed:
                disconnected_clients.add(client)
            except Exception as e:
                logger.error(f"Erro ao enviar para cliente: {e}")
                disconnected_clients.add(client)

        # Remove disconnected clients
        self.clients -= disconnected_clients


async def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='IHM v4 Server - Expert Series Web Emulator')
    parser.add_argument('--port', type=str, default=None, help='Porta serial (ex: /dev/ttyUSB0)')
    parser.add_argument('--stub', action='store_true', help='Modo stub (sem CLP real)')
    parser.add_argument('--ws-port', type=int, default=8080, help='Porta WebSocket (padrão: 8080)')

    args = parser.parse_args()

    # Configure Modbus
    config = ModbusConfig(
        port=args.port or '/dev/ttyUSB0',
        baudrate=57600,
        stopbits=2,
        parity='N',
        slave_address=1
    )

    # Create Modbus client
    modbus_client = ModbusClient(stub_mode=args.stub, config=config)

    # Connect to PLC
    if not modbus_client.connect():
        logger.error("❌ Falha ao conectar ao CLP!")
        if not args.stub:
            logger.error(f"Verifique se o CLP está ligado e conectado em {config.port}")
            return

    logger.info("✓ Conexão Modbus estabelecida")

    # Create and start server
    server = IHMv4Server(modbus_client, host='localhost', port=args.ws_port)

    try:
        await server.start()
    except KeyboardInterrupt:
        logger.info("Servidor interrompido pelo usuário")
    except Exception as e:
        logger.error(f"Erro fatal: {e}")
        raise


if __name__ == '__main__':
    asyncio.run(main())
