#!/usr/bin/env python3
"""
test_all_keys.py

Teste sistemático de TODAS as 18 teclas da IHM
Verifica se cada tecla está sendo enviada corretamente para o CLP
"""

import sys
import time
import argparse
from modbus_client import ModbusClient, ModbusConfig

# Mapeamento de todas as teclas
ALL_KEYS = {
    # Teclas numéricas
    'K1': 160, 'K2': 161, 'K3': 162, 'K4': 163, 'K5': 164,
    'K6': 165, 'K7': 166, 'K8': 167, 'K9': 168, 'K0': 169,

    # Funções
    'S1': 220, 'S2': 221,

    # Navegação
    'UP': 172, 'DOWN': 173,

    # Controle
    'ENTER': 37, 'ESC': 188, 'EDIT': 38, 'LOCK': 241
}

def test_key(client: ModbusClient, key_name: str, address: int, interactive: bool = False):
    """
    Testa uma tecla individual

    Args:
        client: Cliente Modbus
        key_name: Nome da tecla (ex: 'K1')
        address: Endereço Modbus da tecla
        interactive: Se True, aguarda Enter entre teclas
    """
    print(f"\n{'='*60}")
    print(f"Testando tecla: {key_name} (endereço {address})")
    print(f"{'='*60}")

    if interactive:
        input(f"Pressione ENTER para testar {key_name}...")

    # Tentar pressionar usando press_key (usa o nome)
    success = client.press_key(key_name)

    if success:
        print(f"✅ {key_name} enviada com sucesso")
        print(f"   - Coil {address} → ON (100ms) → OFF")
    else:
        print(f"❌ {key_name} falhou ao enviar")

    if interactive:
        time.sleep(0.5)  # Pequeno delay entre teclas

    return success


def main():
    parser = argparse.ArgumentParser(description='Teste sistemático de todas as teclas')
    parser.add_argument('--port', default='/dev/ttyUSB0', help='Porta serial')
    parser.add_argument('--stub', action='store_true', help='Modo stub (simulação)')
    parser.add_argument('--interactive', action='store_true', help='Aguarda Enter entre cada tecla')
    parser.add_argument('--key', help='Testar apenas uma tecla específica (ex: K1)')

    args = parser.parse_args()

    print("╔═══════════════════════════════════════════════════════════════╗")
    print("║           TESTE DE TODAS AS TECLAS - IHM WEB                 ║")
    print("╚═══════════════════════════════════════════════════════════════╝")
    print()
    print(f"Porta: {args.port}")
    print(f"Modo: {'STUB (simulação)' if args.stub else 'LIVE (CLP real)'}")
    print(f"Interativo: {'SIM' if args.interactive else 'NÃO'}")
    print()

    # Conectar
    config = ModbusConfig(port=args.port)
    client = ModbusClient(stub_mode=args.stub, config=config)

    if not client.connect():
        print("❌ Falha ao conectar ao CLP!")
        return 1

    print("✅ Conectado ao CLP\n")

    # Testar teclas
    results = {}

    if args.key:
        # Testar apenas uma tecla
        key_name = args.key.upper()
        if key_name not in ALL_KEYS:
            print(f"❌ Tecla desconhecida: {key_name}")
            print(f"Teclas válidas: {', '.join(ALL_KEYS.keys())}")
            return 1

        address = ALL_KEYS[key_name]
        success = test_key(client, key_name, address, args.interactive)
        results[key_name] = success
    else:
        # Testar todas as teclas
        print("Testando TODAS as 18 teclas...\n")

        # Agrupar por categoria
        categories = [
            ('TECLADO NUMÉRICO', ['K1', 'K2', 'K3', 'K4', 'K5', 'K6', 'K7', 'K8', 'K9', 'K0']),
            ('FUNÇÕES', ['S1', 'S2']),
            ('NAVEGAÇÃO', ['UP', 'DOWN']),
            ('CONTROLE', ['ENTER', 'ESC', 'EDIT', 'LOCK'])
        ]

        for category, keys in categories:
            print(f"\n{'─'*60}")
            print(f"  {category}")
            print(f"{'─'*60}")

            for key_name in keys:
                address = ALL_KEYS[key_name]
                success = test_key(client, key_name, address, args.interactive)
                results[key_name] = success

    # Resumo
    print("\n" + "="*60)
    print("RESUMO DOS TESTES")
    print("="*60)

    passed = sum(1 for v in results.values() if v)
    failed = len(results) - passed

    print(f"\n✅ Passaram: {passed}/{len(results)}")
    print(f"❌ Falharam: {failed}/{len(results)}")

    if failed > 0:
        print("\nTeclas com falha:")
        for key, success in results.items():
            if not success:
                print(f"  - {key} (endereço {ALL_KEYS[key]})")

    print("\n" + "="*60)

    # Desconectar
    client.disconnect()
    print("\n✅ Desconectado")

    return 0 if failed == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
