#!/usr/bin/env python3
"""
Comparação CLP vs IHM Web
=========================

Lê valores diretamente do CLP e compara com o que está sendo exibido
na interface web em 192.168.0.106
"""

import sys
import asyncio
import aiohttp
from modbus_client import ModbusClientWrapper
import modbus_map as mm

async def fetch_ihm_values():
    """Busca valores exibidos na IHM Web."""
    url = "http://192.168.0.106:8080"

    print("🌐 Conectando à IHM Web em 192.168.0.106...")

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=5) as response:
                if response.status == 200:
                    html = await response.text()
                    print("✅ IHM Web respondeu (HTTP 200)")
                    # A IHM usa WebSocket, então vamos tentar conectar no WS
                    return await fetch_ihm_websocket()
                else:
                    print(f"⚠️  IHM Web respondeu com status {response.status}")
                    return None
    except Exception as e:
        print(f"❌ Erro ao conectar na IHM Web: {e}")
        return None

async def fetch_ihm_websocket():
    """Conecta no WebSocket da IHM para pegar estado atual."""
    import websockets

    ws_url = "ws://192.168.0.106:8765"

    try:
        print(f"🔌 Conectando no WebSocket {ws_url}...")
        async with websockets.connect(ws_url, timeout=5) as ws:
            # Recebe estado inicial
            msg = await asyncio.wait_for(ws.recv(), timeout=5)

            import json
            data = json.loads(msg)

            if data.get('type') == 'full_state':
                print("✅ WebSocket conectado - estado recebido")
                return data.get('data', {})
            else:
                print(f"⚠️  Tipo de mensagem inesperado: {data.get('type')}")
                return None

    except asyncio.TimeoutError:
        print("❌ Timeout ao conectar no WebSocket")
        return None
    except Exception as e:
        print(f"❌ Erro no WebSocket: {e}")
        return None

def read_clp_values(client):
    """Lê valores diretamente do CLP."""
    print("\n📡 Lendo valores DIRETAMENTE do CLP...")
    print("-" * 70)

    values = {}

    # Ler área 0x0500 (setpoints oficiais - 16-bit)
    print("\n📐 Área 0x0500-0x0504 (Setpoints Oficiais):")

    for bend_num in [1, 2, 3]:
        addr = mm.BEND_ANGLES[f'BEND_{bend_num}_SETPOINT']
        value = client.read_register(addr)

        if value is not None:
            degrees = value / 10.0
            values[f'0x0500_bend_{bend_num}'] = degrees
            print(f"  0x{addr:04X} - Dobra {bend_num}: {value:5d} = {degrees:6.1f}°")
        else:
            values[f'0x0500_bend_{bend_num}'] = None
            print(f"  0x{addr:04X} - Dobra {bend_num}: ERRO AO LER")

    # Ler área 0x0840-0x0852 (shadow - 32-bit MSW/LSW)
    print("\n📐 Área 0x0840-0x0852 (Shadow - lida pelo ladder):")

    shadow_addrs = [
        (1, 0x0842, 0x0840),  # MSW, LSW
        (2, 0x0848, 0x0846),
        (3, 0x0852, 0x0850),
    ]

    for bend_num, msw_addr, lsw_addr in shadow_addrs:
        msw = client.read_register(msw_addr)
        lsw = client.read_register(lsw_addr)

        if msw is not None and lsw is not None:
            value_32bit = mm.read_32bit(msw, lsw)
            degrees = mm.clp_to_degrees(value_32bit)
            values[f'0x0840_bend_{bend_num}'] = degrees
            print(f"  0x{msw_addr:04X}/0x{lsw_addr:04X} - Dobra {bend_num}: MSW={msw:5d} LSW={lsw:5d} → {degrees:6.1f}°")
        else:
            values[f'0x0840_bend_{bend_num}'] = None
            print(f"  0x{msw_addr:04X}/0x{lsw_addr:04X} - Dobra {bend_num}: ERRO AO LER")

    # Ler encoder
    print("\n🔄 Encoder (0x04D6/0x04D7):")
    msw = client.read_register(mm.ENCODER['ANGLE_MSW'])
    lsw = client.read_register(mm.ENCODER['ANGLE_LSW'])

    if msw is not None and lsw is not None:
        encoder_value = mm.read_32bit(msw, lsw)
        encoder_degrees = mm.clp_to_degrees(encoder_value)
        values['encoder'] = encoder_degrees
        print(f"  Posição atual: {encoder_degrees:6.1f}° (raw: {encoder_value})")
    else:
        values['encoder'] = None
        print(f"  Posição atual: ERRO AO LER")

    return values

