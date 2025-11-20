#!/usr/bin/env python3
"""
Script para ler valores oficiais do CLP
"""

import sys
sys.path.insert(0, '/home/lucas-junges/Documents/wco/ihm_esp32')

from modbus_client import ModbusClientWrapper
import modbus_map as mm

print("=" * 60)
print("LEITURA DE VALORES OFICIAIS DO CLP")
print("=" * 60)

# Conectar ao CLP
client = ModbusClientWrapper(stub_mode=False, port='/dev/ttyUSB0', slave_id=1)

if not client.connected:
    print("✗ ERRO: Não foi possível conectar ao CLP")
    sys.exit(1)

print(f"✓ Conectado: {client.port} @ {client.baudrate} bps (slave {client.slave_id})\n")

# 1. Ler ângulo atual do encoder
print("=" * 60)
print("1. ÂNGULO ATUAL (ENCODER)")
print("=" * 60)
encoder_raw = client.read_32bit(mm.ENCODER['ANGLE_MSW'], mm.ENCODER['ANGLE_LSW'])
if encoder_raw is not None:
    encoder_degrees = mm.clp_to_degrees(encoder_raw)
    print(f"Endereço: 0x{mm.ENCODER['ANGLE_MSW']:04X}/0x{mm.ENCODER['ANGLE_LSW']:04X}")
    print(f"Valor bruto: {encoder_raw}")
    print(f"Ângulo: {encoder_degrees:.1f}°")
else:
    print("✗ Erro ao ler encoder")

# 2. Ler RPM atual
print("\n" + "=" * 60)
print("2. VELOCIDADE (RPM)")
print("=" * 60)
rpm = client.read_speed_class()
if rpm is not None:
    print(f"Endereço: 0x{mm.RPM_REGISTERS['RPM_READ']:04X}")
    print(f"RPM atual: {rpm}")
else:
    print("✗ Erro ao ler RPM")

# 3. Ler ângulos programados (área shadow 0x0842+)
print("\n" + "=" * 60)
print("3. ÂNGULOS PROGRAMADOS (ÁREA SHADOW)")
print("=" * 60)

angles = client.read_all_bend_angles()
if angles:
    for i in [1, 2, 3]:
        addr = mm.BEND_ANGLES_SHADOW[f'BEND_{i}_LEFT_MSW']
        angle = angles.get(f'bend_{i}', 0.0)
        print(f"Dobra {i}: {angle:6.1f}° (endereço 0x{addr:04X})")
else:
    print("✗ Erro ao ler ângulos programados")

# 4. Ler ângulos da área MODBUS INPUT (0x0A00+)
print("\n" + "=" * 60)
print("4. ÂNGULOS PROGRAMADOS (ÁREA MODBUS INPUT 0x0A00)")
print("=" * 60)

for i in [1, 2, 3]:
    addr = mm.BEND_ANGLES_MODBUS_INPUT[f'BEND_{i}_INPUT_BASE']
    value = client.read_register(addr)
    if value is not None:
        degrees = value / 10.0
        print(f"Dobra {i}: {degrees:6.1f}° (endereço 0x{addr:04X}, valor={value})")
    else:
        print(f"Dobra {i}: Erro ao ler (endereço 0x{addr:04X})")

# 5. Ler LEDs
print("\n" + "=" * 60)
print("5. LEDs (INDICADORES)")
print("=" * 60)
leds = client.read_leds()
if leds:
    for name, status in leds.items():
        symbol = "🟢 ON " if status else "⚫ OFF"
        addr = mm.LEDS[name]
        print(f"{name}: {symbol} (0x{addr:04X})")
else:
    print("✗ Erro ao ler LEDs")

# 6. Ler modo (MANUAL/AUTO)
print("\n" + "=" * 60)
print("6. MODO DE OPERAÇÃO")
print("=" * 60)
mode_bit = client.read_real_mode()
if mode_bit is not None:
    mode_text = "AUTO" if mode_bit else "MANUAL"
    print(f"Bit 0x02FF: {mode_bit}")
    print(f"Modo atual: {mode_text}")
else:
    print("✗ Erro ao ler modo")

# 7. Ler estados críticos
print("\n" + "=" * 60)
print("7. ESTADOS CRÍTICOS")
print("=" * 60)

modbus_enabled = client.read_coil(mm.CRITICAL_STATES['MODBUS_SLAVE_ENABLED'])
print(f"Modbus slave habilitado (0x{mm.CRITICAL_STATES['MODBUS_SLAVE_ENABLED']:04X}): {modbus_enabled}")

cycle_active = client.read_coil(mm.CRITICAL_STATES['CYCLE_ACTIVE'])
print(f"Ciclo ativo (0x{mm.CRITICAL_STATES['CYCLE_ACTIVE']:04X}): {cycle_active}")

print("\n" + "=" * 60)
print("LEITURA CONCLUÍDA")
print("=" * 60)

client.close()
