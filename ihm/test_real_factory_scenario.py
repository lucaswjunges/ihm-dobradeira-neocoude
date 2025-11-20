#!/usr/bin/env python3
"""
TESTE CRÍTICO DE CENÁRIO REAL - MOTOR S0/S1
============================================

Teste RIGOROSO com timers adequados para CLP industrial.

IMPORTANTE:
- CLP tem scan time ~6ms/K (programa típico ~50K = 300ms)
- Saídas físicas levam ~50-100ms para ativar
- Modbus RTU @ 57600 bps tem latência ~20ms por transação

TIMINGS USADOS:
- Após WRITE: aguarda 500ms (tempo para CLP processar e ativar saída)
- Após READ: aguarda 100ms (evita saturar barramento Modbus)
"""
import sys
import time
from modbus_client import ModbusClientWrapper
import modbus_map as mm

# CONFIGURAÇÕES DE TIMING (crítico para confiabilidade)
WRITE_TO_READ_DELAY = 0.5    # 500ms após escrever antes de ler
READ_TO_WRITE_DELAY = 0.1    # 100ms entre leituras
MOTOR_ON_DURATION = 2.0      # 2 segundos com motor ligado
BETWEEN_TESTS_DELAY = 3.0    # 3 segundos entre S0 e S1

def print_section(title):
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)

def wait(seconds, description):
    """Aguarda com feedback visual."""
    print(f"⏳ Aguardando {seconds}s ({description})...")
    time.sleep(seconds)

def test_s0_avancar(client):
    """Teste CRÍTICO de S0 (AVANÇAR)."""
    print_section("TESTE S0 (AVANÇAR - Anti-horário)")

    # PASSO 1: Estado inicial
    print("\n[1/8] Lendo estado inicial...")
    s0_inicial = client.read_coil(mm.DIGITAL_OUTPUTS['S0'])
    wait(READ_TO_WRITE_DELAY, "evitar saturação")
    s1_inicial = client.read_coil(mm.DIGITAL_OUTPUTS['S1'])
    wait(READ_TO_WRITE_DELAY, "evitar saturação")
    print(f"      S0={s0_inicial}, S1={s1_inicial}")

    if s0_inicial is None or s1_inicial is None:
        print("❌ FALHA: Não conseguiu ler estado!")
        return False

    if s0_inicial or s1_inicial:
        print("⚠️  Desligando motor...")
        if s0_inicial:
            client.write_coil(mm.DIGITAL_OUTPUTS['S0'], False)
            wait(WRITE_TO_READ_DELAY, "CLP processar")
        if s1_inicial:
            client.write_coil(mm.DIGITAL_OUTPUTS['S1'], False)
            wait(WRITE_TO_READ_DELAY, "CLP processar")

    # PASSO 2: Confirmar S1 OFF
    print("\n[2/8] Confirmando S1 OFF (segurança)...")
    s1_check = client.read_coil(mm.DIGITAL_OUTPUTS['S1'])
    wait(READ_TO_WRITE_DELAY, "evitar saturação")
    if s1_check:
        print("❌ S1 ainda ON - não seguro!")
        return False
    print("✓ S1 OFF - seguro")

    # PASSO 3: Ligar S0
    print("\n[3/8] Escrevendo S0 = ON...")
    print("⚠️⚠️⚠️  MOTOR VAI LIGAR AGORA! ⚠️⚠️⚠️")
    input("      Pressione ENTER para continuar... ")

    success = client.write_coil(mm.DIGITAL_OUTPUTS['S0'], True)
    if not success:
        print("❌ write_coil(S0, True) falhou!")
        return False
    print("✓ Comando enviado")

    # PASSO 4: Aguardar processamento
    wait(WRITE_TO_READ_DELAY, "CLP processar e ativar saída")

    # PASSO 5: Confirmar S0 ON
    print("\n[4/8] Lendo S0 para confirmar ON...")
    s0_on = client.read_coil(mm.DIGITAL_OUTPUTS['S0'])
    wait(READ_TO_WRITE_DELAY, "evitar saturação")

    if s0_on is None:
        print("❌ Não conseguiu ler S0!")
        client.write_coil(mm.DIGITAL_OUTPUTS['S0'], False)
        return False

    if not s0_on:
        print("❌ S0 NÃO ativou!")
        print("   → Ladder bloqueando ou CLP em PROGRAM")
        return False

    print("✅ S0 CONFIRMADO ON!")
    print("👁️  VERIFIQUE: Motor girando ANTI-HORÁRIO")

    # PASSO 6: Manter ligado
    wait(MOTOR_ON_DURATION, "validação visual")

    # PASSO 7: Desligar S0
    print("\n[5/8] Escrevendo S0 = OFF...")
    success = client.write_coil(mm.DIGITAL_OUTPUTS['S0'], False)
    if not success:
        print("❌ write_coil(S0, False) falhou!")
        print("   ⚠️⚠️  MOTOR AINDA LIGADO!")
        return False
    print("✓ Comando enviado")

    # PASSO 8: Aguardar
    wait(WRITE_TO_READ_DELAY, "CLP desativar saída")

    # PASSO 9: Confirmar S0 OFF
    print("\n[6/8] Lendo S0 para confirmar OFF...")
    s0_off = client.read_coil(mm.DIGITAL_OUTPUTS['S0'])
    wait(READ_TO_WRITE_DELAY, "evitar saturação")

    if s0_off is None:
        print("❌ Não conseguiu ler S0!")
        return False

    if s0_off:
        print("❌ S0 NÃO desligou!")
        print("   ⚠️⚠️  USAR EMERGÊNCIA!")
        return False

    print("✅ S0 CONFIRMADO OFF!")
    print("👁️  VERIFIQUE: Motor PARADO")

    # PASSO 10: Confirmação visual
    print("\n[7/8] Motor parou?")
    resp = input("      Motor PAROU? (s/n): ").strip().lower()
    if resp != 's':
        print("❌ Operador reportou falha!")
        return False

    print("\n[8/8] ✅✅✅ TESTE S0 PASSOU! ✅✅✅")
    return True


