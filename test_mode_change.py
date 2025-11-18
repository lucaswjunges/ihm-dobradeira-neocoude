#!/usr/bin/env python3
"""
Teste para verificar se o bit de modo muda ao pressionar S1
"""
import sys
import time
from modbus_client import ModbusClient, ModbusConfig

def test_mode_change():
    config = ModbusConfig(port='/dev/ttyUSB0')
    client = ModbusClient(stub_mode=False, config=config)

    if not client.connect():
        print("❌ Falha ao conectar")
        return 1

    print("✅ Conectado ao CLP\n")

    # Bit 02FF (767) - bit de modo AUTO/MANUAL
    bit_modo = 767

    # S1 button (220 decimal)
    s1_button = 220

    print("=" * 60)
    print("TESTE: Mudança de modo com S1")
    print("=" * 60)

    # Ler estado inicial
    modo_inicial = client.read_coil(bit_modo)
    modo_texto = "AUTO" if modo_inicial else "MANUAL" if modo_inicial is False else "ERRO"
    print(f"\n📊 Estado inicial: Bit {bit_modo} = {modo_inicial} → {modo_texto}")

    print("\n🔘 Pressionando S1...")
    client.press_key("S1")

    print("⏱️  Aguardando 2 segundos...")
    time.sleep(2)

    # Ler estado após pressionar S1
    modo_final = client.read_coil(bit_modo)
    modo_texto_final = "AUTO" if modo_final else "MANUAL" if modo_final is False else "ERRO"
    print(f"📊 Estado após S1: Bit {bit_modo} = {modo_final} → {modo_texto_final}")

    if modo_inicial != modo_final:
        print("\n✅ SUCESSO: Modo mudou de",
              "AUTO" if modo_inicial else "MANUAL",
              "para",
              "AUTO" if modo_final else "MANUAL")
    else:
        print("\n⚠️  ATENÇÃO: Modo não mudou após pressionar S1")
        print("   Possíveis causas:")
        print("   - Bit 767 não é o bit de modo")
        print("   - S1 requer condições específicas para mudar modo")
        print("   - Sistema em estado que impede mudança de modo")

    print("\n🔍 Vou monitorar o bit por 10 segundos...")
    print("   Pressione S1 manualmente durante este tempo:")

    for i in range(10):
        modo = client.read_coil(bit_modo)
        modo_texto = "AUTO" if modo else "MANUAL" if modo is False else "ERRO"
        print(f"   [{i+1:2d}/10] Bit {bit_modo}: {modo} → {modo_texto}")
        time.sleep(1)

    client.disconnect()
    print("\n✅ Desconectado")
    return 0

if __name__ == '__main__':
    sys.exit(test_mode_change())
