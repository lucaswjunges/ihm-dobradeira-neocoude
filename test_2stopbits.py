"""
test_2stopbits.py

Testa comunicação Modbus RTU com 2 stop bits (configuração correta do Windows).
"""

from pymodbus.client import ModbusSerialClient
import time

PORT = '/dev/ttyUSB0'
BAUDRATE = 57600
SLAVE_ID = 1

print("=" * 80)
print("MODBUS RTU TEST - 2 STOP BITS (Windows Config)")
print("=" * 80)
print(f"Port: {PORT}")
print(f"Baudrate: {BAUDRATE}")
print(f"Parity: None")
print(f"Stop bits: 2")
print(f"Data bits: 8")
print(f"Slave ID: {SLAVE_ID}")
print("=" * 80)

# Conectar com configuração correta
client = ModbusSerialClient(
    port=PORT,
    baudrate=BAUDRATE,
    parity='N',
    stopbits=2,  # CRITICAL: 2 stop bits like Windows!
    bytesize=8,
    timeout=1.0,
    handle_local_echo=False
)

if not client.connect():
    print("❌ Failed to connect!")
    exit(1)

print("✓ Connected to PLC\n")

# ============================================================================
# TESTE 1: Encoder (32-bit) - Registers 1238-1239
# ============================================================================
print("TEST 1: Reading Encoder (32-bit value)")
print("-" * 80)

try:
    response = client.read_holding_registers(address=1238, count=2, device_id=SLAVE_ID)
    if not response.isError():
        msw = response.registers[0]
        lsw = response.registers[1]
        value_32bit = (msw << 16) | lsw
        print(f"✓ SUCCESS!")
        print(f"  MSW (1238): {msw} (0x{msw:04X})")
        print(f"  LSW (1239): {lsw} (0x{lsw:04X})")
        print(f"  32-bit Encoder: {value_32bit}")
    else:
        print(f"❌ Error: {response}")
except Exception as e:
    print(f"❌ Exception: {e}")

time.sleep(0.2)

# ============================================================================
# TESTE 2: Digital Inputs E0-E7
# ============================================================================
print("\n" + "=" * 80)
print("TEST 2: Reading Digital Inputs E0-E7")
print("-" * 80)

# Try with Read Holding Registers (as per manual, digital I/O are in register space)
try:
    response = client.read_holding_registers(address=256, count=8, device_id=SLAVE_ID)
    if not response.isError():
        print(f"✓ SUCCESS!")
        for i, reg in enumerate(response.registers):
            bit_status = bool(reg & 0x0001)
            print(f"  E{i}: {bit_status} (reg: {reg})")
    else:
        print(f"❌ Error: {response}")
except Exception as e:
    print(f"❌ Exception: {e}")

time.sleep(0.2)

# ============================================================================
# TESTE 3: Digital Outputs S0-S7
# ============================================================================
print("\n" + "=" * 80)
print("TEST 3: Reading Digital Outputs S0-S7")
print("-" * 80)

try:
    response = client.read_holding_registers(address=384, count=8, device_id=SLAVE_ID)
    if not response.isError():
        print(f"✓ SUCCESS!")
        for i, reg in enumerate(response.registers):
            bit_status = bool(reg & 0x0001)
            print(f"  S{i}: {bit_status} (reg: {reg})")
    else:
        print(f"❌ Error: {response}")
except Exception as e:
    print(f"❌ Exception: {e}")

time.sleep(0.2)

# ============================================================================
# TESTE 4: Test reading some internal states as registers
# ============================================================================
print("\n" + "=" * 80)
print("TEST 4: Reading Internal States (as registers)")
print("-" * 80)

test_addresses = [
    (190, "MODBUS_ENABLE"),
    (768, "CYCLE_STATE_0"),
    (896, "BEND_1_ACTIVE"),
]

for addr, name in test_addresses:
    try:
        response = client.read_holding_registers(address=addr, count=1, device_id=SLAVE_ID)
        if not response.isError():
            print(f"  ✓ {name} ({addr}): {response.registers[0]}")
        else:
            print(f"  ❌ {name} ({addr}): {response}")
    except Exception as e:
        print(f"  ❌ {name} ({addr}): {e}")
    time.sleep(0.1)

# ============================================================================
# TESTE 5: Button press test (K1)
# ============================================================================
print("\n" + "=" * 80)
print("TEST 5: Testing Button Press (K1 at address 160)")
print("-" * 80)

K1_ADDRESS = 160

try:
    # Press
    print("Pressing K1 (write coil ON)...")
    response = client.write_coil(address=K1_ADDRESS, value=True, device_id=SLAVE_ID)
    if not response.isError():
        print("  ✓ K1 pressed (ON)")
        time.sleep(0.1)

        # Release
        print("Releasing K1 (write coil OFF)...")
        response = client.write_coil(address=K1_ADDRESS, value=False, device_id=SLAVE_ID)
        if not response.isError():
            print("  ✓ K1 released (OFF)")
        else:
            print(f"  ❌ Release failed: {response}")
    else:
        print(f"  ❌ Press failed: {response}")
except Exception as e:
    print(f"  ❌ Exception: {e}")

client.close()

print("\n" + "=" * 80)
print("Test complete!")
print("=" * 80)
