#!/usr/bin/env python3
"""
Teste de comunicação com CLP usando as configurações CORRETAS
Função 01 (Read Coils) - conforme está funcionando
"""

from pymodbus.client import ModbusSerialClient
import time

PORT = '/dev/ttyUSB0'
BAUDRATE = 57600
PARITY = 'N'
STOPBITS = 2
SLAVE_ID = 1

print("=" * 60)
print("TESTE DE COMUNICAÇÃO COM CLP - CONFIGURAÇÃO CONFIRMADA")
print("=" * 60)
print(f"Porta: {PORT}")
print(f"Config: {BAUDRATE} 8{PARITY}{STOPBITS}")
print(f"Slave ID: {SLAVE_ID}")
print()

client = ModbusSerialClient(
    port=PORT,
    baudrate=BAUDRATE,
    parity=PARITY,
    stopbits=STOPBITS,
    bytesize=8,
    timeout=1.0
)

print("Conectando...")
if not client.connect():
    print("❌ Erro ao abrir porta")
    exit(1)

print("✓ Porta aberta\n")

# Teste 1: Read Coils (Função 01) - endereço 256, quantidade 8
print("Teste 1: Read Coils (Função 01) - Entradas E0-E7")
print("  Endereço: 256, Quantidade: 8")
try:
    result = client.read_coils(
        address=256,
        count=8,
        device_id=SLAVE_ID
    )

    if not result.isError():
        print("  ✓ SUCESSO!")
        for i, bit in enumerate(result.bits[:8]):
            estado = "ON " if bit else "OFF"
            print(f"    E{i}: {estado}")
    else:
        print(f"  ❌ Erro: {result}")
except Exception as e:
    print(f"  ❌ Exceção: {e}")

print()

# Teste 2: Read Holding Registers (Função 03) - Encoder
print("Teste 2: Read Holding Registers (Função 03) - Encoder")
print("  Endereço: 1238, Quantidade: 2")
try:
    result = client.read_holding_registers(
        address=1238,
        count=2,
        device_id=SLAVE_ID
    )

    if not result.isError():
        print("  ✓ SUCESSO!")
        msw = result.registers[0]
        lsw = result.registers[1]
        encoder = (msw << 16) | lsw
        print(f"    MSW: {msw}, LSW: {lsw}")
        print(f"    Encoder: {encoder}")
    else:
        print(f"  ❌ Erro: {result}")
except Exception as e:
    print(f"  ❌ Exceção: {e}")

print()

# Teste 3: Read Discrete Inputs (Função 02) - se disponível
print("Teste 3: Read Discrete Inputs (Função 02)")
print("  Endereço: 256, Quantidade: 8")
try:
    result = client.read_discrete_inputs(
        address=256,
        count=8,
        device_id=SLAVE_ID
    )

    if not result.isError():
        print("  ✓ SUCESSO!")
        for i, bit in enumerate(result.bits[:8]):
            estado = "ON " if bit else "OFF"
            print(f"    Input {i}: {estado}")
    else:
        print(f"  ❌ Erro: {result}")
except Exception as e:
    print(f"  ❌ Exceção: {e}")

print()
print("=" * 60)

client.close()
