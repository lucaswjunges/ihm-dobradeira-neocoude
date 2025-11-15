#!/usr/bin/env python3
"""
DEBUG: State Manager - Análise Profunda
Verifica se machine_state está sendo populado corretamente
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import asyncio
import json
from state_manager import MachineStateManager
from modbus_client import ModbusClientWrapper

async def debug_state():
    print("=" * 70)
    print("DEBUG: STATE MANAGER - ANÁLISE PROFUNDA")
    print("=" * 70)

    # Criar cliente Modbus e State Manager
    print("\n1. Criando ModbusClientWrapper...")
    modbus_client = ModbusClientWrapper(port='/dev/ttyUSB0', stub_mode=False)

    print("2. Criando MachineStateManager...")
    manager = MachineStateManager(modbus_client=modbus_client)

    # Aguardar inicialização
    print("3. Aguardando inicialização (2s)...")
    await asyncio.sleep(2)

    # Obter estado
    print("\n4. Obtendo estado via get_state()...")
    state = manager.get_state()

    # Análise detalhada
    print("\n" + "=" * 70)
    print("ESTADO COMPLETO:")
    print("=" * 70)
    print(json.dumps(state, indent=2, default=str))

    print("\n" + "=" * 70)
    print("ANÁLISE POR CATEGORIA:")
    print("=" * 70)

    # Categoria 1: Modo
    print("\n📌 MODO:")
    print(f"   mode_bit_02ff:  {state.get('mode_bit_02ff')}")
    print(f"   mode_text:      {state.get('mode_text')}")
    print(f"   mode_manual:    {state.get('mode_manual')}")

    # Categoria 2: LEDs
    print("\n📌 LEDs:")
    leds = state.get('leds', {})
    for led_name, led_value in leds.items():
        print(f"   {led_name:10s}: {led_value}")

    # Categoria 3: Ângulos
    print("\n📌 ÂNGULOS:")
    angles = state.get('angles', {})
    for ang_name, ang_value in angles.items():
        print(f"   {ang_name:20s}: {ang_value}°")

    # Categoria 4: Encoder
    print("\n📌 ENCODER:")
    print(f"   encoder_angle:  {state.get('encoder_angle')}°")
    print(f"   encoder_raw:    {state.get('encoder_raw')}")

    # Categoria 5: Inputs/Outputs
    print("\n📌 I/O DIGITAL:")
    inputs = state.get('inputs', {})
    outputs = state.get('outputs', {})
    print(f"   Inputs:  {len(inputs)} ({sum(1 for v in inputs.values() if v)} ativos)")
    print(f"   Outputs: {len(outputs)} ({sum(1 for v in outputs.values() if v)} ativos)")

    # Categoria 6: Contadores
    print("\n📌 ESTATÍSTICAS:")
    print(f"   poll_count:         {state.get('poll_count')}")
    print(f"   modbus_connected:   {state.get('modbus_connected')}")
    print(f"   last_update:        {state.get('last_update')}")

    # Diagnóstico
    print("\n" + "=" * 70)
    print("DIAGNÓSTICO:")
    print("=" * 70)

    total_keys = len(state)
    none_values = sum(1 for v in state.values() if v is None)
    empty_dicts = sum(1 for v in state.values() if isinstance(v, dict) and not v)

    print(f"   Total de chaves:     {total_keys}")
    print(f"   Valores None:        {none_values}")
    print(f"   Dicionários vazios:  {empty_dicts}")

    if total_keys < 10:
        print("\n   ⚠️  PROBLEMA: Estado muito pequeno!")
    elif none_values > total_keys * 0.5:
        print("\n   ⚠️  PROBLEMA: Muitos valores None!")
    elif empty_dicts > 3:
        print("\n   ⚠️  PROBLEMA: Muitos dicionários vazios!")
    else:
        print("\n   ✅ Estado parece estar sendo populado corretamente")

    # Aguardar mais alguns polls
    print("\n" + "=" * 70)
    print("Aguardando mais 3 segundos de polling...")
    await asyncio.sleep(3)

    state_after = manager.get_state()
    poll_count_before = state.get('poll_count', 0)
    poll_count_after = state_after.get('poll_count', 0)

    print(f"\nPolls executados: {poll_count_after - poll_count_before}")

    if poll_count_after > poll_count_before:
        print("✅ Polling está ativo e funcionando")
    else:
        print("❌ Polling NÃO está funcionando!")

    # Encerrar
    print("\n" + "=" * 70)
    manager.stop()
    print("DEBUG concluído")

if __name__ == '__main__':
    asyncio.run(debug_state())
