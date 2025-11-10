#!/usr/bin/env python3
"""
test_e0_both_types.py

Teste para descobrir se entradas são TIPO N ou TIPO P.
Monitora E0-E7 continuamente para detectar qualquer mudança.
"""

from pymodbus.client import ModbusSerialClient
import time

PORT = '/dev/ttyUSB0'
BAUDRATE = 57600
SLAVE_ID = 1

print("=" * 80)
print("MONITOR CONTÍNUO DE ENTRADAS E0-E7")
print("=" * 80)
print("Este script vai monitorar as entradas continuamente.")
print("Faça o seguinte teste:")
print()
print("TESTE 1 - TIPO P:")
print("  → Conecte +24V ao E0")
print("  → Aguarde 2 segundos")
print("  → Desconecte")
print()
print("TESTE 2 - TIPO N:")
print("  → Conecte 0V/GND ao E0")
print("  → Aguarde 2 segundos")
print("  → Desconecte")
print()
print("O script vai mostrar qual teste fez E0 acender!")
print("=" * 80)

client = ModbusSerialClient(
    port=PORT,
    baudrate=BAUDRATE,
    parity='N',
    stopbits=2,
    bytesize=8,
    timeout=1.0,
    handle_local_echo=False
)

if not client.connect():
    print("❌ Failed to connect to PLC!")
    exit(1)

print("✓ Conectado ao CLP")
print("\nMonitorando E0-E7... (Ctrl+C para parar)\n")

previous_state = [False] * 8

try:
    while True:
        try:
            response = client.read_discrete_inputs(address=256, count=8, device_id=SLAVE_ID)
            if not response.isError():
                current_state = response.bits[:8]

                # Detectar mudanças
                for i in range(8):
                    if current_state[i] != previous_state[i]:
                        if current_state[i]:
                            print(f"🟢 E{i} ATIVOU! ●●●")
                        else:
                            print(f"⚪ E{i} desativou")

                # Mostrar estado atual se houver entradas ativas
                active = [f'E{i}' for i in range(8) if current_state[i]]
                if active:
                    print(f"   Ativas: {', '.join(active)}")

                previous_state = current_state[:]

            time.sleep(0.2)  # 200ms entre leituras

        except KeyboardInterrupt:
            raise
        except Exception as e:
            print(f"Erro: {e}")
            time.sleep(1)

except KeyboardInterrupt:
    print("\n\n" + "=" * 80)
    print("Monitoramento encerrado")
    print("=" * 80)

client.close()
