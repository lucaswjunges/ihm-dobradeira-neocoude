#!/usr/bin/env python3
"""
Teste de Diagnóstico - Controle de Velocidade
==============================================

Testa comunicação Modbus com inversor WEG CFW08
Identifica se problema é:
- Ladder (não copia 0x0A06 → 0x06E0)
- Fiação (sinal analógico não chega no inversor)
- Inversor (ignora entrada analógica)
"""

import time
from modbus_client import ModbusClientWrapper
import modbus_map as mm

def test_velocidade():
    """Testa controle de velocidade passo a passo"""

    print("=" * 70)
    print("TESTE DE DIAGNÓSTICO - CONTROLE DE VELOCIDADE")
    print("=" * 70)

    # Conecta ao CLP
    print("\n1. Conectando ao CLP...")
    client = ModbusClientWrapper(stub_mode=False, port='/dev/ttyUSB0')

    if not client.connected:
        print("❌ ERRO: CLP não conectado!")
        print("Verifique:")
        print("  - Cabo RS485 conectado")
        print("  - CLP ligado e em RUN")
        return

    print("✅ CLP conectado!")

    # PASSO 1: Ler valor atual em 0x06E0 (saída analógica do inversor)
    print("\n" + "=" * 70)
    print("PASSO 1: Lendo registro de velocidade atual (0x06E0)")
    print("=" * 70)

    current_value = client.read_register(mm.INVERTER['VELOCIDADE_INVERSOR'])

    if current_value is None:
        print("❌ ERRO: Não conseguiu ler 0x06E0!")
        print("   Possível problema de comunicação Modbus")
        return

    current_rpm = mm.register_to_rpm(current_value)
    print(f"✅ Valor atual lido:")
    print(f"   Registro 0x06E0 = {current_value} (0x{current_value:04X})")
    print(f"   Velocidade calculada = {current_rpm:.2f} RPM")

    # PASSO 2: Testar escrita em diferentes velocidades
    print("\n" + "=" * 70)
    print("PASSO 2: Testando escrita de velocidade")
    print("=" * 70)

    test_speeds = [5, 10, 15]

    for rpm in test_speeds:
        print(f"\n🔧 Testando {rpm} RPM...")

        # Converte RPM para valor do registro
        register_value = mm.rpm_to_register(rpm)
        print(f"   Valor a escrever: {register_value} (0x{register_value:04X})")

        # Escreve em 0x0A06 (área de escrita - IHM → Ladder)
        print(f"   Escrevendo em 0x0A06 (VELOCIDADE_WRITE)...")
        success_write = client.write_register(mm.INVERTER['VELOCIDADE_WRITE'], register_value)

        if not success_write:
            print(f"   ❌ Falha ao escrever em 0x0A06!")
            continue

        print(f"   ✅ Escrita em 0x0A06 OK")

        # Aguarda ladder copiar para 0x06E0
        print("   ⏳ Aguardando 1 segundo para ladder processar...")
        time.sleep(1.0)

        # Lê valor em 0x06E0 (saída analógica)
        print(f"   Lendo 0x06E0 (VELOCIDADE_INVERSOR)...")
        read_value = client.read_register(mm.INVERTER['VELOCIDADE_INVERSOR'])

        if read_value is None:
            print(f"   ❌ Falha ao ler 0x06E0!")
            continue

        read_rpm = mm.register_to_rpm(read_value)
        print(f"   ✅ Valor lido em 0x06E0: {read_value} (0x{read_value:04X}) = {read_rpm:.2f} RPM")

        # Verifica se mudou
        if abs(read_rpm - rpm) < 0.5:  # Tolerância de 0.5 RPM
            print(f"   ✅ SUCESSO: Valor mudou corretamente para ~{rpm} RPM!")
        else:
            print(f"   ⚠️ ATENÇÃO: Valor esperado {rpm} RPM, mas leu {read_rpm:.2f} RPM")
            print(f"   Diferença: {abs(read_rpm - rpm):.2f} RPM")

        time.sleep(2)  # Aguarda entre testes

    # PASSO 3: Diagnóstico final
    print("\n" + "=" * 70)
    print("PASSO 3: DIAGNÓSTICO FINAL")
    print("=" * 70)

    # Lê valor final em 0x06E0
    final_value = client.read_register(mm.INVERTER['VELOCIDADE_INVERSOR'])
    final_rpm = mm.register_to_rpm(final_value) if final_value else 0

    print(f"\n📊 Resumo:")
    print(f"   Valor inicial: {current_rpm:.2f} RPM")
    print(f"   Valor final: {final_rpm:.2f} RPM")

    if abs(final_rpm - current_rpm) > 0.5:
        print("\n✅ COMUNICAÇÃO MODBUS OK!")
        print("   O registro 0x06E0 está mudando conforme esperado.")
        print("\n🔍 PRÓXIMOS PASSOS:")
        print("   1. Verificar se o sinal analógico está chegando no inversor WEG")
        print("   2. Usar um multímetro para medir tensão no terminal analógico do inversor")
        print("   3. Valores esperados:")
        print("      - 5 RPM  = ~2.64V (527 / 2000 * 10V)")
        print("      - 10 RPM = ~5.28V (1055 / 2000 * 10V)")
        print("      - 15 RPM = ~7.92V (1583 / 2000 * 10V)")
        print("\n   Se a tensão está correta mas máquina não muda velocidade:")
        print("   → Problema no inversor WEG (configuração ou defeito)")
        print("\n   Se a tensão NÃO está correta:")
        print("   → Problema na saída analógica do CLP ou cabo solto")

    else:
        print("\n❌ PROBLEMA DETECTADO!")
        print("   O registro 0x06E0 NÃO está mudando!")
        print("\n🔍 POSSÍVEIS CAUSAS:")
        print("   1. Ladder não implementado para copiar 0x0A06 → 0x06E0")
        print("   2. Ladder tem lógica que trava mudança de velocidade")
        print("   3. Problema de permissões no ladder (modo manual vs auto)")
        print("\n🔧 SOLUÇÕES:")
        print("   1. Verificar programa ladder (clp.sup) se há lógica de cópia")
        print("   2. Tentar escrever DIRETAMENTE em 0x06E0 (bypass ladder)")
        print("   3. Verificar se há algum bit de habilitação necessário")

    client.close()


