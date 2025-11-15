#!/usr/bin/env python3
"""Teste completo do sistema IHM"""
import asyncio
import websockets
import json
import time

async def test_full_system():
    uri = "ws://localhost:8765"
    print("=" * 70)
    print(" TESTE COMPLETO DO SISTEMA IHM")
    print("=" * 70)

    async with websockets.connect(uri) as ws:
        # 1. Estado inicial
        print("\n1️⃣ RECEBENDO ESTADO INICIAL...")
        msg = await ws.recv()
        data = json.loads(msg)
        print(f"   Tipo: {data.get('type')}")
        if 'data' in data:
            print(f"   Modo: {data['data'].get('mode_text', 'N/A')}")
            print(f"   Encoder: {data['data'].get('encoder_degrees', 'N/A')}°")

        # 2. Toggle MANUAL → AUTO
        print("\n2️⃣ TESTE TOGGLE: MANUAL → AUTO")
        await ws.send(json.dumps({'action': 'toggle_mode'}))

        for _ in range(3):
            msg = await ws.recv()
            data = json.loads(msg)
            if data.get('type') == 'mode_changed':
                print(f"   ✅ {data.get('mode_antes')} → {data.get('mode_depois')}")
                break
        await asyncio.sleep(1)

        # 3. Toggle AUTO → MANUAL
        print("\n3️⃣ TESTE TOGGLE: AUTO → MANUAL")
        await ws.send(json.dumps({'action': 'toggle_mode'}))

        for _ in range(3):
            msg = await ws.recv()
            data = json.loads(msg)
            if data.get('type') == 'mode_changed':
                print(f"   ✅ {data.get('mode_antes')} → {data.get('mode_depois')}")
                break
        await asyncio.sleep(1)

        # 4. Mais um toggle para confirmar
        print("\n4️⃣ TESTE TOGGLE: MANUAL → AUTO (confirmação)")
        await ws.send(json.dumps({'action': 'toggle_mode'}))

        for _ in range(3):
            msg = await ws.recv()
            data = json.loads(msg)
            if data.get('type') == 'mode_changed':
                print(f"   ✅ {data.get('mode_antes')} → {data.get('mode_depois')}")
                break
        await asyncio.sleep(1)

        # 5. Teste de botão
        print("\n5️⃣ TESTE PRESSIONAR BOTÃO K1")
        await ws.send(json.dumps({'action': 'press_key', 'key': 'K1'}))

        msg = await ws.recv()
        data = json.loads(msg)
        if data.get('type') == 'key_response':
            print(f"   ✅ Resposta: {data.get('success')}")

        # 6. Teste escrita de ângulo
        print("\n6️⃣ TESTE ESCREVER ÂNGULO (Dobra 1 = 45.5°)")
        await ws.send(json.dumps({
            'action': 'write_angle',
            'bend': 1,
            'angle': 45.5
        }))

        msg = await ws.recv()
        data = json.loads(msg)
        if data.get('type') == 'angle_response':
            print(f"   ✅ Sucesso: {data.get('success')}")
            print(f"   Dobra: {data.get('bend')}")

        # 7. Teste mudança de velocidade
        print("\n7️⃣ TESTE MUDANÇA DE VELOCIDADE (K1+K7)")
        await ws.send(json.dumps({'action': 'change_speed'}))

        msg = await ws.recv()
        data = json.loads(msg)
        if data.get('type') == 'speed_response':
            print(f"   ✅ Sucesso: {data.get('success')}")

        print("\n" + "=" * 70)
        print(" TESTE CONCLUÍDO")
        print("=" * 70)

asyncio.run(test_full_system())
