#!/usr/bin/env python3
"""
Teste para descobrir o bit de modo AUTO/MANUAL
Baseado na análise do ladder: bit 02FF (767 dec) parece ser o modo
"""
import sys
import time
from modbus_client import ModbusClient, ModbusConfig

def test_mode_bit():
    config = ModbusConfig(port='/dev/ttyUSB0')
    client = ModbusClient(stub_mode=False, config=config)

    if not client.connect():
        print("❌ Falha ao conectar")
        return 1

    print("✅ Conectado ao CLP\n")

    # Bit 02FF (767) - provável bit de modo AUTO
    bit_modo = 767

    print("=" * 60)
    print("TESTE: Bit de modo AUTO/MANUAL")
    print("=" * 60)
    print(f"\nTestando bit {bit_modo} (0x02FF)")
    print("\nPressione S1 várias vezes e veja se o bit muda...\n")

    for i in range(20):
        valor = client.read_coil(bit_modo)
        modo_texto = "AUTO" if valor else "MANUAL" if valor is False else "ERRO"
        print(f"[{i+1:2d}] Bit {bit_modo}: {valor} → {modo_texto}")
        time.sleep(0.5)

    client.disconnect()
    print("\n✅ Desconectado")
    return 0

if __name__ == '__main__':
    sys.exit(test_mode_bit())
