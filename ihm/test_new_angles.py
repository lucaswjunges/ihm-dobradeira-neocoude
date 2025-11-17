#!/usr/bin/env python3
"""
Teste dos Novos Métodos de Ângulos
===================================

Testa escrita/leitura na área 0x0500 (validada 16/Nov/2025)
"""

import sys
sys.path.insert(0, '/home/lucas-junges/Documents/clientes/w&co/ihm')

from modbus_client import ModbusClientWrapper

def main():
    print("=" * 60)
    print("TESTE: Novos Métodos de Ângulos (Área 0x0500)")
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
    print("=== FASE 1: Leitura de Ângulos Atuais ===")
    print()

    angles = client.read_all_bend_angles()
    for i, (key, value) in enumerate(angles.items(), 1):
        status = "✓" if value is not None else "✗"
        print(f"{status} {key}: {value}°")

    print()
    print("=== FASE 2: Gravação de Ângulos de Teste ===")
    print()

    test_angles = {
        1: 90.0,
        2: 120.0,
        3: 45.5
    }

    for bend, angle in test_angles.items():
        success = client.write_bend_angle(bend, angle)
        status = "✓" if success else "✗"
        print(f"{status} Dobra {bend}: {angle}°")

    print()
    print("=== FASE 3: Verificação (aguardando 1s) ===")
    print()

    import time
    time.sleep(1)

    for bend in [1, 2, 3]:
        read_angle = client.read_bend_angle(bend)
        expected = test_angles[bend]

        if read_angle is not None and abs(read_angle - expected) < 0.1:
            print(f"✓ Dobra {bend}: {read_angle}° (esperado: {expected}°) - OK")
        else:
            print(f"✗ Dobra {bend}: {read_angle}° (esperado: {expected}°) - FALHA")

    print()
    print("=== FASE 4: Teste de Valores Extremos ===")
    print()

    extreme_tests = {
        1: 1.0,    # Mínimo
        2: 180.0,  # Máximo
        3: 135.7   # Decimal
    }

    for bend, angle in extreme_tests.items():
        client.write_bend_angle(bend, angle)
        time.sleep(0.3)
        read_back = client.read_bend_angle(bend)
        match = "✓" if read_back and abs(read_back - angle) < 0.1 else "✗"
        print(f"{match} Dobra {bend}: {angle}° → Lido: {read_back}°")

    print()
    print("=== TESTE COMPLETO ===")
    print()

    # Restaurar valores padrão
    print("Restaurando valores padrão (90°, 120°, 56°)...")
    client.write_bend_angle(1, 90.0)
    client.write_bend_angle(2, 120.0)
    client.write_bend_angle(3, 56.0)

    print("✓ Teste finalizado")
    client.close()


if __name__ == "__main__":
    main()
