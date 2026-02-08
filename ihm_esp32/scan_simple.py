#!/usr/bin/env python3
"""
Scan simples para encontrar QUALQUER registro que responda
"""
from pymodbus.client import ModbusSerialClient
import time

PORT = "/dev/ttyUSB0"
BAUDRATE = 57600
SLAVE_ID = 1

# Criar client
client = ModbusSerialClient(
    port=PORT,
    baudrate=BAUDRATE,
    parity='N',
    stopbits=2,
    bytesize=8,
    timeout=0.5
)

if not client.connect():
    print(f"✗ Não conectou em {PORT}")
    exit(1)

print(f"✓ Conectado em {PORT}\n")

# Testar vários endereços estratégicos
test_addrs = [
    (1, "Primeiro registro"),
    (10, "Registro 10"),
    (100, "Registro 100"),
    (256, "Digital I/O 0x0100"),
    (384, "Digital outputs 0x0180"),
    (1024, "Timer/Counter 0x0400"),
    (1232, "High-speed counter 0x04D0"),
    (1238, "Encoder 0x04D6"),
    (1520, "Analog inputs 0x05F0"),
    (2136, "0x0858"),
    (2304, "NUMERO0 0x0900"),
    (6528, "Baudrate config 0x1980"),
    (6536, "Slave address 0x1988"),
]

print("="*70)
print(f"{'Endereço':<20} {'Decimal':<10} {'Hex':<10} {'Resultado':<30}")
print("="*70)

for addr, desc in test_addrs:
    # Tentar FC 0x03 (Read Holding Registers)
    try:
        result = client.read_holding_registers(addr, count=1, slave=SLAVE_ID)

        if not result.isError():
            value = result.registers[0]
            print(f"{desc:<20} {addr:<10} 0x{addr:04X}      ✓ FC03: {value} (0x{value:04X})")
        else:
            print(f"{desc:<20} {addr:<10} 0x{addr:04X}      ✗ FC03: {result}")
    except Exception as e:
        print(f"{desc:<20} {addr:<10} 0x{addr:04X}      ✗ FC03: {e}")

    time.sleep(0.1)

print("\n" + "="*70)
client.close()
print("✓ Conexão fechada")
