#!/usr/bin/env python3
"""
Teste de Validação - Correção de Conversão de Ângulos
======================================================

Testa se a conversão real_angle_to_clp() → clp_to_real_angle()
está funcionando corretamente com o threshold de 28°.
"""

import sys
sys.path.insert(0, '/home/lucas-junges/Documents/wco/ihm_esp32')

from modbus_map import real_angle_to_clp, clp_to_real_angle

def test_angle_conversion(angle_input: float):
    """
    Testa conversão ida e volta para um ângulo.

    Args:
        angle_input: Ângulo de entrada (graus)
    """
    # Conversão IHM → CLP
    clp_value = real_angle_to_clp(angle_input)

    # Conversão CLP → IHM (volta)
    angle_output = clp_to_real_angle(clp_value)

    # Erro
    error = abs(angle_output - angle_input)

    # Determina se usou compensação
    tem_compensacao = angle_input >= 28.0

    # Status
    status = "✅" if error < 0.5 else "❌"

    print(f"{status} {angle_input:6.1f}° → CLP {clp_value:4d} (0x{clp_value:04X}) → {angle_output:6.1f}° | "
          f"erro: {error:5.2f}° | compensação: {'SIM' if tem_compensacao else 'NÃO'}")

    return error < 0.5


if __name__ == "__main__":
    print("=" * 90)
    print("TESTE DE VALIDAÇÃO - CONVERSÃO DE ÂNGULOS")
    print("=" * 90)
    print("\nThreshold de compensação: 28°")
    print("Compensação de inércia: 138 (27 pulsos encoder = 24.3° disco)")
    print("Fator geométrico: 78.9/90 = 0.8767")
    print("\n" + "=" * 90)
    print("   Input  →    CLP Value     →  Output  |  Erro  | Compensação")
    print("=" * 90)

    # Casos de teste
    test_angles = [
        0.0,    # Zero absoluto
        5.0,    # Muito pequeno
        10.0,   # Pequeno
        15.0,   # Pequeno
        20.0,   # Pequeno
        25.0,   # Pequeno (próximo ao threshold)
        27.0,   # Justo antes do threshold
        27.9,   # Justo antes do threshold
        28.0,   # Exatamente no threshold
        28.1,   # Justo depois do threshold
        30.0,   # Com compensação
        35.0,   # Com compensação
        40.0,   # Com compensação
        45.0,   # CASO PROBLEMÁTICO
        50.0,   # Com compensação
        60.0,   # Com compensação
        75.0,   # Com compensação
        90.0,   # Ângulo reto
        100.0,  # Obtuso
        120.0,  # Obtuso
        135.0,  # Obtuso
        150.0,  # Obtuso
        160.0,  # Obtuso
        170.0,  # Obtuso
        180.0,  # Ângulo raso
    ]

    results = []
    for angle in test_angles:
        passed = test_angle_conversion(angle)
        results.append(passed)

    print("=" * 90)
    print(f"\nResultados: {sum(results)}/{len(results)} testes passaram")

    if all(results):
        print("✅ TODOS OS TESTES PASSARAM!")
    else:
        print("❌ ALGUNS TESTES FALHARAM!")
        sys.exit(1)

    print("\n" + "=" * 90)
    print("TESTE ESPECÍFICO: 45° (caso reportado pelo usuário)")
    print("=" * 90)

    angle_in = 45.0
    clp_val = real_angle_to_clp(angle_in)
    angle_out = clp_to_real_angle(clp_val)
    error = abs(angle_out - angle_in)

    print(f"\nEntrada:    {angle_in}°")
    print(f"CLP value:  {clp_val} (0x{clp_val:04X})")
    print(f"Saída:      {angle_out:.2f}°")
    print(f"Erro:       {error:.2f}°")

    if error < 0.5:
        print(f"\n✅ CORREÇÃO FUNCIONOU! Erro {error:.2f}° < 0.5°")
    else:
        print(f"\n❌ CORREÇÃO FALHOU! Erro {error:.2f}° >= 0.5°")
        sys.exit(1)
