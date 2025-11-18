#!/usr/bin/env python3
"""
Teste para verificar se S1 com 300ms consegue trocar o modo
"""
import sys
import time
from modbus_client import ModbusClient, ModbusConfig

def test_s1_mode_change():
    config = ModbusConfig(port='/dev/ttyUSB0')
    client = ModbusClient(stub_mode=False, config=config)

    if not client.connect():
        print("❌ Falha ao conectar")
        return 1

    print("✅ Conectado ao CLP\n")

    # Bit de modo AUTO/MANUAL
    BIT_MODO = 767  # 02FF

    print("=" * 70)
    print("TESTE: S1 com 300ms de hold_time")
    print("=" * 70)

    # Ler estado inicial
    modo_inicial = client.read_coil(BIT_MODO)
    modo_texto = "AUTO" if modo_inicial else "MANUAL"
    print(f"\n📊 Modo inicial: {modo_texto} (bit {BIT_MODO} = {modo_inicial})")

    print("\n🔘 Pressionando S1 com hold_time de 300ms...")
    success = client.press_key("S1", hold_time=0.3)

    if success:
        print("✅ Comando S1 enviado com sucesso")
    else:
        print("❌ Falha ao enviar S1")
        client.disconnect()
        return 1

    print("⏱️  Aguardando 2 segundos para o CLP processar...")
    time.sleep(2)

    # Ler estado após pressionar S1
    modo_final = client.read_coil(BIT_MODO)
    modo_texto_final = "AUTO" if modo_final else "MANUAL"
    print(f"📊 Modo final: {modo_texto_final} (bit {BIT_MODO} = {modo_final})")

    print("\n" + "=" * 70)
    if modo_inicial != modo_final:
        print("✅ SUCESSO! Modo mudou:")
        print(f"   {modo_texto} → {modo_texto_final}")
        print("\n🎯 O botão S1 agora está funcionando corretamente!")
    else:
        print("⚠️  Modo não mudou")
        print("\n🔍 Possíveis causas:")
        print("   1. Sistema em estado que bloqueia mudança de modo (ex: ciclo ativo)")
        print("   2. Bit 0106 (262) está ON (bloqueia S1)")
        print("   3. Lógica do ladder requer condições adicionais")
        print("\n🧪 Vou verificar as condições de bloqueio:")

        bit_0106 = client.read_coil(262)
        print(f"   - Bit 0106 (bloqueio): {bit_0106}")

        # Verificar estados de ciclo
        for i in range(9):
            if i == 6 or i == 7:
                continue
            bit_ciclo = client.read_coil(768 + i)
            if bit_ciclo:
                print(f"   - Ciclo ativo: Estado {i} está ON (bit {768+i})")
    print("=" * 70)

    client.disconnect()
    print("\n✅ Desconectado")
    return 0

if __name__ == '__main__':
    sys.exit(test_s1_mode_change())
