#!/usr/bin/env python3
"""
Servidor IHM Web - Versão Simplificada e Robusta
=================================================
- HTTP server (aiohttp) na porta 8080
- WebSocket server (websockets) na porta 8765
- Modbus RTU cliente
- Broadcasting automático de estado
"""

import asyncio
import json
import websockets
from aiohttp import web
from pathlib import Path
from typing import Set
import signal
import sys

from modbus_client import ModbusClientWrapper
from state_manager import MachineStateManager
import modbus_map as mm

# Clientes WebSocket conectados
clients: Set[websockets.WebSocketServerProtocol] = set()

# Componentes globais
modbus_client = None
state_manager = None

# === HTTP HANDLERS ===

async def http_index(request):
    """Serve index.html"""
    html_path = Path(__file__).parent / 'static' / 'index.html'
    if html_path.exists():
        return web.FileResponse(html_path)
    return web.Response(text="404 - Arquivo não encontrado", status=404)

async def http_test(request):
    """Endpoint de teste"""
    return web.json_response({
        'status': 'ok',
        'modbus_connected': modbus_client.connected if modbus_client else False,
        'clients': len(clients)
    })

# === WEBSOCKET HANDLER ===

async def websocket_handler(websocket, path):
    """Handler WebSocket"""
    clients.add(websocket)
    print(f"✓ Cliente WebSocket conectado: {websocket.remote_address}")

    try:
        # Envia estado completo inicial
        if state_manager:
            initial_state = state_manager.get_state()
            await websocket.send(json.dumps({
                'type': 'full_state',
                'data': initial_state
            }))

        # Loop de recebimento de comandos
        async for message in websocket:
            await handle_client_command(websocket, message)

    except websockets.exceptions.ConnectionClosed:
        print(f"✗ Cliente WebSocket desconectado: {websocket.remote_address}")
    finally:
        clients.discard(websocket)

async def handle_client_command(websocket, message: str):
    """Processa comando do cliente"""
    try:
        data = json.loads(message)
        action = data.get('action')

        print(f"📨 Comando recebido: {action}")

        if action == 'press_key':
            key_name = data.get('key')
            addr = None

            if key_name in mm.KEYBOARD_NUMERIC:
                addr = mm.KEYBOARD_NUMERIC[key_name]
            elif key_name in mm.KEYBOARD_FUNCTION:
                addr = mm.KEYBOARD_FUNCTION[key_name]

            if addr:
                success = modbus_client.press_key(addr)
                await websocket.send(json.dumps({
                    'type': 'key_response',
                    'key': key_name,
                    'success': success
                }))

        elif action == 'write_angle':
            bend_num = data.get('bend')
            angle = float(data.get('angle'))

            if bend_num in [1, 2, 3]:
                success = modbus_client.write_bend_angle(bend_num, angle)
                await websocket.send(json.dumps({
                    'type': 'angle_response',
                    'bend': bend_num,
                    'angle': angle,
                    'success': success
                }))

        elif action == 'write_speed':
            speed = data.get('speed')
            if speed in [5, 10, 15]:
                success = modbus_client.write_speed_class(speed)
                await websocket.send(json.dumps({
                    'type': 'speed_response',
                    'speed': speed,
                    'success': success
                }))

        elif action == 'write_output':
            output_name = data.get('output')
            value = data.get('value')

            if output_name in mm.DIGITAL_OUTPUTS:
                addr = mm.DIGITAL_OUTPUTS[output_name]
                success = modbus_client.write_coil(addr, value)
                await websocket.send(json.dumps({
                    'type': 'output_response',
                    'output': output_name,
                    'value': value,
                    'success': success
                }))

        elif action == 'emergency_stop':
            s0_ok = modbus_client.write_coil(mm.DIGITAL_OUTPUTS['S0'], False)
            s1_ok = modbus_client.write_coil(mm.DIGITAL_OUTPUTS['S1'], False)
            await websocket.send(json.dumps({
                'type': 'emergency_response',
                'success': s0_ok and s1_ok
            }))

    except Exception as e:
        print(f"✗ Erro processando comando: {e}")

# === BROADCAST LOOP ===

async def broadcast_loop():
    """Envia atualizações para todos os clientes"""
    previous_state = {}

    while True:
        await asyncio.sleep(0.5)  # 500ms

        if not clients:
            previous_state = state_manager.get_state()
            continue

        # Pega apenas mudanças
        changes = state_manager.get_changes(previous_state)

        if changes:
            message = json.dumps({
                'type': 'state_update',
                'data': changes
            })

            # Envia para todos os clientes
            disconnected = set()
            for client in clients:
                try:
                    await client.send(message)
                except:
                    disconnected.add(client)

            # Remove desconectados
            clients -= disconnected

        previous_state = state_manager.get_state()

# === MAIN ===

async def main():
    global modbus_client, state_manager

    print("=" * 60)
    print("IHM WEB - DOBRADEIRA NEOCOUDE-HD-15")
    print("=" * 60)
    print()

    # 1. Inicializa Modbus
    modbus_client = ModbusClientWrapper(stub_mode=False, port='/dev/ttyUSB0')

    if not modbus_client.connected:
        print("⚠️  AVISO: Modbus não conectado - servidor continuará rodando")

    # 2. Inicializa State Manager
    state_manager = MachineStateManager(modbus_client)

    # 3. Inicia polling
    polling_task = asyncio.create_task(state_manager.start_polling())

    # 4. Inicia broadcast
    broadcast_task = asyncio.create_task(broadcast_loop())

    # 5. Servidor HTTP
    app = web.Application()
    app.router.add_get('/', http_index)
    app.router.add_get('/test', http_test)
    app.router.add_static('/static', Path(__file__).parent / 'static')

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 8080)
    await site.start()

    print("✓ HTTP Server: http://0.0.0.0:8080")

    # 6. Servidor WebSocket
    ws_server = await websockets.serve(websocket_handler, '0.0.0.0', 8765)

    print("✓ WebSocket Server: ws://0.0.0.0:8765")
    print()
    print("Servidor iniciado com sucesso!")
    print(f"Acesse: http://192.168.0.213:8080")
    print()
    print("Pressione Ctrl+C para parar")
    print("=" * 60)

    # Mantém rodando
    await asyncio.Future()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n✓ Servidor parado pelo usuário")
