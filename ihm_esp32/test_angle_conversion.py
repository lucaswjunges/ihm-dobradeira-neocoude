#!/usr/bin/env python3
"""
Teste de Conversão de Ângulos - DESCOBERTA CRÍTICA 02/Jan/2026

CLP armazena ângulos em escala de 12 bits (0-2048 = 0-360°):
  - 45° → 0x0100 (256 decimal)
  - 90° → 0x0200 (512 decimal)
  - 180° → 0x0400 (1024 decimal)

Este script testa as funções de conversão:
  - real_angle_to_clp(): converte ângulo real → valor CLP (escala 2048)
  - clp_to_real_angle(): converte valor CLP → ângulo real
"""

import sys
sys.path.append('/home/lucas-junges/Documents/wco/ihm_esp32')

import modbus_map as mm

def test_conversions():
    """Testa conversões de ângulos."""

    print("=" * 70)
    print("TESTE DE CONVERSÃO DE ÂNGULOS - ESCALA 2048")
    print("=" * 70)
    print()
    print("⚠️  DESCOBERTA: CLP usa escala de 2048 (12 bits) para ângulos!")
    print()

    # Casos de teste
    test_cases = [
        ("Dobra pequena", 45.0, 256),
        ("Dobra padrão", 90.0, 512),
        ("Dobra grande", 135.0, 768),
        ("Dobra meia-volta", 180.0, 1024),
    ]

    print("ESCRITA (IHM → CLP):")
    print("-" * 70)
    print(f"{'Descrição':<20} {'Ângulo Real':<15} {'Valor CLP':<18} {'Hexa':<15}")
    print("-" * 70)

    for desc, real_angle, expected_value in test_cases:
        clp_value = mm.real_angle_to_clp(real_angle)
        status = "✓" if clp_value == expected_value else f"✗ (esperado {expected_value})"
        print(f"{desc:<20} {real_angle:>8.1f}°      {clp_value:>10}         0x{clp_value:04X} {status}")

    print()
    print()
    print("LEITURA (CLP → IHM):")
    print("-" * 70)
    print(f"{'Valor CLP':<15} {'Hexa':<15} {'Ângulo Real':<15} {'Descrição':<20}")
    print("-" * 70)

    # Casos reversos
    test_values = [
        (256, "0x0100", "1/8 de volta (45°)"),
        (512, "0x0200", "1/4 de volta (90°)"),
        (1024, "0x0400", "1/2 de volta (180°)"),
        (1536, "0x0600", "3/4 de volta (270°)"),
        (2048, "0x0800", "Volta completa (360°)"),
    ]

    for clp_value, hexa, desc in test_values:
        real_angle = mm.clp_to_real_angle(clp_value)
        print(f"{clp_value:>10}      {hexa:<15} {real_angle:>8.1f}°      {desc:<20}")

    print()
    print("=" * 70)
    print("VALIDAÇÃO - Ciclo completo (escrever e ler de volta):")
    print("=" * 70)
    print()

    validation_cases = [45.0, 90.0, 135.0, 180.0, 270.0, 359.5]

    all_ok = True
    for original_real in validation_cases:
        # Simula escrita
        clp_value_written = mm.real_angle_to_clp(original_real)

        # Simula leitura
        read_back_real = mm.clp_to_real_angle(clp_value_written)

        # Valida
        error = abs(original_real - read_back_real)
        ok = error < 0.5  # Tolerância de 0.5° (arredondamento de int)

        status = "✅ OK" if ok else "❌ ERRO"
        print(f"{status}  Original: {original_real:>6.1f}° → CLP: {clp_value_written:>4} (0x{clp_value_written:04X}) → Lido: {read_back_real:>6.1f}° (erro: {error:.3f}°)")

        if not ok:
            all_ok = False

    print()
    if all_ok:
        print("✅ TODAS AS CONVERSÕES VALIDADAS COM SUCESSO!")
    else:
        print("❌ ERRO: Algumas conversões falharam!")

    print()
    print("=" * 70)
    print("IMPORTANTE:")
    print("  - Ângulos armazenados em escala de 2048 (12 bits)")
    print("  - 45° → 256 (0x0100), 90° → 512 (0x0200), 180° → 1024 (0x0400)")
    print("  - Encoder SEPARADO: 400 pulsos/volta (endereço 1238)")
    print("  - Endereços ângulos: 2114, 2116, 2118 (0x0842, 0x0844, 0x0846)")
    print("  - Fórmula: valor_clp = (graus / 360) × 2048")
    print()

if __name__ == "__main__":
    test_conversions()
