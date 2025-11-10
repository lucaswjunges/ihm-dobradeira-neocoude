"""
test_websocket_inputs.py

Conecta ao WebSocket e monitora updates de entradas digitais.
"""

import asyncio
import websockets
import json

async def monitor_inputs():
    uri = "ws://localhost:8080"

    print("=" * 80)
    print("MONITORING DIGITAL INPUTS VIA WEBSOCKET")
    print("=" * 80)

    async with websockets.connect(uri) as websocket:
        print(f"✓ Connected to {uri}\n")

        # Receive initial state
        initial_msg = await websocket.recv()
        data = json.loads(initial_msg)

        if data['type'] == 'initial_state':
            print("Initial state received:")
            print(f"  Connected: {data['data'].get('connected')}")
            print(f"  Encoder angle: {data['data'].get('encoder_angle')}")

            if 'digital_inputs' in data['data']:
                print("\n  Digital Inputs:")
                for name, value in data['data']['digital_inputs'].items():
                    symbol = "●" if value else "○"
                    print(f"    {name}: {symbol} {value}")
            else:
                print("  ⚠️ No digital_inputs in initial state!")

        print("\n" + "=" * 80)
        print("Monitoring for updates (press Ctrl+C to stop)...")
        print("=" * 80)

        # Monitor updates
        try:
            while True:
                msg = await asyncio.wait_for(websocket.recv(), timeout=2.0)
                data = json.loads(msg)

                if data.get('type') == 'state_update':
                    if 'digital_inputs' in data.get('data', {}):
                        print(f"\n[UPDATE] Digital Inputs:")
                        for name, value in data['data']['digital_inputs'].items():
                            symbol = "●" if value else "○"
                            print(f"  {name}: {symbol} {value}")

                    if 'encoder_angle' in data.get('data', {}):
                        print(f"[UPDATE] Encoder: {data['data']['encoder_angle']}°")

        except asyncio.TimeoutError:
            print("\n(No updates in last 2 seconds)")
        except KeyboardInterrupt:
            print("\n\nStopped by user")

if __name__ == '__main__':
    asyncio.run(monitor_inputs())
