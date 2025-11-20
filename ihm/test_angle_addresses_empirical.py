#!/usr/bin/env python3
"""
Teste Empírico - Descoberta de Endereços de Ângulos
===================================================

Como engenheiro sênior, vou testar TODOS os endereços candidatos:
1. Endereços do ladder (0x0840-0x0856)
2. Zona de supervisão (0x0940-0x0960)
3. Área NVRAM (0x0500-0x053F)

Objetivo: Encontrar qual endereço REALMENTE aceita escrita e persiste.
"""

import time
from modbus_client import ModbusClientWrapper

def test_write_32bit_address(client, msw_addr, lsw_addr, test_value=900):
    """
    Testa se um par de endereços aceita escrita 32-bit

    Returns: (can_write, persists, read_value)
    """
    print(f"\n  Testando MSW=0x{msw_addr:04X}, LSW=0x{lsw_addr:04X}...")

    # 1. Ler valor ANTES
    value_before = client.read_32bit(msw_addr, lsw_addr)
    if value_before is None:
        print(f"    ❌ Não conseguiu LER")
        return (False, False, None)

    print(f"    Valor ANTES: {value_before} ({value_before/10.0}°)")

    # 2. Escrever valor de teste
    success = client.write_32bit(msw_addr, lsw_addr, test_value)
    if not success:
        print(f"    ❌ ESCRITA REJEITADA pelo CLP")
        return (False, False, value_before)

    print(f"    ✓ Escrita aceita: {test_value} ({test_value/10.0}°)")

    # 3. Aguardar processamento
    time.sleep(0.15)

    # 4. Ler de volta
    value_after = client.read_32bit(msw_addr, lsw_addr)
    if value_after is None:
        print(f"    ❌ Não conseguiu ler de volta")
        return (True, False, None)

    print(f"    Valor DEPOIS: {value_after} ({value_after/10.0}°)")

    # 5. Verificar persistência
    persists = abs(value_after - test_value) < 5  # Tolerância de 0.5°

    if persists:
        print(f"    ✅ PERSISTIU! Endereço FUNCIONAL para escrita")
        # Restaurar valor original
        client.write_32bit(msw_addr, lsw_addr, value_before)
        time.sleep(0.1)
        return (True, True, value_after)
    else:
        print(f"    ⚠️ NÃO PERSISTIU (ladder pode ter sobrescrito)")
        return (True, False, value_after)


