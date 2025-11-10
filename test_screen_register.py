#!/usr/bin/env python3
"""
Testa leitura do registro de tela ativa em tempo real
"""
import time
from modbus_client import ModbusClient, ModbusConfig

# Configurar Modbus
config = ModbusConfig(
    port='/dev/ttyUSB0',
    baudrate=57600,
    stopbits=2,
    parity='N',
    slave_address=1
)

client = ModbusClient(stub_mode=False, config=config)

if not client.connect():
    print("❌ Falha ao conectar!")
    exit(1)

print("✅ Conectado ao CLP")
print("\n🔍 Monitorando registros de tela ativa...")
print("Pressione Ctrl+C para parar\n")
print(f"{'Tempo':>8} | {'Reg 2039':>10} | {'Reg 4078':>10} | {'Reg 4079':>10}")
print("-" * 50)

last_values = {}

try:
    while True:
        # Ler os 3 registros possíveis
        reg_2039 = client.read_register(2039)
        reg_4078 = client.read_register(4078)
        reg_4079 = client.read_register(4079)
        
        current_values = {
            '2039': reg_2039,
            '4078': reg_4078,
            '4079': reg_4079
        }
        
        # Mostrar apenas se houver mudança
        if current_values != last_values:
            timestamp = time.strftime("%H:%M:%S")
            print(f"{timestamp} | {reg_2039 or 'None':>10} | {reg_4078 or 'None':>10} | {reg_4079 or 'None':>10}")
            last_values = current_values
        
        time.sleep(0.5)

except KeyboardInterrupt:
    print("\n\n✓ Teste finalizado")
    client.disconnect()
