#!/usr/bin/env python3
"""
Teste detalhado para entender a lógica de modo AUTO/MANUAL
"""
import sys
import time
from modbus_client import ModbusClient, ModbusConfig

def test_mode_detailed():
    config = ModbusConfig(port='/dev/ttyUSB0')
    client = ModbusClient(stub_mode=False, config=config)

    if not client.connect():
        print("❌ Falha ao conectar")
        return 1

    print("✅ Conectado ao CLP\n")

    # Bits envolvidos na lógica do modo
    BIT_S1 = 220        # 00DC - botão S1
    BIT_0106 = 262      # 0106 - condição de bloqueio
    BIT_0376 = 886      # 0376 - monoastável ativado por S1
    BIT_MODO = 767      # 02FF - bit de modo AUTO(1)/MANUAL(0)

    print("=" * 70)
    print("ANÁLISE DETALHADA: Lógica de modo AUTO/MANUAL")
    print("=" * 70)

    # Ler todos os bits envolvidos
    print("\n📊 Estado atual dos bits:")
    print(f"   BIT S1    (220):  {client.read_coil(BIT_S1)}")
    print(f"   BIT 0106  (262):  {client.read_coil(BIT_0106)} ← Condição de bloqueio")
    print(f"   BIT 0376  (886):  {client.read_coil(BIT_0376)} ← Monoastável (S1 trigger)")
    print(f"   BIT MODO  (767):  {client.read_coil(BIT_MODO)} ← 0=MANUAL, 1=AUTO")

    modo = client.read_coil(BIT_MODO)
    print(f"\n🎯 Modo atual: {'AUTO' if modo else 'MANUAL'}")

    # Verificar se bit 0106 está bloqueando
    bit_0106 = client.read_coil(BIT_0106)
    if bit_0106:
        print(f"\n⚠️  ATENÇÃO: Bit 0106 está ON! Isso bloqueia a mudança de modo.")
        print("   A lógica do ladder requer que bit 0106 esteja OFF para S1 funcionar.")

    print("\n🔘 Pressionando S1 via Modbus...")
    client.press_key("S1")

    print("⏱️  Monitorando bits por 3 segundos após S1:")
    for i in range(6):
        bit_0106 = client.read_coil(BIT_0106)
        bit_0376 = client.read_coil(BIT_0376)
        bit_modo = client.read_coil(BIT_MODO)
        modo_texto = "AUTO" if bit_modo else "MANUAL"
        print(f"   [{i*0.5:.1f}s] 0106:{bit_0106:5} | 0376:{bit_0376:5} | MODO:{bit_modo:5} ({modo_texto})")
        time.sleep(0.5)

    print("\n🔍 Agora vou monitorar enquanto você pressiona S1 FISICAMENTE:")
    print("   Pressione o botão S1 físico da máquina...\n")

    ultimo_modo = client.read_coil(BIT_MODO)
    for i in range(20):
        bit_0106 = client.read_coil(BIT_0106)
        bit_0376 = client.read_coil(BIT_0376)
        bit_modo = client.read_coil(BIT_MODO)
        modo_texto = "AUTO" if bit_modo else "MANUAL"

        # Detectar mudança
        mudou = "🔄 MUDOU!" if bit_modo != ultimo_modo else ""
        print(f"   [{i+1:2d}/20] 0106:{bit_0106:5} | 0376:{bit_0376:5} | MODO:{bit_modo:5} ({modo_texto:6}) {mudou}")

        ultimo_modo = bit_modo
        time.sleep(0.5)

    client.disconnect()
    print("\n✅ Desconectado")
    return 0

if __name__ == '__main__':
    sys.exit(test_mode_detailed())
