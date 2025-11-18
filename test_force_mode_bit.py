#!/usr/bin/env python3
"""
Teste para forçar mudança de modo diretamente
Abordagem 1: Escrever diretamente no bit 767 (modo)
Abordagem 2: Simular o monoastável 0376
"""
import sys
import time
from modbus_client import ModbusClient, ModbusConfig

def test_force_mode():
    config = ModbusConfig(port='/dev/ttyUSB0')
    client = ModbusClient(stub_mode=False, config=config)

    if not client.connect():
        print("❌ Falha ao conectar")
        return 1

    print("✅ Conectado ao CLP\n")

    BIT_MODO = 767      # 02FF - bit de modo
    BIT_MONO = 886      # 0376 - monoastável

    print("=" * 70)
    print("TESTE: Forçar mudança de modo via Modbus")
    print("=" * 70)

    # Estado inicial
    modo_inicial = client.read_coil(BIT_MODO)
    print(f"\n📊 Modo inicial: {'AUTO' if modo_inicial else 'MANUAL'} (bit {BIT_MODO}={modo_inicial})")

    print("\n" + "=" * 70)
    print("ABORDAGEM 1: Escrever diretamente no bit de modo (767)")
    print("=" * 70)

    novo_modo = not modo_inicial
    print(f"🔧 Tentando escrever {novo_modo} no bit {BIT_MODO}...")

    if client.write_coil(BIT_MODO, novo_modo):
        print("✅ Escrita bem-sucedida")
        time.sleep(0.5)

        modo_verificado = client.read_coil(BIT_MODO)
        print(f"📊 Modo após escrita: {'AUTO' if modo_verificado else 'MANUAL'} (bit={modo_verificado})")

        if modo_verificado == novo_modo:
            print("✅ SUCESSO! Conseguimos mudar o modo escrevendo diretamente no bit 767!")
            client.disconnect()
            return 0
        else:
            print("⚠️  O bit foi resetado - provavelmente é read-only ou controlado por ladder")
    else:
        print("❌ Falha ao escrever no bit 767")

    print("\n" + "=" * 70)
    print("ABORDAGEM 2: Simular o monoastável (bit 886)")
    print("=" * 70)

    print(f"🔧 Tentando acionar o monoastável (bit {BIT_MONO})...")
    print("   Sequência: ON → 300ms → OFF")

    if client.write_coil(BIT_MONO, True):
        print("✅ Monoastável ativado (ON)")
        time.sleep(0.3)

        if client.write_coil(BIT_MONO, False):
            print("✅ Monoastável desativado (OFF)")
            time.sleep(0.5)

            modo_final = client.read_coil(BIT_MODO)
            print(f"📊 Modo após monoastável: {'AUTO' if modo_final else 'MANUAL'} (bit={modo_final})")

            if modo_final != modo_inicial:
                print("✅ SUCESSO! Conseguimos mudar o modo acionando o monoastável!")
                client.disconnect()
                return 0
            else:
                print("⚠️  Modo não mudou - monoastável pode ter condições adicionais")
        else:
            print("❌ Falha ao desativar monoastável")
    else:
        print("❌ Falha ao ativar monoastável")

    print("\n" + "=" * 70)
    print("CONCLUSÃO:")
    print("=" * 70)
    print("❌ Nenhuma abordagem via Modbus conseguiu mudar o modo.")
    print("🔍 Isso significa que:")
    print("   1. S1 (00DC) é uma ENTRADA da IHM física, não um coil do CLP")
    print("   2. O CLP não pode forçar mudança de modo via Modbus")
    print("   3. A IHM web pode apenas MONITORAR o modo, não alterá-lo")
    print("\n💡 SOLUÇÃO:")
    print("   - Use o botão S1 FÍSICO da máquina para mudar o modo")
    print("   - A IHM web exibirá o modo atual em tempo real")
    print("=" * 70)

    client.disconnect()
    return 1

if __name__ == '__main__':
    sys.exit(test_force_mode())
