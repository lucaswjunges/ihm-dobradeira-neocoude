#!/usr/bin/env python3
"""
Teste da ponte TCP/IP (ser2net) para o CLP
Conecta via TCP localhost:5000 -> /dev/ttyUSB0
"""

from pymodbus.client import ModbusTcpClient
import time

HOST = 'localhost'
PORT = 5000
SLAVE_ID = 1

print("=" * 60)
print("TESTE DE PONTE TCP/IP (ser2net)")
print("=" * 60)
print(f"Conectando em: {HOST}:{PORT}")
print(f"Slave ID: {SLAVE_ID}")
print()

client = ModbusTcpClient(
    host=HOST,
    port=PORT,
    timeout=2.0
)

print("Conectando via TCP...")
if not client.connect():
    print("❌ Erro ao conectar TCP")
    print("\nVerifique se o ser2net está rodando:")
    print("  lsof -i :5000")
    exit(1)

print("✓ Conexão TCP estabelecida\n")

# Teste: Read Coils (Função 01)
print("Teste: Read Coils (Função 01) - Entradas E0-E7")
try:
    result = client.read_coils(256, 8, SLAVE_ID)

    if not result.isError():
        print("  ✓ COMUNICAÇÃO VIA TCP/IP FUNCIONANDO!")
        for i, bit in enumerate(result.bits[:8]):
            estado = "ON " if bit else "OFF"
            print(f"    E{i}: {estado}")
    else:
        print(f"  ❌ Erro Modbus: {result}")
except Exception as e:
    print(f"  ❌ Exceção: {e}")

print()
print("=" * 60)
print("Se funcionou, configure o WinSUP com:")
print(f"  Protocolo: TCP/IP")
print(f"  Host: 127.0.0.1 (ou localhost)")
print(f"  Porta: {PORT}")
print("=" * 60)

client.close()
