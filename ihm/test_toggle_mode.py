#!/usr/bin/env python3
"""
TESTE DO TOGGLE VIRTUAL DE MODO
================================
Testa a funcionalidade de toggle direto em 02FF (bypass S1+E6)
"""
import asyncio
import websockets
import json
import time
from modbus_client import ModbusClientWrapper
import modbus_map as mm

async def test_toggle_via_websocket():
    """Testa toggle via WebSocket"""
    print("=" * 70)
    print(" TESTE TOGGLE MODO VIA WEBSOCKET")
    print("=" * 70)

    # Conectar ao WebSocket
    uri = "ws://localhost:8765"

    try:
        async with websockets.connect(uri) as websocket:
            print(f"\n✓ Conectado ao WebSocket: {uri}")

            # Receber estado inicial
            initial_msg = await websocket.recv()
            initial_data = json.loads(initial_msg)
            print(f"\n📨 Estado inicial recebido:")
            print(f"  Tipo: {initial_data.get('type')}")
            print(f"  Modo: {initial_data.get('data', {}).get('mode_text', 'N/A')}")
            print(f"  Bit 02FF: {initial_data.get('data', {}).get('mode_bit_02ff', 'N/A')}")

            # Enviar comando de toggle
            print(f"\n🔄 Enviando comando toggle_mode...")
            await websocket.send(json.dumps({
                'action': 'toggle_mode'
            }))

            # Aguardar resposta
            print(f"⏳ Aguardando resposta...")

            # Receber mensagens até timeout ou mode_changed
            timeout = 5.0
            start_time = time.time()
            mode_changed = False

            while time.time() - start_time < timeout:
                try:
                    msg = await asyncio.wait_for(websocket.recv(), timeout=1.0)
                    data = json.loads(msg)
                    msg_type = data.get('type')

                    print(f"\n📨 Mensagem recebida: {msg_type}")

                    if msg_type == 'mode_changed':
                        print(f"✅ MODO ALTERADO!")
                        print(f"  Modo antes: {data.get('mode_antes')}")
                        print(f"  Modo depois: {data.get('mode_depois')}")
                        print(f"  Bit 02FF: {data.get('mode_bit')}")
                        print(f"  Timestamp: {data.get('timestamp')}")
                        mode_changed = True
                        break
                    elif msg_type == 'error':
                        print(f"❌ ERRO: {data.get('message')}")
                        break
                    elif msg_type == 'state_update':
                        print(f"  (atualização de estado)")
                        if 'mode_text' in data.get('data', {}):
                            print(f"  Novo modo: {data['data']['mode_text']}")

                except asyncio.TimeoutError:
                    continue

            if not mode_changed:
                print(f"\n⚠️  Timeout aguardando mode_changed")

    except Exception as e:
        print(f"\n❌ Erro: {e}")
        import traceback
        traceback.print_exc()


async def test_toggle_direct():
    """Testa toggle direto via modbus_client"""
    print("\n" + "=" * 70)
    print(" TESTE TOGGLE DIRETO (MODBUS CLIENT)")
    print("=" * 70)

    client = ModbusClientWrapper(port=mm.MODBUS_CONFIG['port'], stub_mode=False)

    if not client.connected:
        print("❌ CLP não conectado!")
        return

    try:
        # Ler modo inicial
        print("\n📖 Lendo modo inicial...")
        mode_antes = client.read_real_mode()
        mode_antes_text = "AUTO" if mode_antes else "MANUAL" if mode_antes is not None else "UNKNOWN"
        print(f"  Modo atual: {mode_antes_text} (02FF={mode_antes})")

        # Toggle
        print(f"\n🔄 Executando toggle...")
        new_mode = client.toggle_mode_direct()

        if new_mode is not None:
            mode_depois_text = "AUTO" if new_mode else "MANUAL"
            print(f"\n✅ SUCESSO!")
            print(f"  Modo antes: {mode_antes_text}")
            print(f"  Modo depois: {mode_depois_text}")
            print(f"  Bit 02FF: {new_mode}")

            # Aguardar e re-ler
            time.sleep(0.5)
            verificacao = client.read_real_mode()
            verificacao_text = "AUTO" if verificacao else "MANUAL"
            print(f"\n🔍 Verificação:")
            print(f"  Modo lido: {verificacao_text} (02FF={verificacao})")

            if verificacao == new_mode:
                print(f"  ✅ Consistente!")
            else:
                print(f"  ⚠️  Inconsistência detectada!")
        else:
            print(f"\n❌ FALHA ao alternar modo!")

    finally:
        client.close()


async def main():
    print("\n" + "=" * 70)
    print(" TESTE COMPLETO: TOGGLE VIRTUAL AUTO/MANUAL")
    print("=" * 70)

    # 1. Teste direto
    await test_toggle_direct()

    # Aguardar
    print("\n⏳ Aguardando 2s antes do teste WebSocket...")
    await asyncio.sleep(2)

    # 2. Teste via WebSocket
    await test_toggle_via_websocket()

    print("\n" + "=" * 70)
    print(" TESTES CONCLUÍDOS")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())
