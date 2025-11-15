#!/usr/bin/env python3
"""
Script para corrigir erros de registro na ROT10.lad
- Corrige tipo T:0048 → T:0028 para registros especiais
- Corrige Size:001 → Size:003 para registros 32-bit
- Remove instruções MOV inválidas para registros de I/O digital
"""

import re
import sys

def fix_rot10_lad(input_file, output_file):
    """
    Corrige a ROT10.lad para usar tipos e tamanhos corretos
    """

    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()

    corrections = []

    # CORREÇÃO 1: MOV para registros de encoder (04D6/04D7)
    # Trocar T:0048 Size:001 → T:0028 Size:003
    pattern1 = r'Out:MOV\s+T:0048\s+Size:001(\s+E:04D[67]\s+E:\w+)'
    replacement1 = r'Out:MOV     T:0028 Size:003\1'
    content, count1 = re.subn(pattern1, replacement1, content)
    if count1:
        corrections.append(f"✓ Corrigidos {count1} registros de encoder (04D6/04D7)")

    # CORREÇÃO 2: MOV para registros de ângulo (084x, 085x)
    # Trocar T:0048 Size:001 → T:0028 Size:003
    pattern2 = r'Out:MOV\s+T:0048\s+Size:001(\s+E:08[45][0-9A-F]\s+E:\w+)'
    replacement2 = r'Out:MOV     T:0028 Size:003\1'
    content, count2 = re.subn(pattern2, replacement2, content)
    if count2:
        corrections.append(f"✓ Corrigidos {count2} registros de ângulo (084x/085x)")

    # CORREÇÃO 3: MOV para registros de I/O digital (0100-0107, 0180-0187)
    # OPÇÃO A: Comentar linhas inválidas (mais seguro)
    # OPÇÃO B: Remover linhas completamente
    # Vou usar OPÇÃO A para preservar histórico

    lines = content.split('\n')
    fixed_lines = []
    in_invalid_block = False
    block_lines = []

    for i, line in enumerate(lines):
        # Detecta início de bloco com MOV de I/O inválido
        if re.search(r'Out:MOV\s+T:0048\s+Size:001\s+E:0(10[0-7]|18[0-7])', line):
            in_invalid_block = True
            block_lines = [f"# COMENTADO - Instrução inválida: {line}"]
            corrections.append(f"✓ Linha {i+1}: MOV inválido para I/O (E:{re.search('E:(0[0-9A-F]+)', line).group(1)})")
            continue

        # Se está em bloco inválido, acumula até encontrar ###
        if in_invalid_block:
            block_lines.append(f"# {line}")
            if '###' in line:
                in_invalid_block = False
                # Adiciona bloco comentado
                fixed_lines.extend(block_lines)
                block_lines = []
            continue

        # Linha normal, adiciona
        fixed_lines.append(line)

    # Reconstrói conteúdo
    content = '\n'.join(fixed_lines)

    # Recalcula número de linhas ativas
    active_lines = len([l for l in fixed_lines if not l.strip().startswith('#') and '[Line' in l])

    # Atualiza Lines:XXXXX no cabeçalho
    content = re.sub(r'Lines:\d+', f'Lines:{active_lines:05d}', content, count=1)

    # Salva arquivo corrigido
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(content)

    print("=" * 60)
    print("CORREÇÕES APLICADAS NA ROT10.lad:")
    print("=" * 60)
    for correction in corrections:
        print(correction)
    print("=" * 60)
    print(f"Arquivo original: {input_file}")
    print(f"Arquivo corrigido: {output_file}")
    print(f"Linhas ativas: {active_lines}")
    print("=" * 60)

    return len(corrections)

if __name__ == '__main__':
    input_file = 'ROT10.lad'
    output_file = 'ROT10_FIXED.lad'

    try:
        num_corrections = fix_rot10_lad(input_file, output_file)

        if num_corrections > 0:
            print("\n✅ Correção concluída com sucesso!")
            print(f"\nPróximos passos:")
            print(f"1. Revise o arquivo: {output_file}")
            print(f"2. Substitua ROT10.lad pelo arquivo corrigido")
            print(f"3. Recompacte o .sup: zip -r CLP_FIXED.sup *.lad *.txt *.dbf *.smt *.spr *.nsx")
            print(f"4. Abra CLP_FIXED.sup no WinSUP2 e verifique os erros")
        else:
            print("\n⚠️  Nenhuma correção foi necessária ou padrões não encontrados")

        sys.exit(0)

    except FileNotFoundError:
        print(f"❌ ERRO: Arquivo {input_file} não encontrado")
        print(f"Execute este script no diretório que contém ROT10.lad")
        sys.exit(1)

    except Exception as e:
        print(f"❌ ERRO durante correção: {e}")
        sys.exit(1)
