#!/usr/bin/env python3
"""
Teste de Leitura dos Registros de Tela
=======================================

Testa se registros 0FEE e 0FEC podem ser lidos via Modbus RTU.
"""

import sys
sys.path.insert(0, '/home/lucas-junges/Documents/clientes/w&co/ihm')

from modbus_client import ModbusClientWrapper
import time

def test_screen_registers(port='/dev/ttyUSB0', slave_id=1):
    """
    Testa leitura dos registros de tela
    
    Args:
        port: Porta serial
        slave_id: ID do CLP
    """
    print("=" * 60)
    print("TESTE DE REGISTROS DE TELA (0FEE e 0FEC)")
    print("=" * 60)
    print(f"Porta: {port}")
    print(f"Slave ID: {slave_id}\n")
    
    # Conecta ao CLP
    client = ModbusClientWrapper(stub_mode=False, port=port, slave_id=slave_id)
    
    if not client.connected:
        print("✗ ERRO: CLP não conectado")
        print("  Verifique:")
        print(f"  - Cabo RS485 em {port}")
        print("  - CLP ligado e em RUN")
        return False
    
    print("✓ Conexão Modbus estabelecida\n")
    
    # Teste 1: Ler registro 0FEE (tela atual)
    print("[Teste 1] Registro 0FEE (4078 decimal) - TELA ATUAL")
    print("-" * 60)
    
    try:
        # Tenta ler
        current_screen = client.read_register(0x0FEE)
        
        if current_screen is None:
            print("  ✗ ERRO: Não foi possível ler registro 0FEE")
            print("  Possível que este registro não esteja implementado no firmware")
        else:
            print(f"  ✓ Registro 0FEE lido com sucesso!")
            print(f"  Valor: 0x{current_screen:04X} ({current_screen} decimal)")
            
            # Interpreta valor
            screen_names = {
                1: "Tela principal/inicial",
                2: "Tela de configuração?",
                3: "Tela de status?",
                4: "Tela Dobra 1 (K1)",
                5: "Tela Dobra 2 (K2)",
                6: "Tela Dobra 3 (K3)",
                7: "Tela de diagnóstico?",
                8: "Tela auxiliar?",
            }
            
            if current_screen in screen_names:
                print(f"  Interpretação: {screen_names[current_screen]}")
            else:
                print(f"  Interpretação: Tela desconhecida (número {current_screen})")
                
    except Exception as e:
        print(f"  ✗ EXCEÇÃO ao ler 0FEE: {e}")
    
    # Teste 2: Ler registro 0FEC (tela alvo)
    print("\n[Teste 2] Registro 0FEC (4076 decimal) - TELA ALVO")
    print("-" * 60)
    
    try:
        # Tenta ler
        target_screen = client.read_register(0x0FEC)
        
        if target_screen is None:
            print("  ✗ ERRO: Não foi possível ler registro 0FEC")
            print("  Possível que este registro não esteja implementado no firmware")
        else:
            print(f"  ✓ Registro 0FEC lido com sucesso!")
            print(f"  Valor: 0x{target_screen:04X} ({target_screen} decimal)")
            print(f"  Nota: Este registro é usado para ESCREVER (mudar de tela)")
                
    except Exception as e:
        print(f"  ✗ EXCEÇÃO ao ler 0FEC: {e}")
    
    # Teste 3: Ler estado 00DA (trigger de carregamento)
    print("\n[Teste 3] Estado 00DA (218 decimal) - TRIGGER CARREGA TELA")
    print("-" * 60)
    
    try:
        # Tenta ler coil
        load_trigger = client.read_coil(0x00DA)
        
        if load_trigger is None:
            print("  ✗ ERRO: Não foi possível ler estado 00DA")
        else:
            print(f"  ✓ Estado 00DA lido com sucesso!")
            print(f"  Valor: {'ON' if load_trigger else 'OFF'}")
            print(f"  Nota: Transição OFF→ON carrega tela definida em 0FEC")
                
    except Exception as e:
        print(f"  ✗ EXCEÇÃO ao ler 00DA: {e}")
    
    # Teste 4: Múltiplas leituras para verificar se muda
    print("\n[Teste 4] Monitoramento por 5 segundos")
    print("-" * 60)
    print("  Pressione botões K1, K2 ou K3 no CLP físico se possível...")
    print("  Verificando se registro 0FEE muda:\n")
    
    last_screen = None
    for i in range(10):
        try:
            screen = client.read_register(0x0FEE)
            if screen is not None:
                if screen != last_screen:
                    print(f"  [{i*0.5:.1f}s] Tela mudou para: {screen}")
                    last_screen = screen
                else:
                    print(f"  [{i*0.5:.1f}s] Tela: {screen} (sem mudança)")
        except:
            print(f"  [{i*0.5:.1f}s] Erro na leitura")
        
        time.sleep(0.5)
    
    # Fecha conexão
    client.close()
    
    print("\n" + "=" * 60)
    print("✓ TESTE CONCLUÍDO")
    print("=" * 60)
    
    print("\n[Resumo]")
    print("  Se 0FEE e 0FEC foram lidos com sucesso:")
    print("    → Podemos implementar sincronização de telas!")
    print("  Se retornaram erro:")
    print("    → Registros não disponíveis neste firmware")
    print("    → Precisaremos criar via ROT5")
    
    return True


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Teste registros de tela')
    parser.add_argument('--port', default='/dev/ttyUSB0', help='Porta serial')
    parser.add_argument('--slave', type=int, default=1, help='Slave ID')
    
    args = parser.parse_args()
    
    test_screen_registers(port=args.port, slave_id=args.slave)
