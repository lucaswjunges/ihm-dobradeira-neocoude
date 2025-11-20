#!/usr/bin/env python3
"""
Testa comunicação Modbus com múltiplos baudrates
"""

from pymodbus.client import ModbusSerialClient
import time

PORT = '/dev/ttyUSB0'
SLAVE_IDS = [1, 2, 3, 4, 5]
BAUDRATES = [9600, 19200, 38400, 57600, 115200]
PARITY_OPTIONS = ['N', 'E', 'O']
STOPBITS_OPTIONS = [1, 2]

print("=" * 70)
print("TESTE EXAUSTIVO DE COMUNICAÇÃO MODBUS")
print("=" * 70)
print(f"Porta: {PORT}")
print(f"Testando {len(BAUDRATES)} baudrates x {len(SLAVE_IDS)} slave IDs")
print(f"Testando paridades: {PARITY_OPTIONS}")
print(f"Testando stop bits: {STOPBITS_OPTIONS}")
print()

for baudrate in BAUDRATES:
    for parity in PARITY_OPTIONS:
        for stopbits in STOPBITS_OPTIONS:
            config_str = f"{baudrate} 8{parity}{stopbits}"
            print(f"\n[{config_str}]", end=" ", flush=True)

            client = ModbusSerialClient(
                port=PORT,
                baudrate=baudrate,
                parity=parity,
                stopbits=stopbits,
                bytesize=8,
                timeout=0.5
            )

            if not client.connect():
                print("❌ Erro ao abrir porta")
                continue

            found = False
            for slave_id in SLAVE_IDS:
                try:
                    # Tentar ler registro 1238 (encoder MSW)
                    result = client.read_holding_registers(
                        address=1238,
                        count=1,
                        device_id=slave_id
                    )

                    if not result.isError():
                        print(f"\n✓ RESPOSTA! Slave ID: {slave_id}, Config: {config_str}")
                        print(f"  Valor lido (reg 1238): {result.registers[0]}")
                        found = True
                        break

                except Exception as e:
                    pass

                time.sleep(0.05)

            if not found:
                print(".", end="", flush=True)

            client.close()
            time.sleep(0.1)

print("\n\n" + "=" * 70)
print("Teste concluído")
print("=" * 70)
