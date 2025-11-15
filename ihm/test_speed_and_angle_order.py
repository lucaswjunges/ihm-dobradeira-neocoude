#!/usr/bin/env python3
"""
Teste: Investigar Problemas de Velocidade e Ordem de Gravação

Testa:
1. Por que mudança de velocidade falha agora
2. Por que primeira gravação de ângulo falha
"""

import time
from modbus_client import ModbusClientWrapper
import modbus_map as mm

def test_speed_change_detailed():
    """Testa mudança de velocidade com diagnóstico detalhado."""

    print("=" * 60)
    print("TESTE: Mudança de Velocidade (Diagnóstico)")
    print("=" * 60)
    print()

    client = ModbusClientWrapper(stub_mode=False)

    if not client.connected:
        print("❌ Falha ao conectar com CLP")
        return False

    print("✅ Conectado ao CLP")
    print()

    # Verificar condições antes de tentar
    print("--- Verificação de Condições ---")

    e6 = client.read_coil(0x0106)
    print(f"E6 (0x0106): {'ATIVA' if e6 else 'INATIVA'}")

    mode_bit = client.read_coil(0x02FF)
    mode_text = "AUTO" if mode_bit else "MANUAL"
    print(f"Modo (0x02FF): {mode_text}")

    # Verificar se K1 e K7 estão disponíveis
    k1_addr = mm.KEYBOARD_NUMERIC['K1']
    k7_addr = mm.KEYBOARD_NUMERIC['K7']

    k1_state = client.read_coil(k1_addr)
    k7_state = client.read_coil(k7_addr)

    print(f"K1 (0x{k1_addr:04X}): {k1_state}")
    print(f"K7 (0x{k7_addr:04X}): {k7_state}")
    print()

    # Tentar mudança de velocidade
    print("--- Tentativa de Mudança de Velocidade ---")
    print("Executando change_speed_class()...")
    print()

    success = client.change_speed_class()

    print()
    print(f"Resultado: {'✓ SUCESSO' if success else '✗ FALHA'}")
    print()

    # Verificar se E6 é necessária
    if not e6 and not success:
        print("⚠️ Hipótese: Mudança de velocidade pode depender de E6 ativa")
        print("   (Similar ao problema de mudança de modo)")

    print()

    if hasattr(client.client, 'close'):
        client.client.close()

    return success


def test_angle_write_order():
    """Testa ordem de gravação de ângulos."""

    print("=" * 60)
    print("TESTE: Ordem de Gravação de Ângulos")
    print("=" * 60)
    print()

    client = ModbusClientWrapper(stub_mode=False)

    if not client.connected:
        print("❌ Falha ao conectar com CLP")
        return False

    print("✅ Conectado ao CLP")
    print()

    # Teste 1: Gravar na ordem 1, 2, 3
    print("--- TESTE 1: Ordem Normal (1 → 2 → 3) ---")

    angles = [
        (1, 90.0, mm.BEND_ANGLES['BEND_1_LEFT_MSW'], mm.BEND_ANGLES['BEND_1_LEFT_LSW']),
        (2, 120.0, mm.BEND_ANGLES['BEND_2_LEFT_MSW'], mm.BEND_ANGLES['BEND_2_LEFT_LSW']),
        (3, 45.0, mm.BEND_ANGLES['BEND_3_LEFT_MSW'], mm.BEND_ANGLES['BEND_3_LEFT_LSW']),
    ]

    results_normal = []

    # Delay inicial maior antes da primeira gravação
    print("Aguardando 2s antes da primeira gravação...")
    time.sleep(2.0)

    for bend_num, angle_deg, msw_addr, lsw_addr in angles:
        print(f"\n📝 Gravando dobra {bend_num}: {angle_deg}°")
        print(f"   Endereços: MSW=0x{msw_addr:04X}, LSW=0x{lsw_addr:04X}")

        value_clp = int(angle_deg * 10)
        success = client.write_32bit(msw_addr, lsw_addr, value_clp)

        print(f"   Resultado: {'✓ Sucesso' if success else '✗ Falha'}")
        results_normal.append(success)

        # Delay entre gravações
        if bend_num < 3:
            print(f"   Aguardando 1.5s...")
            time.sleep(1.5)

    print()
    print(f"Taxa de sucesso (ordem normal): {sum(results_normal)}/{len(results_normal)} = {sum(results_normal)/len(results_normal)*100:.0f}%")
    print()

    # Aguardar antes do próximo teste
    print("Aguardando 3s antes do próximo teste...")
    time.sleep(3.0)

    # Teste 2: Gravar na ordem reversa 3, 2, 1
    print("--- TESTE 2: Ordem Reversa (3 → 2 → 1) ---")

    angles_reverse = list(reversed(angles))
    results_reverse = []

    # Delay inicial maior antes da primeira gravação
    print("Aguardando 2s antes da primeira gravação...")
    time.sleep(2.0)

    for bend_num, angle_deg, msw_addr, lsw_addr in angles_reverse:
        print(f"\n📝 Gravando dobra {bend_num}: {angle_deg}°")
        print(f"   Endereços: MSW=0x{msw_addr:04X}, LSW=0x{lsw_addr:04X}")

        value_clp = int(angle_deg * 10)
        success = client.write_32bit(msw_addr, lsw_addr, value_clp)

        print(f"   Resultado: {'✓ Sucesso' if success else '✗ Falha'}")
        results_reverse.append(success)

        # Delay entre gravações
        if bend_num != 1:  # Última da lista reversa
            print(f"   Aguardando 1.5s...")
            time.sleep(1.5)

    print()
    print(f"Taxa de sucesso (ordem reversa): {sum(results_reverse)}/{len(results_reverse)} = {sum(results_reverse)/len(results_reverse)*100:.0f}%")
    print()

    # Comparação
    print("=" * 60)
    print("ANÁLISE")
    print("=" * 60)
    print()
    print(f"Ordem normal (1→2→3): {results_normal}")
    print(f"Ordem reversa (3→2→1): {results_reverse}")
    print()

    if results_normal[0] == False and sum(results_normal[1:]) > 0:
        print("⚠️ Padrão detectado: Primeira gravação sempre falha")
        print("   Hipótese: CLP precisa de inicialização/warmup")
        print("   Solução: Adicionar delay inicial de 2s antes da primeira gravação")

    if sum(results_reverse) > sum(results_normal):
        print("⚠️ Ordem reversa teve mais sucesso!")
        print("   Hipótese: Problema específico com endereço da dobra 1")
    elif sum(results_reverse) < sum(results_normal):
        print("✓ Ordem normal teve mais sucesso")
    else:
        print("= Ambas as ordens tiveram mesma taxa de sucesso")

    print()

    if hasattr(client.client, 'close'):
        client.client.close()

    return True


