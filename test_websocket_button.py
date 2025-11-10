"""
test_websocket_button.py

Testa pressionar botão K1 via WebSocket e verifica resposta.
"""

import asyncio
import websockets
import json

async def test_button_press():
    uri = "ws://localhost:8080"

    print("=" * 80)
    print("WEBSOCKET BUTTON PRESS TEST")
    print("=" * 80)

    async with websockets.connect(uri) as websocket:
        print(f"✓ Connected to {uri}\n")

        # Receber estado inicial
        print("Waiting for initial state...")
        initial_msg = await websocket.recv()
        data = json.loads(initial_msg)
        print(f"✓ Received: {data['type']}")

        if data['type'] == 'initial_state':
            print(f"  Encoder angle: {data['data'].get('encoder_angle', 'N/A')}")
            print(f"  Connected: {data['data'].get('connected', 'N/A')}")
            print(f"  Poll count: {data['data'].get('poll_count', 'N/A')}")

        # Enviar comando para pressionar K1
        print("\nSending K1 button press command...")
        command = {
            'action': 'press_button',
            'button': 'K1'
        }
        await websocket.send(json.dumps(command))

        # Esperar resposta
        print("Waiting for response...")
        response_msg = await asyncio.wait_for(websocket.recv(), timeout=5.0)
        response = json.loads(response_msg)

        print(f"\n✓ Response received:")
        print(f"  Type: {response.get('type')}")
        print(f"  Success: {response.get('success')}")
        print(f"  Button: {response.get('button')}")

        # Receber alguns state updates
        print("\nListening for state updates (5 seconds)...")
        try:
            for i in range(5):
                update_msg = await asyncio.wait_for(websocket.recv(), timeout=2.0)
                update = json.loads(update_msg)
                if update.get('type') == 'state_update':
                    if 'encoder_angle' in update.get('data', {}):
                        print(f"  Encoder: {update['data']['encoder_angle']}")
        except asyncio.TimeoutError:
            print("  (No more updates)")

    print("\n" + "=" * 80)
    print("Test complete!")
    print("=" * 80)

if __name__ == '__main__':
    asyncio.run(test_button_press())
