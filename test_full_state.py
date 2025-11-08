"""
test_full_state.py

Testa WebSocket e mostra estado completo com novos dados mapeados
"""

import asyncio
import json
import websockets


async def test():
    print("Conectando ao ws://localhost:8080...")

    async with websockets.connect('ws://localhost:8080') as websocket:
        print("✓ Conectado!\n")

        # Receber estado inicial
        initial = await websocket.recv()
        message = json.loads(initial)

        if message['type'] == 'initial_state':
            state = message['data']

            print("=" * 80)
            print("ESTADO COMPLETO DO CLP")
            print("=" * 80)

            print(f"\n📊 ENCODER:")
            print(f"  Ângulo: {state.get('encoder_angle', 'N/A')}°")
            print(f"  RPM: {state.get('encoder_rpm', 'N/A')}")

            print(f"\n🔢 SETPOINTS DE ÂNGULO:")
            if 'angle_setpoints' in state:
                for name, value in state['angle_setpoints'].items():
                    print(f"  {name:15s}: {value}")
            else:
                print("  (não disponível)")

            print(f"\n📈 SETPOINTS DE QUANTIDADE:")
            if 'quantity_setpoints' in state:
                for name, value in state['quantity_setpoints'].items():
                    print(f"  {name:15s}: {value}")
            else:
                print("  (não disponível)")

            print(f"\n⚙️  BITS DE MODO/CICLO:")
            if 'mode_bits' in state:
                for name, value in state['mode_bits'].items():
                    status = "ON " if value else "OFF"
                    print(f"  {name:25s}: {status}")
            else:
                print("  (não disponível)")

            print(f"\n🔌 ENTRADAS DIGITAIS:")
            if 'digital_inputs' in state:
                for name, value in sorted(state['digital_inputs'].items()):
                    status = "ON " if value else "OFF"
                    print(f"  {name}: {status}")

            print(f"\n💡 SAÍDAS DIGITAIS:")
            if 'digital_outputs' in state:
                for name, value in sorted(state['digital_outputs'].items()):
                    status = "ON " if value else "OFF"
                    print(f"  {name}: {status}")

            print(f"\n📡 DIAGNÓSTICO:")
            print(f"  Conectado: {state.get('connected', 'N/A')}")
            print(f"  Poll count: {state.get('poll_count', 'N/A')}")
            print(f"  Errors: {state.get('error_count', 'N/A')}")
            print(f"  Slave ID: {state.get('plc_slave_address', 'N/A')}")

            print("\n" + "=" * 80)


if __name__ == '__main__':
    asyncio.run(test())
