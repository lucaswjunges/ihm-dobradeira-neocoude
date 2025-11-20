#!/usr/bin/env python3
"""
TESTE CRÍTICO AUTOMATIZADO - S0/S1 MOTOR
=========================================

Testa controle de motor com TIMERS ADEQUADOS:
- 500ms após write antes de read
- 100ms entre reads
- 2s com motor ligado (validação)

SEM input() - roda automaticamente.
"""
import sys
import time
from modbus_client import ModbusClientWrapper
import modbus_map as mm

WRITE_READ_DELAY = 0.5
READ_DELAY = 0.1
MOTOR_ON_TIME = 2.0

def test_motor_s0_s1():
    print("=" * 70)
    print("TESTE CRÍTICO AUTOMATIZADO - MOTOR S0/S1")
    print("=" * 70)
    
    client = ModbusClientWrapper(stub_mode=False, port='/dev/ttyUSB0')
    
    if not client.connected:
        print("❌ CLP não conectado!")
        return False
    
    print("✅ CLP conectado")
    
    # Verificar 00BE
    estado = client.read_coil(mm.CRITICAL_STATES['MODBUS_SLAVE_ENABLED'])
    if not estado:
        print("❌ Estado 00BE OFF!")
        client.close()
        return False
    print("✅ Estado 00BE ON\n")
    
    # === TESTE S0 (AVANÇAR) ===
    print("=" * 70)
    print("TESTE S0 (AVANÇAR)")
    print("=" * 70)
    
    # 1. Garantir S0 e S1 OFF
    print("\n[1] Garantindo S0 e S1 estão OFF...")
    client.write_coil(mm.DIGITAL_OUTPUTS['S0'], False)
    time.sleep(WRITE_READ_DELAY)
    client.write_coil(mm.DIGITAL_OUTPUTS['S1'], False)
    time.sleep(WRITE_READ_DELAY)
    print("✓ Comandos enviados")
    
    # 2. Confirmar OFF
    s0_before = client.read_coil(mm.DIGITAL_OUTPUTS['S0'])
    time.sleep(READ_DELAY)
    s1_before = client.read_coil(mm.DIGITAL_OUTPUTS['S1'])
    time.sleep(READ_DELAY)
    print(f"[2] Estado confirmado: S0={s0_before}, S1={s1_before}")
    
    if s0_before or s1_before:
        print("❌ Motor ainda ativo após desligar!")
        client.close()
        return False
    print("✓ Motor confirmado OFF")
    
    # 3. Ligar S0
    print("\n[3] ⚠️⚠️  LIGANDO S0 (MOTOR VAI GIRAR)...")
    client.write_coil(mm.DIGITAL_OUTPUTS['S0'], True)
    time.sleep(WRITE_READ_DELAY)  # Aguardar CLP processar
    print("✓ Comando S0=ON enviado, aguardou 500ms")
    
    # 4. Confirmar S0 ON
    print("[4] Lendo S0 para confirmar ativação...")
    s0_on = client.read_coil(mm.DIGITAL_OUTPUTS['S0'])
    time.sleep(READ_DELAY)
    
    if s0_on is None:
        print("❌ FALHA: Não conseguiu ler S0!")
        client.write_coil(mm.DIGITAL_OUTPUTS['S0'], False)
        client.close()
        return False
    
    if not s0_on:
        print("❌ FALHA CRÍTICA: S0 não ativou após write!")
        print("   → Ladder pode estar bloqueando")
        print("   → CLP pode estar em modo PROGRAM")
        client.close()
        return False
    
    print("✅✅ S0 CONFIRMADO ON!")
    print(f"   👁️  Motor deve estar girando ANTI-HORÁRIO")
    print(f"   Mantendo ligado por {MOTOR_ON_TIME}s...")
    time.sleep(MOTOR_ON_TIME)
    
    # 5. Desligar S0
    print("\n[5] Desligando S0...")
    client.write_coil(mm.DIGITAL_OUTPUTS['S0'], False)
    time.sleep(WRITE_READ_DELAY)
    print("✓ Comando S0=OFF enviado, aguardou 500ms")
    
    # 6. Confirmar S0 OFF
    print("[6] Lendo S0 para confirmar desligamento...")
    s0_off = client.read_coil(mm.DIGITAL_OUTPUTS['S0'])
    time.sleep(READ_DELAY)
    
    if s0_off is None:
        print("❌ FALHA: Não conseguiu ler S0!")
        client.close()
        return False
    
    if s0_off:
        print("❌ FALHA CRÍTICA: S0 não desligou!")
        print("   ⚠️⚠️  MOTOR AINDA LIGADO!")
        client.close()
        return False
    
    print("✅✅ S0 CONFIRMADO OFF!")
    print("   👁️  Motor deve estar PARADO\n")
    
    # Intervalo segurança
    print("⏳ Aguardando 3s (segurança)...")
    time.sleep(3.0)
    
    # === TESTE S1 (RECUAR) ===
    print("\n" + "=" * 70)
    print("TESTE S1 (RECUAR)")
    print("=" * 70)
    
    # 7. Confirmar S0 OFF antes de ligar S1
    print("\n[7] Confirmando S0 OFF (segurança)...")
    s0_check = client.read_coil(mm.DIGITAL_OUTPUTS['S0'])
    time.sleep(READ_DELAY)
    
    if s0_check:
        print("❌ S0 ainda ON - não seguro ligar S1!")
        client.close()
        return False
    print("✓ S0 confirmado OFF")
    
    # 8. Ligar S1
    print("\n[8] ⚠️⚠️  LIGANDO S1 (MOTOR VAI GIRAR REVERSO)...")
    client.write_coil(mm.DIGITAL_OUTPUTS['S1'], True)
    time.sleep(WRITE_READ_DELAY)
    print("✓ Comando S1=ON enviado, aguardou 500ms")
    
    # 9. Confirmar S1 ON
    print("[9] Lendo S1 para confirmar ativação...")
    s1_on = client.read_coil(mm.DIGITAL_OUTPUTS['S1'])
    time.sleep(READ_DELAY)
    
    if s1_on is None:
        print("❌ FALHA: Não conseguiu ler S1!")
        client.write_coil(mm.DIGITAL_OUTPUTS['S1'], False)
        client.close()
        return False
    
    if not s1_on:
        print("❌ FALHA CRÍTICA: S1 não ativou!")
        client.close()
        return False
    
    print("✅✅ S1 CONFIRMADO ON!")
    print(f"   👁️  Motor deve estar girando HORÁRIO")
    print(f"   Mantendo ligado por {MOTOR_ON_TIME}s...")
    time.sleep(MOTOR_ON_TIME)
    
    # 10. Desligar S1
    print("\n[10] Desligando S1...")
    client.write_coil(mm.DIGITAL_OUTPUTS['S1'], False)
    time.sleep(WRITE_READ_DELAY)
    print("✓ Comando S1=OFF enviado, aguardou 500ms")
    
    # 11. Confirmar S1 OFF
    print("[11] Lendo S1 para confirmar desligamento...")
    s1_off = client.read_coil(mm.DIGITAL_OUTPUTS['S1'])
    time.sleep(READ_DELAY)
    
    if s1_off is None:
        print("❌ FALHA: Não conseguiu ler S1!")
        client.close()
        return False
    
    if s1_off:
        print("❌ FALHA CRÍTICA: S1 não desligou!")
        client.close()
        return False
    
    print("✅✅ S1 CONFIRMADO OFF!")
    print("   👁️  Motor deve estar PARADO\n")
    
    client.close()
    
    print("\n" + "=" * 70)
    print("🎉🎉🎉 TODOS OS TESTES PASSARAM! 🎉🎉🎉")
    print("=" * 70)
    print("\n✅ S0 (AVANÇAR): Liga → Confirma ON → Desliga → Confirma OFF")
    print("✅ S1 (RECUAR): Liga → Confirma ON → Desliga → Confirma OFF")
    print("\nTIMINGS VALIDADOS:")
    print(f"  ✓ Write→Read delay: {WRITE_READ_DELAY*1000:.0f}ms")
    print(f"  ✓ Read delay: {READ_DELAY*1000:.0f}ms")
    print(f"  ✓ Motor ON time: {MOTOR_ON_TIME:.1f}s")
    print("\n🚀 SEGUNDA-FEIRA VAI DAR CERTO!")
    print("   Interface web usa EXATAMENTE os mesmos comandos.")
    print("=" * 70 + "\n")
    
    return True

if __name__ == "__main__":
    try:
        success = test_motor_s0_s1()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⚠️  Teste cancelado!")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
