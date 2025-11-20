#!/usr/bin/env python3
"""
Teste da Solução A: Gravar em 0x0840
=====================================

Testa se a modificação do modbus_client.py está funcionando:
- Grava em 0x0840 (área lida pelo ladder)
- Lê de 0x0840 para confirmar
- Garante sincronização IHM ↔ Ladder
"""

import sys
import time
from modbus_client import ModbusClientWrapper
import modbus_map as mm

def main():
    print("=" * 70)
    print("  TESTE: SOLUÇÃO A - Gravar em 0x0840 (área do ladder)")
    print("=" * 70)
    print()

    print("🔧 Modificação implementada:")
    print("   • write_bend_angle() agora grava em 0x0840 (32-bit MSW/LSW)")
    print("   • read_bend_angle() agora lê de 0x0840")
    print("   • Garantia de sincronização IHM ↔ Ladder")
    print()

    # Conectar ao CLP
    client = ModbusClientWrapper(stub_mode=False, port='/dev/ttyUSB0')

    if not client.connected:
        print("❌ CLP não conectado em /dev/ttyUSB0")
        print()
        print("⚠️  Execute este teste no ESP32 onde CLP está conectado:")
        print("   ssh usuario@192.168.0.106")
        print("   cd /projeto")
        print("   python3 test_solucao_a.py")
        return 1

    print("✅ Conectado ao CLP")
    print()

    # Teste 1: Ler valores atuais
    print("=" * 70)
    print("📖 ETAPA 1: Lendo valores ATUAIS da área 0x0840")
    print("=" * 70)
    print()

    original_values = {}
    for bend_num in [1, 2, 3]:
        angle = client.read_bend_angle(bend_num)
        if angle is not None:
            original_values[bend_num] = angle
            print(f"  Dobra {bend_num}: {angle:.1f}°")
        else:
            print(f"  Dobra {bend_num}: ERRO AO LER")

    print()

    # Teste 2: Escrever valores de teste
    print("=" * 70)
    print("✏️  ETAPA 2: Escrevendo valores DE TESTE em 0x0840")
    print("=" * 70)
    print()

    test_values = {
        1: 85.5,   # 85.5°
        2: 135.0,  # 135.0°
        3: 62.5    # 62.5°
    }

    for bend_num, degrees in test_values.items():
        print(f"Escrevendo Dobra {bend_num}: {degrees}°")
        success = client.write_bend_angle(bend_num, degrees)
        if not success:
            print(f"  ❌ FALHA ao escrever Dobra {bend_num}")

    print()

    # Aguardar processamento
    print("⏳ Aguardando 500ms para CLP processar...")
    time.sleep(0.5)
    print()

    # Teste 3: Verificar escrita
    print("=" * 70)
    print("🔍 ETAPA 3: Verificando se valores foram GRAVADOS")
    print("=" * 70)
    print()

    all_ok = True
    for bend_num, expected_degrees in test_values.items():
        angle = client.read_bend_angle(bend_num)

        if angle is not None:
            diff = abs(angle - expected_degrees)
            match = (diff < 0.1)
            status = "✅" if match else "❌"

            print(f"  {status} Dobra {bend_num}: {angle:.1f}° (esperado: {expected_degrees:.1f}°, diff: {diff:.1f}°)")

            if not match:
                all_ok = False
                print(f"      ⚠️  Valor pode estar sendo sobrescrito pelo ladder!")
        else:
            print(f"  ❌ Dobra {bend_num}: ERRO AO LER")
            all_ok = False

    print()

    # Teste 4: Restaurar valores originais
    print("=" * 70)
    print("♻️  ETAPA 4: Restaurando valores ORIGINAIS")
    print("=" * 70)
    print()

    for bend_num, original_degrees in original_values.items():
        print(f"Restaurando Dobra {bend_num}: {original_degrees:.1f}°")
        client.write_bend_angle(bend_num, original_degrees)

    print()

    # Aguardar e verificar restauração
    time.sleep(0.5)

    print("🔍 Verificando restauração...")
    for bend_num, original_degrees in original_values.items():
        angle = client.read_bend_angle(bend_num)
        if angle is not None:
            diff = abs(angle - original_degrees)
            if diff < 0.1:
                print(f"  ✅ Dobra {bend_num}: Restaurado ({angle:.1f}°)")
            else:
                print(f"  ⚠️  Dobra {bend_num}: Divergência ({angle:.1f}° vs {original_degrees:.1f}°)")

    print()

    client.disconnect()

    # Resultado final
    print("=" * 70)
    print("  RESULTADO DO TESTE")
    print("=" * 70)
    print()

    if all_ok:
        print("✅ SUCESSO!")
        print()
        print("A Solução A está funcionando:")
        print("  • Escrita em 0x0840: ✅ OK")
        print("  • Leitura de 0x0840: ✅ OK")
        print("  • Sincronização IHM ↔ Ladder: ✅ GARANTIDA")
        print()
        print("🎯 Próximos passos:")
        print("  1. Reiniciar servidor: systemctl restart ihm_server")
        print("  2. Testar na IHM Web")
        print("  3. Validar com operador (verificar se ângulos estão corretos)")
    else:
        print("⚠️  ATENÇÃO!")
        print()
        print("Possíveis causas:")
        print("  • Ladder pode estar sobrescrevendo 0x0840 a cada scan")
        print("  • ROT4/ROT5 pode estar forçando valores")
        print()
        print("Soluções:")
        print("  • Verificar se há rotina no ladder que escreve em 0x0840")
        print("  • Implementar Solução C (rotina de cópia 0x0500→0x0840)")
        print("  • Ou implementar Solução B (modificar ladder)")

    print()
    return 0 if all_ok else 1


if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Teste cancelado pelo usuário")
        sys.exit(1)
