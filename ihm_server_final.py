"""
ihm_server_final.py

Servidor WebSocket COMPLETO para IHM NEOCOUDE-HD-15
Suporta LEITURA e ESCRITA de todos os registros do CLP

Features:
- Leitura periódica (encoder, I/Os, ângulos)
- Envio de teclas (pulso ON/OFF)
- ESCRITA de ângulos (setpoints)
- Validação de valores
- Logs completos
"""

import asyncio
import json
import logging
import argparse
import signal
import sys
from datetime import datetime

# Importar cliente Modbus
import modbus_client

try:
    import websockets
except ImportError:
    print("❌ websockets não instalado! Instale com: pip3 install websockets")
    sys.exit(1)

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ihm_server_final.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Conjunto de clientes conectados
connected_clients = set()

# Cliente Modbus global
modbus: modbus_client.ModbusClient = None

# Estado do sistema
system_state = {
    'server_started': None,
    'clients_connected': 0,
    'modbus_connected': False,
    'last_update': None
}


async def broadcast_to_clients(message: dict):
    """
    Envia mensagem para todos os clientes conectados

    Args:
        message: Dicionário JSON para enviar
    """
    if not connected_clients:
        return

    message_json = json.dumps(message)
    disconnected = set()

    for client in connected_clients:
        try:
            await client.send(message_json)
        except Exception as e:
            logger.error(f"Erro ao enviar para cliente: {e}")
            disconnected.add(client)

    # Remover clientes desconectados
    connected_clients.difference_update(disconnected)


async def poll_clp_data():
    """
    Loop de polling dos dados do CLP
    Lê encoder, I/Os e ângulos a cada 250ms
    """
    logger.info("Iniciando polling do CLP...")

    while True:
        try:
            # Ler encoder (32-bit, registros 1238/1239)
            encoder = modbus.get_encoder_angle()

            # Ler ângulos
            angle1 = modbus.read_angle_1()
            angle2 = modbus.read_angle_2()
            angle3 = modbus.read_angle_3()

            # Ler entradas digitais E0-E7
            # DESABILITADO: Registros 256-263 não existem neste CLP
            inputs = [False] * 8

            # Ler saídas digitais S0-S7
            # DESABILITADO: Registros 384-391 não existem neste CLP
            outputs = [False] * 8

            # Ler classe de velocidade (registro 2304)
            # DESABILITADO: Registro não validado ainda
            velocidade_classe = 0

            # Ler modo AUTO/MANUAL
            # Bit 02FF (767 dec) - descoberto no ladder ROT1.lad
            # TRUE = AUTO, FALSE = MANUAL
            modo_auto = modbus.read_coil(767) if modbus.connected else None

            # Montar dados
            data = {
                'action': 'update',
                'data': {
                    'encoder': encoder if encoder is not None else 0,
                    'angle1': angle1 if angle1 is not None else 0,
                    'angle2': angle2 if angle2 is not None else 0,
                    'angle3': angle3 if angle3 is not None else 0,
                    'inputs': inputs,
                    'outputs': outputs,
                    'velocidade_classe': velocidade_classe,
                    'modo_auto': modo_auto,  # True = AUTO, False = MANUAL
                    'connected': modbus.connected
                },
                'timestamp': datetime.now().isoformat()
            }

            # Broadcast para clientes
            await broadcast_to_clients(data)

            # Atualizar timestamp
            system_state['last_update'] = datetime.now().isoformat()
            system_state['modbus_connected'] = modbus.connected

        except Exception as e:
            logger.error(f"Erro no polling: {e}")

        # Aguardar 250ms
        await asyncio.sleep(0.25)


