"""
IHM v6 Server - Data Provider Mode
Envia dados do CLP (encoder, I/Os, etc.) para o frontend
Frontend controla navegação entre telas localmente
"""

import asyncio
import json
import logging
import argparse
from typing import Set, Dict, Any

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
        logging.FileHandler('ihm_v6_server.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class IHMv6Server:
    """
    IHM v6 - Data Provider Server
    Envia dados do CLP, frontend controla navegação
    """

    def __init__(self, modbus_client: ModbusClient, host: str = 'localhost', port: int = 8086):
        if not WEBSOCKETS_AVAILABLE:
            raise ImportError("websockets não instalado!")

        self.modbus = modbus_client
        self.host = host
        self.port = port

        # Connected clients
        self.clients: Set[WebSocketServerProtocol] = set()

        # Dados do CLP
        self.clp_data = {
            'encoder': 0,
            'inputs': [False] * 8,
            'outputs': [False] * 8,
            'connected': False
        }

    async def start(self):
        """Inicia servidor WebSocket e polling do CLP"""
        logger.info(f"🚀 Iniciando IHM v6 Server (Data Provider) em ws://{self.host}:{self.port}")

        # Start polling dos dados do CLP
        polling_task = asyncio.create_task(self._poll_clp_data())

        # Start WebSocket server
        async with websockets.serve(self._handle_client, self.host, self.port):
            logger.info(f"✓ IHM v6 Server rodando em ws://{self.host}:{self.port}")
            logger.info(f"📱 Abra ihm_v6.html no navegador")
            await asyncio.Future()  # Run forever

    async def _handle_client(self, websocket: WebSocketServerProtocol):
        """Handle new WebSocket client"""
        client_addr = websocket.remote_address
        logger.info(f"Cliente conectado: {client_addr}")

        self.clients.add(websocket)

        try:
            # Enviar estado inicial
            await websocket.send(json.dumps({
                'type': 'state',
                'data': self.clp_data
            }))

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
                await websocket.send(json.dumps({
                    'type': 'state',
                    'data': self.clp_data
                }))

            elif action == 'press_key':
                # Cliente pressionou tecla - enviar para CLP
                key_code = data.get('key_code')
                if key_code is not None:
                    await self._send_key_to_clp(key_code)

        except json.JSONDecodeError:
            logger.error(f"JSON inválido: {message}")
        except Exception as e:
            logger.error(f"Erro ao processar mensagem: {e}")

    async def _poll_clp_data(self):
        """
        Loop de polling dos dados do CLP
        Lê encoder, entradas, saídas a cada 250ms
        """
        logger.info("📡 Iniciando polling de dados do CLP...")

        while True:
            try:
                # Ler encoder (32-bit, registros 1238/1239)
                encoder_msw = await asyncio.to_thread(self.modbus.read_register, 1238)
                encoder_lsw = await asyncio.to_thread(self.modbus.read_register, 1239)

                if encoder_msw is not None and encoder_lsw is not None:
                    encoder_value = (encoder_msw << 16) | encoder_lsw
                    self.clp_data['encoder'] = encoder_value
                    self.clp_data['connected'] = True
                else:
                    self.clp_data['connected'] = False

                # Ler entradas E0-E7
                for i in range(8):
                    value = await asyncio.to_thread(self.modbus.read_discrete_input, 256 + i)
                    if value is not None:
                        self.clp_data['inputs'][i] = value

                # Ler saídas S0-S7
                for i in range(8):
                    value = await asyncio.to_thread(self.modbus.read_coil, 384 + i)
                    if value is not None:
                        self.clp_data['outputs'][i] = value

                # Broadcast para todos os clientes
                if self.clients:
                    await self._broadcast({
                        'type': 'update',
                        'data': self.clp_data
                    })

            except Exception as e:
                logger.error(f"Erro no polling: {e}")
                self.clp_data['connected'] = False

            # Polling a cada 250ms
            await asyncio.sleep(0.25)

    async def _send_key_to_clp(self, key_code: int):
        """Envia tecla para o CLP via Modbus"""
        try:
            logger.info(f"⌨️  Tecla {key_code}")

            await asyncio.to_thread(self.modbus.write_coil, key_code, True)
            await asyncio.sleep(0.1)
            await asyncio.to_thread(self.modbus.write_coil, key_code, False)

            logger.debug(f"✓ Tecla {key_code} OK")

        except Exception as e:
            logger.error(f"Erro ao enviar tecla {key_code}: {e}")

    async def _broadcast(self, message: Dict[str, Any]):
        """Broadcast to all clients"""
        if not self.clients:
            return

        message_json = json.dumps(message)
        disconnected = set()

        for client in self.clients:
            try:
                await client.send(message_json)
            except:
                disconnected.add(client)

        self.clients -= disconnected


async def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='IHM v6 Server')
    parser.add_argument('--port', type=str, default='/dev/ttyUSB0')
    parser.add_argument('--stub', action='store_true')
    parser.add_argument('--ws-port', type=int, default=8086)

    args = parser.parse_args()

    config = ModbusConfig(
        port=args.port,
        baudrate=57600,
        stopbits=2,
        parity='N',
        slave_address=1
    )

    modbus_client = ModbusClient(stub_mode=args.stub, config=config)

    if not modbus_client.connect():
        logger.error("❌ Falha ao conectar ao CLP!")
        if not args.stub:
            return

    logger.info("✓ Conexão Modbus OK")

    server = IHMv6Server(modbus_client, host='localhost', port=args.ws_port)

    try:
        await server.start()
    except KeyboardInterrupt:
        logger.info("Servidor interrompido")


if __name__ == '__main__':
    asyncio.run(main())
