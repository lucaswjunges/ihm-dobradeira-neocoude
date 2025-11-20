#!/usr/bin/env python3
"""
Teste: Simulação de IHM Original
================================

Como engenheiro sênior, vou simular o OPERADOR REAL usando o painel físico:

SEQUÊNCIA ORIGINAL (painel físico):
1. Pressiona K1 → Vai para Tela 4 (Dobra 1)
2. Pressiona EDIT → Ativa modo edição
3. Digita 9-0-ENTER → Programa 90°
4. Aguarda confirmação

SEQUÊNCIA VIA MODBUS (nossa implementação):
1. Force coil K1 (100ms pulse)
2. Aguarda 200ms (tela carregar)
3. Force coil EDIT (100ms pulse)
4. Aguarda 200ms (modo edit ativar)
5. Force coil K9 (100ms pulse)
6. Aguarda 100ms
7. Force coil K0 (100ms pulse)
8. Aguarda 100ms
9. Force coil ENTER (100ms pulse)
10. Aguarda 500ms (CLP processar e gravar)
11. Lê valor para confirmar
"""

import time
from modbus_client import ModbusClientWrapper

def print_step(step, desc):
    print(f"\n[{step}] {desc}")

def simulate_key_sequence(client, key_sequence, delay_ms=120):
    """
    Simula sequência de teclas (como operador real)

    Args:
        key_sequence: Lista de endereços de coils
        delay_ms: Delay entre teclas (padrão 120ms)
    """
    for i, key_addr in enumerate(key_sequence):
        print(f"  Tecla {i+1}: 0x{key_addr:04X}...", end='')

        # Pulso ON
        client.write_coil(key_addr, True)
        time.sleep(0.1)  # 100ms ON

        # Pulso OFF
        client.write_coil(key_addr, False)
        time.sleep(delay_ms / 1000.0)  # Delay entre teclas

        print(" OK")


def test_program_angle_via_ihm(client):
    """
    Testa programação de ângulo simulando IHM física
    """
    print("=" * 70)
    print("TESTE: PROGRAMAR ÂNGULO 90° VIA SIMULAÇÃO DE IHM")
    print("=" * 70)

    # Endereços de teclas
    KEY_K1 = 0x00A0  # 160 - Vai para tela 4
    KEY_K9 = 0x00A8  # 168
    KEY_K0 = 0x00A9  # 169
    KEY_EDIT = 0x0026  # 38
    KEY_ENTER = 0x0025  # 37

    # Endereços de ângulos (testados empiricamente)
    BEND_1_ESQ_MSW = 0x0840
    BEND_1_ESQ_LSW = 0x0842

    # 1. Ler valor ANTES
    print_step(1, "Lendo ângulo ANTES da simulação...")
    value_before = client.read_32bit(BEND_1_ESQ_MSW, BEND_1_ESQ_LSW)
    if value_before:
        print(f"   Ângulo ANTES: {value_before/10.0}° (raw={value_before})")
    else:
        print("   ⚠️ Não conseguiu ler valor inicial")

    # 2. Simular operador pressionando K1 (ir para tela 4)
    print_step(2, "Pressionando K1 (ir para Tela 4 - Dobra 1)...")
    client.press_key(KEY_K1, hold_ms=100)
    time.sleep(0.3)  # Aguarda tela carregar (300ms)

    # 3. Ativar modo EDIT
    print_step(3, "Pressionando EDIT (ativar modo edição)...")
    client.press_key(KEY_EDIT, hold_ms=100)
    time.sleep(0.3)  # Aguarda modo edit ativar

    # 4. Digitar "90" (K9 + K0)
    print_step(4, "Digitando '90' no teclado numérico...")
    simulate_key_sequence(client, [KEY_K9, KEY_K0], delay_ms=150)

    # 5. Confirmar com ENTER
    print_step(5, "Pressionando ENTER (confirmar)...")
    client.press_key(KEY_ENTER, hold_ms=100)
    time.sleep(0.5)  # Aguarda CLP gravar (500ms)

    # 6. Ler valor DEPOIS
    print_step(6, "Lendo ângulo DEPOIS da simulação...")
    value_after = client.read_32bit(BEND_1_ESQ_MSW, BEND_1_ESQ_LSW)

    if value_after:
        print(f"   Ângulo DEPOIS: {value_after/10.0}° (raw={value_after})")
    else:
        print("   ❌ Não conseguiu ler valor final")
        return False

    # 7. Validar
    print_step(7, "Validando resultado...")

    esperado = 900  # 90.0° → 900 units
    tolerancia = 50  # 5° de tolerância

    if abs(value_after - esperado) <= tolerancia:
        print(f"\n   ✅ SUCESSO! Ângulo programado: {value_after/10.0}°")
        print(f"   📌 Simulação de IHM FUNCIONOU!")
        print(f"   🏭 Sistema pronto para substituir painel físico!")
        return True
    else:
        print(f"\n   ❌ FALHOU! Esperado ~90°, obtido {value_after/10.0}°")
        print(f"   Diferença: {abs(value_after - esperado)/10.0}°")

        if value_after == value_before:
            print(f"\n   ⚠️ Valor não mudou! Possíveis causas:")
            print(f"   1. Sequência de teclas incorreta")
            print(f"   2. Timing entre teclas muito rápido/lento")
            print(f"   3. Ladder requer condições adicionais")
            print(f"   4. Modo EDIT não ativou corretamente")

        return False


