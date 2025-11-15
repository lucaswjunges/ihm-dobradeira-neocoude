#!/usr/bin/env python3
"""
Debug detalhado da função read_coil()
Investiga por que retorna False quando mbpoll lê 1
"""

from pymodbus.client import ModbusSerialClient
import time

PORT = '/dev/ttyUSB0'
BAUDRATE = 57600
SLAVE_ID = 1

print("=" * 60)
print("DEBUG: read_coil()")
print("=" * 60)
print()

# Conectar
client = ModbusSerialClient(
    port=PORT,
    baudrate=BAUDRATE,
    parity='N',
    stopbits=2,
    bytesize=8,
    timeout=1
)

if not client.connect():
    print("❌ Falha ao conectar")
    exit(1)

print("✅ Conectado ao CLP")
print()

# Testar E6 (0x0106 = 262)
print("-" * 60)
print("Teste 1: E6 (endereço 0x0106 = 262)")
print("-" * 60)

address = 0x0106

try:
    result = client.read_coils(address=address, count=1)

    print(f"Tipo de result: {type(result)}")
    print(f"result.isError(): {result.isError()}")
    print(f"result: {result}")

    if hasattr(result, 'bits'):
        print(f"result.bits: {result.bits}")
        print(f"result.bits[0]: {result.bits[0]}")
        print(f"type(result.bits[0]): {type(result.bits[0])}")
        print(f"bool(result.bits[0]): {bool(result.bits[0])}")

    if hasattr(result, '__dict__'):
        print(f"result.__dict__: {result.__dict__}")

except Exception as e:
    print(f"✗ Exceção: {e}")
    import traceback
    traceback.print_exc()

print()

# Testar Mode (0x02FF = 767)
print("-" * 60)
print("Teste 2: Mode (endereço 0x02FF = 767)")
print("-" * 60)

address = 0x02FF

try:
    result = client.read_coils(address=address, count=1)

    print(f"Tipo de result: {type(result)}")
    print(f"result.isError(): {result.isError()}")
    print(f"result: {result}")

    if hasattr(result, 'bits'):
        print(f"result.bits: {result.bits}")
        print(f"result.bits[0]: {result.bits[0]}")
        print(f"type(result.bits[0]): {type(result.bits[0])}")
        print(f"bool(result.bits[0]): {bool(result.bits[0])}")

    if hasattr(result, '__dict__'):
        print(f"result.__dict__: {result.__dict__}")

except Exception as e:
    print(f"✗ Exceção: {e}")
    import traceback
    traceback.print_exc()

print()

# Testar K1 (0x00A0 = 160) - deveria estar False
print("-" * 60)
print("Teste 3: K1 (endereço 0x00A0 = 160) - deveria estar False")
print("-" * 60)

address = 0x00A0

try:
    result = client.read_coils(address=address, count=1)

    print(f"Tipo de result: {type(result)}")
    print(f"result.isError(): {result.isError()}")
    print(f"result: {result}")

    if hasattr(result, 'bits'):
        print(f"result.bits: {result.bits}")
        print(f"result.bits[0]: {result.bits[0]}")
        print(f"type(result.bits[0]): {type(result.bits[0])}")
        print(f"bool(result.bits[0]): {bool(result.bits[0])}")

    if hasattr(result, '__dict__'):
        print(f"result.__dict__: {result.__dict__}")

except Exception as e:
    print(f"✗ Exceção: {e}")
    import traceback
    traceback.print_exc()

print()
print("=" * 60)
print("FIM DO DEBUG")
print("=" * 60)

client.close()
