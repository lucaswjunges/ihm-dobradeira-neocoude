#!/usr/bin/env python3
"""
Teste Simples de Registros de Tela
===================================
Usa sintaxe direta do pymodbus para evitar erros de wrapper.
"""

from pymodbus.client import ModbusSerialClient
import time

PORT = '/dev/ttyUSB0'
BAUDRATE = 57600
SLAVE_ID = 1

print("=" * 60)
print("TESTE DIRETO - REGISTROS DE TELA")
print("=" * 60)

# Conecta
client = ModbusSerialClient(
    port=PORT,
    baudrate=BAUDRATE,
    parity='N',
    stopbits=1,
    bytesize=8,
    timeout=1.0
)

if not client.connect():
    print("✗ Erro ao conectar")
    exit(1)

print("✓ Conectado\n")

# Teste registro 0FEE (tela atual)
print("[1] Lendo registro 0FEE (4078) - TELA ATUAL")
print("-" * 60)

try:
    result = client.read_holding_registers(address=0x0FEE, count=1, slave=SLAVE_ID)
    
    if hasattr(result, 'isError') and result.isError():
        print(f"  ✗ Erro Modbus: {result}")
    elif hasattr(result, 'registers'):
        value = result.registers[0]
        print(f"  ✓ SUCESSO! Registro 0FEE = {value} (0x{value:04X})")
        
        # Interpreta
        screens = {
            0: "Valor zero (não usado?)",
            1: "Tela principal",
            4: "Tela Dobra 1 (K1)",
            5: "Tela Dobra 2 (K2)",
            6: "Tela Dobra 3 (K3)",
        }
        print(f"  Interpretação: {screens.get(value, f'Tela {value}')}")
    else:
        print(f"  ⚠️  Resposta inesperada: {result}")
        
except Exception as e:
    print(f"  ✗ Exceção: {e}")

# Teste registro 0FEC (tela alvo)
print("\n[2] Lendo registro 0FEC (4076) - TELA ALVO")
print("-" * 60)

try:
    result = client.read_holding_registers(address=0x0FEC, count=1, slave=SLAVE_ID)
    
    if hasattr(result, 'isError') and result.isError():
        print(f"  ✗ Erro Modbus: {result}")
    elif hasattr(result, 'registers'):
        value = result.registers[0]
        print(f"  ✓ SUCESSO! Registro 0FEC = {value} (0x{value:04X})")
    else:
        print(f"  ⚠️  Resposta inesperada: {result}")
        
except Exception as e:
    print(f"  ✗ Exceção: {e}")

# Teste estado 00DA (trigger)
print("\n[3] Lendo estado 00DA (218) - TRIGGER")
print("-" * 60)

try:
    result = client.read_coils(address=0x00DA, count=1, slave=SLAVE_ID)
    
    if hasattr(result, 'isError') and result.isError():
        print(f"  ✗ Erro Modbus: {result}")
    elif hasattr(result, 'bits'):
        value = result.bits[0]
        print(f"  ✓ SUCESSO! Estado 00DA = {'ON' if value else 'OFF'}")
    else:
        print(f"  ⚠️  Resposta inesperada: {result}")
        
except Exception as e:
    print(f"  ✗ Exceção: {e}")

# Monitoramento
print("\n[4] Monitorando 0FEE por 5 segundos...")
print("-" * 60)
print("  Pressione K1, K2 ou K3 no CLP se possível\n")

last_value = None
for i in range(10):
    try:
        result = client.read_holding_registers(address=0x0FEE, count=1, slave=SLAVE_ID)
        
        if hasattr(result, 'registers'):
            value = result.registers[0]
            
            if value != last_value:
                print(f"  [{i*0.5:.1f}s] Tela MUDOU para: {value}")
                last_value = value
            else:
                print(f"  [{i*0.5:.1f}s] Tela: {value}")
        else:
            print(f"  [{i*0.5:.1f}s] Erro na leitura")
            
    except Exception as e:
        print(f"  [{i*0.5:.1f}s] Exceção: {e}")
    
    time.sleep(0.5)

client.close()

print("\n" + "=" * 60)
print("✓ TESTE CONCLUÍDO")
print("=" * 60)

print("\n[CONCLUSÃO]")
print("  Se viu valores lidos com sucesso:")
print("    → Registros 0FEE/0FEC existem e funcionam!")
print("  Se teve erros Modbus:")
print("    → Registros não implementados, usar ROT5")
