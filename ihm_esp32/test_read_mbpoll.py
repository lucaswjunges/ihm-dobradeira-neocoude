#!/usr/bin/env python3
"""
Test reading registers with pymodbus (what works) vs mbpoll
"""
import sys
sys.path.insert(0, '/home/lucas-junges/Documents/wco/ihm_esp32')

from modbus_client import ModbusClientWrapper
import modbus_map as mm

# Connect
client = ModbusClientWrapper(stub_mode=False, port='/dev/ttyUSB0', slave_id=1)

if not client.connected:
    print("✗ Não conectou!")
    sys.exit(1)

print("✓ Conectado ao CLP!\n")

# Test encoder
print("="*60)
print("TESTE 1: Encoder (0x04D6 = 1238)")
print("="*60)
encoder_val = client.read_register(mm.ENCODER['ANGLE_MSW'])
print(f"Encoder MSW (1238): {encoder_val}")
print(f"  Hex: 0x{encoder_val:04X}" if encoder_val is not None else "  ERRO")
print(f"  Decimal: {encoder_val}\n" if encoder_val is not None else "")

# Test work registers
print("="*60)
print("TESTE 2: Work Registers")
print("="*60)
for name, addr in mm.WORK_REGISTERS.items():
    val = client.read_register(addr)
    if val is not None:
        print(f"{name:20s} (0x{addr:04X} = {addr:4d}): {val:5d} (0x{val:04X})")
    else:
        print(f"{name:20s} (0x{addr:04X} = {addr:4d}): ERRO")

print("\n" + "="*60)
print("COMANDOS MBPOLL EQUIVALENTES:")
print("="*60)
print(f"# Encoder:")
print(f"mbpoll -a 1 -b 57600 -P none -s 2 -t 3 -r {mm.ENCODER['ANGLE_MSW']} -c 1 /dev/ttyUSB0")
print(f"\n# Work Registers:")
print(f"mbpoll -a 1 -b 57600 -P none -s 2 -t 3 -r 2304 -c 13 /dev/ttyUSB0")

client.close()
