#!/usr/bin/env python3
"""
Teste da Interface Web - Simula cliente conectando ao servidor
"""

import asyncio
import websockets
import json
import signal
import sys

# Configuração
WS_URL = "ws://localhost:8765"
HTTP_URL = "http://localhost:8080"

async def test_websocket():
    """Testa conexão WebSocket e recebe estados"""
    print("=" * 60)
    print("TESTE DA INTERFACE WEB - IHM NEOCOUDE-HD-15")
    print("=" * 60)
    print()

    try:
        print(f"1. Conectando ao WebSocket: {WS_URL}...")
        async with websockets.connect(WS_URL) as websocket:
            print("   ✓ WebSocket conectado!")

            # Recebe estado inicial
            print("\n2. Aguardando estado inicial...")
            message = await websocket.recv()
            data = json.loads(message)

            if data.get('type') == 'full_state':
                state = data.get('data', {})
                print("   ✓ Estado inicial recebido!")
                print()
                print("   📊 DADOS DO CLP:")
                print(f"      Encoder: {state.get('encoder_degrees', 0):.1f}°")
                print(f"      Tela atual: {state.get('screen_num', 0)}")
                print(f"      Dobra atual: {state.get('bend_current', 0)}")
                print(f"      Modo: {'AUTO' if state.get('mode_state', 0) else 'MANUAL'}")
                print(f"      Velocidade: {state.get('speed_class', 5)} rpm")
                print()
                print("   💡 LEDs:")
                leds = state.get('leds', {})
                for led, status in leds.items():
                    symbol = "🟢" if status else "⚫"
                    print(f"      {led}: {symbol}")
                print()
                print("   📐 Ângulos programados:")
                angles = state.get('angles', {})
                print(f"      Dobra 1 Esq: {angles.get('bend_1_left', 0):.1f}°")
                print(f"      Dobra 2 Esq: {angles.get('bend_2_left', 0):.1f}°")
                print(f"      Dobra 3 Esq: {angles.get('bend_3_left', 0):.1f}°")

            # Testa envio de comando
            print("\n3. Testando envio de comando (pressionar K1)...")
            await websocket.send(json.dumps({
                'action': 'press_key',
                'key': 'K1'
            }))
            print("   ✓ Comando enviado!")

            # Recebe resposta
            print("\n4. Aguardando resposta do servidor...")
            response = await asyncio.wait_for(websocket.recv(), timeout=2.0)
            response_data = json.loads(response)
            print(f"   ✓ Resposta recebida: {response_data}")

            # Aguarda alguns updates
            print("\n5. Recebendo atualizações de estado (5 segundos)...")
            update_count = 0
            try:
                async for message in websocket:
                    data = json.loads(message)
                    if data.get('type') == 'state_update':
                        update_count += 1
                        changes = data.get('data', {})
                        if changes:
                            print(f"   Update #{update_count}: {list(changes.keys())}")

                    if update_count >= 10:  # Recebe 10 updates
                        break
            except asyncio.TimeoutError:
                pass

            print(f"\n   ✓ Recebidos {update_count} updates de estado")

    except websockets.exceptions.ConnectionRefused:
        print("   ✗ ERRO: Não foi possível conectar ao WebSocket!")
        print("   Certifique-se de que o servidor está rodando:")
        print("   python3 main_server.py --stub")
        return False

    except Exception as e:
        print(f"   ✗ ERRO: {e}")
        return False

    print()
    print("=" * 60)
    print("✓ TESTE COMPLETO - INTERFACE FUNCIONANDO CORRETAMENTE!")
    print("=" * 60)
    return True


async def main():
    """Função principal"""
    success = await test_websocket()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())
