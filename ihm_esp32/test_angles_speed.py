#!/usr/bin/env python3
"""
Teste de Leitura/Escrita de Ângulos e Velocidade
"""

from modbus_client import ModbusClientWrapper
import time

print("=" * 60)
print("TESTE: Ângulos e Velocidade")
print("=" * 60)
print()

# Conecta ao CLP
client = ModbusClientWrapper(stub_mode=False, port='/dev/ttyUSB0')

if not client.connected:
    print("✗ Falha ao conectar no CLP")
    exit(1)

print("✓ Conectado ao CLP")
print()

# 1. LER ÂNGULOS ATUAIS
print("1. Lendo ângulos atuais do CLP...")
angles = client.read_all_bend_angles()
if angles:
    print(f"   Dobra 1: {angles.get('bend_1', 0)}°")
    print(f"   Dobra 2: {angles.get('bend_2', 0)}°")
    print(f"   Dobra 3: {angles.get('bend_3', 0)}°")
else:
    print("   ✗ Falha ao ler ângulos")

print()

# 2. ESCREVER NOVOS ÂNGULOS
print("2. Escrevendo novos ângulos...")
test_angles = [90.0, 120.0, 45.0]

for i, angle in enumerate(test_angles, 1):
    success = client.write_bend_angle(i, angle)
    print(f"   Dobra {i}: {angle}° {'✓' if success else '✗'}")

time.sleep(1)
print()

# 3. LER ÂNGULOS NOVAMENTE (VERIFICAR ESCRITA)
print("3. Verificando se ângulos foram salvos...")
angles_new = client.read_all_bend_angles()
if angles_new:
    print(f"   Dobra 1: {angles_new.get('bend_1', 0)}° (esperado: 90.0)")
    print(f"   Dobra 2: {angles_new.get('bend_2', 0)}° (esperado: 120.0)")
    print(f"   Dobra 3: {angles_new.get('bend_3', 0)}° (esperado: 45.0)")

    # Verifica se salvou
    if (abs(angles_new.get('bend_1', 0) - 90.0) < 0.1 and
        abs(angles_new.get('bend_2', 0) - 120.0) < 0.1 and
        abs(angles_new.get('bend_3', 0) - 45.0) < 0.1):
        print("   ✅ Ângulos salvos corretamente!")
    else:
        print("   ⚠️  Ângulos não correspondem aos escritos")
else:
    print("   ✗ Falha ao ler ângulos")

print()

# 4. LER VELOCIDADE ATUAL
print("4. Lendo velocidade atual do CLP...")
speed = client.read_speed_class()
if speed is not None:
    print(f"   Velocidade: {speed} RPM")
else:
    print("   ✗ Falha ao ler velocidade")

print()

# 5. ESCREVER NOVA VELOCIDADE
print("5. Escrevendo velocidade 10 RPM...")
success = client.write_speed_class(10)
print(f"   {'✓' if success else '✗'} Escrita")

time.sleep(1)

# 6. VERIFICAR VELOCIDADE
print()
print("6. Verificando velocidade salva...")
speed_new = client.read_speed_class()
if speed_new is not None:
    print(f"   Velocidade: {speed_new} RPM (esperado: 10)")
    if speed_new == 10:
        print("   ✅ Velocidade salva corretamente!")
    else:
        print(f"   ⚠️  Velocidade não corresponde (lido: {speed_new}, esperado: 10)")
else:
    print("   ✗ Falha ao ler velocidade")

print()
print("=" * 60)
print("TESTE CONCLUÍDO")
print("=" * 60)

client.close()
