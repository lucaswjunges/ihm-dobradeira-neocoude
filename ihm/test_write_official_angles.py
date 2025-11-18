#!/usr/bin/env python3
"""
Teste de Escrita nos Ângulos Oficiais do CLP
=============================================

Testa se é possível escrever valores nos registros oficiais:
- Área 0x0500-0x0504 (setpoints - 16-bit)
- Área 0x0840-0x0852 (shadow - 32-bit MSW/LSW)

O teste:
1. Lê valores atuais
2. Escreve valores de teste
3. Lê novamente para confirmar
4. Restaura valores originais
"""

import sys
import time
from modbus_client import ModbusClientWrapper
import modbus_map as mm

def test_write_16bit_area():
    """Testa escrita na área 0x0500 (16-bit)."""
    print("=" * 70)
    print("  TESTE 1: ÁREA 0x0500 (Setpoints Oficiais - 16-bit)")
    print("=" * 70)
    print()

    client = ModbusClientWrapper(stub_mode=False, port='/dev/ttyUSB0')

    if not client.connected:
        print("❌ CLP não conectado")
        return False

    print("✅ Conectado ao CLP")
    print()

    # 1. Ler valores originais
    print("📖 ETAPA 1: Lendo valores ORIGINAIS...")
    print("-" * 70)

    original_values = {}
    for bend_num in [1, 2, 3]:
        addr = mm.BEND_ANGLES[f'BEND_{bend_num}_SETPOINT']
        value = client.read_register(addr)

        if value is not None:
            degrees = value / 10.0
            original_values[bend_num] = value
            print(f"  0x{addr:04X} - Dobra {bend_num}: {value:5d} ({degrees:6.1f}°)")
        else:
            print(f"  0x{addr:04X} - Dobra {bend_num}: ERRO AO LER")
            client.disconnect()
            return False

    print()

    # 2. Escrever valores de teste
    print("✏️  ETAPA 2: Escrevendo valores DE TESTE...")
    print("-" * 70)

    test_values = {
        1: 900,   # 90.0°
        2: 1200,  # 120.0°
        3: 450    # 45.0°
    }

    write_success = {}
    for bend_num, test_value in test_values.items():
        addr = mm.BEND_ANGLES[f'BEND_{bend_num}_SETPOINT']
        degrees = test_value / 10.0

        print(f"  Escrevendo em 0x{addr:04X} - Dobra {bend_num}: {test_value} ({degrees:.1f}°)... ", end='', flush=True)

        success = client.write_register(addr, test_value)

        if success:
            print("✅ OK")
            write_success[bend_num] = True
        else:
            print("❌ FALHA")
            write_success[bend_num] = False

    print()

    # Aguarda CLP processar
    print("⏳ Aguardando 500ms para CLP processar...")
    time.sleep(0.5)
    print()

    # 3. Ler de volta para verificar
    print("🔍 ETAPA 3: Verificando se valores foram GRAVADOS...")
    print("-" * 70)

    verification_ok = True
    for bend_num, expected_value in test_values.items():
        addr = mm.BEND_ANGLES[f'BEND_{bend_num}_SETPOINT']
        read_value = client.read_register(addr)

        if read_value is not None:
            degrees = read_value / 10.0
            expected_degrees = expected_value / 10.0

            match = (read_value == expected_value)
            status = "✅" if match else "❌"

            print(f"  {status} 0x{addr:04X} - Dobra {bend_num}: {read_value:5d} ({degrees:6.1f}°) - Esperado: {expected_value} ({expected_degrees:.1f}°)")

            if not match:
                verification_ok = False
        else:
            print(f"  ❌ 0x{addr:04X} - Dobra {bend_num}: ERRO AO LER")
            verification_ok = False

    print()

    # 4. Restaurar valores originais
    print("♻️  ETAPA 4: Restaurando valores ORIGINAIS...")
    print("-" * 70)

    for bend_num, original_value in original_values.items():
        addr = mm.BEND_ANGLES[f'BEND_{bend_num}_SETPOINT']
        degrees = original_value / 10.0

        print(f"  Restaurando 0x{addr:04X} - Dobra {bend_num}: {original_value} ({degrees:.1f}°)... ", end='', flush=True)

        success = client.write_register(addr, original_value)

        if success:
            print("✅ OK")
        else:
            print("❌ FALHA")

    print()

    # Verificar restauração
    print("🔍 Verificando restauração...")
    time.sleep(0.5)

    all_restored = True
    for bend_num, original_value in original_values.items():
        addr = mm.BEND_ANGLES[f'BEND_{bend_num}_SETPOINT']
        read_value = client.read_register(addr)

        if read_value == original_value:
            print(f"  ✅ Dobra {bend_num}: Restaurado corretamente")
        else:
            print(f"  ❌ Dobra {bend_num}: Falha na restauração ({read_value} != {original_value})")
            all_restored = False

    print()

    client.disconnect()

    # Resultado final
    print("=" * 70)
    print("  RESULTADO DO TESTE - ÁREA 0x0500")
    print("=" * 70)
    print()

    if verification_ok and all_restored:
        print("✅ SUCESSO!")
        print("   → Área 0x0500 é GRAVÁVEL via Modbus")
        print("   → Valores foram escritos e lidos corretamente")
        print("   → Valores originais foram restaurados")
        return True
    elif verification_ok and not all_restored:
        print("⚠️  PARCIAL")
        print("   → Escrita funcionou")
        print("   → Mas houve problema na restauração")
        return True
    else:
        print("❌ FALHA")
        print("   → Área 0x0500 pode estar protegida contra escrita")
        print("   → Ou houve erro de comunicação")
        return False


