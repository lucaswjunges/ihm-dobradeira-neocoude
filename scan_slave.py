"""
scan_slave.py

Escaneia Slave IDs de 1 a 247 para encontrar o CLP.
"""

from pymodbus.client import ModbusSerialClient

client = ModbusSerialClient(
    port='/dev/ttyUSB0',
    baudrate=57600,
    parity='N',
    stopbits=1,
    bytesize=8,
    timeout=0.5
)

print("Conectando ao /dev/ttyUSB0...")
if not client.connect():
    print("✗ Falha ao conectar!")
    exit(1)

print("✓ Conectado! Escaneando slave IDs de 1 a 247...\n")

found = []

for slave_id in range(1, 248):
    try:
        # Tenta ler holding register 0 (quase todo CLP tem)
        response = client.read_holding_registers(0, count=1, device_id=slave_id)

        if not response.isError():
            print(f"✓ ENCONTRADO! Slave ID: {slave_id} - Valor registro 0: {response.registers[0]}")
            found.append(slave_id)
    except:
        pass

    if slave_id % 50 == 0:
        print(f"  ... escaneado até {slave_id}")

client.close()

print(f"\n{'='*60}")
if found:
    print(f"SLAVE IDs encontrados: {found}")
else:
    print("Nenhum slave ID respondeu :(")
print("=" * 60)
