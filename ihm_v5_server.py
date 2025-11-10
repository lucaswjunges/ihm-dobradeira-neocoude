"""
IHM v5 Server - Mirror Mode
Espelha a tela ativa do CLP lendo o registro 0x0FEF

Arquitetura:
1. Lê registro 0x0FEF (4079) para descobrir qual tela está ativa no CLP
2. Carrega definição da tela do screens_map.json
3. Envia texto formatado para o frontend via WebSocket
4. Frontend apenas exibe (modo "espelho puro")
"""

import asyncio
import json
import logging
import argparse
from typing import Set, Dict, Any
from pathlib import Path

try:
    import websockets
    from websockets.server import WebSocketServerProtocol
    WEBSOCKETS_AVAILABLE = True
except ImportError:
    WEBSOCKETS_AVAILABLE = False
    WebSocketServerProtocol = None

from modbus_client import ModbusClient, ModbusConfig

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ihm_v5_server.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Registro que contém o ID da tela ativa no CLP
# Endereçamento interno: 0x0FEE/0x0FEF (4078 bytes)
# Endereçamento Modbus: 4078 / 2 = 2039 (WORD)
ACTIVE_SCREEN_REGISTER = 2039  # Endereço Modbus corrigido
ACTIVE_SCREEN_REGISTER_FALLBACK = 4078  # Fallback se mapeamento for 1:1