async def main():
    print("=" * 70)
    print("  COMPARAÇÃO: VALORES CLP vs IHM WEB")
    print("=" * 70)
    print()

    # 1. Ler valores do CLP
    print("🔌 ETAPA 1: Conectar ao CLP")
    print("-" * 70)

    client = ModbusClientWrapper(stub_mode=False, port='/dev/ttyUSB0')

    if not client.connected:
        # Tenta USB1
        print("⚠️  /dev/ttyUSB0 não disponível, tentando /dev/ttyUSB1...")
        client = ModbusClientWrapper(stub_mode=False, port='/dev/ttyUSB1')

        if not client.connected:
            print("❌ ERRO: Não foi possível conectar ao CLP")
            print("   → Verifique se o cabo está conectado")
            print("   → Verifique se a porta é /dev/ttyUSB0 ou /dev/ttyUSB1")
            return 1

    print("✅ Conectado ao CLP")

    clp_values = read_clp_values(client)

    # 2. Ler valores da IHM Web
    print("\n" + "=" * 70)
    print("🌐 ETAPA 2: Conectar à IHM Web (192.168.0.106)")
    print("-" * 70)

    ihm_state = await fetch_ihm_websocket()

    # 3. Comparar valores
    print("\n" + "=" * 70)
    print("🔍 ETAPA 3: COMPARAÇÃO")
    print("=" * 70)

    if ihm_state:
        print("\n📊 IHM Web - Estado Recebido:")
        print("-" * 70)

        ihm_angles = ihm_state.get('angles', {})
        print(f"  Dobra 1: {ihm_angles.get('bend_1_left', 'N/A'):.1f}°")
        print(f"  Dobra 2: {ihm_angles.get('bend_2_left', 'N/A'):.1f}°")
        print(f"  Dobra 3: {ihm_angles.get('bend_3_left', 'N/A'):.1f}°")
        print(f"  Encoder: {ihm_state.get('encoder_degrees', 'N/A'):.1f}°")

        # Comparação detalhada
        print("\n" + "=" * 70)
        print("📋 COMPARAÇÃO DETALHADA")
        print("=" * 70)
        print()

        print("┌─────────────┬──────────────┬──────────────┬──────────────┬──────────┐")
        print("│   Registro  │  CLP 0x0500  │  CLP 0x0840  │   IHM Web    │  Status  │")
        print("├─────────────┼──────────────┼──────────────┼──────────────┼──────────┤")

        for bend_num in [1, 2, 3]:
            clp_0500 = clp_values.get(f'0x0500_bend_{bend_num}')
            clp_0840 = clp_values.get(f'0x0840_bend_{bend_num}')
            ihm_val = ihm_angles.get(f'bend_{bend_num}_left')

            clp_0500_str = f"{clp_0500:6.1f}°" if clp_0500 is not None else "  ERRO  "
            clp_0840_str = f"{clp_0840:6.1f}°" if clp_0840 is not None else "  ERRO  "
            ihm_val_str = f"{ihm_val:6.1f}°" if ihm_val is not None else "  N/A   "

            # Verificar coincidência
            if clp_0500 is not None and ihm_val is not None:
                diff = abs(clp_0500 - ihm_val)
                if diff < 0.1:
                    status = "✅ OK"
                else:
                    status = f"⚠️ Δ{diff:.1f}°"
            else:
                status = "❌ ERR"

            print(f"│  Dobra {bend_num}    │  {clp_0500_str:>10s}  │  {clp_0840_str:>10s}  │  {ihm_val_str:>10s}  │  {status:>6s}  │")

        print("├─────────────┼──────────────┼──────────────┼──────────────┼──────────┤")

        # Encoder
        clp_enc = clp_values.get('encoder')
        ihm_enc = ihm_state.get('encoder_degrees')

        clp_enc_str = f"{clp_enc:6.1f}°" if clp_enc is not None else "  ERRO  "
        ihm_enc_str = f"{ihm_enc:6.1f}°" if ihm_enc is not None else "  N/A   "

        if clp_enc is not None and ihm_enc is not None:
            diff = abs(clp_enc - ihm_enc)
            if diff < 0.5:
                status = "✅ OK"
            else:
                status = f"⚠️ Δ{diff:.1f}°"
        else:
            status = "❌ ERR"

        print(f"│  Encoder    │      -       │      -       │  {ihm_enc_str:>10s}  │  {status:>6s}  │")
        print("└─────────────┴──────────────┴──────────────┴──────────────┴──────────┘")

        # Conclusão
        print("\n" + "=" * 70)
        print("💡 CONCLUSÃO")
        print("=" * 70)
        print()

        # Verificar se IHM está lendo de 0x0500
        all_match_0500 = True
        for bend_num in [1, 2, 3]:
            clp_0500 = clp_values.get(f'0x0500_bend_{bend_num}')
            ihm_val = ihm_angles.get(f'bend_{bend_num}_left')
            if clp_0500 is not None and ihm_val is not None:
                if abs(clp_0500 - ihm_val) > 0.1:
                    all_match_0500 = False
                    break

        if all_match_0500:
            print("✅ IHM Web está LENDO CORRETAMENTE de 0x0500 (setpoints oficiais)")
        else:
            print("⚠️  IHM Web NÃO está sincronizada com 0x0500")

        # Verificar se 0x0500 e 0x0840 estão sincronizados
        areas_synced = True
        for bend_num in [1, 2, 3]:
            clp_0500 = clp_values.get(f'0x0500_bend_{bend_num}')
            clp_0840 = clp_values.get(f'0x0840_bend_{bend_num}')
            if clp_0500 is not None and clp_0840 is not None:
                if abs(clp_0500 - clp_0840) > 0.1:
                    areas_synced = False
                    break

        if areas_synced:
            print("✅ Áreas 0x0500 e 0x0840 estão SINCRONIZADAS")
            print("   → Ladder está lendo valores corretos!")
        else:
            print("❌ Áreas 0x0500 e 0x0840 estão DESSINCRONIZADAS")
            print("   → Ladder pode estar usando valores diferentes!")
            print("   → Necessário copiar 0x0500 → 0x0840 ou modificar ladder")

    else:
        print("\n❌ Não foi possível obter dados da IHM Web")
        print("   → Verifique se o servidor está rodando em 192.168.0.106:8765")
        print("   → Verifique se há firewall bloqueando a porta 8765")

    print()
    client.disconnect()
    return 0

if __name__ == '__main__':
    try:
        sys.exit(asyncio.run(main()))
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrompido pelo usuário")
        sys.exit(1)