async def handle_client_message(websocket, message: str):
    """
    Processa mensagens recebidas do cliente

    Args:
        websocket: Conexão do cliente
        message: Mensagem JSON recebida
    """
    try:
        data = json.loads(message)
        action = data.get('action')

        logger.info(f"Ação recebida: {action}")

        # ===== ENVIAR TECLA =====
        if action == 'press_key':
            key_code = data.get('key_code')

            if key_code is None:
                await websocket.send(json.dumps({
                    'status': 'error',
                    'message': 'key_code não fornecido'
                }))
                return

            # Converter código para nome do botão
            key_map = {
                160: 'K1', 161: 'K2', 162: 'K3', 163: 'K4', 164: 'K5',
                165: 'K6', 166: 'K7', 167: 'K8', 168: 'K9', 169: 'K0',
                220: 'S1', 221: 'S2',
                172: 'UP', 173: 'DOWN',
                37: 'ENTER', 188: 'ESC', 38: 'EDIT', 241: 'LOCK'
            }

            # Se o código não está no mapa, usar endereço diretamente
            if key_code in key_map:
                button_name = key_map[key_code]

                # S1 e S2 precisam de hold_time maior (300ms) para o ladder detectar
                if button_name in ['S1', 'S2']:
                    success = modbus.press_key(button_name, hold_time=0.3)
                else:
                    success = modbus.press_key(button_name)
            else:
                # Enviar pulso diretamente no endereço
                success = modbus.write_coil(key_code, True)
                await asyncio.sleep(0.1)
                success = success and modbus.write_coil(key_code, False)

            if success:
                logger.info(f"Tecla {key_code} enviada com sucesso")
                await websocket.send(json.dumps({
                    'status': 'ok',
                    'action': 'press_key',
                    'key_code': key_code
                }))
            else:
                logger.error(f"Erro ao enviar tecla {key_code}")
                await websocket.send(json.dumps({
                    'status': 'error',
                    'message': f'Erro ao enviar tecla {key_code}'
                }))

        # ===== ESCREVER ÂNGULO =====
        elif action == 'write_angle':
            tela = data.get('tela')
            angle_value = data.get('value')

            if tela is None or angle_value is None:
                await websocket.send(json.dumps({
                    'status': 'error',
                    'message': 'tela ou value não fornecidos'
                }))
                return

            # Validar valor
            if not (0 <= angle_value <= 360):
                await websocket.send(json.dumps({
                    'status': 'error',
                    'message': f'Ângulo fora da faixa (0-360): {angle_value}'
                }))
                return

            # Escrever no registro correto
            success = False
            if tela == 4:
                success = modbus.write_angle_1(angle_value)
            elif tela == 5:
                success = modbus.write_angle_2(angle_value)
            elif tela == 6:
                success = modbus.write_angle_3(angle_value)
            else:
                await websocket.send(json.dumps({
                    'status': 'error',
                    'message': f'Tela inválida: {tela}'
                }))
                return

            if success:
                logger.info(f"Ângulo da Tela {tela} escrito: {angle_value}°")
                await websocket.send(json.dumps({
                    'status': 'ok',
                    'action': 'write_angle',
                    'tela': tela,
                    'value': angle_value
                }))
            else:
                logger.error(f"Erro ao escrever ângulo da Tela {tela}")
                await websocket.send(json.dumps({
                    'status': 'error',
                    'message': f'Erro ao escrever ângulo da Tela {tela}'
                }))

        # ===== AÇÃO DESCONHECIDA =====
        else:
            logger.warning(f"Ação desconhecida: {action}")
            await websocket.send(json.dumps({
                'status': 'error',
                'message': f'Ação desconhecida: {action}'
            }))

    except json.JSONDecodeError as e:
        logger.error(f"Erro ao decodificar JSON: {e}")
        await websocket.send(json.dumps({
            'status': 'error',
            'message': 'JSON inválido'
        }))
    except Exception as e:
        logger.error(f"Erro ao processar mensagem: {e}")
        await websocket.send(json.dumps({
            'status': 'error',
            'message': str(e)
        }))


