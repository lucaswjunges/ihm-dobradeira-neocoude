"""
scan_coils.py

Escaneia Slave IDs lendo coils (states) ao invés de holding registers.
Tenta ler o estado 0BE (190 dec) que deve estar ON para Modbus ativo.
"""

from pymodbus.client import ModbusSerialClient
import time

client = ModbusSerialClient(
    port='/dev/ttyUSB0',
    baudrate=57600,
    parity='N',
    stopbits=1,
    bytesize=8,
    timeout=0.3
)

print("Conectando ao /dev/ttyUSB0...")
if not client.connect():
    print("✗ Falha ao conectar!")
    exit(1)

print("✓ Conectado! Escaneando slave IDs de 1 a 50...\n")
print("Testando coil 190 (0xBE - Modbus Enable)...\n")

found = []

for slave_id in range(1, 51):
    try:
        # Tenta ler coil 190 (0xBE - Modbus enable)
        response = client.read_coils(190, count=1, device_id=slave_id)

        if not response.isError():
            print(f"✓ ENCONTRADO! Slave ID: {slave_id} - Coil 0xBE: {response.bits[0]}")
            found.append(slave_id)
        time.sleep(0.05)
    except Exception as e:
        pass

print(f"\n{'='*60}")
if found:
    print(f"SLAVE IDs encontrados: {found}")
    print(f"\nUSE: --slave-address {found[0]}")
else:
    print("Nenhum slave ID respondeu. Verificar:")
    print("  1. Estado 0BE está ON no ladder?")
    print("  2. Cabo RS485 A/B conectado corretamente?")
    print("  3. Baudrate correto (57600)?")
print("=" * 60)

client.close()