def test_read_verify_angle():
    """Testa leitura de ângulo após escrita para verificar."""

    print("=" * 60)
    print("TESTE: Escrita com Verificação de Leitura")
    print("=" * 60)
    print()

    client = ModbusClientWrapper(stub_mode=False)

    if not client.connected:
        print("❌ Falha ao conectar com CLP")
        return False

    print("✅ Conectado ao CLP")
    print()

    # Testar escrita com verificação
    print("--- Escrita com Verificação ---")
    print("Aguardando 2s inicial...")
    time.sleep(2.0)

    msw_addr = mm.BEND_ANGLES['BEND_1_LEFT_MSW']
    lsw_addr = mm.BEND_ANGLES['BEND_1_LEFT_LSW']
    target_angle = 90.0
    target_value = int(target_angle * 10)

    print(f"\n📝 Tentando gravar {target_angle}° na dobra 1")
    print(f"   Valor CLP: {target_value}")

    # Múltiplas tentativas com verificação
    for attempt in range(5):
        print(f"\nTentativa {attempt + 1}/5:")

        # Escrever
        write_ok = client.write_32bit(msw_addr, lsw_addr, target_value)
        print(f"  Escrita: {'✓' if write_ok else '✗'}")

        # Aguardar processamento
        time.sleep(0.3)

        # Ler de volta
        read_value = client.read_32bit(msw_addr, lsw_addr)

        if read_value is not None:
            read_angle = read_value / 10.0
            print(f"  Leitura: {read_angle}° (valor CLP: {read_value})")

            if read_value == target_value:
                print(f"  ✓ SUCESSO na tentativa {attempt + 1}!")
                break
            else:
                print(f"  ✗ Valor diferente (esperado {target_value}, leu {read_value})")
        else:
            print(f"  ✗ Falha na leitura")

        # Delay entre tentativas
        if attempt < 4:
            time.sleep(0.5)
    else:
        print("\n❌ Todas as 5 tentativas falharam")

    print()

    if hasattr(client.client, 'close'):
        client.client.close()

    return True


if __name__ == "__main__":
    print()
    print("╔════════════════════════════════════════════════════════╗")
    print("║  DIAGNÓSTICO: Velocidade e Ordem de Gravação          ║")
    print("╚════════════════════════════════════════════════════════╝")
    print()

    # Teste 1: Mudança de velocidade
    test_speed_change_detailed()

    print("\n" + "="*60 + "\n")

    # Teste 2: Ordem de gravação
    test_angle_write_order()

    print("\n" + "="*60 + "\n")

    # Teste 3: Escrita com verificação
    test_read_verify_angle()

    print()
    print("=" * 60)
    print("DIAGNÓSTICO COMPLETO")
    print("=" * 60)
    print()
