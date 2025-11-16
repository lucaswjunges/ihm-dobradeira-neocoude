#!/usr/bin/env python3
"""
TESTE DE CENÁRIO REAL DE FÁBRICA
=================================

Simula exatamente o que acontecerá na segunda-feira:
1. Conecta ao CLP via RS485
2. Lê encoder
3. Testa pressionar botões
4. Escreve ângulo de dobra
5. Testa controle de motor

Se algo falhar, você saberá ANTES de ir na fábrica.
"""
import sys
from modbus_client import ModbusClientWrapper
import modbus_map as mm
import time

def print_header(text):
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)

def test_connection():
    print_header("1. TESTE DE CONEXÃO")
    client = ModbusClientWrapper(stub_mode=False, port='/dev/ttyUSB0')

    if not client.connected:
        print("❌ FALHA CRÍTICA: Não conectou ao CLP!")
        print("   AÇÃO: Verifique cabo RS485 e CLP ligado")
        return None

    print("✅ CLP conectado")

    # Verificar estado 00BE (Modbus habilitado)
    estado_modbus = client.read_coil(mm.CRITICAL_STATES['MODBUS_SLAVE_ENABLED'])
    if not estado_modbus:
        print("❌ FALHA CRÍTICA: Estado 00BE não está ON!")
        print("   AÇÃO: Force estado 00BE=ON no ladder do CLP")
        return None

    print("✅ Estado 00BE (Modbus) ativo")
    return client

def test_encoder_reading(client):
    print_header("2. TESTE DE LEITURA DE ENCODER")

    raw = client.read_32bit(mm.ENCODER['ANGLE_MSW'], mm.ENCODER['ANGLE_LSW'])
    if raw is None:
        print("❌ FALHA: Não conseguiu ler encoder!")
        return False

    degrees = mm.clp_to_degrees(raw)
    print(f"✅ Encoder lido: {raw} raw = {degrees:.1f}°")
    return True

def test_angle_reading(client):
    print_header("3. TESTE DE LEITURA DE ÂNGULOS")

    angles = {
        'Dobra 1': (mm.BEND_ANGLES['BEND_1_LEFT_MSW'], mm.BEND_ANGLES['BEND_1_LEFT_LSW']),
        'Dobra 2': (mm.BEND_ANGLES['BEND_2_LEFT_MSW'], mm.BEND_ANGLES['BEND_2_LEFT_LSW']),
        'Dobra 3': (mm.BEND_ANGLES['BEND_3_LEFT_MSW'], mm.BEND_ANGLES['BEND_3_LEFT_LSW']),
    }

    success = True
    for name, (msw, lsw) in angles.items():
        raw = client.read_32bit(msw, lsw)
        if raw is None:
            print(f"❌ FALHA: {name} não leu")
            success = False
        else:
            degrees = mm.clp_to_degrees(raw)
            print(f"✅ {name}: {degrees:.1f}°")

    return success

def test_button_press(client):
    print_header("4. TESTE DE PRESSIONAR BOTÃO (K1)")

    print("Pressionando K1 (tecla numérica 1)...")
    success = client.press_key(mm.KEYBOARD_NUMERIC['K1'])

    if not success:
        print("❌ FALHA: Botão K1 não respondeu!")
        print("   AÇÃO: Verifique se ladder aceita comandos via Modbus")
        return False

    print("✅ Botão K1 pressionado com sucesso")
    return True

def test_angle_writing(client):
    print_header("5. TESTE DE ESCRITA DE ÂNGULO")

    # Ler ângulo atual
    raw_antes = client.read_32bit(
        mm.BEND_ANGLES['BEND_1_LEFT_MSW'],
        mm.BEND_ANGLES['BEND_1_LEFT_LSW']
    )

    if raw_antes is None:
        print("❌ FALHA: Não conseguiu ler ângulo antes de escrever")
        return False

    angle_antes = mm.clp_to_degrees(raw_antes)
    print(f"Ângulo atual Dobra 1: {angle_antes:.1f}°")

    # Escrever novo ângulo (45.0°)
    print("Escrevendo 45.0° na Dobra 1...")
    test_angle = 45.0
    test_value = mm.degrees_to_clp(test_angle)

    success = client.write_32bit(
        mm.BEND_ANGLES['BEND_1_LEFT_MSW'],
        mm.BEND_ANGLES['BEND_1_LEFT_LSW'],
        test_value
    )

    if not success:
        print("❌ FALHA: Escrita falhou!")
        return False

    # Aguardar e reler
    time.sleep(0.2)
    raw_depois = client.read_32bit(
        mm.BEND_ANGLES['BEND_1_LEFT_MSW'],
        mm.BEND_ANGLES['BEND_1_LEFT_LSW']
    )

    if raw_depois is None:
        print("❌ FALHA: Não conseguiu reler ângulo")
        return False

    angle_depois = mm.clp_to_degrees(raw_depois)
    print(f"Ângulo após escrita: {angle_depois:.1f}°")

    if abs(angle_depois - test_angle) > 0.5:
        print(f"⚠️  AVISO: Ângulo não mudou corretamente!")
        print(f"   Esperado: {test_angle:.1f}°, Lido: {angle_depois:.1f}°")
        return False

    print("✅ Escrita de ângulo funcionou!")

    # Restaurar ângulo original
    print(f"Restaurando ângulo original ({angle_antes:.1f}°)...")
    client.write_32bit(
        mm.BEND_ANGLES['BEND_1_LEFT_MSW'],
        mm.BEND_ANGLES['BEND_1_LEFT_LSW'],
        raw_antes
    )

    return True

