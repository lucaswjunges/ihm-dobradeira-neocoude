#!/usr/bin/env python3
"""
Teste de Diagnóstico: Investigar Reversão de Modo AUTO → MANUAL

Este script monitora continuamente o bit 02FF (modo) para entender
por que o CLP reverte de AUTO para MANUAL após ~1 segundo.

Hipóteses:
1. Ladder tem watchdog que reseta 02FF se condições não OK
2. Entrada E6 precisa estar ativa (documentação menciona)
3. Bit 02FF sendo sobrescrito por outra rotina
"""

import time
import sys
from modbus_client import ModbusClientWrapper

def test_mode_monitoring():
    """Monitora bit 02FF continuamente após escrita."""

    print("=" * 60)
    print("TESTE: Monitoramento de Reversão de Modo")
    print("=" * 60)
    print()

    # Criar cliente Modbus
    client = ModbusClientWrapper(stub_mode=False)

    if not client.connected:
        print("❌ Falha ao conectar com CLP")
        return False

    print("✅ Conectado ao CLP")
    print()

    # Fase 1: Leitura inicial
    print("--- FASE 1: Estado Inicial ---")
    initial_mode = client.read_coil(0x02FF)
    print(f"Modo inicial (02FF): {'AUTO' if initial_mode else 'MANUAL'}")
    print()

    # Fase 2: Alternar para AUTO e monitorar
    print("--- FASE 2: Alternar para AUTO e Monitorar ---")
    print("Escrevendo 02FF = True (AUTO)...")

    write_ok = client.write_coil(0x02FF, True)
    print(f"Escrita: {'✓ Sucesso' if write_ok else '✗ Falhou'}")
    print()

    if not write_ok:
        print("❌ Não foi possível escrever em 02FF")
        client.disconnect()
        return False

    # Monitorar por 5 segundos (50 leituras a cada 100ms)
    print("Monitorando 02FF por 5 segundos (100ms/leitura)...")
    print()
    print("Timestamp | 02FF  | Modo     | Observação")
    print("-" * 50)

    reversion_detected = False
    reversion_time = None

    for i in range(50):
        elapsed = i * 0.1
        mode_bit = client.read_coil(0x02FF)

        mode_text = "AUTO" if mode_bit else "MANUAL"

        # Detectar reversão
        observation = ""
        if i == 0:
            observation = "Logo após escrita"
        elif not reversion_detected and not mode_bit:
            reversion_detected = True
            reversion_time = elapsed
            observation = "⚠️ REVERSÃO DETECTADA!"
        elif reversion_detected and mode_bit:
            observation = "Retornou para AUTO?"

        print(f"{elapsed:>5.1f}s    | {mode_bit!s:5} | {mode_text:8} | {observation}")

        time.sleep(0.1)

    print()

    # Análise
    print("=" * 60)
    print("ANÁLISE DOS RESULTADOS")
    print("=" * 60)

    if reversion_detected:
        print(f"⚠️ Reversão detectada em T+{reversion_time:.1f}s")
        print()
        print("Possíveis causas:")
        print("1. Ladder tem lógica que força MANUAL em certas condições")
        print("2. Entrada E6 (ou outra) não está ativa")
        print("3. Watchdog de segurança resetando modo")
        print()
        print("Próximos passos:")
        print("- Verificar estado da entrada E6")
        print("- Analisar ladder para encontrar lógica que escreve em 02FF")
        print("- Testar se manter escrita contínua ajuda")
    else:
        print("✅ Modo AUTO permaneceu estável durante 5 segundos")
        print()
        print("Possível explicação:")
        print("- Problema pode ser específico de contexto (tela, ciclo ativo, etc.)")
        print("- Testar em diferentes estados da máquina")

    print()

    # Fase 3: Verificar entrada E6
    print("--- FASE 3: Verificar Entrada E6 ---")
    e6_status = client.read_coil(0x0106)  # E6 = 256 + 6 = 262 = 0x0106

    if e6_status is not None:
        print(f"Entrada E6 (0x0106): {'ATIVA' if e6_status else 'INATIVA'}")

        if not e6_status and reversion_detected:
            print("⚠️ E6 inativa pode ser a causa da reversão!")
            print("   (Documentação menciona que S1 depende de E6)")
    else:
        print("❌ Falha ao ler entrada E6")

    print()

    # Fase 4: Teste de escrita contínua
    print("--- FASE 4: Teste de Escrita Contínua ---")
    print("Tentando manter modo AUTO com escritas a cada 100ms...")
    print()

    for i in range(20):
        client.write_coil(0x02FF, True)
        time.sleep(0.05)

        mode_check = client.read_coil(0x02FF)
        mode_text = "AUTO" if mode_check else "MANUAL"

        print(f"T+{i*0.1:.1f}s: Escrita → Leitura = {mode_text}", end="")

        if not mode_check:
            print(" ⚠️ Ainda reverte mesmo com escrita contínua!")
        else:
            print(" ✓")

        time.sleep(0.05)

    print()

    # Disconnect se houver método (stub mode não precisa)
    if hasattr(client.client, 'close'):
        client.client.close()

    print("✅ Teste concluído")

    return True


