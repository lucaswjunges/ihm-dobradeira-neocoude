#!/usr/bin/env python3
"""Teste rápido do toggle de modo"""
import asyncio
import websockets
import json

async def test():
    uri = "ws://localhost:8765"

    async with websockets.connect(uri) as ws:
        # Receber estado inicial
        msg = await ws.recv()
        data = json.loads(msg)
        print(f"Estado inicial: {data.get('type')}")
        if 'data' in data:
            print(f"  Modo: {data['data'].get('mode_text', 'N/A')}")

        # Enviar toggle
        print("\nEnviando toggle_mode...")
        await ws.send(json.dumps({'action': 'toggle_mode'}))

        # Aguardar resposta
        for i in range(5):
            msg = await ws.recv()
            data = json.loads(msg)
            print(f"\nMensagem {i+1}: {data.get('type')}")

            if data.get('type') == 'mode_changed':
                print(f"  ✅ Modo alterado!")
                print(f"  Antes: {data.get('mode_antes')}")
                print(f"  Depois: {data.get('mode_depois')}")
                break

asyncio.run(test())