async def websocket_handler(websocket):
    """
    Handler para conexões WebSocket

    Args:
        websocket: Conexão do cliente
    """
    # Adicionar cliente à lista
    connected_clients.add(websocket)
    system_state['clients_connected'] = len(connected_clients)

    logger.info(f"Cliente conectado. Total de clientes: {len(connected_clients)}")

    try:
        # Enviar estado inicial
        initial_state = {
            'action': 'connected',
            'data': {
                'encoder': modbus.get_encoder_angle() or 0,
                'angle1': modbus.read_angle_1() or 0,
                'angle2': modbus.read_angle_2() or 0,
                'angle3': modbus.read_angle_3() or 0,
                'connected': modbus.connected
            },
            'timestamp': datetime.now().isoformat()
        }
        await websocket.send(json.dumps(initial_state))

        # Loop de recebimento de mensagens
        async for message in websocket:
            await handle_client_message(websocket, message)

    except websockets.exceptions.ConnectionClosed:
        logger.info("Cliente desconectado (conexão fechada)")
    except Exception as e:
        logger.error(f"Erro no handler WebSocket: {e}")
    finally:
        # Remover cliente da lista
        connected_clients.discard(websocket)
        system_state['clients_connected'] = len(connected_clients)
        logger.info(f"Cliente removido. Total de clientes: {len(connected_clients)}")


async def main(port: str, ws_port: int, stub_mode: bool):
    """
    Função principal do servidor

    Args:
        port: Porta serial do CLP (ex: /dev/ttyUSB0)
        ws_port: Porta WebSocket (ex: 8086)
        stub_mode: Se True, usa modo stub (sem CLP)
    """
    global modbus

    logger.info("=" * 80)
    logger.info("IHM SERVIDOR FINAL - NEOCOUDE-HD-15")
    logger.info("=" * 80)
    logger.info(f"Porta serial: {port}")
    logger.info(f"WebSocket: localhost:{ws_port}")
    logger.info(f"Modo: {'STUB (simulação)' if stub_mode else 'LIVE (CLP real)'}")
    logger.info("=" * 80)

    # Inicializar cliente Modbus
    config = modbus_client.ModbusConfig(port=port)
    modbus = modbus_client.ModbusClient(stub_mode=stub_mode, config=config)

    if not stub_mode:
        if modbus.connect():
            logger.info("✓ Conectado ao CLP via Modbus RTU")
            system_state['modbus_connected'] = True
        else:
            logger.error("✗ Falha ao conectar ao CLP!")
            logger.warning("Continuando sem conexão Modbus...")
            system_state['modbus_connected'] = False
    else:
        modbus.connect()
        logger.info("✓ Modo stub inicializado")
        system_state['modbus_connected'] = True

    # Marcar hora de início
    system_state['server_started'] = datetime.now().isoformat()

    # Iniciar servidor WebSocket
    logger.info(f"Iniciando servidor WebSocket na porta {ws_port}...")
    async with websockets.serve(websocket_handler, "localhost", ws_port):
        logger.info(f"✓ Servidor WebSocket rodando em ws://localhost:{ws_port}")

        # Iniciar task de polling
        polling_task = asyncio.create_task(poll_clp_data())

        # Aguardar sinal de parada
        try:
            await asyncio.Future()  # Run forever
        except asyncio.CancelledError:
            logger.info("Servidor sendo encerrado...")
            polling_task.cancel()

    # Desconectar Modbus
    modbus.disconnect()
    logger.info("Servidor encerrado")


def signal_handler(sig, frame):
    """Handler para CTRL+C"""
    logger.info("\nSinal de interrupção recebido (CTRL+C)")
    sys.exit(0)


if __name__ == '__main__':
    # Configurar handler de sinal
    signal.signal(signal.SIGINT, signal_handler)

    # Parse argumentos
    parser = argparse.ArgumentParser(description='IHM Servidor Final - NEOCOUDE-HD-15')
    parser.add_argument('--port', default='/dev/ttyUSB0', help='Porta serial (ex: /dev/ttyUSB0)')
    parser.add_argument('--ws-port', type=int, default=8086, help='Porta WebSocket (padrão: 8086)')
    parser.add_argument('--stub', action='store_true', help='Usar modo stub (simulação)')

    args = parser.parse_args()

    # Executar servidor
    try:
        asyncio.run(main(args.port, args.ws_port, args.stub))
    except KeyboardInterrupt:
        logger.info("\nServidor interrompido pelo usuário")
    except Exception as e:
        logger.error(f"Erro fatal: {e}")
        sys.exit(1)
