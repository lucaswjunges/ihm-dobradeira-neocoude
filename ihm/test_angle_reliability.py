#!/usr/bin/env python3
"""
Teste de Confiabilidade: Gravação de Ângulos

Executa múltiplas rodadas de gravação para identificar padrão de falhas.
"""

import time
from modbus_client import ModbusClientWrapper
import modbus_map as mm

def test_angle_write_reliability(num_rounds=10):
    """Testa confiabilidade de gravação de ângulos em múltiplas rodadas."""

    print("=" * 60)
    print("TESTE DE CONFIABILIDADE: Gravação de Ângulos")
    print("=" * 60)
    print()

    client = ModbusClientWrapper(stub_mode=False)

    if not client.connected:
        print("❌ Falha ao conectar com CLP")
        return False

    print("✅ Conectado ao CLP")
    print(f"Executando {num_rounds} rodadas de teste...")
    print()

    # Configuração dos ângulos
    angles = [
        (1, 90.0, mm.BEND_ANGLES['BEND_1_LEFT_MSW'], mm.BEND_ANGLES['BEND_1_LEFT_LSW']),
        (2, 120.0, mm.BEND_ANGLES['BEND_2_LEFT_MSW'], mm.BEND_ANGLES['BEND_2_LEFT_LSW']),
        (3, 45.0, mm.BEND_ANGLES['BEND_3_LEFT_MSW'], mm.BEND_ANGLES['BEND_3_LEFT_LSW']),
    ]

    # Estatísticas
    results = {
        1: {'success': 0, 'fail': 0},
        2: {'success': 0, 'fail': 0},
        3: {'success': 0, 'fail': 0},
    }

    # Executar rodadas
    for round_num in range(1, num_rounds + 1):
        print(f"\n{'='*60}")
        print(f"RODADA {round_num}/{num_rounds}")
        print(f"{'='*60}")

        # Delay inicial
        print("⏱️  Aguardando 2s inicial...")
        time.sleep(2.0)

        round_results = []

        for bend_num, angle_deg, msw_addr, lsw_addr in angles:
            print(f"\n  Dobra {bend_num} ({angle_deg}°)... ", end='', flush=True)

            value_clp = int(angle_deg * 10)
            success = client.write_32bit(msw_addr, lsw_addr, value_clp)

            if success:
                print("✓")
                results[bend_num]['success'] += 1
            else:
                print("✗")
                results[bend_num]['fail'] += 1

            round_results.append(success)

            # Delay entre gravações
            if bend_num < 3:
                time.sleep(1.5)

        # Resumo da rodada
        successes = sum(round_results)
        print(f"\n  Rodada {round_num}: {successes}/3 sucessos ({successes/3*100:.0f}%)")

        # Delay entre rodadas
        if round_num < num_rounds:
            print(f"\n  Aguardando 3s antes da próxima rodada...")
            time.sleep(3.0)

    # Estatísticas finais
    print("\n" + "=" * 60)
    print("ESTATÍSTICAS FINAIS")
    print("=" * 60)
    print()

    print("Por Dobra:")
    print("-" * 60)
    for bend_num in [1, 2, 3]:
        total = results[bend_num]['success'] + results[bend_num]['fail']
        success_rate = results[bend_num]['success'] / total * 100 if total > 0 else 0
        print(f"  Dobra {bend_num}: {results[bend_num]['success']}/{total} sucessos ({success_rate:.0f}%)")

    print()
    print("Geral:")
    print("-" * 60)
    total_success = sum(r['success'] for r in results.values())
    total_attempts = sum(r['success'] + r['fail'] for r in results.values())
    overall_rate = total_success / total_attempts * 100 if total_attempts > 0 else 0
    print(f"  Total: {total_success}/{total_attempts} sucessos ({overall_rate:.0f}%)")

    print()
    print("Análise:")
    print("-" * 60)

    # Identificar padrões
    dobra1_rate = results[1]['success'] / num_rounds * 100
    dobra2_rate = results[2]['success'] / num_rounds * 100
    dobra3_rate = results[3]['success'] / num_rounds * 100

    if dobra1_rate < 50:
        print("  ⚠️ Dobra 1 tem baixa taxa de sucesso (<50%)")
        print("     Hipótese: Primeira gravação sempre problemática")

    if dobra3_rate < 50:
        print("  ⚠️ Dobra 3 tem baixa taxa de sucesso (<50%)")
        print("     Hipótese: CLP pode estar ocupado após 2 gravações")

    if dobra2_rate > 80:
        print("  ✓ Dobra 2 tem alta taxa de sucesso (>80%)")
        print("     Conclusão: Gravações intermediárias mais confiáveis")

    if overall_rate > 80:
        print("\n  ✅ Sistema CONFIÁVEL (>80% taxa geral)")
    elif overall_rate > 60:
        print("\n  ⚠️ Sistema MODERADAMENTE CONFIÁVEL (60-80% taxa geral)")
    else:
        print("\n  ❌ Sistema POUCO CONFIÁVEL (<60% taxa geral)")

    print()

    if hasattr(client.client, 'close'):
        client.client.close()

    return overall_rate


