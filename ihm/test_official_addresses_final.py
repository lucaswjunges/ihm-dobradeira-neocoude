#!/usr/bin/env python3
"""
✅ TESTE FINAL - VALIDAÇÃO DOS ENDEREÇOS OFICIAIS CORRIGIDOS
=============================================================

Após correção do modbus_map.py, validar que:
1. IHM web grava nos endereços oficiais do ladder
2. Ladder mantém os valores (não sobrescreve)
3. Valores são lidos corretamente de volta
"""

import sys
import time
from modbus_client import ModbusClientWrapper
import modbus_map as mm

def test_official_addresses():
    print("=" * 70)
    print("✅ TESTE FINAL - ENDEREÇOS OFICIAIS CORRIGIDOS")
    print("=" * 70)

    client = ModbusClientWrapper(stub_mode=False, port='/dev/ttyUSB0')

    if not client.connected:
        print("❌ CLP não conectado!")
        return False

    print("✅ CLP conectado\n")

    # Endereços que DEVEMOS estar usando agora
    print("📋 ENDEREÇOS NO modbus_map.py APÓS CORREÇÃO:")
    print(f"   Dobra 1: MSW=0x{mm.BEND_ANGLES['BEND_1_LEFT_MSW']:04X}, LSW=0x{mm.BEND_ANGLES['BEND_1_LEFT_LSW']:04X}")
    print(f"   Dobra 2: MSW=0x{mm.BEND_ANGLES['BEND_2_LEFT_MSW']:04X}, LSW=0x{mm.BEND_ANGLES['BEND_2_LEFT_LSW']:04X}")
    print(f"   Dobra 3: MSW=0x{mm.BEND_ANGLES['BEND_3_LEFT_MSW']:04X}, LSW=0x{mm.BEND_ANGLES['BEND_3_LEFT_LSW']:04X}")

    # Verificar se estão corretos
    expected_official = {
        'BEND_1': (0x0842, 0x0840),
        'BEND_2': (0x0848, 0x0846),
        'BEND_3': (0x0852, 0x0850),
    }

    print("\n🔍 VERIFICAÇÃO:")
    all_correct = True
    for bend, (exp_msw, exp_lsw) in expected_official.items():
        bend_num = bend.split('_')[1]
        actual_msw = mm.BEND_ANGLES[f'BEND_{bend_num}_LEFT_MSW']
        actual_lsw = mm.BEND_ANGLES[f'BEND_{bend_num}_LEFT_LSW']

        if actual_msw == exp_msw and actual_lsw == exp_lsw:
            print(f"   ✅ Dobra {bend_num}: Endereços CORRETOS!")
        else:
            print(f"   ❌ Dobra {bend_num}: ERRADO! Esperado 0x{exp_msw:04X}/0x{exp_lsw:04X}, obtido 0x{actual_msw:04X}/0x{actual_lsw:04X}")
            all_correct = False

    if not all_correct:
        print("\n❌ modbus_map.py ainda está com endereços errados!")
        client.close()
        return False

    # TESTE DE ESCRITA E LEITURA
    print("\n" + "=" * 70)
    print("TESTE DE ESCRITA/LEITURA")
    print("=" * 70)

    test_angles = [
        (90.0, "Dobra 1"),
        (120.0, "Dobra 2"),
        (35.0, "Dobra 3"),
    ]

    print("\n📝 Escrevendo ângulos via IHM web (modbus_client):")
    for angle, name in test_angles:
        dobra_num = name.split()[1]
        value_clp = mm.degrees_to_clp(angle)

        success = client.write_32bit(
            mm.BEND_ANGLES[f'BEND_{dobra_num}_LEFT_MSW'],
            mm.BEND_ANGLES[f'BEND_{dobra_num}_LEFT_LSW'],
            value_clp
        )

        status = "✅" if success else "❌"
        print(f"   {status} {name}: {angle}° ({value_clp} em CLP)")

    # Aguardar processamento
    print("\n⏳ Aguardando 2s...")
    time.sleep(2.0)

    # Ler de volta
    print("\n📖 Lendo ângulos DE VOLTA:")
    all_match = True
    for angle_expected, name in test_angles:
        dobra_num = name.split()[1]

        value_read = client.read_32bit(
            mm.BEND_ANGLES[f'BEND_{dobra_num}_LEFT_MSW'],
            mm.BEND_ANGLES[f'BEND_{dobra_num}_LEFT_LSW']
        )

        if value_read is None:
            print(f"   ❌ {name}: Não conseguiu ler!")
            all_match = False
            continue

        angle_read = mm.clp_to_degrees(value_read)
        match = abs(angle_read - angle_expected) < 0.5

        if match:
            print(f"   ✅ {name}: {angle_read:.1f}° (esperado {angle_expected:.1f}°)")
        else:
            print(f"   ❌ {name}: {angle_read:.1f}° (esperado {angle_expected:.1f}° - DISCREPÂNCIA!)")
            all_match = False

    # CONCLUSÃO
    print("\n" + "=" * 70)
    print("🎯 CONCLUSÃO FINAL")
    print("=" * 70)

    if all_match:
        print("\n✅✅✅ SUCESSO TOTAL! ✅✅✅")
        print("\n   → IHM web grava nos endereços OFICIAIS do ladder")
        print("   → Valores persistem corretamente")
        print("   → Leitura confirma valores escritos")
        print("\n   🚀 PRONTO PARA SEGUNDA-FEIRA NA FÁBRICA!")
    else:
        print("\n❌❌❌ AINDA HÁ PROBLEMAS! ❌❌❌")
        print("\n   → Verificar se ladder está sobrescrevendo")
        print("   → Pode precisar análise adicional do ladder")

    client.close()
    print("\n" + "=" * 70)

    return all_match

if __name__ == "__main__":
    try:
        success = test_official_addresses()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⚠️  Teste interrompido!")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
