#!/usr/bin/env python3
"""
Script de Teste Completo - Ângulos de Dobra
Versão: 1.0 - Validação área 0x0A00/0x0B00
Data: 18/Novembro/2025

Testa:
1. Escrita na área MODBUS INPUT (0x0A00) com triggers
2. Leitura da área SCADA (0x0B00) - espelho read-only
3. Validação do fluxo completo: IHM → ROT5 → PRINCIPAL → SCADA
"""

import sys
import time
sys.path.insert(0, '/home/lucas-junges/Documents/clientes/w&co/ihm_esp32')

from modbus_client_esp32 import ModbusClientWrapper
import modbus_map as mm


def test_write_angles(client):
    """Testa escrita de ângulos via área 0x0A00"""
    print("\n" + "="*70)
    print("TESTE 1: ESCRITA DE ÂNGULOS (área 0x0A00 + triggers)")
    print("="*70)

    test_angles = {
        1: 90.5,   # Dobra 1: 90.5°
        2: 120.0,  # Dobra 2: 120.0°
        3: 45.8,   # Dobra 3: 45.8°
    }

    for bend_num, angle in test_angles.items():
        print(f"\n📝 Gravando Dobra {bend_num}: {angle}°")
        success = client.write_bend_angle(bend_num, angle)

        if success:
            print(f"   ✅ Sucesso! Dobra {bend_num} = {angle}°")
        else:
            print(f"   ❌ FALHA ao gravar Dobra {bend_num}")

        time.sleep(0.5)  # Pausa entre escritas


def test_read_angles(client):
    """Testa leitura de ângulos via área SCADA 0x0B00"""
    print("\n" + "="*70)
    print("TESTE 2: LEITURA DE ÂNGULOS (área SCADA 0x0B00)")
    print("="*70)

    for bend_num in [1, 2, 3]:
        print(f"\n📖 Lendo Dobra {bend_num}...")
        angle = client.read_bend_angle(bend_num)

        if angle is not None:
            print(f"   ✅ Dobra {bend_num} = {angle:.1f}°")
        else:
            print(f"   ❌ FALHA ao ler Dobra {bend_num}")

        time.sleep(0.3)


def test_write_read_cycle(client):
    """Testa ciclo completo: escreve → lê → valida"""
    print("\n" + "="*70)
    print("TESTE 3: CICLO COMPLETO (escrita + leitura + validação)")
    print("="*70)

    test_cases = [
        (1, 135.0),
        (2, 90.0),
        (3, 180.5),
    ]

    for bend_num, expected_angle in test_cases:
        print(f"\n🔄 Testando Dobra {bend_num}: {expected_angle}°")

        # 1. Escreve
        print(f"   1️⃣ Gravando {expected_angle}°...")
        write_ok = client.write_bend_angle(bend_num, expected_angle)

        if not write_ok:
            print(f"   ❌ Erro na escrita - abortando teste Dobra {bend_num}")
            continue

        # 2. Aguarda propagação (ROT5 copia 0x0A00→0x0840→0x0B00)
        time.sleep(0.5)

        # 3. Lê de volta
        print(f"   2️⃣ Lendo de volta...")
        read_angle = client.read_bend_angle(bend_num)

        if read_angle is None:
            print(f"   ❌ Erro na leitura - abortando teste Dobra {bend_num}")
            continue

        # 4. Valida
        tolerance = 0.2  # 0.2° de tolerância (2 unidades CLP)
        diff = abs(read_angle - expected_angle)

        print(f"   3️⃣ Validando...")
        print(f"      Esperado: {expected_angle:.1f}°")
        print(f"      Lido:     {read_angle:.1f}°")
        print(f"      Diferença: {diff:.1f}°")

        if diff <= tolerance:
            print(f"   ✅ PASSOU! (diff={diff:.1f}° < {tolerance}°)")
        else:
            print(f"   ❌ FALHOU! (diff={diff:.1f}° > {tolerance}°)")


