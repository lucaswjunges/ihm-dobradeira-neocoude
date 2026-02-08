#!/usr/bin/env python3
"""
Script de diagnóstico para IHM Web
Identifica problemas de:
- Modbus timeout/travamento
- Broadcast loop
- Heartbeat
- Performance de polling
"""

import asyncio
import time
import sys
from modbus_client import ModbusClientWrapper
from state_manager import MachineStateManager
import modbus_map as mm

async def test_modbus_speed():
    """Testa velocidade de leitura Modbus"""
    print("\n" + "="*60)
    print("TESTE 1: VELOCIDADE MODBUS")
    print("="*60)

    client = ModbusClientWrapper(stub_mode=False, port='/dev/ttyUSB0')

    if not client.connected:
        print("❌ PROBLEMA CRÍTICO: Modbus NÃO conectado!")
        print("   → Isso explica desconexões e falha ao gravar ângulos")
        return False

    print("✅ Modbus conectado")

    # Teste de velocidade de leitura
    print("\n📊 Testando velocidade de leitura...")
    times = []
    for i in range(10):
        start = time.time()
        encoder = client.read_register(mm.ENCODER['ANGLE_MSW'])
        elapsed = (time.time() - start) * 1000
        times.append(elapsed)

        if encoder is None:
            print(f"  {i+1}/10: ❌ TIMEOUT ({elapsed:.0f}ms)")
        else:
            print(f"  {i+1}/10: ✓ {elapsed:.0f}ms (encoder={encoder})")

    avg_time = sum(times) / len(times)
    print(f"\n⏱️  Tempo médio: {avg_time:.0f}ms")

    if avg_time > 500:
        print("⚠️  PROBLEMA: Leituras muito lentas (> 500ms)")
        print("   → Polling vai demorar muito e bloquear broadcast")
        return False

    print("✅ Velocidade OK")
    client.close()
    return True

async def test_state_manager_performance():
    """Testa performance do state manager"""
    print("\n" + "="*60)
    print("TESTE 2: PERFORMANCE DO STATE MANAGER")
    print("="*60)

    client = ModbusClientWrapper(stub_mode=False, port='/dev/ttyUSB0')
    manager = MachineStateManager(client, poll_interval=0.1)

    print("\n📊 Testando 10 ciclos de polling...")
    times = []
    for i in range(10):
        start = time.time()
        await manager.poll_once()
        elapsed = (time.time() - start) * 1000
        times.append(elapsed)
        print(f"  Ciclo {i+1}/10: {elapsed:.0f}ms")

    avg_time = sum(times) / len(times)
    print(f"\n⏱️  Tempo médio de polling: {avg_time:.0f}ms")

    if avg_time > 1000:
        print("❌ PROBLEMA CRÍTICO: Polling demora > 1s")
        print("   → Isso bloqueia o broadcast_loop")
        print("   → Heartbeat não é enviado a tempo")
        print("   → Watchdog desconecta em 10s")
        return False
    elif avg_time > 500:
        print("⚠️  AVISO: Polling demorado (> 500ms)")
        print("   → Pode causar atrasos no heartbeat")
    else:
        print("✅ Performance OK")

    client.close()
    return True

async def test_write_angle():
    """Testa gravação de ângulo"""
    print("\n" + "="*60)
    print("TESTE 3: GRAVAÇÃO DE ÂNGULO")
    print("="*60)

    client = ModbusClientWrapper(stub_mode=False, port='/dev/ttyUSB0')

    if not client.connected:
        print("❌ PROBLEMA: Modbus não conectado")
        return False

    print("\n📝 Testando gravação do Ângulo 1 = 45.0°...")
    start = time.time()
    success = client.write_bend_angle(1, 45.0)
    elapsed = (time.time() - start) * 1000

    if success:
        print(f"✅ Gravação OK em {elapsed:.0f}ms")
    else:
        print(f"❌ PROBLEMA: Gravação falhou após {elapsed:.0f}ms")
        return False

    # Lê de volta para verificar
    print("\n📖 Lendo de volta para validar...")
    angle = client.read_bend_angle(1)
    if angle and abs(angle - 45.0) < 0.1:
        print(f"✅ Validado: {angle:.1f}° (esperado 45.0°)")
    else:
        print(f"❌ PROBLEMA: Leu {angle}° (esperado 45.0°)")
        return False

    client.close()
    return True

async def test_heartbeat_timing():
    """Simula timing do heartbeat"""
    print("\n" + "="*60)
    print("TESTE 4: TIMING DO HEARTBEAT")
    print("="*60)

    HEARTBEAT_INTERVAL = 20  # broadcasts
    BROADCAST_INTERVAL = 0.15  # segundos
    WATCHDOG_TIMEOUT = 10.0  # segundos

    heartbeat_period = HEARTBEAT_INTERVAL * BROADCAST_INTERVAL

    print(f"\n📊 Configuração atual:")
    print(f"  Broadcast: a cada {BROADCAST_INTERVAL*1000:.0f}ms")
    print(f"  Heartbeat: a cada {HEARTBEAT_INTERVAL} broadcasts = {heartbeat_period:.1f}s")
    print(f"  Watchdog: desconecta após {WATCHDOG_TIMEOUT:.1f}s")

    margin = WATCHDOG_TIMEOUT - (3 * heartbeat_period)
    print(f"\n🎯 Análise:")
    print(f"  3 heartbeats = {3 * heartbeat_period:.1f}s")
    print(f"  Margem de segurança: {margin:.1f}s")

    if margin < 1.0:
        print(f"\n❌ PROBLEMA CRÍTICO: Margem muito pequena ({margin:.1f}s)")
        print("   → Qualquer atraso causa desconexão")
        print("   → Heartbeat deveria ser a cada 2s (INTERVAL=13)")
        return False

    print(f"\n✅ Margem OK ({margin:.1f}s)")
    return True

async def main():
    print("\n" + "="*60)
    print("  DIAGNÓSTICO COMPLETO - IHM WEB")
    print("="*60)

    results = []

    # Teste 1: Modbus
    results.append(await test_modbus_speed())

    # Teste 2: State Manager
    results.append(await test_state_manager_performance())

    # Teste 3: Gravação
    results.append(await test_write_angle())

    # Teste 4: Heartbeat timing
    results.append(await test_heartbeat_timing())

    # Resumo
    print("\n" + "="*60)
    print("  RESUMO")
    print("="*60)
    print(f"  Modbus: {'✅ OK' if results[0] else '❌ FALHA'}")
    print(f"  State Manager: {'✅ OK' if results[1] else '❌ FALHA'}")
    print(f"  Gravação: {'✅ OK' if results[2] else '❌ FALHA'}")
    print(f"  Heartbeat: {'✅ OK' if results[3] else '❌ FALHA'}")

    if all(results):
        print("\n✅ TODOS OS TESTES PASSARAM!")
        print("   O problema deve ser outra coisa (cache do navegador?)")
    else:
        print("\n❌ PROBLEMAS IDENTIFICADOS!")
        print("   Revise os erros acima para solução")

    print("="*60)

if __name__ == "__main__":
    asyncio.run(main())