def test_s1_recuar(client):
    """Teste CRÍTICO de S1 (RECUAR)."""
    print_section("TESTE S1 (RECUAR - Horário)")

    # Mesmo padrão do S0
    print("\n[1/8] Lendo estado inicial...")
    s0_inicial = client.read_coil(mm.DIGITAL_OUTPUTS['S0'])
    wait(READ_TO_WRITE_DELAY, "evitar saturação")
    s1_inicial = client.read_coil(mm.DIGITAL_OUTPUTS['S1'])
    wait(READ_TO_WRITE_DELAY, "evitar saturação")
    print(f"      S0={s0_inicial}, S1={s1_inicial}")

    if s0_inicial is None or s1_inicial is None:
        print("❌ FALHA: Não conseguiu ler estado!")
        return False

    if s0_inicial or s1_inicial:
        print("⚠️  Desligando motor...")
        if s0_inicial:
            client.write_coil(mm.DIGITAL_OUTPUTS['S0'], False)
            wait(WRITE_TO_READ_DELAY, "CLP processar")
        if s1_inicial:
            client.write_coil(mm.DIGITAL_OUTPUTS['S1'], False)
            wait(WRITE_TO_READ_DELAY, "CLP processar")

    print("\n[2/8] Confirmando S0 OFF (segurança)...")
    s0_check = client.read_coil(mm.DIGITAL_OUTPUTS['S0'])
    wait(READ_TO_WRITE_DELAY, "evitar saturação")
    if s0_check:
        print("❌ S0 ainda ON - não seguro!")
        return False
    print("✓ S0 OFF - seguro")

    print("\n[3/8] Escrevendo S1 = ON...")
    print("⚠️⚠️⚠️  MOTOR VAI LIGAR (HORÁRIO)! ⚠️⚠️⚠️")
    input("      Pressione ENTER... ")

    success = client.write_coil(mm.DIGITAL_OUTPUTS['S1'], True)
    if not success:
        print("❌ write_coil(S1, True) falhou!")
        return False
    print("✓ Comando enviado")

    wait(WRITE_TO_READ_DELAY, "CLP processar")

    print("\n[4/8] Lendo S1 para confirmar ON...")
    s1_on = client.read_coil(mm.DIGITAL_OUTPUTS['S1'])
    wait(READ_TO_WRITE_DELAY, "evitar saturação")

    if s1_on is None:
        print("❌ Não conseguiu ler S1!")
        client.write_coil(mm.DIGITAL_OUTPUTS['S1'], False)
        return False

    if not s1_on:
        print("❌ S1 NÃO ativou!")
        return False

    print("✅ S1 CONFIRMADO ON!")
    print("👁️  VERIFIQUE: Motor girando HORÁRIO")

    wait(MOTOR_ON_DURATION, "validação visual")

    print("\n[5/8] Escrevendo S1 = OFF...")
    success = client.write_coil(mm.DIGITAL_OUTPUTS['S1'], False)
    if not success:
        print("❌ write_coil(S1, False) falhou!")
        return False
    print("✓ Comando enviado")

    wait(WRITE_TO_READ_DELAY, "CLP desativar")

    print("\n[6/8] Lendo S1 para confirmar OFF...")
    s1_off = client.read_coil(mm.DIGITAL_OUTPUTS['S1'])
    wait(READ_TO_WRITE_DELAY, "evitar saturação")

    if s1_off is None:
        print("❌ Não conseguiu ler S1!")
        return False

    if s1_off:
        print("❌ S1 NÃO desligou!")
        return False

    print("✅ S1 CONFIRMADO OFF!")
    print("👁️  VERIFIQUE: Motor PARADO")

    print("\n[7/8] Motor parou?")
    resp = input("      Motor PAROU? (s/n): ").strip().lower()
    if resp != 's':
        print("❌ Operador reportou falha!")
        return False

    print("\n[8/8] ✅✅✅ TESTE S1 PASSOU! ✅✅✅")
    return True


