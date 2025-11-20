#!/usr/bin/env python3
"""
Script para descobrir endereços dos botões de painel físico
AVANÇAR, RECUAR, PARADA
"""

import sys
sys.path.insert(0, '/home/lucas-junges/Documents/wco/ihm_esp32')

from modbus_client import ModbusClientWrapper
import time

print("=" * 70)
print("DESCOBERTA DE ENDEREÇOS - BOTÕES DE PAINEL")
print("=" * 70)

# Conectar ao CLP
client = ModbusClientWrapper(stub_mode=False, port='/dev/ttyUSB0', slave_id=1)

if not client.connected:
    print("✗ ERRO: Não foi possível conectar ao CLP")
    sys.exit(1)

print(f"✓ Conectado ao CLP\n")

print("INSTRUÇÕES:")
print("=" * 70)
print("Este script vai monitorar coils enquanto você pressiona os botões.")
print("Para cada botão, vamos descobrir qual coil muda de estado.")
print()
print("Vou monitorar coils nas seguintes faixas:")
print("  - 0x0000-0x0010 (entradas digitais básicas)")
print("  - 0x0100-0x010F (entradas digitais E0-E15)")
print("  - 0x00D0-0x00E0 (área de função)")
print("  - 0x00F0-0x0100 (área estendida)")
print()

# Definir ranges de coils para monitorar
coil_ranges = [
    (0x0000, 0x0010, "Entradas básicas"),
    (0x0100, 0x0110, "Entradas digitais E0-E15"),
    (0x00D0, 0x00E0, "Área de função"),
    (0x00F0, 0x0100, "Área estendida"),
]

# Ler estado inicial de todos os coils
print("Lendo estado inicial dos coils...")
initial_state = {}
for start, end, name in coil_ranges:
    for addr in range(start, end):
        try:
            state = client.read_coil(addr)
            if state is not None:
                initial_state[addr] = state
        except:
            pass

print(f"✓ {len(initial_state)} coils lidos no estado inicial\n")

# Função para monitorar mudanças
def monitor_changes(button_name, duration=10):
    print("=" * 70)
    print(f"TESTE: {button_name}")
    print("=" * 70)
    print(f"PRESSIONE E SEGURE o botão {button_name} por {duration} segundos")
    print("Começando em 3...")
    time.sleep(1)
    print("2...")
    time.sleep(1)
    print("1...")
    time.sleep(1)
    print(f"AGORA! Pressione {button_name}!")
    print()

    changes_detected = {}

    for i in range(duration):
        current_state = {}
        for start, end, name in coil_ranges:
            for addr in range(start, end):
                try:
                    state = client.read_coil(addr)
                    if state is not None:
                        current_state[addr] = state

                        # Detectar mudança
                        if addr in initial_state:
                            if initial_state[addr] != state:
                                if addr not in changes_detected:
                                    changes_detected[addr] = {
                                        'from': initial_state[addr],
                                        'to': state,
                                        'count': 0
                                    }
                                changes_detected[addr]['count'] += 1
                except:
                    pass

        print(f"  Monitorando... {i+1}/{duration}s", end='\r')
        time.sleep(1)

    print()

    if changes_detected:
        print(f"✓ MUDANÇAS DETECTADAS:")
        for addr, info in sorted(changes_detected.items()):
            print(f"  0x{addr:04X} ({addr}): {info['from']} → {info['to']} (detectado {info['count']}x)")
    else:
        print("✗ Nenhuma mudança detectada")

    print()
    input("Pressione ENTER para continuar...")
    print()

# Testar cada botão
try:
    monitor_changes("AVANÇAR", duration=8)
    monitor_changes("RECUAR", duration=8)
    monitor_changes("PARADA", duration=8)

    print("=" * 70)
    print("TESTE CONCLUÍDO!")
    print("=" * 70)
    print()
    print("Se nenhum coil foi detectado, os botões podem estar mapeados como:")
    print("  1. Entradas analógicas (não detectáveis por este método)")
    print("  2. Registros ao invés de coils")
    print("  3. Endereços fora das faixas monitoradas")
    print()
    print("Próximo passo: Verificar documentação do ladder ou usar osciloscópio")

except KeyboardInterrupt:
    print("\n\n✗ Teste interrompido pelo usuário")

client.close()
