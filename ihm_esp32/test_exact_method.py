#!/usr/bin/env python3
"""
Testar exatamente como o código original faz
"""
from pymodbus.client import ModbusSerialClient
import time

PORT = "/dev/ttyUSB0"
BAUDRATE = 57600
SLAVE_ID = 1

# Criar client EXATAMENTE como modbus_client.py
client = ModbusSerialClient(
    port=PORT,
    baudrate=BAUDRATE,
    parity='N',
    stopbits=2,  # IMPORTANTE: 2 stop bits
    bytesize=8,
    timeout=0.2  # 200ms como no código original
)

if not client.connect():
    print(f"✗ Falha ao conectar")
    exit(1)

print(f"✓ Conectado!")

# Testar leitura EXATAMENTE como no código
print("\nTestando read_holding_registers com os mesmos parâmetros:")

test_addresses = [
    (1238, "Encoder 0x04D6"),
    (2136, "0x0858"),
    (2304, "NUMERO0 0x0900"),
]

for addr, desc in test_addresses:
    print(f"\n{desc} (addr={addr}):")
    try:
        # EXATAMENTE como no código original
        result = client.read_holding_registers(
            address=addr,
            count=1,
            slave=SLAVE_ID
        )

        if result.isError():
            print(f"  ✗ isError() = True")
            print(f"  ✗ Erro: {result}")
        else:
            print(f"  ✓ Sucesso! Valor: {result.registers[0]} (0x{result.registers[0]:04X})")
    except Exception as e:
        print(f"  ✗ Exception: {e}")

    time.sleep(0.1)

client.close()
print("\n✓ Teste concluído")