def test_program_bend2_directly(client):
    """
    Testa programação direta na Dobra 2 (que sabemos que funciona)
    """
    print("\n" + "=" * 70)
    print("TESTE DE CONTROLE: PROGRAMAR DOBRA 2 DIRETAMENTE")
    print("=" * 70)

    BEND_2_ESQ_MSW = 0x0848
    BEND_2_ESQ_LSW = 0x084A

    print("\n[INFO] Dobra 2 Esquerda: Sabemos que aceita escrita direta")

    # Ler valor antes
    value_before = client.read_32bit(BEND_2_ESQ_MSW, BEND_2_ESQ_LSW)
    print(f"   Ângulo ANTES: {value_before/10.0 if value_before else 'N/A'}°")

    # Escrever 120.0°
    test_value = 1200  # 120.0°
    print(f"\n   Escrevendo {test_value/10.0}°...")
    success = client.write_32bit(BEND_2_ESQ_MSW, BEND_2_ESQ_LSW, test_value)

    if not success:
        print("   ❌ Escrita falhou!")
        return False

    time.sleep(0.2)

    # Ler valor depois
    value_after = client.read_32bit(BEND_2_ESQ_MSW, BEND_2_ESQ_LSW)
    print(f"   Ângulo DEPOIS: {value_after/10.0 if value_after else 'N/A'}°")

    if value_after and abs(value_after - test_value) < 50:
        print(f"\n   ✅ DOBRA 2 FUNCIONA! (confirmado novamente)")

        # Restaurar valor original
        if value_before:
            client.write_32bit(BEND_2_ESQ_MSW, BEND_2_ESQ_LSW, value_before)

        return True
    else:
        print(f"\n   ❌ Dobra 2 falhou (inesperado!)")
        return False


def main():
    print("\n" + "🔬" * 35)
    print("  TESTE DE SIMULAÇÃO DE IHM FÍSICA")
    print("  Engenheiro: Automação Sênior")
    print("🔬" * 35 + "\n")

    client = ModbusClientWrapper(stub_mode=False, port='/dev/ttyUSB0')

    if not client.connected:
        print("❌ CLP não conectado!")
        return 1

    print("✓ Conectado ao CLP Atos MPC4004\n")

    # Teste 1: Simulação de IHM para Dobra 1
    result1 = test_program_angle_via_ihm(client)

    time.sleep(1)

    # Teste 2: Controle - Dobra 2 direta
    result2 = test_program_bend2_directly(client)

    client.close()

    # Relatório final
    print("\n" + "=" * 70)
    print("RELATÓRIO FINAL")
    print("=" * 70)

    print(f"\n  Simulação IHM (Dobra 1): {'✅ PASSOU' if result1 else '❌ FALHOU'}")
    print(f"  Escrita Direta (Dobra 2): {'✅ PASSOU' if result2 else '❌ FALHOU'}")

    if result1:
        print("\n  🎉 SUCESSO! Sistema pode substituir IHM física!")
        print("  ✅ Programação de ângulos via simulação de teclas funciona!")
        return 0
    elif result2:
        print("\n  ⚠️ PARCIAL: Escrita direta funciona, simulação de teclas não")
        print("  💡 RECOMENDAÇÃO: Usar escrita direta nos registros que funcionam")
        print("     - Dobra 2 Esq: 0x0848/0x084A")
        print("     - Dobra 2 Dir: 0x084C/0x084E")
        print("     - Dobra 3 Dir: 0x0854/0x0856")
        return 0
    else:
        print("\n  ❌ FALHA TOTAL: Nenhum método funcionou")
        return 1


if __name__ == '__main__':
    exit(main())
