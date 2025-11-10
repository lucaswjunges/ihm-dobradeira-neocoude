"""
force_modbus_enable.py

Força o estado 0x00BE (190 decimal) ON para habilitar Modbus no CLP Atos.
"""

from pymodbus.client import ModbusSerialClient

PORT = '/dev/ttyUSB0'
BAUDRATE = 57600
SLAVE_ID = 1
MODBUS_ENABLE_COIL = 190  # 0x00BE

print("=" * 80)
print("FORCE MODBUS ENABLE - ATOS MPC4004")
print("=" * 80)
print(f"Port: {PORT}")
print(f"Baudrate: {BAUDRATE}")
print(f"Slave ID: {SLAVE_ID}")
print(f"Target Coil: {MODBUS_ENABLE_COIL} (0x{MODBUS_ENABLE_COIL:04X})")
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

# Tentar forçar o coil 190 (Modbus enable) para ON
print(f"Forcing coil {MODBUS_ENABLE_COIL} to ON...")

try:
    response = client.write_coil(address=MODBUS_ENABLE_COIL, value=True, device_id=SLAVE_ID)

    if response.isError():
        print(f"❌ Error: {response}")
    else:
        print(f"✓ Coil {MODBUS_ENABLE_COIL} forced to ON!")

        # Tentar ler de volta para confirmar
        print("\nReading back coil value...")
        read_response = client.read_coils(address=MODBUS_ENABLE_COIL, count=1, device_id=SLAVE_ID)

        if not read_response.isError():
            print(f"✓ Coil value: {read_response.bits[0]}")
        else:
            print(f"❌ Read error: {read_response}")

except Exception as e:
    print(f"❌ Exception: {e}")

client.close()

print("\n" + "=" * 80)
print("Done! Try running Modbus commands now.")
print("=" * 80)
