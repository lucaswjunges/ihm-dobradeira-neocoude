#!/usr/bin/env python3
"""
TESTE CRÍTICO - CONTROLE DE MOTOR VIA REGISTROS HOLDING
==========================================================

Hipótese: CLP não aceita write_coil() para S0/S1, mas pode aceitar
comandos via registros da área SUPERVISION_AREA:

- 0x094A (DIRECTION): 0=Esquerda/Avanço, 1=Direita/Recuo
- 0x094E (CYCLE_ACTIVE): 0=Parado, 1=Ativo

Lógica testada:
1. Escrever DIRECTION = 0 (avanço)
2. Escrever CYCLE_ACTIVE = 1 (iniciar)
3. Aguardar 2s
4. Escrever CYCLE_ACTIVE = 0 (parar)
5. Verificar se motor girou via encoder
"""
import sys
import time
from modbus_client import ModbusClientWrapper
import modbus_map as mm

MOTOR_ON_TIME = 2.0
WRITE_DELAY = 0.5

def test_motor_via_registers():
    print("=" * 70)
    print("  TESTE CRÍTICO - MOTOR VIA REGISTROS HOLDING")
    print("=" * 70)

    client = ModbusClientWrapper(stub_mode=False, port='/dev/ttyUSB0')

    if not client.connected:
        print("❌ CLP não conectado!")
        return False

    print("✅ CLP conectado\n")

    # Verificar 00BE
    modbus_enabled = client.read_coil(mm.CRITICAL_STATES['MODBUS_SLAVE_ENABLED'])
    if not modbus_enabled:
        print("❌ Estado 00BE OFF!")
        client.close()
        return False
    print("✅ Estado 00BE ON\n")

    # === TESTE 1: AVANÇAR (DIRECTION=0) ===
    print("=" * 70)
    print("TESTE 1: AVANÇAR (via registros)")
    print("=" * 70)

    # Ler encoder inicial
    print("\n[1] Lendo encoder inicial...")
    encoder_before = client.read_32bit(
        mm.ENCODER['ANGLE_MSW'],
        mm.ENCODER['ANGLE_LSW']
    )
    if encoder_before is None:
        print("❌ Não conseguiu ler encoder!")
        client.close()
        return False

    angle_before = mm.clp_to_degrees(encoder_before)
    print(f"    Encoder inicial: {encoder_before} → {angle_before:.1f}°")

    # Garantir que motor está parado
    print("\n[2] Garantindo motor parado (CYCLE_ACTIVE=0)...")
    success = client.write_register(mm.SUPERVISION_AREA['CYCLE_ACTIVE'], 0)
    if not success:
        print("❌ Não conseguiu escrever CYCLE_ACTIVE!")
        client.close()
        return False
    time.sleep(WRITE_DELAY)
    print("    ✓ Comando enviado")

    # Confirmar parado
    cycle_state = client.read_register(mm.SUPERVISION_AREA['CYCLE_ACTIVE'])
    print(f"    Confirmado: CYCLE_ACTIVE = {cycle_state}")

    # Configurar direção AVANÇO (0)
    print("\n[3] Configurando direção AVANÇO (DIRECTION=0)...")
    success = client.write_register(mm.SUPERVISION_AREA['DIRECTION'], 0)
    if not success:
        print("❌ Não conseguiu escrever DIRECTION!")
        client.close()
        return False
    time.sleep(WRITE_DELAY)

    direction = client.read_register(mm.SUPERVISION_AREA['DIRECTION'])
    print(f"    Confirmado: DIRECTION = {direction}")

    if direction != 0:
        print("❌ Direção não foi configurada corretamente!")
        client.close()
        return False

    # INICIAR MOTOR (CYCLE_ACTIVE=1)
    print("\n[4] ⚠️⚠️  INICIANDO MOTOR (CYCLE_ACTIVE=1)...")
    print("    Se ladder aceitar comandos via registros, motor vai girar!")

    success = client.write_register(mm.SUPERVISION_AREA['CYCLE_ACTIVE'], 1)
    if not success:
        print("❌ Não conseguiu escrever CYCLE_ACTIVE=1!")
        client.close()
        return False
    time.sleep(WRITE_DELAY)
    print("    ✓ Comando enviado, aguardando processamento...")

    # Verificar se CLP aceitou
    cycle_state = client.read_register(mm.SUPERVISION_AREA['CYCLE_ACTIVE'])
    print(f"    Estado lido de volta: CYCLE_ACTIVE = {cycle_state}")

    if cycle_state != 1:
        print("❌ CLP NÃO aceitou comando CYCLE_ACTIVE=1!")
        print("    → Ladder pode estar bloqueando ou registro é somente leitura")
        client.close()
        return False

    print(f"✅ CYCLE_ACTIVE confirmado = 1!")
    print(f"   👁️  Verificar se motor está girando...")
    print(f"   Mantendo ligado por {MOTOR_ON_TIME}s...")
    time.sleep(MOTOR_ON_TIME)

    # Ler encoder durante movimento
    encoder_during = client.read_32bit(
        mm.ENCODER['ANGLE_MSW'],
        mm.ENCODER['ANGLE_LSW']
    )
    angle_during = mm.clp_to_degrees(encoder_during) if encoder_during else 0
    print(f"    Encoder durante movimento: {encoder_during} → {angle_during:.1f}°")

    # PARAR MOTOR (CYCLE_ACTIVE=0)
    print("\n[5] PARANDO MOTOR (CYCLE_ACTIVE=0)...")
    success = client.write_register(mm.SUPERVISION_AREA['CYCLE_ACTIVE'], 0)
    if not success:
        print("❌ Não conseguiu escrever CYCLE_ACTIVE=0!")
        client.close()
        return False
    time.sleep(WRITE_DELAY)
    print("    ✓ Comando enviado")

    # Confirmar parado
    cycle_state = client.read_register(mm.SUPERVISION_AREA['CYCLE_ACTIVE'])
    print(f"    Confirmado: CYCLE_ACTIVE = {cycle_state}")

    # Ler encoder final
    print("\n[6] Lendo encoder final...")
    encoder_after = client.read_32bit(
        mm.ENCODER['ANGLE_MSW'],
        mm.ENCODER['ANGLE_LSW']
    )
    angle_after = mm.clp_to_degrees(encoder_after) if encoder_after else 0
    print(f"    Encoder final: {encoder_after} → {angle_after:.1f}°")

    # Calcular movimento
    delta = encoder_after - encoder_before
    delta_degrees = angle_after - angle_before

    print("\n" + "=" * 70)
    print("RESULTADO DO TESTE AVANÇO")
    print("=" * 70)
    print(f"  Encoder inicial:  {encoder_before} → {angle_before:.1f}°")
    print(f"  Encoder final:    {encoder_after} → {angle_after:.1f}°")
    print(f"  Variação:         {delta:+d} pulsos ({delta_degrees:+.1f}°)")

    if abs(delta) < 10:
        print("\n❌ MOTOR NÃO GIROU!")
        print("   → Registros DIRECTION/CYCLE_ACTIVE não controlam motor")
        print("   → OU ladder bloqueia ativação")
        client.close()
        return False

    print("\n✅✅✅ MOTOR GIROU! ✅✅✅")
    print("   → Controle via registros FUNCIONA!")
    print("   → IHM web pode usar SUPERVISION_AREA!")

    client.close()
    return True


if __name__ == "__main__":
    try:
        success = test_motor_via_registers()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⚠️  Teste cancelado!")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
