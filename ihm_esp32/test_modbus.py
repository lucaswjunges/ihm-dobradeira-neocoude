#!/usr/bin/env python3
"""
Teste rápido de comunicação Modbus
"""

from modbus_client import ModbusClientWrapper
import modbus_map as mm
import time

print("=" * 60)
print("TESTE DE COMUNICAÇÃO MODBUS")
print("=" * 60)

# Criar cliente
client = ModbusClientWrapper(stub_mode=False, port='/dev/ttyUSB0')

if not client.connected:
    print("❌ NÃO CONECTADO - verifique cabo e CLP")
    exit(1)

print(f"✅ Conectado: {client.connected}")
print(f"   Erros consecutivos: {client.consecutive_errors}")
print()

# Teste 1: Ler encoder (32-bit)
print("Teste 1: Lendo encoder (0x04D6/0x04D7)...")
for i in range(3):
    encoder = client.read_32bit(mm.ENCODER['ANGLE_MSW'], mm.ENCODER['ANGLE_LSW'])
    print(f"  Tentativa {i+1}: {encoder}")
    print(f"  Conectado: {client.connected}, Erros: {client.consecutive_errors}")
    time.sleep(0.5)

print()

# Teste 2: Ler coil
print("Teste 2: Lendo coil 0x00BE (Modbus slave enabled)...")
for i in range(3):
    coil = client.read_coil(mm.CRITICAL_STATES['MODBUS_SLAVE_ENABLED'])
    print(f"  Tentativa {i+1}: {coil}")
    print(f"  Conectado: {client.connected}, Erros: {client.consecutive_errors}")
    time.sleep(0.5)

print()

# Teste 3: Ler registro simples
print("Teste 3: Lendo registro 0x06E0 (velocidade)...")
for i in range(3):
    reg = client.read_register(mm.RPM_REGISTERS['RPM_READ'])
    print(f"  Tentativa {i+1}: {reg}")
    print(f"  Conectado: {client.connected}, Erros: {client.consecutive_errors}")
    time.sleep(0.5)

print()
print("=" * 60)
print(f"RESULTADO FINAL:")
print(f"  Conectado: {client.connected}")
print(f"  Erros consecutivos: {client.consecutive_errors}")
print("=" * 60)

client.close()