def test_motor_control(client):
    print_header("6. TESTE DE CONTROLE DE MOTOR")

    # Ler estado atual
    s0_antes = client.read_coil(mm.DIGITAL_OUTPUTS['S0'])
    s1_antes = client.read_coil(mm.DIGITAL_OUTPUTS['S1'])

    print(f"Estado inicial: S0={s0_antes}, S1={s1_antes}")

    if s0_antes or s1_antes:
        print("⚠️  AVISO: Motor já está ligado! Desligando primeiro...")
        client.write_coil(mm.DIGITAL_OUTPUTS['S0'], False)
        client.write_coil(mm.DIGITAL_OUTPUTS['S1'], False)
        time.sleep(0.5)

    # Teste S0 (Avançar)
    print("\nTestando S0 (Avançar)...")
    print("⚠️  ATENÇÃO: Motor vai ligar por 1 segundo!")
    input("Pressione ENTER para continuar (ou Ctrl+C para cancelar)... ")

    success_s0 = client.write_coil(mm.DIGITAL_OUTPUTS['S0'], True)
    if success_s0:
        print("✅ S0 ligado")
        time.sleep(1)
        client.write_coil(mm.DIGITAL_OUTPUTS['S0'], False)
        print("✅ S0 desligado")
    else:
        print("❌ FALHA: S0 não respondeu!")
        return False

    time.sleep(1)

    # Teste S1 (Recuar)
    print("\nTestando S1 (Recuar)...")
    print("⚠️  ATENÇÃO: Motor vai ligar por 1 segundo!")
    input("Pressione ENTER para continuar (ou Ctrl+C para cancelar)... ")

    success_s1 = client.write_coil(mm.DIGITAL_OUTPUTS['S1'], True)
    if success_s1:
        print("✅ S1 ligado")
        time.sleep(1)
        client.write_coil(mm.DIGITAL_OUTPUTS['S1'], False)
        print("✅ S1 desligado")
    else:
        print("❌ FALHA: S1 não respondeu!")
        return False

    print("\n✅ Controle de motor funcionando!")
    return True

def main():
    print("\n" + "#" * 60)
    print("#  TESTE DE CENÁRIO REAL - FÁBRICA")
    print("#  Segunda-feira você vai fazer EXATAMENTE isso")
    print("#" * 60)

    results = {
        'Conexão': False,
        'Encoder': False,
        'Ângulos (leitura)': False,
        'Botões': False,
        'Ângulos (escrita)': False,
        'Motor': False
    }

    # Teste 1: Conexão
    client = test_connection()
    if client is None:
        print("\n❌ TESTE ABORTADO: Sem conexão com CLP")
        print_summary(results)
        sys.exit(1)
    results['Conexão'] = True

    # Teste 2: Encoder
    results['Encoder'] = test_encoder_reading(client)

    # Teste 3: Ângulos (leitura)
    results['Ângulos (leitura)'] = test_angle_reading(client)

    # Teste 4: Botões
    results['Botões'] = test_button_press(client)

    # Teste 5: Ângulos (escrita)
    results['Ângulos (escrita)'] = test_angle_writing(client)

    # Teste 6: Motor (opcional, perigoso)
    print("\n" + "⚠️ " * 20)
    print("TESTE DE MOTOR: Vai ligar o motor da máquina!")
    print("Se não estiver seguro, pressione Ctrl+C agora")
    print("⚠️ " * 20)

    try:
        results['Motor'] = test_motor_control(client)
    except KeyboardInterrupt:
        print("\n⚠️  Teste de motor cancelado pelo usuário")
        results['Motor'] = None

    # Fechar conexão
    client.close()

    # Resumo
    print_summary(results)

def print_summary(results):
    print("\n" + "=" * 60)
    print("  RESUMO DOS TESTES")
    print("=" * 60)

    for test, result in results.items():
        if result is True:
            status = "✅ PASSOU"
        elif result is False:
            status = "❌ FALHOU"
        else:
            status = "⊘  PULADO"

        print(f"{status}  {test}")

    total = len([r for r in results.values() if r is True])
    failed = len([r for r in results.values() if r is False])

    print("\n" + "=" * 60)
    if failed == 0:
        print("🎉 TUDO FUNCIONANDO! Você está pronto para segunda-feira.")
    else:
        print(f"⚠️  {failed} TESTE(S) FALHARAM!")
        print("   AÇÃO: Corrija os problemas antes de ir na fábrica!")
    print("=" * 60 + "\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Teste interrompido pelo usuário")
        sys.exit(1)
