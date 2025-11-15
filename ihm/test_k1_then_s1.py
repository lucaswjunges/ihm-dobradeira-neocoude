#!/usr/bin/env python3
"""
TESTE SEQUENCIAL: K1 → S1
==========================
Pressiona K1 para ativar Dobra 1, depois S1 para mudar modo
"""
import sys
import time
from modbus_client import ModbusClientWrapper
import modbus_map as mm

def read_all_states(client, title=""):
    """Lê todos os estados relevantes"""
    if title:
        print(f"\n{'=' * 70}")
        print(f" {title}")
        print('=' * 70)

    mode_state = client.read_register(mm.SUPERVISION_AREA['MODE_STATE'])
    mode_text = "AUTO" if mode_state == 1 else "MANUAL" if mode_state == 0 else f"DESCONHECIDO ({mode_state})"

    bend_1_active = client.read_coil(0x0380)  # Bit interno
    led1 = client.read_coil(mm.LEDS['LED1'])  # LED físico

    screen = client.read_register(mm.SUPERVISION_AREA['SCREEN_NUM'])
    cycle = client.read_register(mm.SUPERVISION_AREA['CYCLE_ACTIVE'])

    print(f"""
  MODE_STATE (0x0946):      {mode_state} = {mode_text}
  BEND_1_ACTIVE (0x0380):   {bend_1_active}
  LED1 físico (0x00C0):     {led1}
  SCREEN_NUM (0x0940):      {screen}
  CYCLE_ACTIVE (0x094E):    {cycle}
    """)

    return mode_state, bend_1_active, led1

def press_key(client, key_name, addr):
    """Pressiona uma tecla com pulso"""
    print(f"🔘 Pressionando {key_name} (0x{addr:04X})...")
    client.write_coil(addr, True)
    time.sleep(0.1)
    client.write_coil(addr, False)
    time.sleep(0.5)  # Aguarda processamento
    print(f"✓ {key_name} pressionado")

def main():
    print("=" * 70)
    print(" TESTE: K1 → S1 (Ativar Dobra 1 → Mudar Modo)")
    print("=" * 70)

    client = ModbusClientWrapper(port=mm.MODBUS_CONFIG['port'], stub_mode=False)

    if not client.connected:
        print("❌ CLP não conectado!")
        return 1

    try:
        # FASE 1: Estado inicial
        mode_before, bend1_before, led1_before = read_all_states(client, "FASE 1: ESTADO INICIAL")

        # FASE 2: Pressionar K1
        print("\n" + "=" * 70)
        print(" FASE 2: PRESSIONAR K1 (Dobra 1)")
        print("=" * 70)
        press_key(client, "K1", mm.KEYBOARD_NUMERIC['K1'])
        mode_k1, bend1_k1, led1_k1 = read_all_states(client, "ESTADO APÓS K1")

        if led1_k1 and not led1_before:
            print("✅ LED1 acendeu!")
        elif bend1_k1 and not bend1_before:
            print("✅ Bit BEND_1_ACTIVE ativou!")
        else:
            print("⚠️  K1 não mudou estado visível")

        # FASE 3: Pressionar S1
        print("\n" + "=" * 70)
        print(" FASE 3: PRESSIONAR S1 (Mudança de Modo)")
        print("=" * 70)
        press_key(client, "S1", mm.KEYBOARD_FUNCTION['S1'])
        mode_s1, bend1_s1, led1_s1 = read_all_states(client, "ESTADO APÓS S1")

        # ANÁLISE FINAL
        print("\n" + "=" * 70)
        print(" ANÁLISE FINAL")
        print("=" * 70)

        mode_before_text = "AUTO" if mode_before == 1 else "MANUAL"
        mode_s1_text = "AUTO" if mode_s1 == 1 else "MANUAL"

        print(f"\n📊 MUDANÇAS:")
        print(f"  Modo: {mode_before_text} → {mode_s1_text}")
        print(f"  BEND_1_ACTIVE: {bend1_before} → {bend1_s1}")
        print(f"  LED1: {led1_before} → {led1_s1}")

        if mode_before != mode_s1:
            print(f"\n✅ SUCESSO! Modo mudou de {mode_before_text} para {mode_s1_text}!")
        else:
            print(f"\n⚠️  Modo NÃO mudou (permaneceu {mode_before_text})")
            print("\n🔍 Possíveis causas:")
            print("  1. S1 pode requerer tela específica (não tela 2)")
            print("  2. Ladder pode ter lógica adicional de segurança")
            print("  3. Modo pode estar bloqueado por outra condição")
            print("  4. S1 pode não implementar mudança AUTO/MANUAL no ladder atual")

        return 0

    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        import traceback
        traceback.print_exc()
        return 1

    finally:
        client.close()

if __name__ == '__main__':
    sys.exit(main())
