#!/usr/bin/env python3
"""
FIND: Encontrar onde está o encoder de verdade
================================================

Varre TODOS os registros e mostra quais MUDAM quando você gira o eixo.
"""

import time
from modbus_client import ModbusClientWrapper

def scan_range(client, start, end, func_name, read_func):
    """Varre um range de endereços"""
    print(f"\n{'='*80}")
    print(f"Varrendo {func_name}: 0x{start:04X} até 0x{end:04X}")
    print(f"{'='*80}\n")

    # Lê valores iniciais
    print("Lendo valores iniciais...")
    initial_values = {}

    for addr in range(start, end + 1):
        try:
            result = read_func(address=addr, count=1, slave=client.slave_id)
            if not result.isError():
                initial_values[addr] = result.registers[0]
        except:
            pass

    print(f"✓ Lidos {len(initial_values)} registros com sucesso\n")

    if len(initial_values) == 0:
        print(f"✗ Nenhum registro lido! {func_name} não funciona neste range.\n")
        return

    print("=" * 80)
    print("AGORA: Gire o eixo do encoder LENTAMENTE...")
    print("Pressione Ctrl+C quando terminar")
    print("=" * 80)
    print()

    changed = {}

    try:
        count = 0
        while True:
            count += 1

            # A cada 5 leituras, mostra progresso
            if count % 5 == 0:
                print(f"Leituras: {count} | Registros que mudaram: {len(changed)}", end='\r')

            # Lê todos os endereços novamente
            for addr in initial_values.keys():
                try:
                    result = read_func(address=addr, count=1, slave=client.slave_id)
                    if not result.isError():
                        current_value = result.registers[0]

                        # Verifica se mudou
                        if current_value != initial_values[addr]:
                            if addr not in changed:
                                changed[addr] = {
                                    'initial': initial_values[addr],
                                    'current': current_value,
                                    'delta': current_value - initial_values[addr]
                                }
                                print(f"\n🎯 ENCONTRADO! 0x{addr:04X} mudou: {initial_values[addr]} → {current_value} (Δ={current_value - initial_values[addr]:+d})")
                            else:
                                # Atualiza delta
                                changed[addr]['current'] = current_value
                                changed[addr]['delta'] = current_value - changed[addr]['initial']
                except:
                    pass

            time.sleep(0.05)

    except KeyboardInterrupt:
        print("\n\n" + "=" * 80)
        print("RESULTADOS:")
        print("=" * 80)

        if len(changed) == 0:
            print("\n✗ Nenhum registro mudou!")
            print(f"   {func_name} pode não ser a função correta para o encoder.\n")
        else:
            print(f"\n✓ Encontrados {len(changed)} registros que mudaram:\n")

            for addr, info in sorted(changed.items()):
                print(f"  0x{addr:04X} ({addr:4d}): {info['initial']:5d} → {info['current']:5d} (Δ={info['delta']:+6d})")

            print("\n🎯 PROVÁVEL ENCODER:")
            # O encoder deve ter o maior delta (mais mudanças)
            max_delta_addr = max(changed.items(), key=lambda x: abs(x[1]['delta']))
            addr, info = max_delta_addr
            print(f"   Endereço: 0x{addr:04X} ({addr} decimal)")
            print(f"   Função:   {func_name}")
            print(f"   Delta:    {info['delta']:+d} pulsos\n")

def main():
    print("=" * 80)
    print("FIND: Encontrando o encoder REAL no CLP")
    print("=" * 80)
    print()

    client = ModbusClientWrapper(stub_mode=False, port='/dev/ttyUSB0', baudrate=57600, slave_id=1)

    if not client.connected:
        print("✗ CLP não conectado!")
        return

    print("✓ Conectado ao CLP!\n")

    # Range importante: área do high-speed counter
    start = 0x04D0  # 1232
    end = 0x04DF    # 1247

    print("Vamos testar HOLDING REGISTERS e INPUT REGISTERS...")
    print()

    # Testa HOLDING REGISTERS (FC 0x03)
    scan_range(client, start, end, "HOLDING REGISTERS (FC 0x03)",
               client.client.read_holding_registers)

    # Testa INPUT REGISTERS (FC 0x04)
    scan_range(client, start, end, "INPUT REGISTERS (FC 0x04)",
               client.client.read_input_registers)

    client.close()

if __name__ == "__main__":
    main()