class IHMv5Server:
    """
    IHM v5 - Mirror Mode Server
    Lê qual tela está ativa no CLP e espelha no navegador
    """

    def __init__(self, modbus_client: ModbusClient, host: str = 'localhost', port: int = 8085):
        if not WEBSOCKETS_AVAILABLE:
            raise ImportError("websockets não instalado! Instale com: pip install websockets")

        self.modbus = modbus_client
        self.host = host
        self.port = port

        # Carregar mapeamento de telas
        screens_file = Path('screens_map.json')
        if not screens_file.exists():
            raise FileNotFoundError("screens_map.json não encontrado! Execute analyze_screens.py primeiro")

        with open(screens_file, 'r', encoding='utf-8') as f:
            self.screens_map = json.load(f)

        logger.info(f"📺 Carregadas {len(self.screens_map)} telas do screens_map.json")

        # Connected clients
        self.clients: Set[WebSocketServerProtocol] = set()

        # Estado atual
        self.current_screen_id = 0
        self.last_screen_id = -1

        # Status de conexão
        self.modbus_connected = False
        self.connection_errors = 0
        self.max_connection_errors = 5  # Tentar reconectar após 5 erros consecutivos

    async def start(self):
        """Inicia servidor WebSocket e polling do CLP"""
        logger.info(f"🚀 Iniciando IHM v5 Server (Mirror Mode) em ws://{self.host}:{self.port}")

        # Verificar conexão inicial
        self.modbus_connected = self.modbus.connected

        # Start polling do registro de tela ativa
        polling_task = asyncio.create_task(self._poll_active_screen())

        # Start connection health monitor
        health_task = asyncio.create_task(self._monitor_connection_health())

        # Start WebSocket server
        async with websockets.serve(self._handle_client, self.host, self.port):
            logger.info(f"✓ IHM v5 Server rodando em ws://{self.host}:{self.port}")
            logger.info(f"📱 Abra ihm_v5.html no navegador")
            logger.info(f"🔍 Monitorando registro 0x{ACTIVE_SCREEN_REGISTER:04X} do CLP...")
            await asyncio.Future()  # Run forever

    async def _handle_client(self, websocket: WebSocketServerProtocol):
        """Handle new WebSocket client"""
        client_addr = websocket.remote_address
        logger.info(f"Cliente conectado: {client_addr}")

        self.clients.add(websocket)

        try:
            # Enviar estado inicial
            state = self._get_display_state()
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

            if action == 'get_state':
                # Cliente solicitou estado atual
                state = self._get_display_state()
                await websocket.send(json.dumps(state))

            elif action == 'press_key':
                # Cliente pressionou tecla - enviar para CLP
                key_code = data.get('key_code')
                if key_code is not None:
                    await self._send_key_to_clp(key_code)
                else:
                    logger.warning("press_key sem key_code")

            else:
                logger.warning(f"Ação desconhecida: {action}")

        except json.JSONDecodeError:
            logger.error(f"JSON inválido recebido: {message}")
        except Exception as e:
            logger.error(f"Erro ao processar mensagem: {e}")

    async def _poll_active_screen(self):
        """
        Loop de polling do registro de tela ativa (0x0FEF)
        Lê a cada 500ms qual tela o CLP está exibindo

        Implementa fallback: tenta 2039 primeiro, depois 4078 se necessário
        """
        logger.info("📡 Iniciando polling do registro de tela ativa...")
        register_to_use = ACTIVE_SCREEN_REGISTER  # Inicia com 2039
        fallback_attempted = False

        while True:
            try:
                # Ler registro da tela ativa
                screen_id = await asyncio.to_thread(
                    self.modbus.read_register,
                    register_to_use
                )

                # DEBUG: Log do valor lido (a cada 10 leituras para não poluir)
                if not hasattr(self, '_poll_count'):
                    self._poll_count = 0
                self._poll_count += 1
                if self._poll_count % 20 == 0:  # A cada 10 segundos (20 * 500ms)
                    logger.debug(f"🔍 Registro {register_to_use}: {screen_id}")

                # Validar se o valor está no range esperado (0-255 para ID de tela)
                if screen_id is not None and 0 <= screen_id <= 255:
                    # Valor válido - resetar contador de erros
                    self.connection_errors = 0
                    self.modbus_connected = True

                    # Verificar se a tela mudou
                    if screen_id != self.last_screen_id:
                        logger.info(f"📺 Mudança de tela detectada: {self.last_screen_id} → {screen_id} (registro {register_to_use})")
                        self.current_screen_id = screen_id
                        self.last_screen_id = screen_id

                        # Broadcast para todos os clientes
                        if self.clients:
                            state = self._get_display_state()
                            await self._broadcast(state)

                elif screen_id is not None and not fallback_attempted:
                    # Valor fora do range - tentar fallback para registro 4078
                    logger.warning(f"⚠️  Registro {register_to_use} retornou valor inválido: {screen_id}")
                    logger.info(f"🔄 Tentando fallback para registro {ACTIVE_SCREEN_REGISTER_FALLBACK}...")
                    register_to_use = ACTIVE_SCREEN_REGISTER_FALLBACK
                    fallback_attempted = True

                elif screen_id is None:
                    # Falha na leitura - incrementar contador de erros
                    self.connection_errors += 1

                    # Tentar fallback se ainda não tentou
                    if not fallback_attempted:
                        logger.warning(f"⚠️  Falha ao ler registro {register_to_use}")
                        logger.info(f"🔄 Tentando fallback para registro {ACTIVE_SCREEN_REGISTER_FALLBACK}...")
                        register_to_use = ACTIVE_SCREEN_REGISTER_FALLBACK
                        fallback_attempted = True
                    else:
                        logger.error(f"❌ Falha ao ler ambos os registros ({ACTIVE_SCREEN_REGISTER} e {ACTIVE_SCREEN_REGISTER_FALLBACK}) - Erro {self.connection_errors}/{self.max_connection_errors}")

            except Exception as e:
                logger.error(f"Erro no polling de tela ativa: {e}")
                self.connection_errors += 1
                # Continuar tentando - não crashar o servidor

            # Polling a cada 500ms
            await asyncio.sleep(0.5)

    async def _monitor_connection_health(self):
        """
        Monitora saúde da conexão Modbus e tenta reconectar se necessário
        """
        logger.info("🏥 Iniciando monitor de saúde da conexão...")

        while True:
            try:
                # Verificar se excedeu limite de erros
                if self.connection_errors >= self.max_connection_errors:
                    logger.warning(f"⚠️  Muitos erros consecutivos ({self.connection_errors}). Tentando reconectar...")
                    self.modbus_connected = False

                    # Notificar clientes
                    if self.clients:
                        await self._broadcast({
                            'connection_status': 'reconnecting',
                            'message': 'Tentando reconectar ao CLP...'
                        })

                    # Tentar reconectar
                    await asyncio.to_thread(self.modbus.disconnect)
                    await asyncio.sleep(2)  # Aguardar antes de reconectar

                    success = await asyncio.to_thread(self.modbus.connect)

                    if success:
                        logger.info("✅ Reconexão bem-sucedida!")
                        self.modbus_connected = True
                        self.connection_errors = 0

                        # Notificar clientes
                        if self.clients:
                            await self._broadcast({
                                'connection_status': 'connected',
                                'message': 'Reconectado ao CLP'
                            })
                    else:
                        logger.error("❌ Falha na reconexão. Tentando novamente em 10s...")
                        await asyncio.sleep(10)

            except Exception as e:
                logger.error(f"Erro no monitor de saúde: {e}")

            # Verificar a cada 5 segundos
            await asyncio.sleep(5)

    def _get_display_state(self) -> Dict[str, Any]:
        """
        Retorna estado do display baseado na tela ativa do CLP

        Returns:
            {
                'screen_id': int,
                'line1': str,
                'line2': str,
                'mode': 'mirror',
                'connection_status': str,
                'modbus_connected': bool
            }
        """
        screen_id_str = str(self.current_screen_id)

        # Determinar status de conexão
        if not self.modbus_connected:
            connection_status = 'disconnected'
        elif self.connection_errors > 0:
            connection_status = 'unstable'
        else:
            connection_status = 'connected'

        # Buscar tela no mapeamento
        if screen_id_str not in self.screens_map:
            logger.warning(f"Tela {self.current_screen_id} não encontrada no mapeamento")
            return {
                'screen_id': self.current_screen_id,
                'line1': f'TELA {self.current_screen_id} NAO MAPEADA'.ljust(20),
                'line2': ''.ljust(20),
                'mode': 'mirror',
                'connection_status': connection_status,
                'modbus_connected': self.modbus_connected
            }

        screen_data = self.screens_map[screen_id_str]

        # Extrair linhas de texto
        line1 = screen_data.get('TEXT1', '').ljust(20)[:20]
        line2 = screen_data.get('TEXT2', '').ljust(20)[:20]

        # TODO: Ler variáveis dinâmicas se screen_data['FIELDS'] > 0
        # Por enquanto, apenas exibir texto estático

        return {
            'screen_id': self.current_screen_id,
            'line1': line1,
            'line2': line2,
            'mode': 'mirror',
            'connection_status': connection_status,
            'modbus_connected': self.modbus_connected
        }

    async def _send_key_to_clp(self, key_code: int):
        """
        Envia tecla pressionada para o CLP via Modbus
        Pulsa o coil por 200ms
        """
        try:
            logger.info(f"⌨️  Tecla pressionada: {key_code}")

            # Escrever coil ON
            await asyncio.to_thread(
                self.modbus.write_coil,
                key_code,
                True
            )

            # Aguardar 200ms
            await asyncio.sleep(0.2)

            # Escrever coil OFF
            await asyncio.to_thread(
                self.modbus.write_coil,
                key_code,
                False
            )

            logger.info(f"✓ Tecla {key_code} enviada ao CLP")

        except Exception as e:
            logger.error(f"Erro ao enviar tecla {key_code} para CLP: {e}")

    async def _broadcast(self, message: Dict[str, Any]):
        """
        Broadcast message to all connected clients
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
    parser = argparse.ArgumentParser(description='IHM v5 Server - Mirror Mode')
    parser.add_argument('--port', type=str, default=None, help='Porta serial (ex: /dev/ttyUSB0)')
    parser.add_argument('--stub', action='store_true', help='Modo stub (sem CLP real)')
    parser.add_argument('--ws-port', type=int, default=8085, help='Porta WebSocket (padrão: 8085)')

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
    server = IHMv5Server(modbus_client, host='localhost', port=args.ws_port)

    try:
        await server.start()
    except KeyboardInterrupt:
        logger.info("Servidor interrompido pelo usuário")
    except Exception as e:
        logger.error(f"Erro fatal: {e}")
        raise


if __name__ == '__main__':
    asyncio.run(main())
