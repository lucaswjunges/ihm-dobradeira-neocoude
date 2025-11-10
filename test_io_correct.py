"""
test_io_correct.py

Testa leitura de I/O digital usando as funções Modbus corretas.
"""

from pymodbus.client import ModbusSerialClient
import time

PORT = '/dev/ttyUSB0'
BAUDRATE = 57600
SLAVE_ID = 1

print("=" * 80)
print("MODBUS I/O TEST - Correct Functions")
print("=" * 80)

client = ModbusSerialClient(
    port=PORT,
    baudrate=BAUDRATE,
    parity='N',
    stopbits=2,
    bytesize=8,
    timeout=1.0,
    handle_local_echo=False
)

if not client.connect():
    print("❌ Failed to connect!")
    exit(1)

print("✓ Connected to PLC\n")

# ============================================================================
# TEST 1: Digital Inputs E0-E7 (try as Discrete Inputs - Function 0x02)
# ============================================================================
print("TEST 1: Digital Inputs E0-E7 (Discrete Inputs)")
print("-" * 80)

try:
    # The Atos manual says digital inputs are at 0x0100-0x0107 (256-263)
    # But they might be readable as COILS at addresses 0x0100-0x0107
    response = client.read_discrete_inputs(address=256, count=8, device_id=SLAVE_ID)
    if not response.isError():
        print("✓ SUCCESS with Read Discrete Inputs!")
        for i, bit in enumerate(response.bits[:8]):
            print(f"  E{i}: {bit}")
    else:
        print(f"❌ Discrete Inputs failed: {response}")

        # Try as Coils (Function 0x01)
        print("\nTrying as Coils (Function 0x01)...")
        response = client.read_coils(address=256, count=8, device_id=SLAVE_ID)
        if not response.isError():
            print("✓ SUCCESS with Read Coils!")
            for i, bit in enumerate(response.bits[:8]):
                print(f"  E{i}: {bit}")
        else:
            print(f"❌ Coils also failed: {response}")

except Exception as e:
    print(f"❌ Exception: {e}")

time.sleep(0.2)

# ============================================================================
# TEST 2: Digital Outputs S0-S7 (try as Coils - Function 0x01)
# ============================================================================
print("\n" + "=" * 80)
print("TEST 2: Digital Outputs S0-S7 (Coils)")
print("-" * 80)

try:
    # Outputs should be readable as coils
    response = client.read_coils(address=384, count=8, device_id=SLAVE_ID)
    if not response.isError():
        print("✓ SUCCESS with Read Coils!")
        for i, bit in enumerate(response.bits[:8]):
            print(f"  S{i}: {bit}")
    else:
        print(f"❌ Read Coils failed: {response}")

        # Try as Discrete Inputs
        print("\nTrying as Discrete Inputs...")
        response = client.read_discrete_inputs(address=384, count=8, device_id=SLAVE_ID)
        if not response.isError():
            print("✓ SUCCESS with Read Discrete Inputs!")
            for i, bit in enumerate(response.bits[:8]):
                print(f"  S{i}: {bit}")
        else:
            print(f"❌ Discrete Inputs also failed: {response}")

except Exception as e:
    print(f"❌ Exception: {e}")

time.sleep(0.2)

# ============================================================================
# TEST 3: Try reading actual physical I/O addresses
# ============================================================================
print("\n" + "=" * 80)
print("TEST 3: Scanning for actual I/O addresses")
print("-" * 80)

# According to Atos manual, digital I/O might be at different addresses
# Let's try scanning the typical ranges
test_ranges = [
    (0, 16, "Low range (0-15)"),
    (100, 116, "E100-E115 (encoder inputs)"),
    (256, 264, "0x0100-0x0107 (manual addresses)"),
]

print("Scanning with Read Coils...")
for start, end, desc in test_ranges:
    try:
        response = client.read_coils(address=start, count=end-start, device_id=SLAVE_ID)
        if not response.isError():
            print(f"\n✓ Found coils at {desc}:")
            for i, bit in enumerate(response.bits[:end-start]):
                if bit:  # Only print ON bits
                    print(f"    Coil {start+i}: ON")
        else:
            pass  # Silent failure for scanning
    except:
        pass
    time.sleep(0.1)

client.close()

print("\n" + "=" * 80)
print("Test complete!")
print("=" * 80)
