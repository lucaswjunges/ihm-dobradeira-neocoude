#!/usr/bin/env python3
"""
test_e0_direct.py

Direct test to verify E0 input status at the PLC level.
User has E0 connected to 24VDC.
"""

from pymodbus.client import ModbusSerialClient

PORT = '/dev/ttyUSB0'
BAUDRATE = 57600
SLAVE_ID = 1

print("=" * 80)
print("DIRECT E0 INPUT TEST")
print("=" * 80)
print(f"Port: {PORT}")
print(f"Config: {BAUDRATE} baud, 2 stop bits, no parity")
print(f"Slave ID: {SLAVE_ID}")
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
    print("❌ Failed to connect to PLC!")
    exit(1)

print("✓ Connected to PLC\n")

# Test reading E0 (address 256) using Read Discrete Inputs (0x02)
print("Reading E0 input (address 256) using Function 0x02:")
try:
    response = client.read_discrete_inputs(address=256, count=1, device_id=SLAVE_ID)
    if not response.isError():
        e0_status = response.bits[0]
        symbol = "🟢 ●" if e0_status else "⚪ ○"
        status_text = "ON (ACTIVE)" if e0_status else "OFF (INACTIVE)"
        print(f"\n{symbol} E0: {status_text}")

        if e0_status:
            print("\n✅ SUCCESS! E0 is reading as ACTIVE at PLC level")
            print("   → The PLC is correctly detecting the 24VDC signal")
            print("   → Issue must be in state_manager or WebSocket communication")
        else:
            print("\n⚠️  WARNING! E0 is reading as INACTIVE")
            print("   → Check wiring:")
            print("     - E0 connected to 24VDC+")
            print("     - Common ground connected")
            print("     - Terminal connections tight")
    else:
        print(f"❌ Modbus Error: {response}")
except Exception as e:
    print(f"❌ Exception: {e}")

print("\n" + "=" * 80)

# Also read all E0-E7 for context
print("\nReading all digital inputs E0-E7:")
try:
    response = client.read_discrete_inputs(address=256, count=8, device_id=SLAVE_ID)
    if not response.isError():
        active_inputs = []
        print("\nStatus:")
        for i, bit in enumerate(response.bits[:8]):
            status = "ON " if bit else "OFF"
            symbol = "●" if bit else "○"
            print(f"  E{i}: {symbol} {status}")
            if bit:
                active_inputs.append(f'E{i}')

        if active_inputs:
            print(f"\n✓ Active inputs detected: {', '.join(active_inputs)}")
        else:
            print("\n⚠️  No active inputs detected")
    else:
        print(f"❌ Error: {response}")
except Exception as e:
    print(f"❌ Exception: {e}")

client.close()
print("\n" + "=" * 80)
print("Test complete!")
print("=" * 80)