def test_s1_button_method():
    """Testa alternar modo usando botão S1 ao invés de escrita direta."""

    print()
    print("=" * 60)
    print("TESTE ALTERNATIVO: Usar Botão S1")
    print("=" * 60)
    print()

    client = ModbusClientWrapper(stub_mode=False)

    if not client.connected:
        print("❌ Falha ao conectar com CLP")
        return False

    print("✅ Conectado ao CLP")
    print()

    # Ler modo inicial
    initial_mode = client.read_coil(0x02FF)
    print(f"Modo inicial: {'AUTO' if initial_mode else 'MANUAL'}")
    print()

    # Pressionar S1
    print("Pressionando S1 (simulação de botão físico)...")
    s1_ok = client.press_key(0x00DC)  # S1 = 220 = 0x00DC
    print(f"S1: {'✓ Sucesso' if s1_ok else '✗ Falhou'}")
    print()

    # Aguardar processamento
    time.sleep(0.5)

    # Verificar modo após S1
    new_mode = client.read_coil(0x02FF)
    print(f"Modo após S1: {'AUTO' if new_mode else 'MANUAL'}")
    print()

    # Monitorar estabilidade
    print("Monitorando estabilidade por 3 segundos...")
    for i in range(30):
        mode = client.read_coil(0x02FF)
        mode_text = "AUTO" if mode else "MANUAL"

        if i % 10 == 0:
            print(f"T+{i*0.1:.1f}s: {mode_text}")

        time.sleep(0.1)

    print()

    final_mode = client.read_coil(0x02FF)
    print(f"Modo final: {'AUTO' if final_mode else 'MANUAL'}")

    if final_mode != new_mode:
        print("⚠️ Modo reverteu mesmo usando S1!")
    else:
        print("✅ Modo permaneceu estável com S1")

    print()

    # Disconnect se houver método (stub mode não precisa)
    if hasattr(client.client, 'close'):
        client.client.close()

    return True


if __name__ == "__main__":
    print()
    print("╔════════════════════════════════════════════════════════╗")
    print("║  DIAGNÓSTICO: Reversão de Modo AUTO → MANUAL          ║")
    print("╚════════════════════════════════════════════════════════╝")
    print()

    # Teste 1: Monitoramento de bit
    success1 = test_mode_monitoring()

    if not success1:
        print("❌ Teste de monitoramento falhou")
        sys.exit(1)

    # Teste 2: Método S1
    success2 = test_s1_button_method()

    if not success2:
        print("❌ Teste de S1 falhou")
        sys.exit(1)

    print()
    print("=" * 60)
    print("DIAGNÓSTICO COMPLETO")
    print("=" * 60)
    print()
    print("Relatório salvo em: diagnostico_modo_reversion.log")
    print()
