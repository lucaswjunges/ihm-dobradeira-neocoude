"""
test_plc.py

Teste direto de comunicação com CLP - Slave ID 1
"""

from pymodbus.client import ModbusSerialClient
import time

client = ModbusSerialClient(
    port='/dev/ttyUSB0',
    baudrate=57600,
    parity='N',
    stopbits=1,
    bytesize=8,
    timeout=1.0
)

print("=" * 60)
print("TESTE DE COMUNICAÇÃO MODBUS RTU")
print("=" * 60)
print(f"Porta: /dev/ttyUSB0")
print(f"Baudrate: 57600")
print(f"Slave ID: 1")
print(f"Timeout: 1.0s")
print()

print("Conectando...")
if not client.connect():
    print("✗ ERRO: Falha ao abrir porta serial")
    exit(1)

print("✓ Porta serial aberta\n")

# Teste 1: Ler coil 190 (0xBE - Modbus enable)
print("Teste 1: Lendo coil 190 (0xBE - Modbus Enable)...")
try:
    response = client.read_coils(190, count=1, device_id=1)
    if response.isError():
        print(f"  ✗ ERRO: {response}")
    else:
        print(f"  ✓ Coil 190 = {response.bits[0]}")
except Exception as e:
    print(f"  ✗ EXCEÇÃO: {e}")

time.sleep(0.5)

# Teste 2: Ler holding register 0
print("\nTeste 2: Lendo holding register 0...")
try:
    response = client.read_holding_registers(0, count=1, device_id=1)
    if response.isError():
        print(f"  ✗ ERRO: {response}")
    else:
        print(f"  ✓ Registro 0 = {response.registers[0]}")
except Exception as e:
    print(f"  ✗ EXCEÇÃO: {e}")

time.sleep(0.5)

# Teste 3: Ler encoder (registros 1238/1239)
print("\nTeste 3: Lendo encoder (registro 1238)...")
try:
    response = client.read_holding_registers(1238, count=2, device_id=1)
    if response.isError():
        print(f"  ✗ ERRO: {response}")
    else:
        msw = response.registers[0]
        lsw = response.registers[1]
        angle = (msw << 16) | lsw
        print(f"  ✓ MSW (1238) = {msw}")
        print(f"  ✓ LSW (1239) = {lsw}")
        print(f"  ✓ Ângulo = {angle}")
except Exception as e:
    print(f"  ✗ EXCEÇÃO: {e}")

time.sleep(0.5)

# Teste 4: Ler input status (função 0x02)
print("\nTeste 4: Lendo input status (coil 0-7)...")
try:
    response = client.read_discrete_inputs(0, count=8, device_id=1)
    if response.isError():
        print(f"  ✗ ERRO: {response}")
    else:
        print(f"  ✓ Inputs 0-7: {response.bits[:8]}")
except Exception as e:
    print(f"  ✗ EXCEÇÃO: {e}")

time.sleep(0.5)

# Teste 5: Ler estado 0 (coil 0)
print("\nTeste 5: Lendo coil 0...")
try:
    response = client.read_coils(0, count=1, device_id=1)
    if response.isError():
        print(f"  ✗ ERRO: {response}")
    else:
        print(f"  ✓ Coil 0 = {response.bits[0]}")
except Exception as e:
    print(f"  ✗ EXCEÇÃO: {e}")

print("\n" + "=" * 60)
print("Testes concluídos")
print("=" * 60)

client.close()
