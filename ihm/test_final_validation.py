#!/usr/bin/env python3
"""
TESTE DE VALIDAÇÃO FINAL - IHM WEB NEOCOUDE-HD-15
Executa todos os testes críticos para validação de entrega
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from modbus_client import ModbusClientWrapper
import time

def print_test(name):
    print(f"\n{'═' * 70}")
    print(f"  TESTE: {name}")
    print(f"{'═' * 70}")

def print_result(success, message):
    icon = "✅" if success else "❌"
    print(f"{icon} {message}")

def test_connection(client):
    """Teste 1: Conexão Modbus"""
    print_test("1. CONEXÃO MODBUS")
    connected = client.connected and client.client and client.client.is_socket_open()
    print_result(connected, f"Conexão em /dev/ttyUSB0 @ 57600 bps")
    return connected

def test_encoder_read(client):
    """Teste 2: Leitura de Encoder"""
    print_test("2. LEITURA DE ENCODER")

    msw = client.read_register(0x04D6)
    lsw = client.read_register(0x04D7)

    if msw is not None and lsw is not None:
        value_32bit = (msw << 16) | lsw
        angle = value_32bit / 10.0
        print_result(True, f"Encoder: {angle:.1f}° (raw: {value_32bit})")
        return True
    else:
        print_result(False, "Erro na leitura do encoder")
        return False

def test_mode_change(client):
    """Teste 3: Mudança de Modo (MANUAL ↔ AUTO)"""
    print_test("3. MUDANÇA DE MODO (WORKAROUND DIRETO)")

    # Estado inicial
    MODE_BIT = 0x02FF
    initial_mode = client.read_coil(MODE_BIT)
    print(f"  Modo inicial: {'AUTO' if initial_mode else 'MANUAL'}")

    # Tentar mudar para AUTO
    print("  Mudando para AUTO...")
    success_auto = client.change_mode_direct(to_auto=True)
    time.sleep(0.3)
    mode_auto = client.read_coil(MODE_BIT)

    if mode_auto:
        print_result(True, "Modo AUTO ativado")
    else:
        print_result(False, "Falha ao ativar AUTO")
        return False

    # Voltar para MANUAL
    print("  Voltando para MANUAL...")
    success_manual = client.change_mode_direct(to_auto=False)
    time.sleep(0.3)
    mode_manual = client.read_coil(MODE_BIT)

    if not mode_manual:
        print_result(True, "Modo MANUAL restaurado")
    else:
        print_result(False, "Falha ao voltar para MANUAL")
        return False

    return True

def test_angle_write_read(client):
    """Teste 4: Escrita e Leitura de Ângulo"""
    print_test("4. ESCRITA E LEITURA DE ÂNGULO")

    test_angle = 90.0
    bend_num = 1
    direction = 'left'
    addr = 0x0842  # Dobra 1 Esquerda

    # Ler valor original
    original = client.read_register(addr)
    print(f"  Ângulo original: {original/10.0 if original else 'N/A'}°")

    # Escrever teste
    print(f"  Escrevendo {test_angle}°...")
    success_write = client.write_angle(bend_num, direction, test_angle)

    if not success_write:
        print_result(False, "Erro na escrita")
        return False

    # Verificar leitura
    time.sleep(0.2)
    readback = client.read_register(addr)

    if readback is not None:
        angle_read = readback / 10.0
        if abs(angle_read - test_angle) < 0.1:
            print_result(True, f"Ângulo lido: {angle_read}° (esperado: {test_angle}°)")
            success = True
        else:
            print_result(False, f"Ângulo incorreto: {angle_read}° (esperado: {test_angle}°)")
            success = False
    else:
        print_result(False, "Erro na leitura de verificação")
        success = False

    # Restaurar original
    if original is not None:
        client.write_register(addr, original)
        print(f"  Ângulo original restaurado")

    return success

def test_digital_io(client):
    """Teste 5: Leitura de I/O Digital"""
    print_test("5. LEITURA DE I/O DIGITAL")

    # Ler E0-E7
    inputs_ok = 0
    for i in range(8):
        addr = 0x0100 + i
        value = client.read_coil(addr)
        if value is not None:
            inputs_ok += 1

    # Ler S0-S7 (S0 pode falhar, é conhecido)
    outputs_ok = 0
    for i in range(8):
        addr = 0x0180 + i
        value = client.read_coil(addr)
        if value is not None:
            outputs_ok += 1

    print_result(inputs_ok >= 7, f"Entradas E0-E7: {inputs_ok}/8 lidas")
    print_result(outputs_ok >= 7, f"Saídas S0-S7: {outputs_ok}/8 lidas (S0 pode falhar)")

    return inputs_ok >= 7 and outputs_ok >= 7

def test_supervision_area(client):
    """Teste 6: Área de Supervisão"""
    print_test("6. ÁREA DE SUPERVISÃO")

    registers = {
        'SCREEN_NUM': 0x0940,
        'MODE_STATE': 0x0946,
        'BEND_CURRENT': 0x0948,
        'SPEED_CLASS': 0x094C,
    }

    success_count = 0
    for name, addr in registers.items():
        value = client.read_register(addr)
        if value is not None:
            print(f"  {name:14s} (0x{addr:04X}): {value}")
            success_count += 1
        else:
            print(f"  {name:14s} (0x{addr:04X}): ❌ Erro")

    print_result(success_count == len(registers), f"{success_count}/{len(registers)} registros lidos")
    return success_count == len(registers)

def main():
    print("=" * 70)
    print("  VALIDAÇÃO FINAL - IHM WEB NEOCOUDE-HD-15")
    print("  Engenharia de Controle e Automação")
    print("=" * 70)

    client = ModbusClientWrapper(port='/dev/ttyUSB0', stub_mode=False)

    results = {}

    try:
        results['connection'] = test_connection(client)
        if not results['connection']:
            print("\n❌ ABORTADO: Sem conexão Modbus")
            return

        results['encoder'] = test_encoder_read(client)
        results['mode'] = test_mode_change(client)
        results['angle'] = test_angle_write_read(client)
        results['io'] = test_digital_io(client)
        results['supervision'] = test_supervision_area(client)

        # Resumo Final
        print("\n" + "=" * 70)
        print("  RESUMO FINAL")
        print("=" * 70)

        total = len(results)
        passed = sum(1 for v in results.values() if v)

        for test_name, passed_test in results.items():
            icon = "✅" if passed_test else "❌"
            print(f"{icon} {test_name.upper():15s}: {'PASSOU' if passed_test else 'FALHOU'}")

        print("\n" + "-" * 70)
        print(f"  RESULTADO: {passed}/{total} testes passaram ({passed*100//total}%)")
        print("-" * 70)

        if passed == total:
            print("\n🎉 SISTEMA PRONTO PARA ENTREGA!")
        elif passed >= total * 0.8:
            print("\n⚠️  SISTEMA FUNCIONAL COM LIMITAÇÕES CONHECIDAS")
        else:
            print("\n❌ SISTEMA REQUER CORREÇÕES")

    except Exception as e:
        print(f"\n❌ Erro durante validação: {e}")
        import traceback
        traceback.print_exc()
    finally:
        client.close()

if __name__ == '__main__':
    main()
