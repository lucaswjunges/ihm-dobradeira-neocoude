"""
test_mapped_addresses.py

Testa leitura dos endereços mapeados do ladder
"""

from pymodbus.client import ModbusSerialClient
import modbus_map as mm

client = ModbusSerialClient(
    port='/dev/ttyUSB0',
    baudrate=57600,
    parity='N',
    stopbits=1,
    bytesize=8,
    timeout=1.0
)

print("=" * 80)
print("TESTE DE ENDEREÇOS MAPEADOS DO LADDER")
print("=" * 80)

if not client.connect():
    print("✗ Falha ao conectar")
    exit(1)

print("✓ Conectado ao CLP\n")

# Testar setpoints de ângulo
print("SETPOINTS DE ÂNGULO:")
print("-" * 80)
for name, addr in mm.ANGLE_SETPOINTS.items():
    try:
        response = client.read_holding_registers(addr, count=1, device_id=1)
        if not response.isError():
            print(f"  ✓ {name:15s} (0x{addr:04X} / {addr:4d}): {response.registers[0]}")
        else:
            print(f"  ✗ {name:15s} (0x{addr:04X} / {addr:4d}): {response}")
    except Exception as e:
        print(f"  ✗ {name:15s} (0x{addr:04X} / {addr:4d}): {e}")

# Testar bits de modo
print("\nBITS DE MODO/CICLO:")
print("-" * 80)
for name, addr in mm.MODE_BITS.items():
    try:
        response = client.read_coils(addr, count=1, device_id=1)
        if not response.isError():
            print(f"  ✓ {name:20s} (0x{addr:04X} / {addr:4d}): {response.bits[0]}")
        else:
            print(f"  ✗ {name:20s} (0x{addr:04X} / {addr:4d}): {response}")
    except Exception as e:
        print(f"  ✗ {name:20s} (0x{addr:04X} / {addr:4d}): {e}")

# Testar setpoints de quantidade
print("\nSETPOINTS DE QUANTIDADE:")
print("-" * 80)
for name, addr in mm.QUANTITY_SETPOINTS.items():
    try:
        response = client.read_holding_registers(addr, count=1, device_id=1)
        if not response.isError():
            print(f"  ✓ {name:15s} (0x{addr:04X} / {addr:4d}): {response.registers[0]}")
        else:
            print(f"  ✗ {name:15s} (0x{addr:04X} / {addr:4d}): {response}")
    except Exception as e:
        print(f"  ✗ {name:15s} (0x{addr:04X} / {addr:4d}): {e}")

print("\n" + "=" * 80)
client.close()
