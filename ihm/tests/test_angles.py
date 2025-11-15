#!/usr/bin/env python3
"""
Teste de Leitura e Escrita de Ângulos
======================================

Testa conversão graus ↔ unidades CLP e escrita de ângulos.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modbus_client import ModbusClientWrapper
import modbus_map as mm

def test_angles(port='/dev/ttyUSB0', write_test=False):
    """
    Testa leitura e opcionalmente escrita de ângulos
    
    Args:
        port: Porta serial
        write_test: Se True, testa escrita (CUIDADO!)
    """
    print("=" * 60)
    print("TESTE DE ÂNGULOS - LEITURA/ESCRITA")
    print("=" * 60)
    print(f"Porta: {port}")
    print(f"Modo escrita: {'SIM' if write_test else 'NÃO (somente leitura)'}\n")
    
    client = ModbusClientWrapper(stub_mode=False, port=port)
    
    if not client.connected:
        print("✗ Erro: CLP não conectado")
        return False
    
    # Leitura inicial
    print("[1] Leitura inicial dos ângulos:")
    print("-" * 40)
    
    angles_before = {}
    for bend_num in [1, 2, 3]:
        msw_addr = [mm.BEND_1_LEFT_MSW, mm.BEND_2_LEFT_MSW, mm.BEND_3_LEFT_MSW][bend_num-1]
        lsw_addr = [mm.BEND_1_LEFT_LSW, mm.BEND_2_LEFT_LSW, mm.BEND_3_LEFT_LSW][bend_num-1]
        
        value_clp = client.read_32bit(msw_addr, lsw_addr)
        if value_clp is not None:
            value_degrees = value_clp / 10.0
            angles_before[bend_num] = value_degrees
            print(f"  Dobra {bend_num}: {value_degrees:.1f}° ({value_clp} unidades CLP)")
        else:
            print(f"  Dobra {bend_num}: ERRO na leitura")
    
    # Teste de escrita (OPCIONAL)
    if write_test:
        print("\n[2] Teste de escrita:")
        print("-" * 40)
        print("⚠️  ATENÇÃO: Vai sobrescrever ângulos no CLP!")
        
        response = input("Continuar? (sim/não): ")
        if response.lower() != 'sim':
            print("Teste de escrita cancelado")
            client.close()
            return True
        
        # Escreve valores de teste
        test_angles = {
            1: 45.5,   # 455 unidades
            2: 90.0,   # 900 unidades
            3: 135.5   # 1355 unidades
        }
        
        for bend_num, angle_degrees in test_angles.items():
            msw_addr = [mm.BEND_1_LEFT_MSW, mm.BEND_2_LEFT_MSW, mm.BEND_3_LEFT_MSW][bend_num-1]
            lsw_addr = [mm.BEND_1_LEFT_LSW, mm.BEND_2_LEFT_LSW, mm.BEND_3_LEFT_LSW][bend_num-1]
            
            value_clp = int(angle_degrees * 10)
            
            print(f"\n  Escrevendo Dobra {bend_num}: {angle_degrees}° ({value_clp} unidades)")
            success = client.write_32bit(msw_addr, lsw_addr, value_clp)
            
            if success:
                print(f"    ✓ Escrita bem-sucedida")
                
                # Verifica leitura
                import time
                time.sleep(0.2)
                
                value_read = client.read_32bit(msw_addr, lsw_addr)
                if value_read == value_clp:
                    print(f"    ✓ Verificação OK: {value_read/10.0:.1f}°")
                else:
                    print(f"    ✗ Verificação FALHOU: esperado {value_clp}, lido {value_read}")
            else:
                print(f"    ✗ Erro na escrita")
        
        # Restaura valores originais
        print("\n[3] Restaurando valores originais:")
        print("-" * 40)
        
        for bend_num, angle_degrees in angles_before.items():
            msw_addr = [mm.BEND_1_LEFT_MSW, mm.BEND_2_LEFT_MSW, mm.BEND_3_LEFT_MSW][bend_num-1]
            lsw_addr = [mm.BEND_1_LEFT_LSW, mm.BEND_2_LEFT_LSW, mm.BEND_3_LEFT_LSW][bend_num-1]
            
            value_clp = int(angle_degrees * 10)
            success = client.write_32bit(msw_addr, lsw_addr, value_clp)
            
            if success:
                print(f"  ✓ Dobra {bend_num} restaurada: {angle_degrees:.1f}°")
            else:
                print(f"  ✗ Erro ao restaurar Dobra {bend_num}")
    
    # Teste de conversão
    print("\n[Teste] Conversão graus ↔ unidades CLP:")
    print("-" * 40)
    test_values = [0, 45.5, 90.0, 120.0, 135.5, 180.0]
    
    for degrees in test_values:
        clp_units = int(degrees * 10)
        back_to_degrees = clp_units / 10.0
        print(f"  {degrees}° → {clp_units} unidades → {back_to_degrees}°")
    
    client.close()
    
    print("\n" + "=" * 60)
    print("✓ TESTE CONCLUÍDO")
    print("=" * 60)
    
    return True


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Teste ângulos')
    parser.add_argument('--port', default='/dev/ttyUSB0', help='Porta serial')
    parser.add_argument('--write', action='store_true', help='Habilita teste de escrita')
    
    args = parser.parse_args()
    
    test_angles(port=args.port, write_test=args.write)
