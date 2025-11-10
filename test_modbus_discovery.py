"""
test_modbus_discovery.py

Descobre quais endereços e funções Modbus funcionam no CLP Atos MPC4004.
Testa diferentes funções Modbus em endereços conhecidos do manual.
"""

from pymodbus.client import ModbusSerialClient
import time

# Configuração
PORT = '/dev/ttyUSB0'
BAUDRATE = 57600
SLAVE_ID = 1

print("=" * 80)
print("MODBUS DISCOVERY - ATOS MPC4004")
print("=" * 80)
print(f"Port: {PORT}")
print(f"Baudrate: {BAUDRATE}")
print(f"Slave ID: {SLAVE_ID}")
print("=" * 80)

# Conectar
client = ModbusSerialClient(
    port=PORT,
    baudrate=BAUDRATE,
    parity='N',
    stopbits=1,
    bytesize=8,
    timeout=1.0
)

if not client.connect():
    print("❌ Failed to connect!")
    exit(1)

print("✓ Connected to PLC\n")

# ============================================================================
# TESTE 1: Encoder (32-bit counter) - Addresses 0x04D6/0x04D7 (1238/1239 dec)
# ============================================================================
print("\n" + "=" * 80)
print("TEST 1: ENCODER (High-speed counter)")
print("=" * 80)

# Tentar com Read Holding Registers (0x03)
print("\nTrying Read Holding Registers (0x03) at 1238-1239...")
try:
    response = client.read_holding_registers(address=1238, count=2, device_id=SLAVE_ID)
    if not response.isError():
        msw = response.registers[0]
        lsw = response.registers[1]
        value_32bit = (msw << 16) | lsw
        print(f"✓ SUCCESS!")
        print(f"  MSW (1238): {msw} (0x{msw:04X})")
        print(f"  LSW (1239): {lsw} (0x{lsw:04X})")
        print(f"  32-bit value: {value_32bit}")
    else:
        print(f"❌ Error: {response}")
except Exception as e:
    print(f"❌ Exception: {e}")

# Tentar com Read Input Registers (0x04)
print("\nTrying Read Input Registers (0x04) at 1238-1239...")
try:
    response = client.read_input_registers(address=1238, count=2, device_id=SLAVE_ID)
    if not response.isError():
        msw = response.registers[0]
        lsw = response.registers[1]
        value_32bit = (msw << 16) | lsw
        print(f"✓ SUCCESS!")
        print(f"  MSW (1238): {msw} (0x{msw:04X})")
        print(f"  LSW (1239): {lsw} (0x{lsw:04X})")
        print(f"  32-bit value: {value_32bit}")
    else:
        print(f"❌ Error: {response}")
except Exception as e:
    print(f"❌ Exception: {e}")

# ============================================================================
# TESTE 2: Digital Inputs E0-E7 - Addresses 0x0100-0x0107 (256-263 dec)
# ============================================================================
print("\n" + "=" * 80)
print("TEST 2: DIGITAL INPUTS E0-E7")
print("=" * 80)

# Tentar com Read Discrete Inputs (0x02)
print("\nTrying Read Discrete Inputs (0x02) at 256-263...")
try:
    response = client.read_discrete_inputs(address=256, count=8, device_id=SLAVE_ID)
    if not response.isError():
        print(f"✓ SUCCESS!")
        for i, bit in enumerate(response.bits[:8]):
            print(f"  E{i}: {bit}")
    else:
        print(f"❌ Error: {response}")
except Exception as e:
    print(f"❌ Exception: {e}")

# Tentar com Read Input Registers (0x04)
print("\nTrying Read Input Registers (0x04) at 256-263...")
try:
    response = client.read_input_registers(address=256, count=8, device_id=SLAVE_ID)
    if not response.isError():
        print(f"✓ SUCCESS!")
        for i, reg in enumerate(response.registers):
            bit_status = bool(reg & 0x0001)
            print(f"  E{i}: {bit_status} (reg value: {reg})")
    else:
        print(f"❌ Error: {response}")
