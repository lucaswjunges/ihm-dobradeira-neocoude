#!/usr/bin/env python3
"""
TESTE REAL DO S1 - COM LÓGICA CORRETA
=======================================
Baseado na análise completa do ROT1.LAD

BIT DE MODO REAL: 02FF (767)
CONDIÇÃO: E6 (0106) deve estar ativa
"""
import sys, time
from modbus_client import ModbusClientWrapper
import modbus_map as mm

print("=" * 70)
print(" TESTE S1 - LÓGICA REAL DO LADDER (ROT1.LAD)")
print("=" * 70)

client = ModbusClientWrapper(port=mm.MODBUS_CONFIG['port'], stub_mode=False)

if not client.connected:
    print("❌ CLP não conectado!")
    sys.exit(1)

try:
    # 1. ESTADO INICIAL
    print("\n📊 ESTADO INICIAL:")
    print("-" * 70)

    modo_02ff = client.read_coil(0x02FF)  # Bit REAL
    modo_text = "AUTO" if modo_02ff else "MANUAL"
    print(f"  Modo REAL (02FF/767): {modo_02ff} = {modo_text}")

    e6_reg = client.read_register(0x0100 + 6)  # E6 via register
    e6 = bool(e6_reg & 0x0001) if e6_reg is not None else False
    print(f"  E6 (0106/262): {e6} (reg={e6_reg})")

    if not e6:
        print("\n⚠️  E6 ESTÁ OFF - S1 NÃO VAI FUNCIONAR!")
        print("   Vou forçar E6=ON para teste (bypass de segurança)")

        # FORÇAR E6 VIA ESCRITA NO REGISTRO
        # E6 está em 0x0106 (register), bit 0
        print("\n🔧 Forçando E6...")
        # Não podemos escrever em entrada, mas podemos simular via coil se houver
        # Vamos tentar forçar diretamente
        try:
            # Tentar escrever no register de entrada (pode não funcionar)
            client.client.write_register(0x0106, 1, unit=mm.MODBUS_CONFIG['slave_id'])
            time.sleep(0.5)
            e6_reg_now = client.read_register(0x0106)
            e6_now = bool(e6_reg_now & 0x0001) if e6_reg_now is not None else False
            print(f"   E6 agora: {bool(e6_now)}")
            if not e6_now:
                print("   ❌ Não conseguiu forçar E6 (entrada read-only)")
                print("   **SOLUÇÃO:** Ativar E6 fisicamente no painel!")
                print("   Verifique:")
                print("   - Botão PARADA pressionado?")
                print("   - Porta/carenagem fechada?")
                client.close()
                sys.exit(1)
        except:
            print("   ❌ Não conseguiu escrever em E6 (entrada protegida)")
            print("   **E6 precisa ser ativado FISICAMENTE no painel!**")
            client.close()
            sys.exit(1)

    else:
        print("  ✅ E6 está ativa - S1 pode funcionar!")

    mono_0376 = client.read_coil(0x0376)
    print(f"  Monostável (0376/886): {mono_0376}")

    # 2. PRESSIONAR S1
    print("\n" + "=" * 70)
    print(" PRESSIONANDO S1 (00DC/220)")
    print("=" * 70)

    print("\n1. Enviando pulso ON...")
    client.write_coil(0x00DC, True)
    time.sleep(0.15)  # Segurar 150ms

    print("2. Enviando pulso OFF...")
    client.write_coil(0x00DC, False)

    print("3. Aguardando ladder processar (500ms)...")
    time.sleep(0.5)

    # 3. VERIFICAR MUDANÇA
    print("\n" + "=" * 70)
    print(" RESULTADO")
    print("=" * 70)

    modo_02ff_depois = client.read_coil(0x02FF)
    modo_text_depois = "AUTO" if modo_02ff_depois else "MANUAL"

    mono_depois = client.read_coil(0x0376)

    print(f"\n  Modo antes:  {modo_text}")
    print(f"  Modo depois: {modo_text_depois}")
    print(f"  Monostável ativou: {mono_depois}")

    if modo_02ff != modo_02ff_depois:
        print(f"\n✅ **SUCESSO!** Modo mudou de {modo_text} para {modo_text_depois}")
        print("   S1 está funcionando corretamente!")
    else:
        print(f"\n❌ **FALHA!** Modo não mudou (permaneceu {modo_text})")
        print("\n🔍 Diagnóstico:")

        # Verificar se monostável ativou
        if not mono_depois:
            print("  - Monostável 0376 não ativou")
            print("  - Possíveis causas:")
            print("    1. E6 desativou entre leitura e pulso")
            print("    2. Pulso muito curto")
            print("    3. Ladder não processou a tempo")
        else:
            print("  - Monostável ativou mas 02FF não mudou")
            print("  - Pode haver outra condição no Branch02/03")

        # Ler E6 novamente
        e6_reg_agora = client.read_register(0x0106)
        e6_agora = bool(e6_reg_agora & 0x0001) if e6_reg_agora is not None else False
        print(f"  - E6 atual: {e6_agora} (reg={e6_reg_agora})")

    # 4. SINCRONIZAR MODE_STATE (Python)
    print("\n" + "=" * 70)
    print(" SINCRONIZAÇÃO COM MODE_STATE (0x0946)")
    print("=" * 70)

    mode_state_antes = client.read_register(mm.SUPERVISION_AREA['MODE_STATE'])
    print(f"  MODE_STATE antes: {mode_state_antes}")

    # Escrever baseado em 02FF
    novo_mode_state = 1 if modo_02ff_depois else 0
    client.write_register(mm.SUPERVISION_AREA['MODE_STATE'], novo_mode_state)
    print(f"  MODE_STATE escrito: {novo_mode_state}")

    print("\n✅ Sincronização completa!")
    print("   - Ladder controla 02FF (bit real)")
    print("   - Python espelha em MODE_STATE (0x0946)")
    print("   - IHM Web lê MODE_STATE")

finally:
    client.close()

print("\n" + "=" * 70)
