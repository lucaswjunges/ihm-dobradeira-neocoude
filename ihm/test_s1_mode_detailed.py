#!/usr/bin/env python3
"""
TESTE DETALHADO: Botão S1 - Mudança AUTO/MANUAL
=================================================
Engenheiro de Controle e Automação Sênior
Data: 14 de novembro de 2025

Este teste verifica:
1. Estado atual do sistema (AUTO/MANUAL)
2. LEDs ativos antes da mudança
3. Bit de proteção 02FF
4. Pressionamento do botão S1
5. Mudança do MODE_STATE
6. LEDs após a mudança
7. Monostável MONO_MODE
"""

import sys
import time
from modbus_client import ModbusClientWrapper
import modbus_map as mm

def print_separator(title=""):
    print("=" * 70)
    if title:
        print(f" {title}")
        print("=" * 70)

def read_mode_indicators(client):
    """Lê todos os indicadores relacionados ao modo"""
    print("\n📊 INDICADORES DE MODO:")
    print("-" * 70)

    # Modo atual (área de supervisão)
    mode_state = client.read_register(mm.SUPERVISION_AREA['MODE_STATE'])
    mode_text = "AUTO" if mode_state == 1 else "MANUAL" if mode_state == 0 else f"DESCONHECIDO ({mode_state})"
    print(f"  MODE_STATE (0x0946):  {mode_state} = {mode_text}")

    # Bit de proteção
    protection = client.read_coil(0x02FF)  # 767 decimal
    prot_text = "ATIVO (bloqueado)" if protection else "INATIVO (permitido)"
    print(f"  Proteção 02FF (767):  {protection} = {prot_text}")

    # Monostável de modo (se disponível)
    try:
        mono_mode = client.read_coil(0x0376)  # 886 decimal
        print(f"  MONO_MODE (0x0376):   {mono_mode}")
    except:
        print(f"  MONO_MODE (0x0376):   N/A")

    # Estado do botão S1
    s1_state = client.read_coil(mm.KEYBOARD_FUNCTION['S1'])
    print(f"  Botão S1 (00DC):      {s1_state}")

    # Ciclo ativo
    cycle = client.read_register(mm.SUPERVISION_AREA['CYCLE_ACTIVE'])
    print(f"  Ciclo ativo:          {cycle}")

    return mode_state, protection

def read_all_leds(client):
    """Lê todos os LEDs"""
    print("\n💡 ESTADO DOS LEDs:")
    print("-" * 70)

    leds = {}
    for name, address in mm.LEDS.items():
        state = client.read_coil(address)
        leds[name] = state
        status = "🟢 ON" if state else "⚫ OFF"
        print(f"  {name} (0x{address:04X}): {status}")

    return leds

def press_s1_button(client):
    """Pressiona o botão S1 com pulso de 100ms"""
    print("\n🔘 PRESSIONANDO BOTÃO S1 (00DC)...")
    print("-" * 70)

    s1_addr = mm.KEYBOARD_FUNCTION['S1']

    # Pulso: ON → Wait → OFF
    print(f"  1. Setando coil 0x{s1_addr:04X} = ON")
    success1 = client.write_coil(s1_addr, True)
    print(f"     Resultado: {'✅ OK' if success1 else '❌ FALHA'}")

    print(f"  2. Aguardando 100ms...")
    time.sleep(0.1)

    print(f"  3. Setando coil 0x{s1_addr:04X} = OFF")
    success2 = client.write_coil(s1_addr, False)
    print(f"     Resultado: {'✅ OK' if success2 else '❌ FALHA'}")

    print(f"  4. Aguardando 500ms para ladder processar...")
    time.sleep(0.5)

    return success1 and success2

def main():
    print_separator("TESTE S1: MUDANÇA AUTO/MANUAL")
    print(f"Data/Hora: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Porta: {mm.MODBUS_CONFIG['port']}")
    print(f"Baudrate: {mm.MODBUS_CONFIG['baudrate']}")

    # Conectar
    print("\n🔌 CONECTANDO AO CLP...")
    client = ModbusClientWrapper(
        port=mm.MODBUS_CONFIG['port'],
        stub_mode=False
    )

    if not client.connected:
        print("❌ ERRO: Não foi possível conectar ao CLP!")
        print("   Verifique:")
        print("   - Porta USB correta")
        print("   - CLP ligado e em RUN")
        print("   - Cabo RS485 conectado")
        return 1

    print("✅ CLP conectado!")

    try:
        # FASE 1: Estado ANTES
        print_separator("FASE 1: ESTADO ANTES DA MUDANÇA")
        mode_before, protection = read_mode_indicators(client)
        leds_before = read_all_leds(client)

        # Verificar se pode mudar de modo
        print("\n⚠️  VERIFICAÇÕES DE SEGURANÇA:")
        print("-" * 70)

        cycle = client.read_register(mm.SUPERVISION_AREA['CYCLE_ACTIVE'])
        if cycle:
            print("  ❌ BLOQUEADO: Ciclo ativo! Não pode mudar de modo durante operação.")
            return 1
        else:
            print("  ✅ OK: Máquina parada, pode mudar de modo.")

        if protection:
            print("  ⚠️  AVISO: Bit de proteção 02FF ativo - pode bloquear mudança.")
        else:
            print("  ✅ OK: Bit de proteção inativo.")

        # FASE 2: Pressionar S1
        print_separator("FASE 2: PRESSIONAMENTO DO BOTÃO S1")
        success = press_s1_button(client)

        if not success:
            print("❌ ERRO ao pressionar S1!")
            return 1

        # FASE 3: Estado DEPOIS
        print_separator("FASE 3: ESTADO DEPOIS DA MUDANÇA")
        mode_after, _ = read_mode_indicators(client)
        leds_after = read_all_leds(client)

        # ANÁLISE
        print_separator("ANÁLISE DE RESULTADOS")

        mode_before_text = "AUTO" if mode_before == 1 else "MANUAL"
        mode_after_text = "AUTO" if mode_after == 1 else "MANUAL"

        print(f"\n📊 MUDANÇA DE MODO:")
        print(f"   Antes:  {mode_before_text} (MODE_STATE={mode_before})")
        print(f"   Depois: {mode_after_text} (MODE_STATE={mode_after})")

        if mode_before != mode_after:
            print(f"\n✅ SUCESSO! Modo mudou de {mode_before_text} para {mode_after_text}")
            print("\n💡 Mudanças nos LEDs:")
            for name in leds_before:
                if leds_before[name] != leds_after[name]:
                    before_str = "🟢" if leds_before[name] else "⚫"
                    after_str = "🟢" if leds_after[name] else "⚫"
                    print(f"   {name}: {before_str} → {after_str}")
        else:
            print(f"\n⚠️  ATENÇÃO: Modo NÃO mudou (permaneceu {mode_before_text})")
            print("\n🔍 Possíveis causas:")
            print("   1. Ladder requer condições específicas (ex: dobra 1 ativa)")
            print("   2. Bit de proteção 02FF bloqueando")
            print("   3. Pulso muito curto (aumentar tempo)")
            print("   4. CLP não está na tela correta")

            # Verificar tela atual
            screen = client.read_register(mm.SUPERVISION_AREA['SCREEN_NUM'])
            print(f"\n   Tela atual: {screen}")
            print("   Nota: Alguns CLPs só permitem mudança de modo em telas específicas")

        print_separator("FIM DO TESTE")
        return 0

    except Exception as e:
        print(f"\n❌ ERRO durante teste: {e}")
        import traceback
        traceback.print_exc()
        return 1

    finally:
        client.close()

if __name__ == '__main__':
    sys.exit(main())
