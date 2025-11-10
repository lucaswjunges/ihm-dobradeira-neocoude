"""
test_slave_id.py

Testa diferentes Slave IDs para encontrar o correto.
"""

from pymodbus.client import ModbusSerialClient
import time

PORT = '/dev/ttyUSB0'
BAUDRATE = 57600

print("=" * 80)
print("SLAVE ID DISCOVERY - ATOS MPC4004")
print("=" * 80)

# Conectar
client = ModbusSerialClient(
    port=PORT,
    baudrate=BAUDRATE,
    parity='N',
    stopbits=1,
    bytesize=8,
    timeout=0.5
)

if not client.connect():
    print("❌ Failed to connect!")
    exit(1)

print("✓ Connected to serial port\n")

# Testar slave IDs de 1 a 10
print("Testing Slave IDs from 1 to 10...")
print("-" * 80)

for slave_id in range(1, 11):
    print(f"\nTesting Slave ID = {slave_id}:")

    # Tentar ler registro 0 (comum em muitos PLCs)
    try:
        response = client.read_holding_registers(address=0, count=1, device_id=slave_id)
        if not response.isError():
            print(f"  ✓ Read Holding Register 0: {response.registers[0]} (0x{response.registers[0]:04X})")
        else:
            print(f"  ❌ Holding Register 0: {response}")
    except Exception as e:
        print(f"  ❌ Holding Register 0: {e}")

    time.sleep(0.1)

    # Tentar ler coil 0
    try:
        response = client.read_coils(address=0, count=1, device_id=slave_id)
        if not response.isError():
            print(f"  ✓ Read Coil 0: {response.bits[0]}")
        else:
            print(f"  ❌ Coil 0: {response}")
    except Exception as e:
        print(f"  ❌ Coil 0: {e}")

    time.sleep(0.1)

# Agora testar com broadcast (slave 0) para ver se o CLP responde
print("\n" + "=" * 80)
print("Testing with Broadcast Address (0):")
print("-" * 80)

try:
    response = client.read_holding_registers(address=0, count=1, device_id=0)
    if not response.isError():
        print(f"✓ Broadcast works! Register 0: {response.registers[0]}")
    else:
        print(f"❌ Broadcast: {response}")
except Exception as e:
    print(f"❌ Broadcast: {e}")

client.close()
print("\n" + "=" * 80)
print("Test complete!")
print("=" * 80)
