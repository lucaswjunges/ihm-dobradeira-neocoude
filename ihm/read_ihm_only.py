#!/usr/bin/env python3
"""
Leitura apenas da IHM Web
=========================

Mostra os valores que estão sendo exibidos na interface web.
"""

import sys
import asyncio
import websockets
import json

async def main():
    print("=" * 70)
    print("  VALORES EXIBIDOS NA IHM WEB (192.168.0.106)")
    print("=" * 70)
    print()

    # Conecta no ESP32
    ws_urls = [
        "ws://192.168.0.106:8765"
    ]

    connected = False
    state = None

    for ws_url in ws_urls:
        try:
            print(f"🔌 Tentando {ws_url}...")
            async with websockets.connect(ws_url) as ws:
                print(f"✅ Conectado em {ws_url}")
                print()

                # Recebe estado inicial
                msg = await asyncio.wait_for(ws.recv(), timeout=5)
                data = json.loads(msg)

                if data.get('type') == 'full_state':
                    state = data.get('data', {})
                    connected = True
                    break
                else:
                    print(f"⚠️  Tipo de mensagem inesperado: {data.get('type')}")
                    continue

        except (ConnectionRefusedError, OSError):
            print(f"   ✗ Não conectou em {ws_url}")
            continue
        except Exception as e:
            print(f"   ✗ Erro em {ws_url}: {e}")
            continue

    if not connected or state is None:
        print()
        print("❌ Não foi possível conectar em nenhum endereço")
        print("   → Verifique se o servidor está rodando")
        return 1

    # Processar estado recebido
    print("📊 ESTADO ATUAL DA MÁQUINA")
    print("-" * 70)
    print()

    # Encoder
    encoder_degrees = state.get('encoder_degrees', 0)
    encoder_raw = state.get('encoder_raw', 0)
    print(f"🔄 Encoder:")
    print(f"   Posição: {encoder_degrees:.1f}°")
    print(f"   Raw: {encoder_raw}")
    print()

    # Ângulos
    angles = state.get('angles', {})
    print(f"📐 Ângulos Programados:")
    print(f"   Dobra 1: {angles.get('bend_1_left', 0):.1f}°")
    print(f"   Dobra 2: {angles.get('bend_2_left', 0):.1f}°")
    print(f"   Dobra 3: {angles.get('bend_3_left', 0):.1f}°")
    print()

    # Velocidade
    speed_class = state.get('speed_class', 0)
    print(f"⚡ Velocidade: {speed_class} rpm")
    print()

    # Modo
    mode_auto = state.get('mode_auto', False)
    mode_str = "AUTOMÁTICO" if mode_auto else "MANUAL"
    print(f"🎮 Modo: {mode_str}")
    print()

    # Dobra atual
    bend_current = state.get('bend_current', 0)
    print(f"📍 Dobra Atual: {bend_current}")
    print()

    # LEDs
    leds = state.get('leds', {})
    print(f"💡 LEDs:")
    for led_name, led_state in leds.items():
        status = "🟢 ON " if led_state else "⚫ OFF"
        print(f"   {led_name}: {status}")
    print()

    # Conexão
    modbus_connected = state.get('modbus_connected', False)
    conn_status = "✅ CONECTADO" if modbus_connected else "❌ DESCONECTADO"
    print(f"🔌 Modbus: {conn_status}")
    print()

    # Timestamp
    last_update = state.get('last_update', 'N/A')
    print(f"🕐 Última atualização: {last_update}")
    print()

    print("=" * 70)
    print("💾 DADOS BRUTOS (JSON)")
    print("=" * 70)
    print(json.dumps(state, indent=2, ensure_ascii=False))
    print()

    return 0

if __name__ == '__main__':
    try:
        sys.exit(asyncio.run(main()))
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrompido pelo usuário")
        sys.exit(1)
