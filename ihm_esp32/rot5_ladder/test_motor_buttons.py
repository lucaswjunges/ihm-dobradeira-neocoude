#!/usr/bin/env python3
"""
Teste rápido dos botões de motor via Modbus.
Verifica se consegue escrever nos coils S0 (0x0180) e S1 (0x0181).
"""

import sys
sys.path.insert(0, '/home/lucas-junges/Documents/wco/ihm_esp32')

from modbus_client import ModbusClientWrapper
import time

print("=" * 70)
print("TESTE DE BOTÕES DE MOTOR - AVANÇAR/RECUAR/PARADA")
print("=" * 70)
print()

# Conectar ao CLP
print("🔌 Conectando ao CLP...")
client = ModbusClientWrapper(stub_mode=False, port='/dev/ttyUSB0', slave_id=1)

if not client.connected:
    print("❌ ERRO: Não foi possível conectar ao CLP")
    sys.exit(1)

print("✅ Conectado ao CLP\n")

# Ler estado inicial das saídas S0 e S1
print("📊 Estado inicial das saídas:")
s0_initial = client.read_coil(0x0180)
s1_initial = client.read_coil(0x0181)
print(f"  S0 (0x0180): {'ON' if s0_initial else 'OFF'}")
print(f"  S1 (0x0181): {'ON' if s1_initial else 'OFF'}")
print()

# Teste 1: AVANÇAR
print("=" * 70)
print("TESTE 1: AVANÇAR (S0 ON)")
print("=" * 70)
input("Pressione ENTER para ativar AVANÇAR por 2 segundos...")
success = client.start_forward()
if success:
    print("✅ Comando AVANÇAR enviado com sucesso")
    print("⏳ Aguardando 2 segundos...")
    time.sleep(2)
    # Ler estado
    s0_state = client.read_coil(0x0180)
    print(f"📊 Estado S0: {'ON' if s0_state else 'OFF'}")
else:
    print("❌ Falha ao enviar comando AVANÇAR")
print()

# Desligar
print("🛑 Parando motor...")
client.stop_motor()
time.sleep(1)
print()

# Teste 2: RECUAR
print("=" * 70)
print("TESTE 2: RECUAR (S1 ON)")
print("=" * 70)
input("Pressione ENTER para ativar RECUAR por 2 segundos...")
success = client.start_backward()
if success:
    print("✅ Comando RECUAR enviado com sucesso")
    print("⏳ Aguardando 2 segundos...")
    time.sleep(2)
    # Ler estado
    s1_state = client.read_coil(0x0181)
    print(f"📊 Estado S1: {'ON' if s1_state else 'OFF'}")
else:
    print("❌ Falha ao enviar comando RECUAR")
print()

# Desligar
print("🛑 Parando motor...")
client.stop_motor()
time.sleep(1)
print()

# Teste 3: Ler botões físicos
print("=" * 70)
print("TESTE 3: LEITURA DE BOTÕES FÍSICOS")
print("=" * 70)
print("Pressione os botões físicos do painel e observe os valores:")
print("  E2 (0x0102): AVANÇAR")
print("  E3 (0x0103): PARADA")
print("  E4 (0x0104): RECUAR")
print("  E5 (0x0105): SENSOR")
print()
print("Lendo por 10 segundos (pressione Ctrl+C para parar)...")
print()

try:
    for i in range(10):
        buttons = client.read_panel_buttons()
        print(f"  [{i+1:2d}/10] AVANÇAR: {buttons['forward']}  |  PARADA: {buttons['stop']}  |  RECUAR: {buttons['backward']}  |  SENSOR: {buttons['sensor']}")
        time.sleep(1)
except KeyboardInterrupt:
    print("\n\n⏸️  Leitura interrompida")

print()
print("=" * 70)
print("TESTE CONCLUÍDO!")
print("=" * 70)
print()
print("Se os comandos foram enviados com sucesso, os botões da IHM web")
print("devem funcionar corretamente. Acesse:")
print()
print("  http://192.168.50.1/")
print()
print("e teste os botões AVANÇAR, RECUAR e PARAR.")
print()

# Garantir que motor está parado
client.stop_motor()
client.close()
