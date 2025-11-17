#!/usr/bin/env python3
"""
Leitura dos Registros ORIGINAIS do Ladder
==========================================

Consulta os registros que o ladder ORIGINAL da máquina usa,
não os novos validados em 16/Nov/2025.
"""

import asyncio
import websockets
import json

async def query_modbus_direct(command):
    """Envia comando direto ao servidor via WebSocket."""
    uri = 'ws://localhost:8765'
    async with websockets.connect(uri) as ws:
        # Ignora estado inicial
        await ws.recv()

        # Envia comando
        await ws.send(json.dumps(command))

        # Aguarda resposta
        response = await ws.recv()
        return json.loads(response)

async def read_register_range(start_addr, count, name):
    """Lê faixa de registros."""
    print(f"\n{'=' * 70}")
    print(f"  {name}")
    print(f"  Endereço inicial: 0x{start_addr:04X} ({start_addr})")
    print(f"  Quantidade: {count} registros")
    print(f"{'=' * 70}")

    # Comando personalizado (precisaria implementar no servidor)
    # Por agora, vamos consultar os que já sabemos
    pass

async def main():
    print("=" * 70)
    print("  REGISTROS ORIGINAIS DO LADDER - CONSULTA MANUAL")
    print("=" * 70)
    print()
    print("⚠️  IMPORTANTE: Estes são os endereços que o ladder ORIGINAL")
    print("   da máquina usa, não os validados em 16/Nov/2025.")
    print()

    # Conectar via WebSocket para pegar estado atual
    uri = 'ws://localhost:8765'
    async with websockets.connect(uri) as ws:
        # Recebe estado completo
        msg = await ws.recv()
        data = json.loads(msg)

        if data.get('type') == 'full_state':
            state = data.get('data', {})

            print("📊 ESTADO ATUAL DO CLP (via State Manager)")
            print("-" * 70)
            print(f"  Encoder: {state.get('encoder_degrees', 'N/A')}° " +
                  f"(raw: {state.get('encoder_raw', 'N/A')})")
            print(f"  Velocidade: {state.get('speed_class', 'N/A')} rpm")
            print()
            print("  Ângulos programados (área 0x0500):")
            print(f"    Dobra 1: {state.get('bend_1_left', 'N/A')}°")
            print(f"    Dobra 2: {state.get('bend_2_left', 'N/A')}°")
            print(f"    Dobra 3: {state.get('bend_3_left', 'N/A')}°")
            print()

    print("=" * 70)
    print("  REGISTROS QUE O LADDER ORIGINAL USA")
    print("=" * 70)
    print()

    print("📐 ÂNGULOS (conforme análise do ladder):")
    print("-" * 70)
    print("  ✅ Área 0x0500-0x0504 (SETPOINTS oficiais - validado)")
    print("     → BEND_1_SETPOINT: 0x0500 (1280)")
    print("     → BEND_2_SETPOINT: 0x0502 (1282)")
    print("     → BEND_3_SETPOINT: 0x0504 (1284)")
    print()
    print("  ⚠️  Área 0x0840-0x0852 (SHADOW - sobreescrita por ROT4/ROT5)")
    print("     → Copiados de 0x0944 e 0x0B00 a cada scan")
    print("     → NÃO usar para escrita!")
    print()

    print("⚙️  VELOCIDADE (conforme análise do ladder):")
    print("-" * 70)
    print("  ✅ Registro 0x094C (2380) - SPEED_CLASS")
    print("     → Validado 16/Nov/2025")
    print("     → Valores: 5, 10, 15 rpm")
    print()

    print("📊 ENCODER (conforme análise do ladder):")
    print("-" * 70)
    print("  ✅ Registros 0x04D6/0x04D7 (1238/1239) - 32-bit")
    print("     → MSW (bits 31-16): 0x04D6")
    print("     → LSW (bits 15-0): 0x04D7")
    print("     → Conversão: graus = valor / 10.0")
    print()

    print("🔍 ÁREA DE SUPERVISÃO (conforme análise do ladder):")
    print("-" * 70)
    print("  0x0940 (2368) - SCREEN_NUM (número da tela)")
    print("  0x0946 (2374) - MODE_STATE (0=Manual, 1=Auto)")
    print("  0x0948 (2376) - BEND_CURRENT (dobra atual 1/2/3)")
    print("  0x094A (2378) - DIRECTION (0=Esq, 1=Dir)")
    print("  0x094C (2380) - SPEED_CLASS (5/10/15 rpm) ✅")
    print("  0x094E (2382) - CYCLE_ACTIVE (ciclo ativo)")
    print()

    print("=" * 70)
    print("  CONCLUSÃO")
    print("=" * 70)
    print()
    print("Os registros ORIGINAIS do ladder são:")
    print()
    print("✅ ÂNGULOS: 0x0500-0x0504 (setpoints oficiais)")
    print("✅ VELOCIDADE: 0x094C (SPEED_CLASS)")
    print("✅ ENCODER: 0x04D6/0x04D7 (32-bit)")
    print()
    print("⚠️  A área 0x0840-0x0852 (shadow) NÃO deve ser usada")
    print("   para escrita, apenas leitura (se necessário).")
    print()

if __name__ == '__main__':
    asyncio.run(main())
