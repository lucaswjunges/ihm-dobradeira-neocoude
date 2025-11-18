#!/usr/bin/env python3
"""
Teste simples de comunicação Modbus RTU com CLP Atos
"""

from pymodbus.client import ModbusSerialClient

# Configuração
PORT = '/dev/ttyUSB0'
BAUDRATE = 57600
SLAVE_ID = 1

print("Conectando ao CLP...")
client = ModbusSerialClient(
    port=PORT,
    baudrate=BAUDRATE,
    parity='N',
    stopbits=1,
    bytesize=8,
    timeout=1.0
)

if not client.connect():
    print("ERRO: Não foi possível abrir a porta serial")
    exit(1)

print(f"✓ Conectado em {PORT}")

# Testar leitura do encoder (registros 04D6/04D7)
print(f"\nTestando leitura do encoder (slave {SLAVE_ID})...")

try:
    # Tentar sintaxe antiga (pymodbus 2.x)
    result = client.read_holding_registers(1238, 2, slave=SLAVE_ID)
    print(f"✓ Resposta recebida! Encoder MSW={result.registers[0]}, LSW={result.registers[1]}")
except TypeError:
    # Tentar sintaxe nova (pymodbus 3.x)
    try:
        result = client.read_holding_registers(1238, 2, unit=SLAVE_ID)
        print(f"✓ Resposta recebida! Encoder MSW={result.registers[0]}, LSW={result.registers[1]}")
    except Exception as e:
        print(f"✗ Erro com 'unit': {e}")
        # Tentar sem especificar slave (usa padrão)
        try:
            client.slave_id = SLAVE_ID
            result = client.read_holding_registers(1238, 2)
            print(f"✓ Resposta recebida! Encoder MSW={result.registers[0]}, LSW={result.registers[1]}")
        except Exception as e2:
            print(f"✗ Erro sem parâmetro: {e2}")

client.close()
print("\nTeste concluído")
