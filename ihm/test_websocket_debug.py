#!/usr/bin/env python3
"""
Teste de conexão WebSocket - Simula navegador
"""
import asyncio
import websockets
import json

async def test_websocket():
    uri = "ws://localhost:8765"
    print(f"🔌 Conectando em {uri}...")

    try:
        async with websockets.connect(uri) as websocket:
            print("✅ Conectado!")

            # Aguarda mensagem do servidor
            print("\n⏳ Aguardando mensagem do servidor...")
            message = await websocket.recv()
            data = json.loads(message)

            print(f"\n📨 Mensagem recebida:")
            print(f"   Tipo: {data.get('type')}")

            if 'data' in data:
                state = data['data']
                print(f"\n📊 Estado recebido ({len(state)} campos):")
                print(f"   modbus_connected: {state.get('modbus_connected')}")
                print(f"   connected: {state.get('connected')}")
                print(f"   encoder_raw: {state.get('encoder_raw')}")
                print(f"   encoder_degrees: {state.get('encoder_degrees')}")

                # Mostra todos os campos
                print(f"\n📝 Todos os campos:")
                for key, value in sorted(state.items()):
                    print(f"   {key}: {value}")
            else:
                print(f"   Sem campo 'data'")

    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_websocket())
