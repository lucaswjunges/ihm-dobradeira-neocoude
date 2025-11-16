#!/usr/bin/env python3
"""
🔍 TESTE EXPLORATÓRIO - VARREDURA COMPLETA DE REGISTROS GRAVÁVEIS
==================================================================

Objetivo: Encontrar registros que:
1. Aceitam escrita via Modbus
2. Persistem por 10+ segundos (não sobrescritos pelo ladder)
3. Podem ser os registros que IHM física original usava

Áreas a testar:
- NVRAM Angles (0x0500-0x053F): 16 ângulos iniciais/finais
- Timers/Counters (0x0400-0x047F): Presets e efetivos
- Supervision Area (0x0940-0x0960): Área supervisória
- Holding Registers gerais (0x0400-0x0FFF): Todos os registros

ATENÇÃO: Este teste pode demorar 30-60 minutos!
"""

import sys
import time
from modbus_client import ModbusClientWrapper

TEST_VALUE = 12345  # Valor único para detectar persistência
PERSISTENCE_TIME = 5  # Segundos para verificar se persiste

def test_register_pair(client, msw_addr, lsw_addr, verbose=False):
    """
    Testa se um par de registros aceita escrita e persiste.

    Returns: (can_write, persists, read_value)
    """
    # 1. Ler valor atual
    try:
        msw_before = client.read_register(msw_addr)
        lsw_before = client.read_register(lsw_addr)

        if msw_before is None or lsw_before is None:
            return (False, False, None, None)

        value_before = (msw_before << 16) | lsw_before
    except:
        return (False, False, None, None)

    # 2. Escrever valor de teste
    try:
        msw_test = (TEST_VALUE >> 16) & 0xFFFF
        lsw_test = TEST_VALUE & 0xFFFF

        write_ok = (client.write_register(msw_addr, msw_test) and
                    client.write_register(lsw_addr, lsw_test))

        if not write_ok:
            return (False, False, value_before, value_before)
    except:
        return (False, False, value_before, value_before)

    time.sleep(0.1)  # Aguardar CLP processar

    # 3. Ler imediatamente
    try:
        msw_after = client.read_register(msw_addr)
        lsw_after = client.read_register(lsw_addr)

        if msw_after is None or lsw_after is None:
            return (True, False, value_before, None)

        value_immediate = (msw_after << 16) | lsw_after
    except:
        return (True, False, value_before, None)

    # 4. Verificar persistência
    if abs(value_immediate - TEST_VALUE) > 5:
        # Valor não foi escrito corretamente
        return (True, False, value_before, value_immediate)

    if verbose:
        print(f"    [0x{msw_addr:04X}/0x{lsw_addr:04X}] Escrita OK, aguardando {PERSISTENCE_TIME}s...")

    time.sleep(PERSISTENCE_TIME)

    # 5. Ler após delay
    try:
        msw_delayed = client.read_register(msw_addr)
        lsw_delayed = client.read_register(lsw_addr)

        if msw_delayed is None or lsw_delayed is None:
            return (True, False, value_before, value_immediate)

        value_delayed = (msw_delayed << 16) | lsw_delayed
    except:
        return (True, False, value_before, value_immediate)

    # 6. Verificar se persistiu
    persists = abs(value_delayed - TEST_VALUE) < 5

    # 7. Restaurar valor original
    try:
        msw_orig = (value_before >> 16) & 0xFFFF
        lsw_orig = value_before & 0xFFFF
        client.write_register(msw_addr, msw_orig)
        client.write_register(lsw_addr, lsw_orig)
        time.sleep(0.1)
    except:
        pass

    return (True, persists, value_before, value_delayed)


