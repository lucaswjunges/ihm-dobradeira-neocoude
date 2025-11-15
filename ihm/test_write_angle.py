#!/usr/bin/env python3
"""
Teste de Escrita de Ângulo
Testa diferentes formatos de escrita
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from modbus_client import ModbusClientWrapper
import time

def test_angle_write():
    """Testa escrita de ângulo 90.0°"""

    client = ModbusClientWrapper(port='/dev/ttyUSB0', stub_mode=False)

    print("=" * 70)
    print("TESTE: ESCRITA DE ÂNGULO 90.0°")
    print("=" * 70)

    # Endereços dobra 1 esquerda
    msw_addr = 0x0840  # 2112
    lsw_addr = 0x0842  # 2114

    # Valor: 90.0° → 900 (internal) → 0x0384
    angle_degrees = 90.0
    angle_internal = int(angle_degrees * 10)  # 900

    print(f"\nÂngulo desejado: {angle_degrees}°")
    print(f"Valor interno: {angle_internal}")
    print(f"Hex: 0x{angle_internal:04X}")

    # ANTES
    print("\n" + "─" * 70)
    print("ANTES DA ESCRITA:")
    print("─" * 70)
    msw_before = client.read_register(msw_addr)
    lsw_before = client.read_register(lsw_addr)
    print(f"MSW (0x{msw_addr:04X}): {msw_before}")
    print(f"LSW (0x{lsw_addr:04X}): {lsw_before}")

    if msw_before is not None and lsw_before is not None:
        value_before = (msw_before << 16) | lsw_before
        print(f"Valor 32-bit: {value_before} → {value_before/10.0:.1f}°")

    # TESTE 1: Escrever como 16-bit direto no LSW
    print("\n" + "─" * 70)
    print("TESTE 1: Escrever 900 diretamente no LSW")
    print("─" * 70)

    success = client.write_register(lsw_addr, angle_internal)
    print(f"Escrita: {'✅ Sucesso' if success else '❌ Falha'}")
    time.sleep(0.3)

    lsw_test1 = client.read_register(lsw_addr)
    print(f"LSW depois: {lsw_test1}")
    if lsw_test1:
        print(f"Ângulo: {lsw_test1/10.0:.1f}°")

    # TESTE 2: Escrever MSW=0, LSW=900
    print("\n" + "─" * 70)
    print("TESTE 2: Escrever MSW=0, LSW=900")
    print("─" * 70)

    client.write_register(msw_addr, 0)
    client.write_register(lsw_addr, angle_internal)
    time.sleep(0.3)

    msw_test2 = client.read_register(msw_addr)
    lsw_test2 = client.read_register(lsw_addr)
    print(f"MSW: {msw_test2}, LSW: {lsw_test2}")

    if msw_test2 is not None and lsw_test2 is not None:
        value_32bit = (msw_test2 << 16) | lsw_test2
        print(f"Valor 32-bit: {value_32bit} → {value_32bit/10.0:.1f}°")

    # TESTE 3: Escrever usando write_32bit (se disponível)
    print("\n" + "─" * 70)
    print("TESTE 3: Testar diferentes interpretações")
    print("─" * 70)

    # Tentar escrever 900 em diferentes formatos
    tests = [
        (900, "Valor direto 900"),
        (90, "Valor sem multiplicar (90)"),
        (9000, "Valor com mais zeros (9000)"),
    ]

    for test_value, desc in tests:
        client.write_register(lsw_addr, test_value)
        time.sleep(0.2)
        result = client.read_register(lsw_addr)
        angle = result / 10.0 if result else 0
        print(f"  {desc:30s} → LSW={result:5d} → {angle:6.1f}°")

    # RESTAURAR valor original
    print("\n" + "─" * 70)
    print("RESTAURANDO valor original...")
    print("─" * 70)
    if msw_before is not None:
        client.write_register(msw_addr, msw_before)
    if lsw_before is not None:
        client.write_register(lsw_addr, lsw_before)

    print("\n✅ Teste concluído")
    client.close()

if __name__ == '__main__':
    try:
        test_angle_write()
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        import traceback
        traceback.print_exc()