def test_with_longer_delays():
    """Testa com delays maiores para ver se melhora."""

    print("\n" + "=" * 60)
    print("TESTE ALTERNATIVO: Delays Maiores")
    print("=" * 60)
    print()

    client = ModbusClientWrapper(stub_mode=False)

    if not client.connected:
        print("❌ Falha ao conectar com CLP")
        return False

    print("✅ Conectado ao CLP")
    print("Testando com delays aumentados:")
    print("  - Delay inicial: 3s (era 2s)")
    print("  - Delay entre gravações: 2s (era 1.5s)")
    print()

    angles = [
        (1, 90.0, mm.BEND_ANGLES['BEND_1_LEFT_MSW'], mm.BEND_ANGLES['BEND_1_LEFT_LSW']),
        (2, 120.0, mm.BEND_ANGLES['BEND_2_LEFT_MSW'], mm.BEND_ANGLES['BEND_2_LEFT_LSW']),
        (3, 45.0, mm.BEND_ANGLES['BEND_3_LEFT_MSW'], mm.BEND_ANGLES['BEND_3_LEFT_LSW']),
    ]

    # Executar 5 rodadas
    results = []

    for round_num in range(1, 6):
        print(f"\nRodada {round_num}/5:")

        # Delay inicial maior
        print("  Aguardando 3s inicial...")
        time.sleep(3.0)

        round_success = 0

        for bend_num, angle_deg, msw_addr, lsw_addr in angles:
            value_clp = int(angle_deg * 10)
            success = client.write_32bit(msw_addr, lsw_addr, value_clp)

            status = "✓" if success else "✗"
            print(f"  Dobra {bend_num}: {status}")

            if success:
                round_success += 1

            # Delay maior entre gravações
            if bend_num < 3:
                time.sleep(2.0)

        results.append(round_success)
        print(f"  Resultado: {round_success}/3 ({round_success/3*100:.0f}%)")

        if round_num < 5:
            time.sleep(3.0)

    # Análise
    print()
    print("Resultados com delays maiores:")
    print(f"  {results}")
    avg = sum(results) / len(results)
    print(f"  Média: {avg:.1f}/3 ({avg/3*100:.0f}%)")

    if avg > 2.5:
        print("  ✅ Delays maiores MELHORARAM confiabilidade!")
        print("  Recomendação: Usar 3s inicial + 2s entre gravações")
    else:
        print("  ⚠️ Delays maiores NÃO melhoraram significativamente")
        print("  Problema pode ser outra coisa além de timing")

    print()

    if hasattr(client.client, 'close'):
        client.client.close()

    return True


if __name__ == "__main__":
    print()
    print("╔════════════════════════════════════════════════════════╗")
    print("║  TESTE DE CONFIABILIDADE: Gravação de Ângulos         ║")
    print("╚════════════════════════════════════════════════════════╝")
    print()

    # Teste 1: Confiabilidade padrão
    overall_rate = test_angle_write_reliability(num_rounds=10)

    print("\n" + "="*60 + "\n")

    # Teste 2: Delays maiores
    test_with_longer_delays()

    print()
    print("=" * 60)
    print("TESTE COMPLETO")
    print("=" * 60)
    print()
    print(f"Taxa geral com delays padrão: {overall_rate:.0f}%")
    print()