except Exception as e:
    print(f"❌ Exception: {e}")

# Tentar com Read Holding Registers (0x03)
print("\nTrying Read Holding Registers (0x03) at 256-263...")
try:
    response = client.read_holding_registers(address=256, count=8, device_id=SLAVE_ID)
    if not response.isError():
        print(f"✓ SUCCESS!")
        for i, reg in enumerate(response.registers):
            bit_status = bool(reg & 0x0001)
            print(f"  E{i}: {bit_status} (reg value: {reg})")
    else:
        print(f"❌ Error: {response}")
except Exception as e:
    print(f"❌ Exception: {e}")

# ============================================================================
# TESTE 3: Digital Outputs S0-S7 - Addresses 0x0180-0x0187 (384-391 dec)
# ============================================================================
print("\n" + "=" * 80)
print("TEST 3: DIGITAL OUTPUTS S0-S7")
print("=" * 80)

# Tentar com Read Coils (0x01)
print("\nTrying Read Coils (0x01) at 384-391...")
try:
    response = client.read_coils(address=384, count=8, device_id=SLAVE_ID)
    if not response.isError():
        print(f"✓ SUCCESS!")
        for i, bit in enumerate(response.bits[:8]):
            print(f"  S{i}: {bit}")
    else:
        print(f"❌ Error: {response}")
except Exception as e:
    print(f"❌ Exception: {e}")

# Tentar com Read Holding Registers (0x03)
print("\nTrying Read Holding Registers (0x03) at 384-391...")
try:
    response = client.read_holding_registers(address=384, count=8, device_id=SLAVE_ID)
    if not response.isError():
        print(f"✓ SUCCESS!")
        for i, reg in enumerate(response.registers):
            bit_status = bool(reg & 0x0001)
            print(f"  S{i}: {bit_status} (reg value: {reg})")
    else:
        print(f"❌ Error: {response}")
except Exception as e:
    print(f"❌ Exception: {e}")

# ============================================================================
# TESTE 4: Internal States - Addresses 0x0000-0x03FF (0-1023 dec)
# ============================================================================
print("\n" + "=" * 80)
print("TEST 4: INTERNAL STATES (Coils)")
print("=" * 80)

# Tentar ler alguns estados internos conhecidos
test_states = [
    (190, "MODBUS_ENABLE (0x00BE)"),
    (768, "CYCLE_STATE_0 (0x0300)"),
    (896, "BEND_1_ACTIVE (0x0380)"),
]

for addr, name in test_states:
    print(f"\nTrying Read Coils (0x01) at {addr} - {name}...")
    try:
        response = client.read_coils(address=addr, count=1, device_id=SLAVE_ID)
        if not response.isError():
            print(f"✓ SUCCESS! State: {response.bits[0]}")
        else:
            print(f"❌ Error: {response}")
    except Exception as e:
        print(f"❌ Exception: {e}")

# ============================================================================
# TESTE 5: Scan range to find valid registers
# ============================================================================
print("\n" + "=" * 80)
print("TEST 5: SCANNING REGISTER RANGE")
print("=" * 80)

print("\nScanning registers 0-100 with Read Holding Registers (0x03)...")
successful_reads = []

for addr in range(0, 100, 10):
    try:
        response = client.read_holding_registers(address=addr, count=1, device_id=SLAVE_ID)
        if not response.isError():
            successful_reads.append((addr, response.registers[0]))
            print(f"  ✓ Addr {addr:4d} (0x{addr:04X}): {response.registers[0]:5d} (0x{response.registers[0]:04X})")
    except:
        pass
    time.sleep(0.05)  # Small delay between reads

if successful_reads:
    print(f"\nFound {len(successful_reads)} readable registers!")
else:
    print("\nNo readable registers found in range 0-100")

# Desconectar
client.close()
print("\n" + "=" * 80)
print("Discovery complete!")
print("=" * 80)