def main():
    print("\n" + "#" * 70)
    print("#  TESTE CRÍTICO - MOTOR S0/S1")
    print("#  VALIDAÇÃO RIGOROSA COM TIMERS")
    print("#" * 70)

    print(f"\nTIMINGS:")
    print(f"  Write→Read: {WRITE_TO_READ_DELAY*1000:.0f}ms")
    print(f"  Read→Write: {READ_TO_WRITE_DELAY*1000:.0f}ms")
    print(f"  Motor ON: {MOTOR_ON_DURATION:.1f}s")

    results = {
        'S0 (AVANÇAR)': None,
        'S1 (RECUAR)': None,
    }

    print_section("CONEXÃO COM CLP")
    client = ModbusClientWrapper(stub_mode=False, port='/dev/ttyUSB0')

    if not client.connected:
        print("❌ CLP não conectado!")
        return

    print("✅ CLP conectado")

    # Verificar 00BE
    estado = client.read_coil(mm.CRITICAL_STATES['MODBUS_SLAVE_ENABLED'])
    if not estado:
        print("❌ Estado 00BE não está ON!")
        client.close()
        return
    print("✅ Estado 00BE ativo")

    try:
        # Teste S0
        results['S0 (AVANÇAR)'] = test_s0_avancar(client)

        if results['S0 (AVANÇAR)']:
            wait(BETWEEN_TESTS_DELAY, "segurança")
            # Teste S1
            results['S1 (RECUAR)'] = test_s1_recuar(client)

    except KeyboardInterrupt:
        print("\n⚠️  INTERROMPIDO!")
        client.write_coil(mm.DIGITAL_OUTPUTS['S0'], False)
        client.write_coil(mm.DIGITAL_OUTPUTS['S1'], False)
    finally:
        client.close()

    # Resumo
    print_section("RESUMO")
    for name, result in results.items():
        status = "✅ PASSOU" if result else "❌ FALHOU" if result is False else "⊘  PULADO"
        print(f"{status}  {name}")

    passed = sum(1 for r in results.values() if r is True)
    failed = sum(1 for r in results.values() if r is False)

    print("\n" + "=" * 70)
    if failed == 0 and passed == 2:
        print("🎉🎉🎉 TODOS PASSARAM! 🎉🎉🎉")
        print("\nSEGUNDA-FEIRA VAI DAR CERTO!")
        print("  ✅ AVANÇAR → S0 → Motor anti-horário")
        print("  ✅ RECUAR → S1 → Motor horário")
    else:
        print(f"⚠️  {failed} FALHOU(ARAM)!")
        print("\nCORRIJA ANTES DA FÁBRICA!")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n⚠️  Cancelado")
        sys.exit(1)
