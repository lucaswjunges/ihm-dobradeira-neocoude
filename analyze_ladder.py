"""
analyze_ladder.py

Analisa os arquivos ladder para identificar endereços importantes
"""

import re
from collections import defaultdict

# Endereços conhecidos para referência
known = {
    '00A0-00A8': 'Teclas K1-K9',
    '00A9': 'Tecla K0',
    '00DC': 'Tecla S1',
    '00DD': 'Tecla S2',
    '00AC': 'Seta UP',
    '00AD': 'Seta DOWN',
    '00BC': 'ESC',
    '00F1': 'LOCK',
    '0026': 'EDIT',
    '0025': 'ENTER',
    '04D6-04D7': 'Encoder (32-bit)',
    '0100-0107': 'Entradas E0-E7',
    '0180-0187': 'Saídas S0-S7',
    '00BE': 'Modbus Enable (190 dec)',
}

# Dicionário para contagem de endereços
address_count = defaultdict(int)
address_context = defaultdict(list)

# Ler todos os arquivos .lad
import os
ladder_dir = '/home/lucas-junges/Documents/clientes/w&co/ladder_extract'

for filename in os.listdir(ladder_dir):
    if filename.endswith('.lad'):
        filepath = os.path.join(ladder_dir, filename)
        with open(filepath, 'r') as f:
            content = f.read()

            # Encontrar todos os endereços E:XXXX
            matches = re.findall(r'E:([0-9A-F]{4})', content)

            for addr in matches:
                address_count[addr] += 1
                if filename not in address_context[addr]:
                    address_context[addr].append(filename)

# Análise por faixa
print("=" * 80)
print("ANÁLISE DE ENDEREÇOS - LADDER NEOCOUDE-HD-15")
print("=" * 80)

# Agrupar por faixas
ranges = {
    'Entradas (0100-0107)': [],
    'Saídas (0180-0187)': [],
    'Estados baixos (0000-00FF)': [],
    'Estados médios (0100-01FF)': [],
    'Estados altos (0200-02FF)': [],
    'Estados controle (0300-03FF)': [],
    'Registros (0400-0FFF)': [],
    'Dados (0800-09FF)': [],
}

for addr in sorted(address_count.keys()):
    addr_int = int(addr, 16)

    if 0x0100 <= addr_int <= 0x0107:
        ranges['Entradas (0100-0107)'].append(addr)
    elif 0x0180 <= addr_int <= 0x0187:
        ranges['Saídas (0180-0187)'].append(addr)
    elif addr_int <= 0x00FF:
        ranges['Estados baixos (0000-00FF)'].append(addr)
    elif 0x0100 <= addr_int <= 0x01FF:
        ranges['Estados médios (0100-01FF)'].append(addr)
    elif 0x0200 <= addr_int <= 0x02FF:
        ranges['Estados altos (0200-02FF)'].append(addr)
    elif 0x0300 <= addr_int <= 0x03FF:
        ranges['Estados controle (0300-03FF)'].append(addr)
    elif 0x0400 <= addr_int <= 0x07FF:
        ranges['Registros (0400-0FFF)'].append(addr)
    elif 0x0800 <= addr_int <= 0x09FF:
        ranges['Dados (0800-09FF)'].append(addr)

for range_name, addrs in ranges.items():
    if addrs:
        print(f"\n{range_name}:")
        for addr in sorted(addrs):
            count = address_count[addr]
            files = ', '.join(address_context[addr])
            print(f"  {addr} ({int(addr, 16):4d} dec) - usado {count:2d}x em: {files}")

print("\n" + "=" * 80)
print("ENDEREÇOS MAIS USADOS (>5 vezes):")
print("=" * 80)

for addr, count in sorted(address_count.items(), key=lambda x: x[1], reverse=True):
    if count > 5:
        files = ', '.join(address_context[addr])
        print(f"{addr} ({int(addr, 16):4d} dec): {count:2d}x - {files}")

print("\n" + "=" * 80)
print("POSSÍVEIS MAPEAMENTOS:")
print("=" * 80)

# Baseado na documentação, tentar mapear
mappings = {
    '0300-0308': 'Bits de modo/ciclo (ver manual - estados de dobra)',
    '0190-0191': 'Estados de entrada (relacionados a E0-E7)',
    '0200-0201': 'Estados intermediários',
    '0210-0215': 'Estados de saída',
    '0840-0858': 'POSSÍVEL: Setpoints de ângulo (registros)',
    '0942-0944': 'POSSÍVEL: Valores de comparação',
    '0960-0966': 'POSSÍVEL: Parâmetros adicionais',
}

for range_desc, description in mappings.items():
    print(f"{range_desc}: {description}")