def test_write_32bit_area():
    """Testa escrita na área 0x0840 (32-bit MSW/LSW)."""
    print()
    print("=" * 70)
    print("  TESTE 2: ÁREA 0x0840 (Shadow - 32-bit MSW/LSW)")
    print("=" * 70)
    print()

    client = ModbusClientWrapper(stub_mode=False, port='/dev/ttyUSB0')

    if not client.connected:
        print("❌ CLP não conectado")
        return False

    print("✅ Conectado ao CLP")
    print()

    shadow_addrs = [
        (1, 0x0842, 0x0840),  # MSW, LSW
        (2, 0x0848, 0x0846),
        (3, 0x0852, 0x0850),
    ]

    # 1. Ler valores originais
    print("📖 ETAPA 1: Lendo valores ORIGINAIS...")
    print("-" * 70)

    original_values = {}
    for bend_num, msw_addr, lsw_addr in shadow_addrs:
        msw = client.read_register(msw_addr)
        lsw = client.read_register(lsw_addr)

        if msw is not None and lsw is not None:
            value_32bit = mm.read_32bit(msw, lsw)
            degrees = mm.clp_to_degrees(value_32bit)
            original_values[bend_num] = (msw, lsw, value_32bit)
            print(f"  0x{msw_addr:04X}/0x{lsw_addr:04X} - Dobra {bend_num}: {degrees:6.1f}° (MSW={msw}, LSW={lsw})")
        else:
            print(f"  Dobra {bend_num}: ERRO AO LER")
            client.disconnect()
            return False

    print()

    # 2. Escrever valores de teste
    print("✏️  ETAPA 2: Escrevendo valores DE TESTE...")
    print("-" * 70)

    test_angles = {
        1: 85.0,   # 85°
        2: 135.0,  # 135°
        3: 60.0    # 60°
    }

    for bend_num, test_degrees in test_angles.items():
        msw_addr = shadow_addrs[bend_num - 1][1]
        lsw_addr = shadow_addrs[bend_num - 1][2]

        test_value = mm.degrees_to_clp(test_degrees)
        msw, lsw = mm.split_32bit(test_value)

        print(f"  Escrevendo Dobra {bend_num}: {test_degrees:.1f}° (MSW={msw}, LSW={lsw})")
        print(f"    → 0x{msw_addr:04X} = {msw}... ", end='', flush=True)

        success_msw = client.write_register(msw_addr, msw)
        print("✅" if success_msw else "❌")

        print(f"    → 0x{lsw_addr:04X} = {lsw}... ", end='', flush=True)
        success_lsw = client.write_register(lsw_addr, lsw)
        print("✅" if success_lsw else "❌")

    print()

    # Aguarda processamento
    print("⏳ Aguardando 500ms para CLP processar...")
    time.sleep(0.5)
    print()

    # 3. Verificar escrita
    print("🔍 ETAPA 3: Verificando se valores foram GRAVADOS...")
    print("-" * 70)

    verification_ok = True
    for bend_num, test_degrees in test_angles.items():
        msw_addr = shadow_addrs[bend_num - 1][1]
        lsw_addr = shadow_addrs[bend_num - 1][2]

        msw = client.read_register(msw_addr)
        lsw = client.read_register(lsw_addr)

        if msw is not None and lsw is not None:
            value_32bit = mm.read_32bit(msw, lsw)
            degrees = mm.clp_to_degrees(value_32bit)

            diff = abs(degrees - test_degrees)
            match = (diff < 0.1)
            status = "✅" if match else "❌"

            print(f"  {status} Dobra {bend_num}: {degrees:6.1f}° - Esperado: {test_degrees:.1f}° (diff: {diff:.1f}°)")

            if not match:
                verification_ok = False
                print(f"      ⚠️  Pode estar sendo sobrescrito pelo ladder!")
        else:
            print(f"  ❌ Dobra {bend_num}: ERRO AO LER")
            verification_ok = False

    print()

    # 4. Restaurar valores originais
    print("♻️  ETAPA 4: Restaurando valores ORIGINAIS...")
    print("-" * 70)

    for bend_num, (orig_msw, orig_lsw, orig_value) in original_values.items():
        msw_addr = shadow_addrs[bend_num - 1][1]
        lsw_addr = shadow_addrs[bend_num - 1][2]

        print(f"  Restaurando Dobra {bend_num}...")
        client.write_register(msw_addr, orig_msw)
        client.write_register(lsw_addr, orig_lsw)
        print(f"    ✅ 0x{msw_addr:04X}={orig_msw}, 0x{lsw_addr:04X}={orig_lsw}")

    print()

    client.disconnect()

    # Resultado
    print("=" * 70)
    print("  RESULTADO DO TESTE - ÁREA 0x0840")
    print("=" * 70)
    print()

    if verification_ok:
        print("✅ SUCESSO PARCIAL")
        print("   → Área 0x0840 é GRAVÁVEL via Modbus")
        print("   ⚠️  Mas valores podem ser sobrescritos pelo ladder")
        print("   → Recomendado usar área 0x0500 ao invés de 0x0840")
        return True
    else:
        print("❌ FALHA")
        print("   → Área 0x0840 está sendo sobrescrita pelo ladder")
        print("   → Não é confiável para escrita")
        return False


