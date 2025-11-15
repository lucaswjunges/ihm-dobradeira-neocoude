#!/usr/bin/env python3
"""
Teste Completo S1 - Mudança AUTO/MANUAL
Baseado em SOLUCAO_S1_DEFINITIVA.md
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from modbus_client import ModbusClientWrapper
import modbus_map as mm
import time

def test_s1_complete():
    """Testa mudança de modo via S1 com todas as verificações"""

    print("=" * 60)
    print("TESTE COMPLETO: BOTÃO S1 (AUTO/MANUAL)")
    print("=" * 60)

    client = ModbusClientWrapper(port='/dev/ttyUSB0', stub_mode=False)

    # 1. ESTADO INICIAL
    print("\n1️⃣ ESTADO INICIAL:")
    modo_02ff_antes = client.read_coil(0x02FF)  # Bit REAL de modo
    e6_status = client.read_coil(0x0106)  # E6 safety
    mono_0376 = client.read_coil(0x0376)  # Monostável
    s1_status = client.read_coil(0x00DC)  # S1

    print(f"   Modo (0x02FF):      {modo_02ff_antes} ({'AUTO' if modo_02ff_antes else 'MANUAL'})")
    print(f"   E6 (0x0106):        {e6_status} ({'✅ OK' if e6_status else '❌ OFF - BLOQUEADO!'})")
    print(f"   Monostável (0x0376): {mono_0376}")
    print(f"   S1 (0x00DC):        {s1_status}")

    # 2. FORÇAR E6 SE NECESSÁRIO
    if not e6_status:
        print("\n2️⃣ FORÇANDO E6 = ON (bypass segurança para teste):")
        client.write_coil(0x0106, True)
        time.sleep(0.5)
        e6_status = client.read_coil(0x0106)
        print(f"   E6 agora: {e6_status}")
    else:
        print("\n2️⃣ E6 já está ATIVA - OK!")

    # 3. PRESSIONAR S1
    print("\n3️⃣ PRESSIONANDO S1:")
    print("   S1 ON...")
    client.write_coil(0x00DC, True)
    time.sleep(0.05)

    # Verificar monostável durante pressão
    mono_durante = client.read_coil(0x0376)
    print(f"   Monostável durante: {mono_durante}")

    time.sleep(0.05)
    print("   S1 OFF...")
    client.write_coil(0x00DC, False)

    # 4. AGUARDAR PROCESSAMENTO
    print("\n4️⃣ AGUARDANDO PROCESSAMENTO (500ms)...")
    time.sleep(0.5)

    # 5. VERIFICAR RESULTADO
    print("\n5️⃣ RESULTADO:")
    modo_02ff_depois = client.read_coil(0x02FF)
    mono_depois = client.read_coil(0x0376)

    print(f"   Modo ANTES:  {modo_02ff_antes} ({'AUTO' if modo_02ff_antes else 'MANUAL'})")
    print(f"   Modo DEPOIS: {modo_02ff_depois} ({'AUTO' if modo_02ff_depois else 'MANUAL'})")
    print(f"   Monostável:  {mono_depois}")

    if modo_02ff_antes != modo_02ff_depois:
        print("\n✅ SUCESSO! Modo mudou de {} para {}".format(
            'MANUAL' if not modo_02ff_antes else 'AUTO',
            'AUTO' if modo_02ff_depois else 'MANUAL'
        ))
        return True
    else:
        print("\n❌ FALHA! Modo não mudou (continua {})".format(
            'AUTO' if modo_02ff_depois else 'MANUAL'
        ))

        # Diagnóstico
        print("\n🔍 DIAGNÓSTICO:")
        if not e6_status:
            print("   ⚠️ E6 está OFF - S1 bloqueado!")
        if not mono_durante:
            print("   ⚠️ Monostável não ativou - lógica ladder não executou!")

        return False

    client.close()

if __name__ == '__main__':
    try:
        test_s1_complete()
    except KeyboardInterrupt:
        print("\n\nTeste interrompido pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        import traceback
        traceback.print_exc()
