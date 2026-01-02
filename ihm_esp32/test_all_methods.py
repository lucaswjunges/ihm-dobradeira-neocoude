#!/usr/bin/env python3
"""
TESTE: Todas as combinações possíveis para encontrar o encoder
================================================================

Testa:
- HOLDING REGISTERS (FC 0x03) vs INPUT REGISTERS (FC 0x04)
- Offset 0 vs Offset -1
- 16-bit vs 32-bit
"""

import time
from modbus_client import ModbusClientWrapper

def test_register(client, func_name, func, addr, offset=0):
    """Testa ler um registro com uma função específica"""
    try:
        addr_with_offset = addr + offset
        result = func(address=addr_with_offset, count=1, slave=client.slave_id)

        if not result.isError():
            val = result.registers[0]
            return val
        else:
            return "ERRO"
    except Exception as e:
        return f"EXC: {str(e)[:30]}"

def main():
    print("=" * 80)
    print("TESTE COMPLETO: Todas combinações para encontrar encoder")
    print("=" * 80)
    print()

    # Conecta
    client = ModbusClientWrapper(stub_mode=False, port='/dev/ttyUSB0', baudrate=57600, slave=1)

    if not client.connected:
        print("✗ CLP não conectado!")
        return

    print("✓ Conectado!\n")

    # Endereços para testar
    test_addresses = [
        0x04D6,  # 1238 - MSW esperado
        0x04D7,  # 1239 - LSW esperado
        0x04D5,  # 1237 - teste offset
        0x04D4,  # 1236 - teste offset
    ]

    print("TESTANDO LEITURA COM DIFERENTES FUNÇÕES E OFFSETS:")
    print("=" * 80)
    print()

    for addr in test_addresses:
        print(f"\n📍 Endereço 0x{addr:04X} ({addr} decimal):")
        print("-" * 60)

        # Teste 1: HOLDING REGISTERS (0x03) - offset 0
        val = test_register(client, "HOLD", client.client.read_holding_registers, addr, offset=0)
        print(f"  HOLDING (FC 0x03) offset=0  : {val}")

        # Teste 2: HOLDING REGISTERS (0x03) - offset -1
        val = test_register(client, "HOLD", client.client.read_holding_registers, addr, offset=-1)
        print(f"  HOLDING (FC 0x03) offset=-1 : {val}")

        # Teste 3: INPUT REGISTERS (0x04) - offset 0
        val = test_register(client, "INPUT", client.client.read_input_registers, addr, offset=0)
        print(f"  INPUT   (FC 0x04) offset=0  : {val}")

        # Teste 4: INPUT REGISTERS (0x04) - offset -1
        val = test_register(client, "INPUT", client.client.read_input_registers, addr, offset=-1)
        print(f"  INPUT   (FC 0x04) offset=-1 : {val}")

        time.sleep(0.1)

    print("\n\n" + "=" * 80)
    print("ANÁLISE: Qual valor está entre 0-399?")
    print("=" * 80)

    client.close()

if __name__ == "__main__":
    main()
