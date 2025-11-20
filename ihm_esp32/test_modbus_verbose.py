#!/usr/bin/env python3
"""
Teste VERBOSE de comunicação Modbus - mostra tudo que está acontecendo
"""

from pymodbus.client import ModbusSerialClient
import time

print("=" * 70)
print("TESTE VERBOSE - COMUNICAÇÃO MODBUS")
print("=" * 70)
print()

# Habilita logging detalhado do pymodbus
import logging
logging.basicConfig()
log = logging.getLogger()
log.setLevel(logging.DEBUG)

port = '/dev/ttyUSB0'
slave_id = 1
baudrate = 57600

print(f"Configuração:")
print(f"  Porta: {port}")
print(f"  Slave ID: {slave_id}")
print(f"  Baudrate: {baudrate}")
print(f"  Parity: None")
print(f"  Stop bits: 1")
print()

print("Criando cliente Modbus...")
client = ModbusSerialClient(
    port=port,
    baudrate=baudrate,
    parity='N',
    stopbits=1,
    bytesize=8,
    timeout=2.0  # Timeout maior para debug
)

print("Tentando conectar...")
if client.connect():
    print("✅ Conexão serial estabelecida!")
    print()

    # Teste 1: Leitura mais simples possível - HOLDING REGISTER 0
    print("TESTE 1: Lendo HOLDING REGISTER 0 (endereço 0)")
    print("  Enviando comando Modbus...")
    result = client.read_holding_registers(address=0, count=1, slave=slave_id)
    print(f"  Resultado: {result}")

    if result.isError():
        print(f"  ❌ ERRO: {result}")
    else:
        print(f"  ✅ SUCESSO! Valor: {result.registers}")

    print()
    time.sleep(1)

    # Teste 2: INPUT REGISTER 0
    print("TESTE 2: Lendo INPUT REGISTER 0 (endereço 0)")
    print("  Enviando comando Modbus...")
    result = client.read_input_registers(address=0, count=1, slave=slave_id)
    print(f"  Resultado: {result}")

    if result.isError():
        print(f"  ❌ ERRO: {result}")
    else:
        print(f"  ✅ SUCESSO! Valor: {result.registers}")

    print()
    time.sleep(1)

    # Teste 3: COILS
    print("TESTE 3: Lendo COILS 0-7")
    print("  Enviando comando Modbus...")
    result = client.read_coils(address=0, count=8, slave=slave_id)
    print(f"  Resultado: {result}")

    if result.isError():
        print(f"  ❌ ERRO: {result}")
    else:
        print(f"  ✅ SUCESSO! Valores: {result.bits[:8]}")

    client.close()
    print()
    print("=" * 70)
    print("Teste concluído - veja os logs acima para detalhes")
    print("=" * 70)
else:
    print("❌ Falha ao abrir porta serial!")
    print(f"  Verifique se {port} existe e se você tem permissão")
