#!/usr/bin/env python3
"""
Servidor IHM Simplificado
Apenas lê encoder e serve interface web
Sem tentativas de escrever em registros de supervisão
"""

import asyncio
import websockets
import json
import time
from pathlib import Path
from aiohttp import web
from pymodbus.client import ModbusSerialClient

# Configuração Modbus (validada)
MODBUS_PORT = '/dev/ttyUSB0'
MODBUS_BAUDRATE = 57600
MODBUS_SLAVE = 1

# Cliente Modbus global
modbus_client = None
websocket_clients = set()

def init_modbus():
    """Inicializa conexão Modbus"""
    global modbus_client
    try:
        modbus_client = ModbusSerialClient(
            port=MODBUS_PORT,
            baudrate=MODBUS_BAUDRATE,
            parity='N',
            stopbits=1,
            timeout=1
        )
        if modbus_client.connect():
            print(f"✓ Modbus conectado: {MODBUS_PORT}")
            return True
        else:
            print(f"✗ Modbus não conectou")
            return False
    except Exception as e:
        print(f"✗ Erro Modbus: {e}")
        return False

def read_encoder():
    """Lê valor do encoder (32-bit)"""
    if not modbus_client or not modbus_client.connected:
        return None

    try:
        result = modbus_client.read_holding_registers(
            address=1238,  # 0x04D6
            count=2,
            slave=MODBUS_SLAVE
        )

        if not result.isError():
            msw = result.registers[0]
            lsw = result.registers[1]
            value_32 = (msw << 16) | lsw
            return value_32
        return None
    except:
        return None

async def handle_websocket(websocket, path):
    """Handler WebSocket"""
    global websocket_clients
    websocket_clients.add(websocket)
    print(f"✓ Cliente WebSocket conectado (total: {len(websocket_clients)})")

    try:
        async for message in websocket:
            # Receber comandos do cliente
            try:
                data = json.loads(message)
                print(f"Recebido: {data}")
                # TODO: Processar comandos (pressionar teclas, etc)
            except json.JSONDecodeError:
                pass
    except websockets.exceptions.ConnectionClosed:
        pass
    finally:
        websocket_clients.remove(websocket)
        print(f"✗ Cliente WebSocket desconectado (total: {len(websocket_clients)})")

async def broadcast_state():
    """Envia estado da máquina para todos os clientes WebSocket"""
    while True:
        if websocket_clients:
            # Ler encoder
            encoder = read_encoder()

            # Criar estado
            state = {
                'encoder': encoder if encoder is not None else 0,
                'angle': round(encoder / 10.0, 1) if encoder is not None else 0.0,
                'connected': encoder is not None,
                'timestamp': time.time()
            }

            # Enviar para todos os clientes
            message = json.dumps(state)
            disconnected = set()

            for client in websocket_clients:
                try:
                    await client.send(message)
                except:
                    disconnected.add(client)

            # Remover clientes desconectados
            websocket_clients.difference_update(disconnected)

        await asyncio.sleep(0.5)  # Atualizar a cada 500ms

async def http_handler(request):
    """Serve index.html"""
    html_path = Path(__file__).parent / 'static' / 'index.html'
    if html_path.exists():
        return web.FileResponse(html_path)
    else:
        return web.Response(text="index.html não encontrado", status=404)

async def main():
    """Função principal"""
    print("=" * 60)
    print("IHM WEB - DOBRADEIRA NEOCOUDE-HD-15 (SIMPLIFICADO)")
    print("=" * 60)
    print()

    # Inicializar Modbus
    if init_modbus():
        # Testar leitura
        encoder = read_encoder()
        if encoder is not None:
            print(f"✓ Encoder lido: {encoder} pulsos ({encoder/10.0:.1f}°)")
        else:
            print("⚠ Encoder não respondeu (CLP pode estar desligado)")

    # Iniciar WebSocket server
    ws_server = await websockets.serve(handle_websocket, 'localhost', 8765)
    print(f"✓ WebSocket: ws://localhost:8765")

    # Iniciar HTTP server
    app = web.Application()
    app.router.add_get('/', http_handler)
    app.router.add_static('/static', Path(__file__).parent / 'static')
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, 'localhost', 8080)
    await site.start()
    print(f"✓ HTTP: http://localhost:8080")
    print()
    print("Servidor rodando. Pressione Ctrl+C para parar")
    print()

    # Iniciar broadcast de estado
    broadcast_task = asyncio.create_task(broadcast_state())

    # Manter rodando
    try:
        await asyncio.Future()  # Rodar para sempre
    except KeyboardInterrupt:
        print("\nEncerrando...")
        broadcast_task.cancel()
        if modbus_client:
            modbus_client.close()

if __name__ == "__main__":
    asyncio.run(main())
