#!/usr/bin/env python3
"""
Teste de Mudança de Velocidade (RPM)
=====================================

Testa escrita/leitura de velocidade no registro 0x094C (2380)
Validado em 16/Nov/2025
"""

import sys
sys.path.insert(0, '/home/lucas-junges/Documents/clientes/w&co/ihm')

from modbus_client import ModbusClientWrapper
import time

def main():
    print("=" * 60)
    print("TESTE: Mudança de Velocidade (RPM)")
    print("=" * 60)
    print()

    # Conectar ao CLP
    client = ModbusClientWrapper(
        stub_mode=False,
        port='/dev/ttyUSB0',
        baudrate=57600,
        slave_id=1
    )

    if not client.connected:
        print("✗ Falha ao conectar no CLP")
        return

    print()
    print("=== FASE 1: Leitura de Velocidade Atual ===")
    print()

    current = client.read_speed_class()
    print(f"Velocidade atual: {current} rpm")

    print()
    print("=== FASE 2: Teste de Mudança de Velocidade ===")
    print()

    speeds = [5, 10, 15, 10]  # Ciclo completo + volta ao padrão

    for speed in speeds:
        print(f"→ Mudando para {speed} rpm...")
        success = client.write_speed_class(speed)

        if success:
            time.sleep(0.3)
            read_back = client.read_speed_class()

            if read_back == speed:
                print(f"  ✓ Confirmado: {read_back} rpm")
            else:
                print(f"  ✗ ERRO: Esperado {speed} rpm, lido {read_back} rpm")
        else:
            print(f"  ✗ Falha ao escrever")

        print()
        time.sleep(0.5)

    print()
    print("=== FASE 3: Teste de Valores Inválidos ===")
    print()

    invalid_speeds = [0, 3, 7, 20, 100]

    for speed in invalid_speeds:
        print(f"Tentando velocidade inválida: {speed} rpm")
        success = client.write_speed_class(speed)

        if not success:
            print(f"  ✓ Corretamente rejeitado")
        else:
            print(f"  ✗ ERRO: Deveria ter rejeitado!")
        print()

    print()
    print("=== FASE 4: Teste de Persistência ===")
    print()

    print("Gravando 15 rpm...")
    client.write_speed_class(15)
    time.sleep(0.5)

    print("Aguardando 3 segundos...")
    for i in range(3, 0, -1):
        print(f"  {i}...")
        time.sleep(1)

    final_speed = client.read_speed_class()
    print(f"Velocidade após 3s: {final_speed} rpm")

    if final_speed == 15:
        print("  ✓ Valor mantido (persistente)")
    else:
        print(f"  ✗ Valor mudou para {final_speed} rpm")

    print()
    print("=== TESTE COMPLETO ===")
    print()

    # Restaurar valor padrão
    print("Restaurando velocidade padrão (10 rpm)...")
    client.write_speed_class(10)
    print(f"Velocidade final: {client.read_speed_class()} rpm")

    print()
    print("✓ Teste finalizado")
    client.close()


if __name__ == "__main__":
    main()
