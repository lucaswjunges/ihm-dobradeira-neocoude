"""
test_read_inputs.py

Testa leitura direta das entradas digitais E0-E7 do CLP.
"""

from pymodbus.client import ModbusSerialClient

PORT = '/dev/ttyUSB0'
BAUDRATE = 57600
SLAVE_ID = 1

print("=" * 80)
print("TEST: Reading Digital Inputs E0-E7")
print("=" * 80)

client = ModbusSerialClient(
    port=PORT,
    baudrate=BAUDRATE,
    parity='N',
    stopbits=2,  # CRITICAL!
    bytesize=8,
    timeout=1.0,
    handle_local_echo=False
)

if not client.connect():
    print("❌ Failed to connect!")
    exit(1)

print("✓ Connected to PLC\n")

# Test reading discrete inputs (Function 0x02)
print("Reading Discrete Inputs (0x02) at addresses 256-263:")
try:
    response = client.read_discrete_inputs(address=256, count=8, device_id=SLAVE_ID)
    if not response.isError():
        print("✓ SUCCESS!")
        for i, bit in enumerate(response.bits[:8]):
            status = "ON " if bit else "OFF"
            symbol = "●" if bit else "○"
            print(f"  E{i}: {symbol} {status}")
    else:
        print(f"❌ Error: {response}")
except Exception as e:
    print(f"❌ Exception: {e}")

print("\n" + "=" * 80)

# Also try reading as Input Registers (Function 0x04) to compare
print("\nTrying Input Registers (0x04) at addresses 256-263:")
try:
    response = client.read_input_registers(address=256, count=8, device_id=SLAVE_ID)
    if not response.isError():
        print("✓ SUCCESS!")
        for i, reg in enumerate(response.registers):
            bit_status = bool(reg & 0x0001)
            status = "ON " if bit_status else "OFF"
            symbol = "●" if bit_status else "○"
            print(f"  E{i}: {symbol} {status} (reg value: {reg})")
    else:
        print(f"❌ Error: {response}")
except Exception as e:
    print(f"❌ Exception: {e}")

client.close()
print("\n" + "=" * 80)
print("Test complete!")
print("=" * 80)
