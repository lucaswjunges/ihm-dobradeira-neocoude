#!/usr/bin/env python3
"""
Verificar estado 00BE (190 decimal) - Habilita modo Modbus slave
Este estado DEVE estar ON para que o CLP aceite escritas via Modbus
"""

from pymodbus.client import ModbusSerialClient

PORT = '/dev/ttyUSB0'
BAUDRATE = 57600
SLAVE_ADDRESS = 1

# Estado 00BE (hex) = 190 (decimal) - Enable Modbus slave mode
STATE_00BE = 190

print("=" * 60)
print("VERIFICAÇÃO DO ESTADO 00BE (Modbus Slave Enable)")
print("=" * 60)

client = ModbusSerialClient(
    port=PORT,
    baudrate=BAUDRATE,
    parity='N',
    stopbits=2,
    bytesize=8,
    timeout=1.0
)

if not client.connect():
    print("❌ Falha ao conectar")
    exit(1)

print(f"✓ Conectado ao PLC (slave {SLAVE_ADDRESS})")

# Ler estado 00BE (coil 190)
print(f"\nLendo estado 00BE (coil {STATE_00BE})...")
response = client.read_coils(
    address=STATE_00BE,
    count=1,
    device_id=SLAVE_ADDRESS
)

if response.isError():
    print(f"❌ ERRO ao ler: {response}")
else:
    state_value = response.bits[0]
    print(f"\nEstado 00BE: {state_value} ({'ON ✓' if state_value else 'OFF ✗'})")

    if not state_value:
        print("\n⚠️ PROBLEMA ENCONTRADO!")
        print("   Estado 00BE está OFF - Modbus slave mode DESABILITADO")
        print("   Isso explica por que as escritas não funcionam!")
        print("\n   SOLUÇÃO:")
        print("   1. Abra o programa ladder (WinSUP)")
        print("   2. Force o estado 00BE para ON")
        print("   3. Grave no CLP")
        print("   4. Teste novamente")
    else:
        print("\n✓ Estado 00BE está ON - Modbus slave habilitado")
        print("   O problema deve ser outra coisa...")
        print("\n   Outras verificações necessárias:")
        print("   - Verificar se saídas S0-S7 estão bloqueadas por ladder logic")
        print("   - Verificar modo de operação do CLP")

# Ler também estados relacionados
print("\n" + "=" * 60)
print("OUTROS ESTADOS RELACIONADOS:")
print("=" * 60)

states_to_check = {
    189: "00BD - Print channel selector",
    976: "03D0 - Modbus master mode (deve estar OFF)",
    241: "00F1 - Keyboard lock"
}

for addr, description in states_to_check.items():
    response = client.read_coils(address=addr, count=1, device_id=SLAVE_ADDRESS)
    if not response.isError():
        value = response.bits[0]
        print(f"  Estado {addr:04d} ({description}): {value} ({'ON' if value else 'OFF'})")

client.close()
print("\n" + "=" * 60)
