#!/usr/bin/env python3
"""
Main Server - IHM Web com Threading
====================================
Servidor principal que usa threading para Modbus (evita block do event loop)
"""

import asyncio
import websockets
import json
import threading
import time
from pathlib import Path
from typing import Set
from aiohttp import web

from modbus_client import ModbusClientWrapper
import modbus_map as mm

# === GLOBALS ===
clients: Set[websockets.WebSocketServerProtocol] = set()
modbus_client = None
machine_state = {}
state_lock = threading.Lock()

# === MODBUS POLLING (THREAD SEPARADA) ===

def modbus_polling_thread():
    """Thread separada para polling Modbus (não bloqueia event loop)"""
    global machine_state

    print("✓ Thread Modbus iniciada")
    poll_count = 0

    while True:
        try:
            poll_count += 1

            with state_lock:
                # Lê encoder (a cada ciclo)
                encoder_raw = modbus_client.read_32bit(
                    mm.ENCODER['ANGLE_MSW'],
                    mm.ENCODER['ANGLE_LSW']
                )
                if encoder_raw is not None:
                    machine_state['encoder_raw'] = encoder_raw
                    machine_state['encoder_degrees'] = mm.clp_to_degrees(encoder_raw)
                    machine_state['encoder_angle'] = machine_state['encoder_degrees']

                # Lê LEDs (a cada ciclo)
                leds = modbus_client.read_leds()
                if leds:
                    machine_state['leds'] = leds

                # Estados críticos (a cada ciclo)
                modbus_enabled = modbus_client.read_coil(mm.CRITICAL_STATES['MODBUS_SLAVE_ENABLED'])
                if modbus_enabled is not None:
                    machine_state['modbus_enabled'] = modbus_enabled

                cycle_active = modbus_client.read_coil(mm.CRITICAL_STATES['CYCLE_ACTIVE'])
                if cycle_active is not None:
                    machine_state['cycle_active'] = cycle_active

                # Modo
                mode_bit = modbus_client.read_coil(mm.CRITICAL_STATES['MODE_BIT_REAL'])
                if mode_bit is not None:
                    machine_state['mode_bit_02ff'] = mode_bit
                    machine_state['mode_text'] = "AUTO" if mode_bit else "MANUAL"
                    machine_state['mode_manual'] = not mode_bit

                # Lê ângulos do CLP (a cada 20 ciclos = ~5 segundos)
                if poll_count % 20 == 0:
                    angles = modbus_client.read_all_bend_angles()
                    if angles:
                        machine_state['bend_1_left'] = angles.get('bend_1', 0.0)
                        machine_state['bend_2_left'] = angles.get('bend_2', 0.0)
                        machine_state['bend_3_left'] = angles.get('bend_3', 0.0)
                        machine_state['angles'] = {
                            'bend_1_left': angles.get('bend_1', 0.0),
                            'bend_2_left': angles.get('bend_2', 0.0),
                            'bend_3_left': angles.get('bend_3', 0.0),
                        }

                # Lê velocidade do CLP (a cada 10 ciclos = ~2.5 segundos)
                if poll_count % 10 == 0:
                    speed = modbus_client.read_speed_class()
                    if speed is not None:
                        machine_state['speed_class'] = speed

                # Status de conexão
                machine_state['connected'] = modbus_client.connected
                machine_state['modbus_connected'] = modbus_client.connected
                machine_state['last_update'] = time.time()

        except Exception as e:
            print(f"✗ Erro no polling Modbus: {e}")
            import traceback
            traceback.print_exc()
            with state_lock:
                machine_state['modbus_connected'] = False

        time.sleep(0.25)  # 250ms

# === WEBSOCKET HANDLER ===

