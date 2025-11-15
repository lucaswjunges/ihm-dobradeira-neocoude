#!/usr/bin/env python3
"""
Teste de Mudança de Velocidade
===============================

Testa simulação K1+K7 para alternar classes de velocidade.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modbus_client import ModbusClientWrapper
import modbus_map as mm
import time

def test_speed_change(port='/dev/ttyUSB0'):
    """
    Testa mudança de classe de velocidade
    
    Args:
        port: Porta serial
    """
    print("=" * 60)
    print("TESTE DE MUDANÇA DE VELOCIDADE")
    print("=" * 60)
    print(f"Porta: {port}\n")
    
    print("⚠️  AVISO: Este teste simula pressionar K1+K7")
    print("   Certifique-se que a máquina está em modo MANUAL e PARADA")
    print()
    
    response = input("Continuar? (sim/não): ")
    if response.lower() != 'sim':
        print("Teste cancelado")
        return False
    
    client = ModbusClientWrapper(stub_mode=False, port=port)
    
    if not client.connected:
        print("✗ Erro: CLP não conectado")
        return False
    
    # Função auxiliar para ler classe atual
    def read_current_class():
        """Lê estados de classe de velocidade"""
        # Nota: Endereços 0x0360-0x0362 podem não estar implementados
        # Verificar no ladder se existem
        print("  [Info] Leitura de classes não implementada")
        print("         Verifique visualmente no display físico")
        return None
    
    # Lê classe inicial
    print("[1] Classe de velocidade atual:")
    print("-" * 40)
    read_current_class()
    
    # Simula K1+K7
    print("\n[2] Simulando pressão simultânea K1+K7:")
    print("-" * 40)
    
    print("  Ativando K1...")
    client.write_coil(mm.BTN_K1, True)
    
    print("  Ativando K7...")
    client.write_coil(mm.BTN_K7, True)
    
    print("  Aguardando 100ms...")
    time.sleep(0.1)
    
    print("  Desativando K1...")
    client.write_coil(mm.BTN_K1, False)
    
    print("  Desativando K7...")
    client.write_coil(mm.BTN_K7, False)
    
    print("  ✓ Comando enviado com sucesso")
    
    # Aguarda processamento
    print("\n[3] Aguardando processamento do ladder...")
    time.sleep(0.5)
    
    # Lê classe final
    print("\n[4] Nova classe de velocidade:")
    print("-" * 40)
    read_current_class()
    
    print("\n[Verificação Manual]")
    print("-" * 40)
    print("  Verifique no display físico do CLP:")
    print("  - A classe de velocidade mudou?")
    print("  - Alternância esperada: 5 → 10 → 15 → 5 RPM")
    
    client.close()
    
    print("\n" + "=" * 60)
    print("✓ TESTE CONCLUÍDO")
    print("=" * 60)
    
    return True


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Teste mudança de velocidade')
    parser.add_argument('--port', default='/dev/ttyUSB0', help='Porta serial')
    
    args = parser.parse_args()
    
    test_speed_change(port=args.port)
