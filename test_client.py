"""
test_client.py

Simple WebSocket client to test HMI server connectivity.
"""

import asyncio
import json
import websockets


async def test_connection():
    """Test WebSocket connection and button press"""
    print("Connecting to ws://localhost:8080...")

    try:
        async with websockets.connect('ws://localhost:8080') as websocket:
            print("✓ Connected!")

            # Receive initial state
            initial = await websocket.recv()
            message = json.loads(initial)
            print(f"\n✓ Received {message['type']}")

            if message['type'] == 'initial_state':
                state = message['data']
                print(f"  - Encoder angle: {state.get('encoder_angle')}°")
                print(f"  - Connected: {state.get('connected')}")
                print(f"  - Poll count: {state.get('poll_count')}")

            # Test button press
            print("\nTesting button press (K1)...")
            await websocket.send(json.dumps({
                'action': 'press_button',
                'button': 'K1'
            }))

            # Wait for response
            response = await websocket.recv()
            resp_msg = json.loads(response)
            print(f"✓ Button response: {resp_msg}")

            # Wait for state updates
            print("\nListening for state updates (5 seconds)...")
            try:
                for i in range(5):
                    update = await asyncio.wait_for(websocket.recv(), timeout=1.0)
                    update_msg = json.loads(update)
                    if update_msg['type'] == 'state_update':
                        print(f"  Update {i+1}: {update_msg['data']}")
            except asyncio.TimeoutError:
                pass

            print("\n✓ Test complete!")

    except Exception as e:
        print(f"✗ Error: {e}")


if __name__ == '__main__':
    asyncio.run(test_connection())