async def websocket_handler(websocket, path):
    """Handler WebSocket"""
    clients.add(websocket)
    print(f"✓ Cliente WebSocket conectado: {websocket.remote_address}")

    try:
        # Envia estado inicial
        with state_lock:
            initial_state = machine_state.copy()

        await websocket.send(json.dumps({
            'type': 'full_state',
            'data': initial_state
        }))

        # Loop de recebimento
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

            print(f"📝 Escrevendo ângulo: Dobra {bend_num} = {angle}°")

            if bend_num in [1, 2, 3]:
                success = modbus_client.write_bend_angle(bend_num, angle)
                print(f"{'✓' if success else '✗'} Ângulo dobra {bend_num}: {angle}°")

                # Atualiza estado imediatamente
                with state_lock:
                    machine_state[f'bend_{bend_num}_left'] = angle
                    if 'angles' not in machine_state:
                        machine_state['angles'] = {}
                    machine_state['angles'][f'bend_{bend_num}_left'] = angle

                await websocket.send(json.dumps({
                    'type': 'angle_response',
                    'bend': bend_num,
                    'angle': angle,
                    'success': success
                }))

        elif action == 'write_speed':
            speed = data.get('speed')
            print(f"📝 Alterando velocidade: {speed} RPM")

            if speed in [5, 10, 15]:
                success = modbus_client.write_speed_class(speed)
                print(f"{'✓' if success else '✗'} Velocidade: {speed} RPM")

                # Atualiza estado imediatamente
                with state_lock:
                    machine_state['speed_class'] = speed

                await websocket.send(json.dumps({
                    'type': 'speed_response',
                    'speed': speed,
                    'success': success
                }))
            else:
                print(f"✗ Velocidade inválida: {speed}")
                await websocket.send(json.dumps({
                    'type': 'error',
                    'message': f'Velocidade inválida: {speed}. Use 5, 10 ou 15 RPM.'
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
            s0 = modbus_client.write_coil(mm.DIGITAL_OUTPUTS['S0'], False)
            s1 = modbus_client.write_coil(mm.DIGITAL_OUTPUTS['S1'], False)
            await websocket.send(json.dumps({
                'type': 'emergency_response',
                'success': s0 and s1
            }))

    except Exception as e:
        print(f"✗ Erro processando comando: {e}")

# === BROADCAST LOOP ===

async def broadcast_loop():
    """Envia atualizações para clientes WebSocket"""
    previous_state = {}

    while True:
        await asyncio.sleep(0.5)

        if not clients:
            with state_lock:
                previous_state = machine_state.copy()
            continue

        # Pega apenas mudanças
        with state_lock:
            current_state = machine_state.copy()

        changes = {}
        for key, value in current_state.items():
            if key not in previous_state or previous_state[key] != value:
                changes[key] = value

        if changes:
            message = json.dumps({
                'type': 'state_update',
                'data': changes
            })

            disconnected = set()
            for client in clients:
                try:
                    await client.send(message)
                except:
                    disconnected.add(client)

            clients -= disconnected

        previous_state = current_state

# === HTTP HANDLERS ===

async def http_index(request):
    """Serve index.html"""
    html_path = Path(__file__).parent / 'static' / 'index.html'
    if html_path.exists():
        return web.FileResponse(html_path)
    return web.Response(text="404 - index.html não encontrado", status=404)

async def http_test(request):
    """Endpoint de teste"""
    with state_lock:
        state_copy = machine_state.copy()

    return web.json_response({
        'status': 'ok',
        'modbus_connected': state_copy.get('modbus_connected', False),
        'encoder_degrees': state_copy.get('encoder_degrees', 0),
        'clients': len(clients)
    })

# === MAIN ===

async def main():
    global modbus_client, machine_state

    print("=" * 60)
    print("IHM WEB - DOBRADEIRA NEOCOUDE-HD-15 (THREADED)")
    print("=" * 60)
    print()

    # 1. Inicializa Modbus
    modbus_client = ModbusClientWrapper(stub_mode=False, port='/dev/ttyUSB0')

    if not modbus_client.connected:
        print("⚠️  AVISO: Modbus não conectado")

    # Estado inicial
    with state_lock:
        machine_state = {
            'encoder_raw': 0,
            'encoder_degrees': 0.0,
            'encoder_angle': 0.0,
            'leds': {},
            'connected': modbus_client.connected,
            'modbus_connected': modbus_client.connected,
            'last_update': time.time()
        }

    # 2. Inicia thread Modbus
    modbus_thread = threading.Thread(target=modbus_polling_thread, daemon=True)
    modbus_thread.start()

    # 3. Inicia broadcast
    broadcast_task = asyncio.create_task(broadcast_loop())

    # 4. Servidor HTTP
    app = web.Application()
    app.router.add_get('/', http_index)
    app.router.add_get('/test', http_test)
    app.router.add_static('/static', Path(__file__).parent / 'static')

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 8080)
    await site.start()

    print("✓ HTTP Server: http://0.0.0.0:8080")

    # 5. Servidor WebSocket
    ws_server = await websockets.serve(websocket_handler, '0.0.0.0', 8765)

    print("✓ WebSocket Server: ws://0.0.0.0:8765")
    print()
    print(f"✓ Servidor iniciado com sucesso!")
    print(f"  Acesse: http://192.168.0.213:8080")
    print()
    print("Pressione Ctrl+C para parar")
    print("=" * 60)

    # Mantém rodando
    await asyncio.Future()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n✓ Servidor parado")
