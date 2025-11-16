#!/usr/bin/env python3
"""
🤖 TESTE - ROBÔ DE BOTÕES PARA PROGRAMAR ÂNGULOS

Testa se conseguimos programar ângulos simulando a sequência exata
que o operador faria no painel físico.

HIPÓTESE: Se os botões K0-K9, EDIT, ENTER já funcionam via Modbus,
          podemos simular a IHM física completamente!
"""

import sys
import time
from modbus_client import ModbusClientWrapper
import modbus_map as mm

# Tempos de espera (ajustar se necessário)
KEY_PRESS_DURATION = 0.1  # Duração do pulso (100ms)
AFTER_KEY_DELAY = 0.3     # Delay após cada tecla
AFTER_EDIT_DELAY = 0.5    # Delay após EDIT
AFTER_ENTER_DELAY = 1.0   # Delay após ENTER para CLP processar

def press_key(client, coil_address, label=""):
    """Simula pressão de botão (pulso de 100ms)"""
    print(f"  → Pressionando {label} (coil 0x{coil_address:04X})...")

    # Pulso: ON → Delay → OFF
    client.write_coil(coil_address, True)
    time.sleep(KEY_PRESS_DURATION)
    client.write_coil(coil_address, False)

    time.sleep(AFTER_KEY_DELAY)


def digit_to_key_address(digit):
    """Converte dígito (0-9) para endereço do botão K0-K9"""
    if digit == 0:
        return mm.KEYBOARD_NUMERIC['K0']  # 0x00A9
    else:
        return mm.KEYBOARD_NUMERIC[f'K{digit}']  # 0x00A0 - 0x00A8


def program_angle_via_buttons(client, bend_number, angle_degrees):
    """
    Programa ângulo simulando sequência de botões da IHM física.

    Sequência esperada (baseada em manual NEOCOUDE):
    1. Pressionar K1/K2/K3 (selecionar dobra)
    2. Pressionar EDIT (entrar modo edição)
    3. Digitar ângulo (ex: 1, 2, 5 para 125°)
    4. Pressionar ENTER (confirmar)

    Args:
        bend_number: 1, 2 ou 3
        angle_degrees: Ângulo em graus (ex: 90, 125, 45)

    Returns:
        True se programou com sucesso, False caso contrário
    """
    print(f"\n{'='*60}")
    print(f"🤖 ROBÔ - Programar Dobra {bend_number} = {angle_degrees}°")
    print(f"{'='*60}\n")

    # 1. Selecionar dobra (K1, K2 ou K3)
    bend_keys = {
        1: mm.KEYBOARD_NUMERIC['K1'],
        2: mm.KEYBOARD_NUMERIC['K2'],
        3: mm.KEYBOARD_NUMERIC['K3'],
    }

    if bend_number not in bend_keys:
        print(f"❌ Dobra inválida: {bend_number}")
        return False

    print(f"1️⃣ Selecionando dobra {bend_number}...")
    press_key(client, bend_keys[bend_number], f"K{bend_number}")

    # 2. Entrar modo edição
    print(f"\n2️⃣ Entrando modo edição...")
    press_key(client, mm.KEYBOARD_FUNCTION['EDIT'], "EDIT")
    time.sleep(AFTER_EDIT_DELAY)  # CLP precisa mudar de tela

    # 3. Digitar ângulo (ex: 125 → "1", "2", "5")
    print(f"\n3️⃣ Digitando ângulo {angle_degrees}...")
    angle_str = str(int(angle_degrees))  # Garantir inteiro

    for i, digit_char in enumerate(angle_str):
        digit = int(digit_char)
        key_addr = digit_to_key_address(digit)
        press_key(client, key_addr, f"K{digit}")

    # 4. Confirmar com ENTER
    print(f"\n4️⃣ Confirmando com ENTER...")
    press_key(client, mm.KEYBOARD_FUNCTION['ENTER'], "ENTER")
    time.sleep(AFTER_ENTER_DELAY)  # CLP precisa gravar

    # 5. Verificar se programou
    print(f"\n5️⃣ Verificando se ângulo foi gravado...")

    # Mapear dobra para endereços Modbus
    bend_addresses = {
        1: (mm.BEND_ANGLES['BEND_1_LEFT_MSW'], mm.BEND_ANGLES['BEND_1_LEFT_LSW']),
        2: (mm.BEND_ANGLES['BEND_2_LEFT_MSW'], mm.BEND_ANGLES['BEND_2_LEFT_LSW']),
        3: (mm.BEND_ANGLES['BEND_3_LEFT_MSW'], mm.BEND_ANGLES['BEND_3_LEFT_LSW']),
    }

    msw_addr, lsw_addr = bend_addresses[bend_number]

    # Ler ângulo atual
    angle_read = client.read_32bit(msw_addr, lsw_addr)
    angle_read_degrees = angle_read / 10.0 if angle_read else None

    print(f"\n📊 Resultado:")
    print(f"   Esperado: {angle_degrees}°")
    print(f"   Lido:     {angle_read_degrees}°")

    # Tolerância de ±0.5°
    if angle_read_degrees and abs(angle_read_degrees - angle_degrees) < 0.5:
        print(f"\n✅ SUCESSO! Ângulo programado corretamente via robô!")
        return True
    else:
        print(f"\n❌ FALHA! Ângulo não foi programado (ou foi sobrescrito).")
        return False