def test_direct_register_access(client):
    """Testa acesso direto aos registros (debug)"""
    print("\n" + "="*70)
    print("TESTE 4: ACESSO DIRETO A REGISTROS (debug)")
    print("="*70)

    # Área MODBUS INPUT (0x0A00)
    print("\n📦 Área MODBUS INPUT (0x0A00):")
    for i, bend_num in enumerate([1, 2, 3]):
        base = 0x0A00 + (i * 4)
        msw = client.read_register(base)
        lsw = client.read_register(base + 2)

        if msw is not None and lsw is not None:
            value = (msw << 16) | lsw
            degrees = value / 10.0
            print(f"   Dobra {bend_num}: 0x{base:04X}/0x{base+2:04X} = MSW:{msw} LSW:{lsw} → {degrees:.1f}°")
        else:
            print(f"   Dobra {bend_num}: 0x{base:04X}/0x{base+2:04X} = ERRO LEITURA")

    # Área SHADOW (0x0840 - oficiais do ladder)
    print("\n👻 Área SHADOW (0x0840 - usada pelo PRINCIPAL.lad):")
    shadow_addrs = {
        1: (0x0840, 0x0842),  # LSW, MSW
        2: (0x0846, 0x0848),
        3: (0x0850, 0x0852),
    }

    for bend_num, (lsw_addr, msw_addr) in shadow_addrs.items():
        lsw = client.read_register(lsw_addr)
        msw = client.read_register(msw_addr)

        if lsw is not None and msw is not None:
            value = (msw << 16) | lsw
            degrees = value / 10.0
            print(f"   Dobra {bend_num}: 0x{lsw_addr:04X}/0x{msw_addr:04X} = LSW:{lsw} MSW:{msw} → {degrees:.1f}°")
        else:
            print(f"   Dobra {bend_num}: 0x{lsw_addr:04X}/0x{msw_addr:04X} = ERRO LEITURA")

    # Área SCADA (0x0B00 - espelho read-only)
    print("\n🖥️  Área SCADA (0x0B00 - espelho para IHM Web):")
    for i, bend_num in enumerate([1, 2, 3]):
        base = 0x0B00 + (i * 4)
        lsw = client.read_register(base)
        msw = client.read_register(base + 2)

        if lsw is not None and msw is not None:
            value = (msw << 16) | lsw
            degrees = value / 10.0
            print(f"   Dobra {bend_num}: 0x{base:04X}/0x{base+2:04X} = LSW:{lsw} MSW:{msw} → {degrees:.1f}°")
        else:
            print(f"   Dobra {bend_num}: 0x{base:04X}/0x{base+2:04X} = ERRO LEITURA")


def main():
    print("\n" + "="*70)
    print("TESTE COMPLETO - ÂNGULOS DE DOBRA")
    print("="*70)
    print("Validando fluxo: IHM → 0x0A00 → ROT5 → 0x0840 → 0x0B00")
    print("="*70)

    # Conecta ao CLP (use stub_mode=False para CLP real)
    print("\n🔌 Conectando ao CLP...")

    # IMPORTANTE: Trocar stub_mode=False quando o CLP estiver conectado!
    client = ModbusClientWrapper(stub_mode=False, slave_id=1)

    if not client.connected:
        print("❌ ERRO: Não foi possível conectar ao CLP!")
        print("   Verifique:")
        print("   1. CLP ligado")
        print("   2. RS485 conectado (GPIO17/16 no ESP32)")
        print("   3. Baudrate 57600")
        print("   4. Estado 0x00BE (190) = ON no ladder")
        return

    print("✅ CLP conectado!\n")

    # Executa testes
    try:
        # Teste 1: Escrita
        test_write_angles(client)

        # Teste 2: Leitura
        test_read_angles(client)

        # Teste 3: Ciclo completo
        test_write_read_cycle(client)

        # Teste 4: Acesso direto (debug)
        test_direct_register_access(client)

    except KeyboardInterrupt:
        print("\n\n⚠️  Teste interrompido pelo usuário")
    except Exception as e:
        print(f"\n\n❌ ERRO durante teste: {e}")
        import traceback
        traceback.print_exc()

    print("\n" + "="*70)
    print("TESTE CONCLUÍDO")
    print("="*70)


if __name__ == '__main__':
    main()
