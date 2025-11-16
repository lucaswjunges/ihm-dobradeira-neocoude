#!/usr/bin/env python3
"""
🚨 TESTE CRÍTICO - AUDITORIA DE ENDEREÇOS DE ÂNGULOS
====================================================

Verificar se LADDER lê dos endereços que nossa IHM está usando!

LADDER OFICIAL (da análise):
- Dobra 1: 0x0840/0x0842 (usados em SUB Line00008)
- Dobra 2: 0x0846/0x0848 (usados em SUB Line00009)
- Dobra 3: 0x0850/0x0852 (usados em SUB Line00010)

NOSSA IHM WEB:
- Dobra 1: 0x0848/0x084A
- Dobra 2: 0x084C/0x084E
- Dobra 3: 0x0854/0x0856

TESTE:
1. Escrever valor DISTINTO em cada par
2. Aguardar 10 segundos (ladder processar)
3. Verificar se ladder COPIOU valores
4. Se NÃO copiou → NOSSOS ÂNGULOS SÃO IGNORADOS!
"""

import sys
import time
from modbus_client import ModbusClientWrapper

# Endereços OFICIAIS do ladder
LADDER_OFFICIAL = {
    'DOBRA_1_MSW': 0x0842,  # Ladder Line00008 lê daqui
    'DOBRA_1_LSW': 0x0840,
    'DOBRA_2_MSW': 0x0848,  # Ladder Line00009 lê daqui
    'DOBRA_2_LSW': 0x0846,
    'DOBRA_3_MSW': 0x0852,  # Ladder Line00010 lê daqui
    'DOBRA_3_LSW': 0x0850,
}

# Endereços que NOSSA IHM usa
OUR_IHM = {
    'DOBRA_1_MSW': 0x0848,  # IHM web escreve aqui
    'DOBRA_1_LSW': 0x084A,
    'DOBRA_2_MSW': 0x084C,
    'DOBRA_2_LSW': 0x084E,
    'DOBRA_3_MSW': 0x0854,
    'DOBRA_3_LSW': 0x0856,
}

def read_32bit_direct(client, msw_addr, lsw_addr):
    """Lê diretamente sem helpers."""
    msw = client.read_register(msw_addr)
    lsw = client.read_register(lsw_addr)
    if msw is None or lsw is None:
        return None
    return (msw << 16) | lsw

def write_32bit_direct(client, msw_addr, lsw_addr, value):
    """Escreve diretamente sem helpers."""
    msw = (value >> 16) & 0xFFFF
    lsw = value & 0xFFFF
    return (client.write_register(msw_addr, msw) and
            client.write_register(lsw_addr, lsw))

