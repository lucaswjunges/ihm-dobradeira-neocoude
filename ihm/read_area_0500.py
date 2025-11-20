#!/usr/bin/env python3
"""
Lê valores ATUAIS da área 0x0500 do CLP
========================================

Verifica quais valores estão gravados nos registros de setpoints oficiais.
"""

import sys
from modbus_client import ModbusClientWrapper
import modbus_map as mm

def main():
    print("=" * 70)
    print("  LEITURA DA ÁREA 0x0500 - SETPOINTS OFICIAIS")
    print("=" * 70)
    print()

    # Conectar ao CLP
    client = ModbusClientWrapper(stub_mode=False, port='/dev/ttyUSB0')

    if not client.connected:
        print("❌ ERRO: Não foi possível conectar ao CLP")
        print("   → Verifique se o cabo está conectado")
        print("   → Verifique se a porta é /dev/ttyUSB0 ou /dev/ttyUSB1")
        return 1

    print("✅ Conectado ao CLP")
    print()

    # Ler área 0x0500-0x0504 (setpoints oficiais - 16-bit)
    print("📐 ÁREA 0x0500-0x0504 (Setpoints Oficiais - 16-bit)")
    print("-" * 70)

    setpoints_16bit = {
        'BEND_1_SETPOINT': 0x0500,  # 1280
        'BEND_2_SETPOINT': 0x0502,  # 1282
        'BEND_3_SETPOINT': 0x0504,  # 1284
    }

    for name, addr in setpoints_16bit.items():
        value = client.read_register(addr)
        if value is not None:
            degrees = value / 10.0
            print(f"  0x{addr:04X} ({addr:4d}) - {name:20s}: {value:5d} ({degrees:6.1f}°)")
        else:
            print(f"  0x{addr:04X} ({addr:4d}) - {name:20s}: ERRO AO LER")

    print()

    # Ler área 0x0840-0x0852 (shadow - 32-bit MSW/LSW)
    print("📐 ÁREA 0x0840-0x0852 (Shadow - 32-bit MSW/LSW)")
    print("-" * 70)

    shadow_pairs = [
        ('BEND_1_LEFT', 0x0842, 0x0840),  # MSW, LSW
        ('BEND_2_LEFT', 0x0848, 0x0846),
        ('BEND_3_LEFT', 0x0852, 0x0850),
    ]

    for name, msw_addr, lsw_addr in shadow_pairs:
        msw = client.read_register(msw_addr)
        lsw = client.read_register(lsw_addr)

        if msw is not None and lsw is not None:
            value_32bit = mm.read_32bit(msw, lsw)
            degrees = mm.clp_to_degrees(value_32bit)
            print(f"  0x{msw_addr:04X}/0x{lsw_addr:04X} - {name:20s}: MSW={msw:5d} LSW={lsw:5d} → {value_32bit:10d} ({degrees:6.1f}°)")
        else:
            print(f"  0x{msw_addr:04X}/0x{lsw_addr:04X} - {name:20s}: ERRO AO LER")

    print()

    # Comparar valores
    print("🔍 COMPARAÇÃO: 0x0500 vs 0x0840")
    print("-" * 70)

    bend1_0500 = client.read_register(0x0500)
    bend1_msw = client.read_register(0x0842)
    bend1_lsw = client.read_register(0x0840)

    if all(v is not None for v in [bend1_0500, bend1_msw, bend1_lsw]):
        value_0500 = bend1_0500 / 10.0
        value_0840 = mm.clp_to_degrees(mm.read_32bit(bend1_msw, bend1_lsw))

        print(f"  Dobra 1 em 0x0500: {value_0500:.1f}°")
        print(f"  Dobra 1 em 0x0840: {value_0840:.1f}°")

        if abs(value_0500 - value_0840) < 0.1:
            print("  ✅ VALORES IGUAIS - Áreas sincronizadas!")
        else:
            print("  ⚠️  VALORES DIFERENTES - Áreas NÃO sincronizadas!")
            print(f"     Diferença: {abs(value_0500 - value_0840):.1f}°")

    print()

    # Ler área estendida 0x0500-0x053F (NVRAM completa)
    print("📊 VARREDURA ÁREA 0x0500-0x0520 (NVRAM - 16 posições)")
    print("-" * 70)
    print("  Endereço     Decimal   Hex      Graus")
    print("  " + "-" * 60)

    non_zero_count = 0
    for addr in range(0x0500, 0x0520, 2):  # Pares de 2 em 2
        value = client.read_register(addr)
        if value is not None:
            degrees = value / 10.0
            status = "✓" if value != 0 else " "
            print(f"  {status} 0x{addr:04X}      {value:6d}   0x{value:04X}   {degrees:7.1f}°")
            if value != 0:
                non_zero_count += 1
        else:
            print(f"    0x{addr:04X}      ERRO")

    print()
    print(f"  Total de registros não-zero: {non_zero_count}/16")
    print()

    print("=" * 70)
    print("  CONCLUSÃO")
    print("=" * 70)
    print()

    if bend1_0500 and bend1_0500 != 0:
        print("✅ Área 0x0500 contém DADOS (não está vazia)")
        print(f"   Exemplo: Dobra 1 = {bend1_0500/10.0:.1f}°")
    else:
        print("⚠️  Área 0x0500 está VAZIA ou ZERADA")
        print("   → IHM Web precisa gravar valores iniciais")

    print()

    client.disconnect()
    return 0

if __name__ == '__main__':
    sys.exit(main())
