#!/usr/bin/env python3
"""
Teste de Comunicação Modbus Completo
=====================================

Testa leitura de todos os registros principais mapeados.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modbus_client import ModbusClientWrapper
import modbus_map as mm

def test_modbus_complete(port='/dev/ttyUSB0', slave_id=1):
    """
    Testa comunicação Modbus completa
    
    Args:
        port: Porta serial
        slave_id: ID do CLP
    """
    print("=" * 60)
    print("TESTE COMPLETO DE COMUNICAÇÃO MODBUS")
    print("=" * 60)
    print(f"Porta: {port}")
    print(f"Slave ID: {slave_id}\n")
    
    # Conecta
    client = ModbusClientWrapper(stub_mode=False, port=port, slave_id=slave_id)
    
    if not client.connected:
        print("✗ ERRO: Não foi possível conectar ao CLP")
        print("  Verifique:")
        print(f"  - Cabo RS485 em {port}")
        print("  - CLP ligado e em modo RUN")
        print("  - Estado 00BE (190) ativo")
        return False
    
    print("✓ Conexão Modbus estabelecida\n")
    
    # Teste 1: Estado Modbus Slave
    print("[Teste 1] Estado Modbus Slave Enable (00BE)")
    modbus_enabled = client.read_coil(mm.STATE_MODBUS_SLAVE_ENABLE)
    if modbus_enabled:
        print(f"  ✓ Estado 00BE: ON (Modbus habilitado)")
    else:
        print(f"  ✗ Estado 00BE: OFF (Modbus NÃO habilitado!)")
        print("  AÇÃO: Ativar estado 0190 (00BE) no ladder")
    
    # Teste 2: Encoder
    print("\n[Teste 2] Leitura Encoder (04D6/04D7)")
    encoder_raw = client.read_32bit(mm.ENCODER_ANGLE_MSW, mm.ENCODER_ANGLE_LSW)
    if encoder_raw is not None:
        encoder_degrees = encoder_raw / 10.0
        print(f"  ✓ Encoder: {encoder_degrees:.1f}° ({encoder_raw} unidades)")
    else:
        print(f"  ✗ Erro ao ler encoder")
    
    # Teste 3: Ângulos Setpoint
    print("\n[Teste 3] Ângulos Programados")
    
    bend1 = client.read_32bit(mm.BEND_1_LEFT_MSW, mm.BEND_1_LEFT_LSW)
    if bend1 is not None:
        print(f"  ✓ Dobra 1: {bend1/10.0:.1f}° ({bend1} unidades)")
    else:
        print(f"  ✗ Erro ao ler dobra 1")
    
    bend2 = client.read_32bit(mm.BEND_2_LEFT_MSW, mm.BEND_2_LEFT_LSW)
    if bend2 is not None:
        print(f"  ✓ Dobra 2: {bend2/10.0:.1f}° ({bend2} unidades)")
    else:
        print(f"  ✗ Erro ao ler dobra 2")
    
    bend3 = client.read_32bit(mm.BEND_3_LEFT_MSW, mm.BEND_3_LEFT_LSW)
    if bend3 is not None:
        print(f"  ✓ Dobra 3: {bend3/10.0:.1f}° ({bend3} unidades)")
    else:
        print(f"  ✗ Erro ao ler dobra 3")
    
    # Teste 4: Entradas Digitais
    print("\n[Teste 4] Entradas Digitais (E0-E7)")
    for name, addr in mm.DIGITAL_INPUTS.items():
        value = client.read_register(addr)
        if value is not None:
            status = "ON" if (value & 0x0001) else "OFF"
            print(f"  {name}: {status}")
        else:
            print(f"  {name}: ERRO")
    
    # Teste 5: Saídas Digitais
    print("\n[Teste 5] Saídas Digitais (S0-S7)")
    for name, addr in mm.DIGITAL_OUTPUTS.items():
        value = client.read_register(addr)
        if value is not None:
            status = "ON" if (value & 0x0001) else "OFF"
            print(f"  {name}: {status}")
        else:
            print(f"  {name}: ERRO")
    
    # Teste 6: LEDs
    print("\n[Teste 6] LEDs Frontais")
    for name, addr in mm.LEDS.items():
        value = client.read_coil(addr)
        if value is not None:
            status = "ON" if value else "OFF"
            print(f"  {name}: {status}")
        else:
            print(f"  {name}: ERRO")
    
    # Teste 7: Botões (verificar se estão soltos)
    print("\n[Teste 7] Verificação de Botões")
    buttons_pressed = []
    for name, addr in mm.KEYBOARD_NUMERIC.items():
        value = client.read_coil(addr)
        if value:
            buttons_pressed.append(name)
    
    for name, addr in mm.KEYBOARD_FUNCTION.items():
        value = client.read_coil(addr)
        if value:
            buttons_pressed.append(name)
    
    if buttons_pressed:
        print(f"  ⚠ Botões pressionados: {', '.join(buttons_pressed)}")
    else:
        print(f"  ✓ Todos os botões soltos (estado normal)")
    
    # Fecha conexão
    client.close()
    
    print("\n" + "=" * 60)
    print("✓ TESTE CONCLUÍDO")
    print("=" * 60)
    
    return True


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Teste comunicação Modbus')
    parser.add_argument('--port', default='/dev/ttyUSB0', help='Porta serial')
    parser.add_argument('--slave', type=int, default=1, help='Slave ID')
    
    args = parser.parse_args()
    
    test_modbus_complete(port=args.port, slave_id=args.slave)
