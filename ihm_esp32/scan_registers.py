#!/usr/bin/env python3
"""
SCAN: Varredura completa de registros para encontrar o encoder
================================================================

Este script lê TODOS os registros ao redor de 0x04D6 para encontrar
onde REALMENTE está o contador do encoder (valor 0-399).
"""

import time
from modbus_client import ModbusClientWrapper

def main():
    print("=" * 80)
    print("SCAN: VARREDURA DE REGISTROS - ENCONTRANDO O ENCODER REAL")
    print("=" * 80)
    print()

    # Conecta ao CLP
    print("🔌 Conectando ao CLP...")
    client = ModbusClientWrapper(stub_mode=False, port='/dev/ttyUSB0', baudrate=57600, slave_id=1)

    if not client.connected:
        print("✗ ERRO: CLP não conectado!")
        return

    print("✓ Conectado!\n")

    # Testa HOLDING REGISTERS
    print("=" * 80)
    print("TESTANDO: HOLDING REGISTERS (Function 0x03)")
    print("=" * 80)
    print()

    # Range ao redor de 0x04D6 (1238 dec)
    start_addr = 0x04D0  # 1232
    end_addr = 0x04E0    # 1248

    print(f"Lendo registros de 0x{start_addr:04X} até 0x{end_addr:04X}...")
    print()
    print(f"{'Endereço':<12} {'Hex':<8} {'Decimal':<10} {'Binário':<20} {'MOD 400':<10}")
    print("-" * 80)

    for addr in range(start_addr, end_addr + 1):
        try:
            # Lê como HOLDING REGISTER
            value = client.client.read_holding_registers(address=addr, count=1, slave=client.slave_id)

            if not value.isError():
                val = value.registers[0]
                mod400 = val % 400

                # Destaca valores que parecem ser encoder (0-399)
                marker = " ← CANDIDATO!" if 0 <= val <= 450 else ""

                print(f"0x{addr:04X} ({addr:<4})  0x{val:04X}  {val:<10} {bin(val):<20} {mod400:<10}{marker}")
            else:
                print(f"0x{addr:04X} ({addr:<4})  ERRO")

        except Exception as e:
            print(f"0x{addr:04X} ({addr:<4})  EXCEÇÃO: {e}")

        time.sleep(0.05)  # Delay entre leituras

    print()
    print("=" * 80)
    print("AGORA: Gire o eixo LENTAMENTE e veja qual valor MUDA!")
    print("=" * 80)
    print()
    print("Pressione Ctrl+C quando identificar o registro correto")
    print()

    try:
        while True:
            print(f"\n{'Timestamp':<12} ", end="")
            for addr in range(start_addr, end_addr + 1):
                print(f"0x{addr:04X}={client.client.read_holding_registers(address=addr, count=1, slave=client.slave_id).registers[0]:<5} ", end="")
            time.sleep(0.2)
    except KeyboardInterrupt:
        print("\n\nFinalizado!")

    client.close()

if __name__ == "__main__":
    main()
