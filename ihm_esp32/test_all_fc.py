#!/usr/bin/env python3
"""
Testar TODOS os function codes para encontrar qual funciona
"""
from pymodbus.client import ModbusSerialClient
import time

PORT = "/dev/ttyUSB0"
BAUDRATE = 57600
SLAVE_ID = 1

client = ModbusSerialClient(
    port=PORT,
    baudrate=BAUDRATE,
    parity='N',
    stopbits=2,
    bytesize=8,
    timeout=0.5
)

if not client.connect():
    print(f"✗ Falha ao conectar")
    exit(1)

print(f"✓ Conectado!\n")

# Endereços para testar
test_addresses = [1, 10, 100, 256, 1238, 2136, 2304]

print("="*80)
print(f"{'Endereço':<15} {'FC 0x01':<15} {'FC 0x02':<15} {'FC 0x03':<15} {'FC 0x04':<15}")
print(f"{'(Dec)':<15} {'Coils':<15} {'Disc.Inp':<15} {'Hold.Reg':<15} {'Inp.Reg':<15}")
print("="*80)

for addr in test_addresses:
    results = []

    # FC 0x01 - Read Coils
    try:
        r = client.read_coils(addr, count=1, slave=SLAVE_ID)
        if not r.isError():
            results.append(f"✓ {r.bits[0]}")
        else:
            results.append("✗")
    except:
        results.append("✗")

    time.sleep(0.05)

    # FC 0x02 - Read Discrete Inputs
    try:
        r = client.read_discrete_inputs(addr, count=1, slave=SLAVE_ID)
        if not r.isError():
            results.append(f"✓ {r.bits[0]}")
        else:
            results.append("✗")
    except:
        results.append("✗")

    time.sleep(0.05)

    # FC 0x03 - Read Holding Registers
    try:
        r = client.read_holding_registers(addr, count=1, slave=SLAVE_ID)
        if not r.isError():
            results.append(f"✓ 0x{r.registers[0]:04X}")
        else:
            results.append("✗")
    except:
        results.append("✗")

    time.sleep(0.05)

    # FC 0x04 - Read Input Registers
    try:
        r = client.read_input_registers(addr, count=1, slave=SLAVE_ID)
        if not r.isError():
            results.append(f"✓ 0x{r.registers[0]:04X}")
        else:
            results.append("✗")
    except:
        results.append("✗")

    print(f"{addr:<15} {results[0]:<15} {results[1]:<15} {results[2]:<15} {results[3]:<15}")
    time.sleep(0.1)

print("="*80)
client.close()
print("\n✓ Teste concluído")
