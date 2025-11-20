#!/usr/bin/env python3
"""
Debug da leitura do encoder - descobrir por que não está lendo 11.9°
"""

import sys
sys.path.insert(0, '/home/lucas-junges/Documents/wco/ihm_esp32')

print("Parando serviço IHM temporariamente...")
import os
os.system("sudo systemctl stop ihm.service")
import time
time.sleep(2)

from pymodbus.client import ModbusSerialClient
import modbus_map as mm

print("\n=== DEBUG: LEITURA DO ENCODER ===\n")

# Conectar direto com pymodbus
client = ModbusSerialClient(
    port='/dev/ttyUSB0',
    baudrate=57600,
    parity='N',
    stopbits=1,
    bytesize=8,
    timeout=1
)

if client.connect():
    print("✓ Conectado ao CLP\n")

    # Testar diferentes formas de ler
    print("TESTE 1: Lendo com endereço decimal direto (1238)")
    result = client.read_holding_registers(address=1238, count=2, slave=1)
    if not result.isError():
        msw = result.registers[0]
        lsw = result.registers[1]
        value_32bit = (msw << 16) | lsw
        degrees = value_32bit / 10.0
        print(f"  MSW: {msw} (0x{msw:04X})")
        print(f"  LSW: {lsw} (0x{lsw:04X})")
        print(f"  32-bit: {value_32bit}")
        print(f"  Graus: {degrees}°")
    else:
        print(f"  ERRO: {result}")

    print("\nTESTE 2: Usando modbus_map constantes")
    print(f"  mm.ENCODER['ANGLE_MSW'] = 0x{mm.ENCODER['ANGLE_MSW']:04X} ({mm.ENCODER['ANGLE_MSW']})")
    print(f"  mm.ENCODER['ANGLE_LSW'] = 0x{mm.ENCODER['ANGLE_LSW']:04X} ({mm.ENCODER['ANGLE_LSW']})")

    result = client.read_holding_registers(address=mm.ENCODER['ANGLE_MSW'], count=2, slave=1)
    if not result.isError():
        msw = result.registers[0]
        lsw = result.registers[1]
        value_32bit = mm.read_32bit(msw, lsw)
        degrees = mm.clp_to_degrees(value_32bit)
        print(f"  MSW: {msw} (0x{msw:04X})")
        print(f"  LSW: {lsw} (0x{lsw:04X})")
        print(f"  32-bit: {value_32bit}")
        print(f"  Graus: {degrees}°")
    else:
        print(f"  ERRO: {result}")

    client.close()
    print("\n✓ Conexão fechada")
else:
    print("✗ Erro ao conectar")

print("\nReiniciando serviço IHM...")
os.system("sudo systemctl start ihm.service")
