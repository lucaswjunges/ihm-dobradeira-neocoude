#!/usr/bin/env python3
"""
test_inputs_mapping.py
Detecta mudanças nas entradas digitais para mapear sensores e botões
"""

from modbus_client import ModbusClient, ModbusConfig
import time
from datetime import datetime

config = ModbusConfig(port='/dev/ttyUSB0')
client = ModbusClient(stub_mode=False, config=config)

print("=" * 60)
print("MAPEAMENTO DE ENTRADAS DIGITAIS (E0-E7)")
print("=" * 60)
print("\nPressione botões e mova sensores para identificar entradas")
print("Pressione Ctrl+C para sair\n")

# Estado anterior das entradas
prev_state = [False] * 8

# Contador de mudanças por entrada
change_count = [0] * 8

try:
    while True:
        # Ler todas as entradas E0-E7 (registradores 256-263)
        inputs = []
        for i in range(8):
            result = client.read_discrete_inputs(256 + i, 1)
            if result and not result.isError():
                inputs.append(result.bits[0])
            else:
                inputs.append(False)

        # Exibir status atual
        status_line = "\r["
        for i in range(8):
            state = "ON " if inputs[i] else "OFF"
            color = "\033[92m" if inputs[i] else "\033[91m"  # Verde/Vermelho
            reset = "\033[0m"
            status_line += f"E{i}:{color}{state}{reset} "
        status_line += "]"
        print(status_line, end='', flush=True)

        # Detectar e anunciar mudanças
        for i in range(8):
            if inputs[i] != prev_state[i]:
                change_count[i] += 1
                status = "ON " if inputs[i] else "OFF"
                timestamp = datetime.now().strftime('%H:%M:%S')

                print()  # Nova linha
                print("=" * 60)
                print(f"⚡ MUDANÇA DETECTADA!")
                print(f"   Entrada: E{i}")
                print(f"   Estado: {prev_state[i]} → {status}")
                print(f"   Hora: {timestamp}")
                print(f"   Total de mudanças em E{i}: {change_count[i]}")
                print(f"   → ANOTE A AÇÃO QUE VOCÊ FEZ!")
                print("=" * 60)

        prev_state = inputs.copy()
        time.sleep(0.05)  # 50ms - bem responsivo

except KeyboardInterrupt:
    print("\n\n" + "=" * 60)
    print("RESUMO DO TESTE")
    print("=" * 60)
    for i in range(8):
        print(f"E{i}: {change_count[i]:3d} mudanças detectadas")
    print("\nTeste finalizado. Revise suas anotações!")