def main():
    print("=" * 70)
    print("  TESTE EMPÍRICO - DESCOBERTA DE ENDEREÇOS DE ÂNGULOS")
    print("  Engenheiro: Automação Sênior")
    print("=" * 70)

    # Conectar ao CLP
    client = ModbusClientWrapper(stub_mode=False, port='/dev/ttyUSB0')

    if not client.connected:
        print("\n❌ CLP não conectado! Abortando.")
        return 1

    print("\n✓ Conectado ao CLP Atos MPC4004")

    # ==============================================
    # TESTE 1: Endereços do LADDER (análise)
    # ==============================================
    print("\n" + "=" * 70)
    print("TESTE 1: ENDEREÇOS DO LADDER (PRINCIPA.LAD)")
    print("=" * 70)

    ladder_candidates = [
        ("Dobra 1 Esq (ladder)", 0x0840, 0x0842),  # Conforme ANALISE_COMPLETA
        ("Dobra 1 Dir (ladder)", 0x0844, 0x0846),
        ("Dobra 2 Esq (ladder)", 0x0848, 0x084A),
        ("Dobra 2 Dir (ladder)", 0x084C, 0x084E),
        ("Dobra 3 Esq (ladder)", 0x0850, 0x0852),
        ("Dobra 3 Dir (ladder)", 0x0854, 0x0856),
    ]

    ladder_results = []
    for name, msw, lsw in ladder_candidates:
        print(f"\n{name}:")
        can_write, persists, value = test_write_32bit_address(client, msw, lsw, 900)
        ladder_results.append((name, msw, lsw, can_write, persists))

    # ==============================================
    # TESTE 2: ZONA DE SUPERVISÃO (empirica)
    # ==============================================
    print("\n" + "=" * 70)
    print("TESTE 2: ZONA DE SUPERVISÃO (0x0940-0x0960)")
    print("=" * 70)

    supervision_candidates = [
        ("Supervisão 0x0940", 0x0940, 0x0941),
        ("Supervisão 0x0942", 0x0942, 0x0943),
        ("Supervisão 0x0944", 0x0944, 0x0945),
        ("Supervisão 0x0946", 0x0946, 0x0947),
        ("Supervisão 0x0948", 0x0948, 0x0949),
        ("Supervisão 0x094A", 0x094A, 0x094B),
        ("Supervisão 0x094C", 0x094C, 0x094D),
        ("Supervisão 0x094E", 0x094E, 0x094F),
        ("Supervisão 0x0950", 0x0950, 0x0951),  # Testado antes
        ("Supervisão 0x0952", 0x0952, 0x0953),
    ]

    supervision_results = []
    for name, msw, lsw in supervision_candidates:
        print(f"\n{name}:")
        can_write, persists, value = test_write_32bit_address(client, msw, lsw, 1200)
        supervision_results.append((name, msw, lsw, can_write, persists))

    # ==============================================
    # TESTE 3: ÁREA NVRAM (manual MPC4004)
    # ==============================================
    print("\n" + "=" * 70)
    print("TESTE 3: ÁREA NVRAM (0x0500-0x0520)")
    print("=" * 70)

    nvram_candidates = [
        ("NVRAM 0x0500", 0x0500, 0x0501),
        ("NVRAM 0x0502", 0x0502, 0x0503),
        ("NVRAM 0x0504", 0x0504, 0x0505),
        ("NVRAM 0x0506", 0x0506, 0x0507),
        ("NVRAM 0x0510", 0x0510, 0x0511),
        ("NVRAM 0x0512", 0x0512, 0x0513),
    ]

    nvram_results = []
    for name, msw, lsw in nvram_candidates:
        print(f"\n{name}:")
        can_write, persists, value = test_write_32bit_address(client, msw, lsw, 1800)
        nvram_results.append((name, msw, lsw, can_write, persists))

    # ==============================================
    # RELATÓRIO FINAL
    # ==============================================
    print("\n" + "=" * 70)
    print("RELATÓRIO FINAL - ENDEREÇOS FUNCIONAIS")
    print("=" * 70)

    print("\n✅ ENDEREÇOS QUE ACEITAM ESCRITA E PERSISTEM:\n")

    all_results = ladder_results + supervision_results + nvram_results
    functional = [r for r in all_results if r[4]]  # persists == True

    if functional:
        for name, msw, lsw, _, _ in functional:
            print(f"  ✓ {name}: MSW=0x{msw:04X} ({msw}), LSW=0x{lsw:04X} ({lsw})")
    else:
        print("  ❌ NENHUM endereço persistiu!")
        print("\n  POSSÍVEIS CAUSAS:")
        print("  1. Ladder sobrescreve todos os registros testados")
        print("  2. Área NVRAM não está configurada")
        print("  3. Necessário ativar modo EDIT (0x0026) antes")
        print("  4. Registros requerem escrita via IHM (simulação de teclas)")

    print("\n⚠️ ENDEREÇOS QUE ACEITAM ESCRITA MAS NÃO PERSISTEM:\n")

    writable_but_not_persist = [r for r in all_results if r[3] and not r[4]]
    if writable_but_not_persist:
        for name, msw, lsw, _, _ in writable_but_not_persist:
            print(f"  - {name}: MSW=0x{msw:04X}, LSW=0x{lsw:04X}")
            print(f"    (Ladder provavelmente sobrescreve estes registros)")

    print("\n❌ ENDEREÇOS QUE REJEITAM ESCRITA:\n")

    readonly = [r for r in all_results if not r[3]]
    if readonly:
        for name, msw, lsw, _, _ in readonly:
            print(f"  - {name}: MSW=0x{msw:04X}, LSW=0x{lsw:04X}")

    client.close()

    print("\n" + "=" * 70)
    print("TESTE CONCLUÍDO")
    print("=" * 70)

    return 0 if functional else 1


if __name__ == '__main__':
    exit(main())
