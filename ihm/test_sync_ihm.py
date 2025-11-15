#!/usr/bin/env python3
"""
TESTE DE SINCRONIZAÇÃO: IHM Web ↔ IHM Física ↔ CLP
Verifica se todos os registros de supervisão estão sendo lidos corretamente
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from modbus_client import ModbusClientWrapper
import modbus_map as mm
import time

def test_supervision_sync():
    """Testa sincronização dos registros de supervisão"""
    
    client = ModbusClientWrapper(port='/dev/ttyUSB0', stub_mode=False)
    
    print("="*70)
    print("TESTE DE SINCRONIZAÇÃO: IHM Web ↔ IHM Física ↔ CLP")
    print("="*70)
    
    print("\n📊 REGISTROS DE SUPERVISÃO (compartilhados pelas 3 interfaces)")
    print("─"*70)
    
    # Ler todos os registros de supervisão
    supervision = {}
    
    # SCREEN_NUM - Tela atual da IHM física
    supervision['SCREEN_NUM'] = client.read_register(mm.SUPERVISION['SCREEN_NUM'])
    print(f"\n1. SCREEN_NUM (0x{mm.SUPERVISION['SCREEN_NUM']:04X} = {mm.SUPERVISION['SCREEN_NUM']})")
    print(f"   Valor: {supervision['SCREEN_NUM']}")
    print(f"   Significado: Tela atual mostrada na IHM física")
    
    # MODE_STATE - Modo de operação
    supervision['MODE_STATE'] = client.read_register(mm.SUPERVISION['MODE_STATE'])
    print(f"\n2. MODE_STATE (0x{mm.SUPERVISION['MODE_STATE']:04X} = {mm.SUPERVISION['MODE_STATE']})")
    print(f"   Valor: {supervision['MODE_STATE']}")
    print(f"   Significado: 0=MANUAL, outro=AUTO (cópia do bit 02FF)")
    
    # Ler bit real de modo para comparação
    mode_real = client.read_coil(0x02FF)
    print(f"   Bit REAL 0x02FF: {mode_real} ({'AUTO' if mode_real else 'MANUAL'})")
    if supervision['MODE_STATE'] == 0 and not mode_real:
        print(f"   ✅ SINCRONIZADO: Ambos em MANUAL")
    elif supervision['MODE_STATE'] != 0 and mode_real:
        print(f"   ✅ SINCRONIZADO: Ambos em AUTO")
    else:
        print(f"   ⚠️  DESSINCRONIZADO!")
    
    # BEND_CURRENT - Dobra atual
    supervision['BEND_CURRENT'] = client.read_register(mm.SUPERVISION['BEND_CURRENT'])
    print(f"\n3. BEND_CURRENT (0x{mm.SUPERVISION['BEND_CURRENT']:04X} = {mm.SUPERVISION['BEND_CURRENT']})")
    print(f"   Valor: {supervision['BEND_CURRENT']}")
    print(f"   Significado: Número da dobra ativa (1, 2 ou 3)")
    
    # DIRECTION - Sentido de rotação
    supervision['DIRECTION'] = client.read_register(mm.SUPERVISION['DIRECTION'])
    print(f"\n4. DIRECTION (0x{mm.SUPERVISION['DIRECTION']:04X} = {mm.SUPERVISION['DIRECTION']})")
    print(f"   Valor: {supervision['DIRECTION']}")
    print(f"   Significado: 0=Esquerda/CCW, 1=Direita/CW")
    
    # SPEED_CLASS - Classe de velocidade
    supervision['SPEED_CLASS'] = client.read_register(mm.SUPERVISION['SPEED_CLASS'])
    print(f"\n5. SPEED_CLASS (0x{mm.SUPERVISION['SPEED_CLASS']:04X} = {mm.SUPERVISION['SPEED_CLASS']})")
    print(f"   Valor: {supervision['SPEED_CLASS']} RPM")
    print(f"   Significado: Velocidade atual (5, 10 ou 15 RPM)")
    
    # CYCLE_ACTIVE - Ciclo ativo
    supervision['CYCLE_ACTIVE'] = client.read_register(mm.SUPERVISION['CYCLE_ACTIVE'])
    print(f"\n6. CYCLE_ACTIVE (0x{mm.SUPERVISION['CYCLE_ACTIVE']:04X} = {mm.SUPERVISION['CYCLE_ACTIVE']})")
    print(f"   Valor: {supervision['CYCLE_ACTIVE']}")
    print(f"   Significado: 0=Parado, 1=Ciclo em execução")
    
    # Verificar LEDs (K1, K2, K3)
    print("\n" + "─"*70)
    print("🔆 LEDS DA IHM FÍSICA (indicadores de dobra)")
    print("─"*70)
    
    led1 = client.read_coil(mm.LEDS['LED1'])  # Dobra 1
    led2 = client.read_coil(mm.LEDS['LED2'])  # Dobra 2
    led3 = client.read_coil(mm.LEDS['LED3'])  # Dobra 3
    
    print(f"LED K1 (Dobra 1): {'🟢 ON' if led1 else '⚫ OFF'}")
    print(f"LED K2 (Dobra 2): {'🟢 ON' if led2 else '⚫ OFF'}")
    print(f"LED K3 (Dobra 3): {'🟢 ON' if led3 else '⚫ OFF'}")
    
    # Comparar com BEND_CURRENT
    if supervision['BEND_CURRENT'] == 1 and led1:
        print("✅ LED1 sincronizado com BEND_CURRENT=1")
    elif supervision['BEND_CURRENT'] == 2 and led2:
        print("✅ LED2 sincronizado com BEND_CURRENT=2")
    elif supervision['BEND_CURRENT'] == 3 and led3:
        print("✅ LED3 sincronizado com BEND_CURRENT=3")
    elif supervision['BEND_CURRENT'] == 0:
        print("ℹ️  Nenhuma dobra ativa (BEND_CURRENT=0)")
    
    # Verificar ângulos programados
    print("\n" + "─"*70)
    print("📐 ÂNGULOS PROGRAMADOS (compartilhados)")
    print("─"*70)
    
    angles = {}
    for name, addrs in mm.BEND_ANGLES.items():
        msw_addr, lsw_addr = addrs
        value_32bit = client.read_32bit(msw_addr, lsw_addr)
        if value_32bit is not None:
            angle = value_32bit / 10.0
            angles[name] = angle
            print(f"{name:20s}: {angle:6.1f}° (raw: {value_32bit})")
        else:
            angles[name] = None
            print(f"{name:20s}: ERRO NA LEITURA")
    
    # Resumo final
    print("\n" + "="*70)
    print("📋 RESUMO DE SINCRONIZAÇÃO")
    print("="*70)
    
    all_synced = True
    
    # Verificar se todos os registros foram lidos
    failed_reads = [k for k, v in supervision.items() if v is None]
    if failed_reads:
        print(f"❌ Falha na leitura: {', '.join(failed_reads)}")
        all_synced = False
    else:
        print("✅ Todos os 6 registros de supervisão lidos com sucesso")
    
    # Verificar sincronização de modo
    if supervision['MODE_STATE'] is not None and mode_real is not None:
        mode_synced = (supervision['MODE_STATE'] == 0 and not mode_real) or \
                      (supervision['MODE_STATE'] != 0 and mode_real)
        if mode_synced:
            print("✅ Modo sincronizado entre MODE_STATE e bit 0x02FF")
        else:
            print("⚠️  Modo DESSINCRONIZADO!")
            all_synced = False
    
    # Verificar se LEDs foram lidos
    if led1 is not None and led2 is not None and led3 is not None:
        print("✅ LEDs K1, K2, K3 lidos com sucesso")
    else:
        print("❌ Falha na leitura de LEDs")
        all_synced = False
    
    # Verificar se ângulos foram lidos
    failed_angles = [k for k, v in angles.items() if v is None]
    if failed_angles:
        print(f"⚠️  Falha na leitura de ângulos: {', '.join(failed_angles)}")
        all_synced = False
    else:
        print(f"✅ Todos os {len(angles)} ângulos lidos com sucesso")
    
    print("\n" + "="*70)
    if all_synced:
        print("🎉 SINCRONIZAÇÃO COMPLETA!")
        print("IHM Web pode exibir os mesmos dados que a IHM Física")
    else:
        print("⚠️  VERIFICAR DESSINCRONIZAÇÃO")
    print("="*70)
    
    client.close()

if __name__ == '__main__':
    try:
        test_supervision_sync()
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        import traceback
        traceback.print_exc()
