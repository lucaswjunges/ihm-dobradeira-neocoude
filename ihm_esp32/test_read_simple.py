#!/usr/bin/env python3
"""Teste simples de leitura Modbus"""

from pymodbus.client import ModbusSerialClient
import time

# Configuração
client = ModbusSerialClient(
    port='/dev/ttyUSB0',
    baudrate=57600,
    parity='N',
    stopbits=1,
    timeout=1
)

print("Conectando...")
if not client.connect():
    print("ERRO: Não conseguiu conectar")
    exit(1)

print("Conectado!")
print("\nLendo dados a cada 1 segundo (Ctrl+C para parar)...\n")

try:
    count = 0
    while count < 5:  # Ler 5 vezes
        count += 1

        # Ler encoder (registros 1238-1239)
        result = client.read_holding_registers(1238, 2, slave=1)

        if not result.isError():
            msw = result.registers[0]
            lsw = result.registers[1]
            value = (msw << 16) | lsw

            print(f"[{count}] Encoder: {value:10d} (0x{value:08X})  MSW={msw:5d}  LSW={lsw:5d}")
        else:
            print(f"[{count}] ERRO: {result}")

        # Ler entradas E0-E7
        result_in = client.read_holding_registers(256, 8, slave=1)
        if not result_in.isError():
            inputs = [r & 1 for r in result_in.registers]
            print(f"     Entradas E0-E7: {inputs}")

        # Ler saídas S0-S7
        result_out = client.read_holding_registers(384, 8, slave=1)
        if not result_out.isError():
            outputs = [r & 1 for r in result_out.registers]
            print(f"     Saídas  S0-S7: {outputs}")

        print()
        time.sleep(1)

except KeyboardInterrupt:
    print("\nInterrompido")

finally:
    client.close()
    print("Conexão fechada")