def test_robot_sequences():
    """Bateria de testes com diferentes ângulos"""
    print("\n" + "="*60)
    print("🧪 BATERIA DE TESTES - ROBÔ DE BOTÕES")
    print("="*60)

    client = ModbusClientWrapper(port='/dev/ttyUSB0', stub_mode=False)

    if not client.connected:
        print("❌ CLP não conectado!")
        return 1

    print("✅ CLP conectado\n")

    # Testes a executar
    test_cases = [
        (1, 90),   # Dobra 1: 90°
        (2, 125),  # Dobra 2: 125°
        (3, 45),   # Dobra 3: 45°
    ]

    results = []

    for bend, angle in test_cases:
        success = program_angle_via_buttons(client, bend, angle)
        results.append((bend, angle, success))

        # Delay entre testes
        print("\n⏳ Aguardando 3s antes do próximo teste...\n")
        time.sleep(3)

    # Resumo final
    print("\n" + "="*60)
    print("📋 RESUMO DOS TESTES")
    print("="*60)

    for bend, angle, success in results:
        status = "✅ OK" if success else "❌ FALHOU"
        print(f"Dobra {bend} ({angle}°): {status}")

    success_count = sum(1 for _, _, s in results if s)
    total = len(results)

    print(f"\n🎯 Taxa de sucesso: {success_count}/{total} ({success_count/total*100:.0f}%)")

    client.close()

    return 0 if success_count == total else 1


def test_single_angle():
    """Teste rápido com um único ângulo"""
    print("\n" + "="*60)
    print("⚡ TESTE RÁPIDO - UM ÚNICO ÂNGULO")
    print("="*60)

    client = ModbusClientWrapper(port='/dev/ttyUSB0', stub_mode=False)

    if not client.connected:
        print("❌ CLP não conectado!")
        return 1

    # Testar: Dobra 1 = 90°
    success = program_angle_via_buttons(client, 1, 90)

    client.close()

    return 0 if success else 1


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Testar programação de ângulos via robô de botões')
    parser.add_argument('--full', action='store_true', help='Executar bateria completa de testes')
    parser.add_argument('--bend', type=int, choices=[1,2,3], help='Testar dobra específica')
    parser.add_argument('--angle', type=float, help='Ângulo a programar (usado com --bend)')

    args = parser.parse_args()

    try:
        if args.full:
            # Bateria completa
            sys.exit(test_robot_sequences())

        elif args.bend and args.angle:
            # Teste customizado
            client = ModbusClientWrapper(port='/dev/ttyUSB0', stub_mode=False)

            if not client.connected:
                print("❌ CLP não conectado!")
                sys.exit(1)

            success = program_angle_via_buttons(client, args.bend, args.angle)
            client.close()

            sys.exit(0 if success else 1)

        else:
            # Teste rápido padrão
            sys.exit(test_single_angle())

    except KeyboardInterrupt:
        print("\n\n⚠️ Teste interrompido pelo usuário!")
        sys.exit(1)

    except Exception as e:
        print(f"\n\n❌ ERRO: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
