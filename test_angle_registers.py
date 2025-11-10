#!/usr/bin/env python3
"""
Teste para encontrar os registros corretos de ângulos
"""
import sys
import time
from modbus_client import ModbusClient, ModbusConfig

def test_write_read(client, reg_address, test_value):
    """Testa escrever e ler um único registro"""
    print(f"  Testando registro {reg_address}...")

    # Escrever
    success = client.write_register(reg_address, test_value)
    if not success:
        print(f"    ❌ Falha ao escrever")
        return None

    time.sleep(0.1)

    # Ler de volta
    result = client.read_register(reg_address)
    if result is None:
        print(f"    ❌ Falha ao ler")
        return None

    if result == test_value:
        print(f"    ✅ OK: Escrito={test_value}, Lido={result}")
        return True
    else:
        print(f"    ⚠️  Escrito={test_value}, Lido={result} (diferente)")
        return False

def main():
    print("=" * 60)
    print("TESTE: Encontrar registros corretos de ângulos")
    print("=" * 60)

    config = ModbusConfig(port='/dev/ttyUSB0')
    client = ModbusClient(stub_mode=False, config=config)

    if not client.connect():
        print("❌ Falha ao conectar!")
        return 1

    print("✅ Conectado ao CLP\n")

    # Testar registros candidatos para Ângulo 1
    print("ÂNGULO 1 - Testando registros individuais:")
    print("-" * 60)

    test_value = 90
    candidates = [2112, 2114, 2118, 2120, 2128, 2130]

    working_regs = []

    for reg in candidates:
        result = test_write_read(client, reg, test_value)
        if result is True:
            working_regs.append(reg)

    print(f"\n{'='*60}")
    print(f"Registros que aceitaram escrita/leitura: {working_regs}")
    print(f"{'='*60}\n")

    # Se encontrou registros, testar sequência
    if working_regs:
        print("Testando sequências de valores:")
        print("-" * 60)

        for reg in working_regs:
            print(f"\nRegistro {reg}:")
            for val in [0, 45, 90, 180, 270, 360]:
                client.write_register(reg, val)
                time.sleep(0.1)
                result = client.read_register(reg)
                match = "✅" if result == val else "❌"
                print(f"  {match} Escrito={val:3d}°, Lido={result:3d}°")

    # Testar leitura atual dos 3 ângulos (como estão agora)
    print(f"\n{'='*60}")
    print("LEITURA ATUAL DOS REGISTROS (como estão):")
    print("-" * 60)

    for i, base_reg in enumerate([2112, 2118, 2128], 1):
        reg_a = base_reg
        reg_b = base_reg + 2

        val_a = client.read_register(reg_a)
        val_b = client.read_register(reg_b)

        print(f"Ângulo {i}:")
        print(f"  Reg {reg_a}: {val_a}")
        print(f"  Reg {reg_b}: {val_b}")

        if val_a is not None and val_b is not None:
            # Tentar como 32-bit
            as_32bit_normal = (val_a << 16) | val_b
            as_32bit_inverse = (val_b << 16) | val_a
            print(f"  Como 32-bit ({reg_a} MSW): {as_32bit_normal}")
            print(f"  Como 32-bit ({reg_b} MSW): {as_32bit_inverse}")
        print()

    client.disconnect()
    print("✅ Desconectado")
    return 0

if __name__ == '__main__':
    sys.exit(main())
