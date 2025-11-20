#!/usr/bin/env python3
"""
Teste rápido: Enviar comando de escrita de ângulo via WebSocket
"""
import asyncio
import websockets
import json
import time

async def test_write_angle():
    print("🔌 Conectando ao servidor WebSocket...")

    try:
        async with websockets.connect('ws://localhost:8765') as ws:
            print("✓ Conectado!")

            # Receber estado inicial
            initial = await ws.recv()
            data = json.loads(initial)
            print(f"\n📥 Estado inicial recebido: {data['type']}")

            # Enviar comando para escrever ângulo
            test_angle = 95.5
            command = {
                'action': 'write_angle',
                'bend': 1,
                'angle': test_angle
            }

            print(f"\n📤 Enviando comando: Gravar Dobra 1 = {test_angle}°")
            await ws.send(json.dumps(command))

            # Aguardar resposta
            response = await asyncio.wait_for(ws.recv(), timeout=5.0)
            resp_data = json.loads(response)

            print(f"\n📥 Resposta recebida:")
            print(f"   Type: {resp_data.get('type')}")
            print(f"   Success: {resp_data.get('success')}")
            print(f"   Bend: {resp_data.get('bend')}")
            print(f"   Angle: {resp_data.get('angle')}")

            if resp_data.get('success'):
                print("\n✅ Ângulo gravado com sucesso via IHM Web!")

                # Aguardar e ler de volta
                print("\n⏳ Aguardando 0.5s para ler de volta...")
                await asyncio.sleep(0.5)

                # Verificar updates
                try:
                    update = await asyncio.wait_for(ws.recv(), timeout=2.0)
                    update_data = json.loads(update)
                    print(f"\n📥 Update recebido: {update_data}")
                except asyncio.TimeoutError:
                    print("   (Nenhum update automático recebido)")

            else:
                print(f"\n❌ ERRO ao gravar ângulo!")
                if 'message' in resp_data:
                    print(f"   Mensagem: {resp_data['message']}")

    except ConnectionRefusedError:
        print("❌ Erro: Servidor não está rodando em ws://localhost:8765")
    except asyncio.TimeoutError:
        print("❌ Timeout aguardando resposta do servidor")
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == '__main__':
    asyncio.run(test_write_angle())