def main():
    print("=" * 70)
    print("  TESTE DE ESCRITA - ÂNGULOS OFICIAIS DO CLP")
    print("=" * 70)
    print()
    print("Este teste irá:")
    print("  1. Ler valores atuais")
    print("  2. Escrever valores de teste")
    print("  3. Verificar se escrita funcionou")
    print("  4. Restaurar valores originais")
    print()
    print("⚠️  IMPORTANTE: Teste seguro - valores são restaurados!")
    print()

    input("Pressione ENTER para iniciar o teste... ")
    print()

    # Teste 1: Área 0x0500
    result_0500 = test_write_16bit_area()

    # Teste 2: Área 0x0840
    result_0840 = test_write_32bit_area()

    # Resumo final
    print()
    print("=" * 70)
    print("  RESUMO FINAL DOS TESTES")
    print("=" * 70)
    print()

    print("┌────────────────────────┬──────────────┬─────────────────────┐")
    print("│  Área                  │   Gravável?  │   Recomendação      │")
    print("├────────────────────────┼──────────────┼─────────────────────┤")

    status_0500 = "✅ SIM" if result_0500 else "❌ NÃO"
    rec_0500 = "✅ USAR" if result_0500 else "❌ EVITAR"
    print(f"│ 0x0500 (16-bit oficial)│  {status_0500:>10s}  │  {rec_0500:>17s}  │")

    status_0840 = "⚠️  SIM*" if result_0840 else "❌ NÃO"
    rec_0840 = "⚠️  CUIDADO" if result_0840 else "❌ EVITAR"
    print(f"│ 0x0840 (32-bit shadow) │  {status_0840:>10s}  │  {rec_0840:>17s}  │")

    print("└────────────────────────┴──────────────┴─────────────────────┘")
    print()

    if result_0500:
        print("💡 CONCLUSÃO:")
        print("   → Use área 0x0500 para gravar ângulos")
        print("   → É a área oficial conforme manual Atos MPC4004")
        print("   → Formato simples: 16-bit (valor = graus * 10)")
    else:
        print("⚠️  ATENÇÃO:")
        print("   → Área 0x0500 não está gravável")
        print("   → Pode estar protegida pelo ladder")
        print("   → Verifique se há rotina de proteção em ROT4/ROT5")

    print()

    return 0 if (result_0500 or result_0840) else 1


if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Teste cancelado pelo usuário")
        sys.exit(1)
