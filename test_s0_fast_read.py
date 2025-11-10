#!/usr/bin/env python3
"""
Teste de leitura RÁPIDA de S0 após escrita
Objetivo: Verificar se S0 é ativada momentaneamente mas desligada rapidamente pela ladder
"""

from pymodbus.client import ModbusSerialClient
import time

PORT = '/dev/ttyUSB0'
BAUDRATE = 57600
SLAVE_ADDRESS = 1
S0_ADDRESS = 384

print("=" * 60)
print("TESTE DE LEITURA RÁPIDA - S0")
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

print("✓ Conectado ao PLC")

try:
    # Garantir que S0 está OFF
    print(f"\n[1] Garantindo S0 está OFF...")
    client.write_coil(address=S0_ADDRESS, value=False, device_id=SLAVE_ADDRESS)
    time.sleep(0.1)

    # Ler estado inicial
    response = client.read_coils(address=S0_ADDRESS, count=1, device_id=SLAVE_ADDRESS)
    initial_state = response.bits[0]
    print(f"    Estado inicial S0: {initial_state}")

    # Escrever TRUE e ler IMEDIATAMENTE (sem delay)
    print(f"\n[2] Escrevendo TRUE e lendo IMEDIATAMENTE (10 vezes)...")

    for i in range(10):
        # Escrever TRUE
        client.write_coil(address=S0_ADDRESS, value=True, device_id=SLAVE_ADDRESS)

        # Ler IMEDIATAMENTE (sem sleep)
        response = client.read_coils(address=S0_ADDRESS, count=1, device_id=SLAVE_ADDRESS)
        state_after_write = response.bits[0]

        print(f"    Tentativa {i+1}: S0 após write(TRUE) = {state_after_write} ({'✓ ON' if state_after_write else '✗ OFF'})")

        # Desligar para próxima tentativa
        client.write_coil(address=S0_ADDRESS, value=False, device_id=SLAVE_ADDRESS)
        time.sleep(0.05)

    print("\n" + "=" * 60)
    print("ANÁLISE:")
    print("=" * 60)
    print("Se TODAS as leituras mostraram OFF:")
    print("  → A ladder logic está SOBRESCREVENDO S0 imediatamente")
    print("  → Solução: Modificar ladder para aceitar comandos Modbus")
    print("\nSe ALGUMA leitura mostrou ON:")
    print("  → A escrita funciona! Mas é muito rápida")
    print("  → Problema pode ser timing ou falta de feedback de E2")
    print("=" * 60)

finally:
    client.close()
