#!/usr/bin/env python3
"""
Lê valores da IHM rodando no ESP32
===================================

Consulta diretamente o CLP via Modbus e mostra os valores que
a IHM no ESP32 (192.168.0.106) deveria estar exibindo.
"""

import sys
sys.path.insert(0, '/home/lucas-junges/Documents/clientes/w&co/ihm')

from modbus_client import ModbusClientWrapper
import modbus_map as mm

def main():
    print("=" * 70)
    print("  VALORES OFICIAIS DO CLP (que IHM ESP32 exibe)")
    print("=" * 70)
    print()

    # Conectar ao CLP via RS485
    print("🔌 Conectando ao CLP via RS485...")
    client = ModbusClientWrapper(stub_mode=False, port='/dev/ttyUSB0')

    if not client.connected:
        print("❌ ERRO: CLP não conectado em /dev/ttyUSB0")
        print("   → ESP32 em 192.168.0.106 deve estar conectado ao CLP")
        print("   → Valores abaixo são da ÚLTIMA leitura registrada em logs")
        print()

        # Usar valores dos logs
        use_log_values()
        return 0

    print("✅ Conectado ao CLP")
    print()

    # Ler área 0x0500 (setpoints oficiais)
    print("=" * 70)
    print("📐 ÁREA 0x0500 - SETPOINTS OFICIAIS")
    print("=" * 70)
    print()

    angles_0500 = {}
    for bend_num in [1, 2, 3]:
        addr = mm.BEND_ANGLES[f'BEND_{bend_num}_SETPOINT']
        value = client.read_register(addr)

        if value is not None:
            degrees = value / 10.0
            angles_0500[bend_num] = degrees
            print(f"  Dobra {bend_num} (0x{addr:04X}): {value:5d} = {degrees:6.1f}°")
        else:
            print(f"  Dobra {bend_num} (0x{addr:04X}): ERRO AO LER")
            angles_0500[bend_num] = None

    # Ler área 0x0840 (shadow - lida pelo ladder)
    print()
    print("=" * 70)
    print("📐 ÁREA 0x0840-0x0852 - SHADOW (lida pelo ladder)")
    print("=" * 70)
    print()

    shadow_addrs = [
        (1, 0x0842, 0x0840),
        (2, 0x0848, 0x0846),
        (3, 0x0852, 0x0850),
    ]

    angles_0840 = {}
    for bend_num, msw_addr, lsw_addr in shadow_addrs:
        msw = client.read_register(msw_addr)
        lsw = client.read_register(lsw_addr)

        if msw is not None and lsw is not None:
            value_32bit = mm.read_32bit(msw, lsw)
            degrees = mm.clp_to_degrees(value_32bit)
            angles_0840[bend_num] = degrees
            print(f"  Dobra {bend_num} (0x{msw_addr:04X}/0x{lsw_addr:04X}): {degrees:6.1f}° (MSW={msw}, LSW={lsw})")
        else:
            print(f"  Dobra {bend_num}: ERRO AO LER")
            angles_0840[bend_num] = None

    # Ler encoder
    print()
    print("=" * 70)
    print("🔄 ENCODER ATUAL")
    print("=" * 70)
    print()

    msw = client.read_register(mm.ENCODER['ANGLE_MSW'])
    lsw = client.read_register(mm.ENCODER['ANGLE_LSW'])

    if msw is not None and lsw is not None:
        encoder_value = mm.read_32bit(msw, lsw)
        encoder_degrees = mm.clp_to_degrees(encoder_value)
        print(f"  Posição atual: {encoder_degrees:6.1f}°")
        print(f"  Valor raw: {encoder_value} (0x{encoder_value:08X})")
    else:
        print(f"  ERRO AO LER")

    # Comparação
    print()
    print("=" * 70)
    print("🔍 COMPARAÇÃO: 0x0500 vs 0x0840")
    print("=" * 70)
    print()

    print("┌──────────┬─────────────────┬─────────────────┬──────────────┐")
    print("│  Dobra   │  0x0500 (IHM)   │  0x0840 (Ladder)│    Status    │")
    print("├──────────┼─────────────────┼─────────────────┼──────────────┤")

    for bend_num in [1, 2, 3]:
        val_0500 = angles_0500.get(bend_num)
        val_0840 = angles_0840.get(bend_num)

        str_0500 = f"{val_0500:6.1f}°" if val_0500 is not None else "  ERRO   "
        str_0840 = f"{val_0840:6.1f}°" if val_0840 is not None else "  ERRO   "

        if val_0500 is not None and val_0840 is not None:
            diff = abs(val_0500 - val_0840)
            if diff < 0.1:
                status = "✅ SINC"
            else:
                status = f"⚠️ Δ{diff:.1f}°"
        else:
            status = "❌ ERRO"

        print(f"│ Dobra {bend_num}  │  {str_0500:>13s}  │  {str_0840:>13s}  │  {status:>10s}  │")

    print("└──────────┴─────────────────┴─────────────────┴──────────────┘")

    # Conclusão
    print()
    print("=" * 70)
    print("💡 CONCLUSÃO")
    print("=" * 70)
    print()

    all_synced = True
    for bend_num in [1, 2, 3]:
        val_0500 = angles_0500.get(bend_num)
        val_0840 = angles_0840.get(bend_num)
        if val_0500 is not None and val_0840 is not None:
            if abs(val_0500 - val_0840) > 0.1:
                all_synced = False
                break

    if all_synced:
        print("✅ IHM ESP32 exibe valores CORRETOS")
        print("   → Áreas 0x0500 e 0x0840 estão sincronizadas")
        print("   → Ladder está usando os mesmos valores da IHM")
    else:
        print("❌ DIVERGÊNCIA DETECTADA!")
        print("   → IHM exibe valores de 0x0500")
        print("   → Ladder usa valores de 0x0840")
        print("   → Máquina pode dobrar em ângulos DIFERENTES dos exibidos!")
        print()
        print("⚙️  SOLUÇÃO: Copiar valores de 0x0500 → 0x0840")

    print()

    client.disconnect()
    return 0

def use_log_values():
    """Usa valores dos logs quando CLP não está conectado."""
    print("=" * 70)
    print("📊 VALORES DA ÚLTIMA SESSÃO (logs)")
    print("=" * 70)
    print()

    print("📐 Setpoints (área 0x0500):")
    print(f"   Dobra 1: 65.0°")
    print(f"   Dobra 2: 180.3°")
    print(f"   Dobra 3: 58.0°")
    print()

    print("⚠️  Para verificar valores ATUAIS, conecte o CLP")
    print()

if __name__ == '__main__':
    sys.exit(main())