def test_address_relationship():
    print("=" * 70)
    print("🚨 AUDITORIA CRÍTICA - VERIFICAÇÃO DE ENDEREÇOS")
    print("=" * 70)

    client = ModbusClientWrapper(stub_mode=False, port='/dev/ttyUSB0')

    if not client.connected:
        print("❌ CLP não conectado!")
        return False

    print("✅ CLP conectado\n")

    # FASE 1: Ler estado atual
    print("=" * 70)
    print("FASE 1: ESTADO ATUAL DO CLP")
    print("=" * 70)

    print("\n📋 ENDEREÇOS OFICIAIS DO LADDER:")
    official_values = {}
    for name, (msw, lsw) in [
        ('Dobra 1', (LADDER_OFFICIAL['DOBRA_1_MSW'], LADDER_OFFICIAL['DOBRA_1_LSW'])),
        ('Dobra 2', (LADDER_OFFICIAL['DOBRA_2_MSW'], LADDER_OFFICIAL['DOBRA_2_LSW'])),
        ('Dobra 3', (LADDER_OFFICIAL['DOBRA_3_MSW'], LADDER_OFFICIAL['DOBRA_3_LSW'])),
    ]:
        value = read_32bit_direct(client, msw, lsw)
        official_values[name] = value
        degrees = value / 10.0 if value else 0
        print(f"  {name} (0x{msw:04X}/0x{lsw:04X}): {value:6d} ({degrees:6.1f}°)")

    print("\n📋 ENDEREÇOS DA NOSSA IHM WEB:")
    our_values = {}
    for name, (msw, lsw) in [
        ('Dobra 1', (OUR_IHM['DOBRA_1_MSW'], OUR_IHM['DOBRA_1_LSW'])),
        ('Dobra 2', (OUR_IHM['DOBRA_2_MSW'], OUR_IHM['DOBRA_2_LSW'])),
        ('Dobra 3', (OUR_IHM['DOBRA_3_MSW'], OUR_IHM['DOBRA_3_LSW'])),
    ]:
        value = read_32bit_direct(client, msw, lsw)
        our_values[name] = value
        degrees = value / 10.0 if value else 0
        print(f"  {name} (0x{msw:04X}/0x{lsw:04X}): {value:6d} ({degrees:6.1f}°)")

    # FASE 2: Escrever valores DISTINTOS
    print("\n" + "=" * 70)
    print("FASE 2: ESCREVENDO VALORES DISTINTOS")
    print("=" * 70)

    test_values = {
        'Dobra 1': 123,  # 12.3°
        'Dobra 2': 456,  # 45.6°
        'Dobra 3': 789,  # 78.9°
    }

    print("\n📝 Escrevendo nos endereços da NOSSA IHM:")
    for dobra, value in test_values.items():
        msw = OUR_IHM[f'{dobra.upper().replace(" ", "_")}_MSW']
        lsw = OUR_IHM[f'{dobra.upper().replace(" ", "_")}_LSW']
        success = write_32bit_direct(client, msw, lsw, value)
        status = "✅" if success else "❌"
        print(f"  {status} {dobra} → {value} ({value/10.0}°)")

    time.sleep(0.5)

    # FASE 3: Aguardar processamento do ladder
    print("\n⏳ Aguardando 10 segundos para ladder processar...")
    for i in range(10, 0, -1):
        print(f"   {i}s...", end='\r')
        time.sleep(1)
    print("   ✓ Tempo concluído       ")

    # FASE 4: Verificar se ladder COPIOU valores
    print("\n" + "=" * 70)
    print("FASE 3: VERIFICAÇÃO - LADDER COPIOU OS VALORES?")
    print("=" * 70)

    print("\n📋 Lendo ENDEREÇOS OFICIAIS DO LADDER (onde ele lê):")

    all_match = True
    for dobra in ['Dobra 1', 'Dobra 2', 'Dobra 3']:
        official_key = f'{dobra.upper().replace(" ", "_")}'
        msw = LADDER_OFFICIAL[f'{official_key}_MSW']
        lsw = LADDER_OFFICIAL[f'{official_key}_LSW']

        value_official = read_32bit_direct(client, msw, lsw)
        value_expected = test_values[dobra]

        degrees_official = value_official / 10.0 if value_official else 0
        degrees_expected = value_expected / 10.0

        match = abs(value_official - value_expected) < 5 if value_official else False

        if match:
            print(f"  ✅ {dobra}: {value_official} ({degrees_official:.1f}°) - COPIADO!")
        else:
            print(f"  ❌ {dobra}: {value_official} ({degrees_official:.1f}°) - Esperado: {value_expected} ({degrees_expected:.1f}°)")
            all_match = False

    # FASE 5: Leitura de confirmação da nossa área
    print("\n📋 Confirmando NOSSA ÁREA (endereços que escrevemos):")
    for dobra in ['Dobra 1', 'Dobra 2', 'Dobra 3']:
        our_key = f'{dobra.upper().replace(" ", "_")}'
        msw = OUR_IHM[f'{our_key}_MSW']
        lsw = OUR_IHM[f'{our_key}_LSW']

        value_our = read_32bit_direct(client, msw, lsw)
        value_expected = test_values[dobra]

        degrees_our = value_our / 10.0 if value_our else 0
        degrees_expected = value_expected / 10.0

        match = abs(value_our - value_expected) < 5 if value_our else False

        status = "✅" if match else "❌"
        print(f"  {status} {dobra}: {value_our} ({degrees_our:.1f}°)")

    # CONCLUSÃO
    print("\n" + "=" * 70)
    print("🎯 CONCLUSÃO DA AUDITORIA")
    print("=" * 70)

    if all_match:
        print("\n✅✅✅ LADDER COPIOU OS VALORES! ✅✅✅")
        print("\n   → Ladder tem lógica que copia dos nossos endereços para oficiais")
        print("   → IHM web VAI FUNCIONAR segunda-feira!")
        print("   → Endereços corretos:\n")
        for dobra in ['Dobra 1', 'Dobra 2', 'Dobra 3']:
            our_key = f'{dobra.upper().replace(" ", "_")}'
            msw = OUR_IHM[f'{our_key}_MSW']
            lsw = OUR_IHM[f'{our_key}_LSW']
            print(f"     {dobra}: 0x{msw:04X}/0x{lsw:04X}")
    else:
        print("\n❌❌❌ LADDER NÃO COPIOU! ❌❌❌")
        print("\n   → Ladder NÃO lê dos endereços que nossa IHM usa")
        print("   → ÂNGULOS SERÃO IGNORADOS!")
        print("   → PRECISA CORRIGIR ANTES DE SEGUNDA-FEIRA!")
        print("\n   🔧 SOLUÇÃO: Mudar modbus_map.py para usar endereços oficiais:")
        print("     - Dobra 1: 0x0842/0x0840")
        print("     - Dobra 2: 0x0848/0x0846")
        print("     - Dobra 3: 0x0852/0x0850")

    # Restaurar valores originais
    print("\n⏳ Restaurando valores originais...")
    for dobra in ['Dobra 1', 'Dobra 2', 'Dobra 3']:
        our_key = f'{dobra.upper().replace(" ", "_")}'
        msw = OUR_IHM[f'{our_key}_MSW']
        lsw = OUR_IHM[f'{our_key}_LSW']
        original = our_values[dobra] if dobra in our_values else 0
        write_32bit_direct(client, msw, lsw, original)

    time.sleep(0.5)
    print("✓ Valores restaurados")

    client.close()
    print("\n" + "=" * 70)

    return all_match

if __name__ == "__main__":
    try:
        success = test_address_relationship()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⚠️  Teste interrompido!")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