def main():
    print("=" * 70)
    print("🔍 VARREDURA COMPLETA - REGISTROS GRAVÁVEIS E PERSISTENTES")
    print("=" * 70)
    print("\nAVISO: Este teste pode demorar 30-60 minutos!")
    print("Pressione Ctrl+C para interromper.\n")

    input("Pressione ENTER para iniciar... ")

    client = ModbusClientWrapper(stub_mode=False, port='/dev/ttyUSB0')

    if not client.connected:
        print("❌ CLP não conectado!")
        return 1

    print("✅ CLP conectado\n")

    # Definir áreas a testar
    test_areas = [
        # Nome, start_addr, end_addr, step
        ("NVRAM Angles (0x0500-0x053F)", 0x0500, 0x053F, 2),
        ("Timers/Counters (0x0400-0x047F)", 0x0400, 0x047F, 2),
        ("Supervision Area (0x0940-0x0960)", 0x0940, 0x0960, 2),
        ("Bend Area Extended (0x0800-0x0870)", 0x0800, 0x0870, 2),
    ]

    candidates = []
    total_tested = 0

    for area_name, start, end, step in test_areas:
        print("\n" + "=" * 70)
        print(f"TESTANDO: {area_name}")
        print("=" * 70)

        area_candidates = []

        for addr in range(start, end, step):
            msw_addr = addr
            lsw_addr = addr + 1

            if lsw_addr > end:
                break

            total_tested += 1

            print(f"\r[{total_tested:4d}] Testando 0x{msw_addr:04X}/0x{lsw_addr:04X}...", end='', flush=True)

            can_write, persists, val_before, val_after = test_register_pair(
                client, msw_addr, lsw_addr
            )

            if persists:
                print(f"\r✅ ENCONTRADO! 0x{msw_addr:04X}/0x{lsw_addr:04X} - PERSISTE!     ")
                area_candidates.append((msw_addr, lsw_addr, val_before, val_after))
                candidates.append({
                    'area': area_name,
                    'msw': msw_addr,
                    'lsw': lsw_addr,
                    'value_before': val_before,
                    'value_after': val_after
                })

        if area_candidates:
            print(f"\n✅ {len(area_candidates)} candidato(s) encontrado(s) em {area_name}")
        else:
            print(f"\n⊘ Nenhum candidato em {area_name}")

    # RESULTADOS
    print("\n" + "=" * 70)
    print("🎯 RESULTADOS DA VARREDURA")
    print("=" * 70)

    print(f"\nTotal de pares testados: {total_tested}")
    print(f"Candidatos encontrados: {len(candidates)}")

    if candidates:
        print("\n📋 REGISTROS QUE ACEITAM ESCRITA E PERSISTEM:")
        print("-" * 70)

        for i, cand in enumerate(candidates, 1):
            msw = cand['msw']
            lsw = cand['lsw']
            area = cand['area']
            val_before = cand['value_before']
            val_after = cand['value_after']

            print(f"\n{i}. MSW=0x{msw:04X} ({msw}), LSW=0x{lsw:04X} ({lsw})")
            print(f"   Área: {area}")
            print(f"   Valor antes: {val_before} ({val_before/10.0:.1f}° se for ângulo)")
            print(f"   Valor após teste: {val_after} (esperado {TEST_VALUE})")

            # Verificar se está na área NVRAM
            if 0x0500 <= msw <= 0x053F:
                angle_idx = (msw - 0x0500) // 2
                print(f"   ⚠️ POSSÍVEL ÂNGULO NVRAM #{angle_idx}")

        print("\n" + "=" * 70)
        print("✅ RECOMENDAÇÃO:")
        print("=" * 70)
        print("\nAtualizar modbus_map.py com os candidatos encontrados:")
        print("\nBEND_ANGLES = {")

        # Sugerir mapeamento se encontrou 3+ candidatos na mesma área
        nvram_candidates = [c for c in candidates if 0x0500 <= c['msw'] <= 0x053F]

        if len(nvram_candidates) >= 3:
            print("    # 🎯 ENDEREÇOS DESCOBERTOS VIA VARREDURA EXPLORATÓRIA")
            for i, cand in enumerate(nvram_candidates[:3], 1):
                msw = cand['msw']
                lsw = cand['lsw']
                print(f"    'BEND_{i}_LEFT_MSW': 0x{msw:04X},  # {msw}")
                print(f"    'BEND_{i}_LEFT_LSW': 0x{lsw:04X},  # {lsw}")
        else:
            print("    # ⚠️ Não foram encontrados 3+ candidatos consecutivos")
            print("    # Manter endereços atuais ou investigar manualmente")

        print("}")

    else:
        print("\n❌ NENHUM CANDIDATO ENCONTRADO!")
        print("\nPossíveis causas:")
        print("1. Ladder sobrescreve TODOS os registros testados")
        print("2. IHM física usava comunicação serial direta (não Modbus)")
        print("3. Registros estão fora das áreas testadas")
        print("\n💡 PRÓXIMA AÇÃO:")
        print("   → Abrir WinSUP segunda-feira")
        print("   → Analisar ladder completo")
        print("   → Procurar instruções MOV/MOVK escrevendo em 0x0500-0x053F")

    client.close()
    print("\n" + "=" * 70)

    return 0 if candidates else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Teste interrompido pelo usuário!")
        print("Candidatos encontrados até agora foram salvos acima.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ ERRO: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
