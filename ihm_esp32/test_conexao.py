#!/usr/bin/env python3
"""
Teste básico de conexão Modbus
"""

from modbus_client import ModbusClientWrapper
import modbus_map as mm

# Conecta
print("Conectando...")
client = ModbusClientWrapper(stub_mode=False, port='/dev/ttyUSB0')

if not client.connected:
    print("❌ Não conectou!")
    exit(1)

print("✅ Conectado!")

# Testa leitura básica
print("\nTentando ler LED1 (0x00C0)...")
led1 = client.read_coil(0x00C0)
print(f"LED1 = {led1}")

# Tenta ler encoder
print("\nTentando ler encoder (0x04D6)...")
encoder_msw = client.read_register(0x04D6)
print(f"Encoder MSW = {encoder_msw}")

# Tenta ler 0x06E0
print("\nTentando ler velocidade inversor (0x06E0)...")
velocidade = client.read_register(0x06E0)
print(f"Velocidade = {velocidade}")

# Tenta ler 0x0A06
print("\nTentando ler 0x0A06 (área de escrita)...")
write_area = client.read_register(0x0A06)
print(f"0x0A06 = {write_area}")

client.close()
