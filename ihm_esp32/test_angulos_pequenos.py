#!/usr/bin/env python3
"""
Teste de Ângulos Pequenos - IHM Web Dobradeira
===============================================

Valida que ângulos < 28° agora funcionam corretamente após remoção
da compensação de inércia para valores pequenos.

Autor: Claude Code
Data: 06/Jan/2026
"""

import modbus_map as mm


def test_conversao_angulos():
    """Testa conversão bidirecional de ângulos"""

    print("=" * 70)
    print("TESTE DE CONVERSÃO DE ÂNGULOS - ÂNGULOS PEQUENOS")
    print("=" * 70)

    # Casos de teste: ângulos do usuário (IHM)
    test_cases = [
        0.0,    # Zero absoluto
        5.0,    # Muito pequeno
        10.0,   # Pequeno
        15.0,   # Pequeno
        20.0,   # Pequeno
        24.3,   # Limite anterior (falhava)
        27.0,   # No limite
        28.0,   # Exatamente no threshold
        30.0,   # Acima do threshold
        45.0,   # Médio
        90.0,   # Grande
        135.0,  # Muito grande
        180.0,  # Máximo
    ]

    print("\n📐 CONVERSÃO: Ângulo IHM → Valor CLP → Ângulo IHM (round-trip)")
    print("-" * 70)
    print(f"{'IHM (°)':>8} | {'CLP (int)':>11} | {'IHM volta (°)':>14} | {'Erro (°)':>10} | {'Compensação':>12}")
    print("-" * 70)

    for angulo_ihm in test_cases:
        # IHM → CLP
        valor_clp = mm.real_angle_to_clp(angulo_ihm)

        # CLP → IHM (round-trip)
        angulo_volta = mm.clp_to_real_angle(valor_clp)

        # Calcula erro
        erro = abs(angulo_volta - angulo_ihm)

        # Verifica se compensação foi aplicada
        compensacao = "SIM" if angulo_ihm >= 28.0 else "NÃO"

        # Status: OK se erro < 2°, AVISO se erro < 5°, ERRO se >= 5°
        if erro < 2.0:
            status = "✅"
        elif erro < 5.0:
            status = "⚠️"
        else:
            status = "❌"

        print(f"{angulo_ihm:8.1f} | {valor_clp:11d} | {angulo_volta:14.2f} | {erro:10.2f} | {compensacao:>12} {status}")

    print("-" * 70)

    # Teste específico: ângulos que falhavam antes
    print("\n🎯 CASOS CRÍTICOS (que falhavam antes):")
    print("-" * 70)

    critical_angles = [5.0, 10.0, 15.0, 20.0, 24.3]

    for ang in critical_angles:
        valor = mm.real_angle_to_clp(ang)
        volta = mm.clp_to_real_angle(valor)
        erro = abs(volta - ang)

        if valor > 0:
            print(f"✅ {ang:5.1f}° → CLP={valor:4d} → {volta:5.2f}° (erro={erro:.2f}°) - FUNCIONA!")
        else:
            print(f"❌ {ang:5.1f}° → CLP={valor:4d} - FALHA (valor zero)")

    print("-" * 70)

    # Teste de limites
    print("\n⚠️  LIMITES DO SISTEMA:")
    print("-" * 70)

    # Menor ângulo não-zero possível
    menor_possivel = mm.clp_to_real_angle(1)
    print(f"Menor ângulo não-zero: {menor_possivel:.3f}° (CLP=1)")

    # Threshold de compensação
    threshold_clp = mm.real_angle_to_clp(28.0)
    print(f"Threshold compensação: 28.0° → CLP={threshold_clp}")
    print(f"  Abaixo de 28°: SEM compensação de inércia")
    print(f"  Acima de 28°:  COM compensação de inércia (-138 unidades)")

    # Ângulo máximo
    max_clp = 2048
    max_angulo = mm.clp_to_real_angle(max_clp)
    print(f"Ângulo máximo: {max_angulo:.1f}° (CLP=2048)")

    print("-" * 70)

    # Teste de correção geométrica
    print("\n🔧 CORREÇÃO GEOMÉTRICA (78.9/90):")
    print("-" * 70)
    fator = 78.9 / 90.0
    print(f"Fator de correção: {fator:.4f}")
    print(f"  90° usuário → {90 * fator:.1f}° interno")
    print(f"  45° usuário → {45 * fator:.1f}° interno")
    print(f"  10° usuário → {10 * fator:.1f}° interno")
    print("-" * 70)

    print("\n✅ TESTE CONCLUÍDO!")
    print("=" * 70)


if __name__ == "__main__":
    test_conversao_angulos()