def test_direct_write():
    """
    Testa escrita DIRETA em 0x06E0 (bypass ladder)
    ATENÇÃO: Isso pode não funcionar se 0x06E0 for somente leitura!
    """
    print("\n" + "=" * 70)
    print("TESTE AVANÇADO: Escrita DIRETA em 0x06E0")
    print("=" * 70)
    print("ATENÇÃO: Ignorando ladder, escrevendo direto na saída analógica!")

    client = ModbusClientWrapper(stub_mode=False, port='/dev/ttyUSB0')

    if not client.connected:
        print("❌ CLP não conectado!")
        return

    # Tenta escrever diretamente em 0x06E0
    test_value = 1055  # 10 RPM
    print(f"\n🔧 Tentando escrever {test_value} (10 RPM) diretamente em 0x06E0...")

    success = client.write_register(mm.INVERTER['VELOCIDADE_INVERSOR'], test_value)

    if success:
        print("✅ Escrita direta em 0x06E0 OK!")

        time.sleep(1)

        # Verifica
        read_value = client.read_register(mm.INVERTER['VELOCIDADE_INVERSOR'])
        read_rpm = mm.register_to_rpm(read_value) if read_value else 0

        print(f"📊 Valor lido após escrita: {read_rpm:.2f} RPM")

        if abs(read_rpm - 10) < 0.5:
            print("✅ SUCESSO: Escrita direta funciona!")
            print("\n💡 CONCLUSÃO:")
            print("   O problema é no ladder (não copia 0x0A06 → 0x06E0)")
            print("   SOLUÇÃO: Modificar programa ladder para implementar essa cópia")
            print("   OU usar escrita direta em 0x06E0 no código Python")
        else:
            print("⚠️ Valor não mudou mesmo com escrita direta")
    else:
        print("❌ Escrita direta falhou!")
        print("   0x06E0 provavelmente é SOMENTE LEITURA (área de saída analógica)")
        print("   O ladder DEVE copiar de 0x0A06 para 0x06E0")

    client.close()


if __name__ == "__main__":
    # Executa teste principal
    test_velocidade()

    # Pergunta se quer testar escrita direta
    print("\n" + "=" * 70)
    resposta = input("\nDeseja testar escrita DIRETA em 0x06E0? (s/n): ")

    if resposta.lower() == 's':
        test_direct_write()

    print("\n✓ Diagnóstico concluído!")
