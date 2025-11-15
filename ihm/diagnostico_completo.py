#!/usr/bin/env python3
"""
DIAGNÓSTICO COMPLETO - IHM WEB NEOCOUDE-HD-15
Engenharia de Controle e Automação
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from modbus_client import ModbusClientWrapper
import modbus_map as mm

def print_header(title):
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)

def print_section(title):
    print(f"\n{'─' * 70}")
    print(f"  {title}")
    print(f"{'─' * 70}")

def test_io_digital(client):
    """Testa todas as entradas e saídas digitais"""
    print_section("ENTRADAS DIGITAIS E0-E7")

    for i in range(8):
        addr = 0x0100 + i  # 256 + i
        value = client.read_coil(addr)
        status = "🟢 ON" if value else "⚫ OFF"
        print(f"  E{i} (0x{addr:04X} / {addr:4d}): {status:8s} [{value}]")

    print_section("SAÍDAS DIGITAIS S0-S7")

    for i in range(8):
        addr = 0x0180 + i  # 384 + i
        value = client.read_coil(addr)
        status = "🟢 ON" if value else "⚫ OFF"
        print(f"  S{i} (0x{addr:04X} / {addr:4d}): {status:8s} [{value}]")

def test_encoder(client):
    """Testa leitura de encoder"""
    print_section("ENCODER (Posição Angular)")

    msw = client.read_register(0x04D6)  # 1238
    lsw = client.read_register(0x04D7)  # 1239

    if msw is not None and lsw is not None:
        # Calcula valor 32-bit
        value_32bit = (msw << 16) | lsw
        graus = value_32bit / 10.0

        print(f"  MSW (0x04D6 / 1238): {msw:5d} (0x{msw:04X})")
        print(f"  LSW (0x04D7 / 1239): {lsw:5d} (0x{lsw:04X})")
        print(f"  Valor 32-bit:        {value_32bit}")
        print(f"  Ângulo:              {graus:.1f}°")
    else:
        print("  ❌ Erro na leitura do encoder")

def test_angles(client):
    """Testa leitura de ângulos programados"""
    print_section("ÂNGULOS PROGRAMADOS")

    angles = [
        ("Dobra 1 Esq", 0x0840, 0x0842, 2112, 2114),
        ("Dobra 2 Esq", 0x0848, 0x084A, 2120, 2122),
        ("Dobra 3 Esq", 0x0850, 0x0852, 2128, 2130),
    ]

    for name, msw_addr, lsw_addr, msw_dec, lsw_dec in angles:
        # Tentar leitura como pares MSW/LSW
        msw = client.read_register(msw_addr)
        lsw = client.read_register(lsw_addr)

        if msw is not None and lsw is not None:
            # Método 1: MSW/LSW tradicional
            value_method1 = (msw << 16) | lsw
            graus_method1 = value_method1 / 10.0

            # Método 2: Ler diretamente como 16-bit e dividir por 10
            graus_method2_msw = msw / 10.0
            graus_method2_lsw = lsw / 10.0

            print(f"\n  {name}:")
            print(f"    Endereços: 0x{msw_addr:04X}/0x{lsw_addr:04X} ({msw_dec}/{lsw_dec})")
            print(f"    MSW: {msw:5d}  LSW: {lsw:5d}")
            print(f"    32-bit tradicional: {value_method1:10d} → {graus_method1:8.1f}°")
            print(f"    16-bit MSW direto:  {msw:10d} → {graus_method2_msw:8.1f}°")
            print(f"    16-bit LSW direto:  {lsw:10d} → {graus_method2_lsw:8.1f}°")
        else:
            print(f"\n  {name}: ❌ Erro na leitura")

def test_leds(client):
    """Testa LEDs K1/K2/K3"""
    print_section("LEDs DE STATUS")

    leds = [
        ("LED1 (K1)", 0x00C0, 192),
        ("LED2 (K2)", 0x00C1, 193),
        ("LED3 (K3)", 0x00C2, 194),
        ("LED4", 0x00C3, 195),
        ("LED5", 0x00C4, 196),
    ]

    for name, addr, dec in leds:
        value = client.read_coil(addr)
        status = "🟢 ON" if value else "⚫ OFF"
        print(f"  {name:12s} (0x{addr:04X} / {dec:3d}): {status}")

def test_supervision(client):
    """Testa área de supervisão"""
    print_section("ÁREA DE SUPERVISÃO (0x0940-0x094F)")

    regs = [
        ("SCREEN_NUM", 0x0940, 2368),
        ("TARGET_MSW", 0x0942, 2370),
        ("TARGET_LSW", 0x0944, 2372),
        ("MODE_STATE", 0x0946, 2374),
        ("BEND_CURRENT", 0x0948, 2376),
        ("DIRECTION", 0x094A, 2378),
        ("SPEED_CLASS", 0x094C, 2380),
        ("CYCLE_ACTIVE", 0x094E, 2382),
    ]

    for name, addr, dec in regs:
        value = client.read_register(addr)
        if value is not None:
            print(f"  {name:14s} (0x{addr:04X} / {dec:4d}): {value:5d}")
        else:
            print(f"  {name:14s} (0x{addr:04X} / {dec:4d}): ❌ Erro")

def test_mode_bits(client):
    """Testa bits críticos de modo"""
    print_section("BITS CRÍTICOS DE MODO")

    bits = [
        ("Modbus Slave", 0x00BE, 190, "DEVE estar ON"),
        ("Modo REAL (02FF)", 0x02FF, 767, "0=MANUAL, 1=AUTO"),
        ("E6 Safety", 0x0106, 262, "Condição para S1"),
        ("Monostável S1", 0x0376, 886, "Pulso de S1"),
        ("Cycle Active", 0x0191, 401, "Ciclo ativo"),
    ]

    for name, addr, dec, desc in bits:
        value = client.read_coil(addr)
        status = "🟢 ON" if value else "⚫ OFF"
        print(f"  {name:20s} (0x{addr:04X} / {dec:3d}): {status:8s} - {desc}")

def main():
    print_header("DIAGNÓSTICO COMPLETO - IHM WEB NEOCOUDE-HD-15")
    print("Conectando ao CLP...")

    client = ModbusClientWrapper(port='/dev/ttyUSB0', stub_mode=False)

    if not client.client or not client.client.is_socket_open():
        print("❌ FALHA: Não foi possível conectar ao CLP")
        return

    print("✅ Conectado com sucesso\n")

    try:
        test_io_digital(client)
        test_encoder(client)
        test_angles(client)
        test_leds(client)
        test_supervision(client)
        test_mode_bits(client)

        print_header("DIAGNÓSTICO CONCLUÍDO")
        print("\n✅ Todos os testes executados")
        print("📄 Revise os resultados acima para validação\n")

    except Exception as e:
        print(f"\n❌ Erro durante testes: {e}")
        import traceback
        traceback.print_exc()
    finally:
        client.close()

if __name__ == '__main__':
    main()
