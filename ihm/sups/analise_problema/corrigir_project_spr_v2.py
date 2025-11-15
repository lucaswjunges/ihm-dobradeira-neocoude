#!/usr/bin/env python3
"""
Corrige o arquivo .SUP adicionando ROT5-ROT9 no Project.spr CORRETAMENTE
e as chamadas CALL no Principal.lad
"""

import zipfile
import os
from datetime import datetime
import re

def update_project_spr(original_content: bytes) -> bytes:
    """
    Atualiza Project.spr para incluir ROT0-ROT9 sem duplicação
    """
    content_str = original_content.decode('latin-1')

    # Procura a linha com ROTx ;~!@
    rot_line_match = re.search(r'(ROT\d+ ;~!@)+', content_str)

    if rot_line_match:
        old_rot_line = rot_line_match.group(0)

        # Extrai quais ROTs já existem
        existing_rots = set(re.findall(r'ROT(\d+)', old_rot_line))

        # Cria a lista completa ROT0-ROT9
        new_rot_line = ''.join([f'ROT{i} ;~!@' for i in range(10)])

        # Substitui
        content_str = content_str.replace(old_rot_line, new_rot_line)

        added_rots = set(str(i) for i in range(10)) - existing_rots
        if added_rots:
            print(f"  ✅ Project.spr: Adicionadas ROT{', ROT'.join(sorted(added_rots))}")
        else:
            print(f"  ℹ️  Project.spr: Todas as rotinas já estavam declaradas")
    else:
        print(f"  ⚠️  Project.spr: Formato não reconhecido, não modificado")

    return content_str.encode('latin-1')

def update_principal_lad(original_content: bytes) -> bytes:
    """
    Adiciona chamadas CALL para ROT5-ROT9 no Principal.lad
    se ainda não existirem
    """
    content_str = original_content.decode('latin-1')

    # Template de uma chamada CALL
    call_template = """[Line{line_num:05d}]
  [Features]
    Branchs:01
    Type:0
    Label:0
    Comment:0
    Out:CALL    T:-001 Size:001 E:ROT{rot_num}
    Height:01
  [Branch01]
    X1position:00
    X2position:13
    Yposition:00
    Height:01
    B1:00
    B2:00
    BInputnumber:00
    {{0;00;-1;-1;-1;-1;-1;00}}
    ###

"""

    # Verifica quais ROTs já têm CALL
    existing_calls = set(re.findall(r'E:ROT(\d+)', content_str))

    # Conta o número de linhas existentes
    lines = re.findall(r'\[Line(\d{5})\]', content_str)
    if lines:
        last_line_num = max(int(line) for line in lines)
    else:
        last_line_num = 0

    # Atualiza o contador de linhas no header
    lines_match = re.search(r'Lines:(\d{5})', content_str)
    if lines_match:
        current_lines = int(lines_match.group(1))
    else:
        current_lines = last_line_num

    additions = []
    next_line_num = last_line_num + 1

    # Adiciona CALL para ROT0-ROT9 que ainda não existem
    for rot_num in range(10):
        if str(rot_num) not in existing_calls:
            additions.append((rot_num, next_line_num))
            next_line_num += 1

    if additions:
        # Adiciona as novas linhas no final
        new_calls = ""
        for rot_num, line_num in additions:
            new_calls += call_template.format(line_num=line_num, rot_num=rot_num)
            print(f"  ✅ Principal.lad: Adicionada CALL ROT{rot_num}")

        # Insere antes do final do arquivo
        content_str = content_str.rstrip('\r\n') + '\r\n' + new_calls

        # Atualiza o contador de linhas
        new_total_lines = current_lines + len(additions)
        content_str = re.sub(r'Lines:\d{5}', f'Lines:{new_total_lines:05d}', content_str)
        print(f"  ✅ Principal.lad: Total de linhas: {current_lines} → {new_total_lines}")
    else:
        print(f"  ℹ️  Principal.lad: Todas as chamadas CALL já existem")

    return content_str.encode('latin-1')

def fix_sup_file(input_sup: str, output_sup: str):
    """
    Corrige o arquivo .SUP adicionando ROT0-ROT9 onde necessário
    """
    print("=" * 70)
    print("CORREÇÃO DE ARQUIVO .SUP - ROT0-ROT9 COMPLETO")
    print("=" * 70)

    # Timestamp único
    now = datetime.now()
    date_time = (now.year, now.month, now.day, now.hour, now.minute, now.second)

    print(f"\n📦 Lendo: {input_sup}")

    # Lê o arquivo original
    with zipfile.ZipFile(input_sup, 'r') as z_in:
        with zipfile.ZipFile(output_sup, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=6) as z_out:

            for name in z_in.namelist():
                content = z_in.read(name)

                # Atualiza Project.spr
                if name == 'Project.spr':
                    print(f"\n🔧 Processando: {name}")
                    content = update_project_spr(content)

                # Atualiza Principal.lad
                elif name == 'Principal.lad':
                    print(f"\n🔧 Processando: {name}")
                    content = update_principal_lad(content)

                # Escreve no novo ZIP
                zinfo = zipfile.ZipInfo(filename=name, date_time=date_time)
                zinfo.compress_type = zipfile.ZIP_DEFLATED
                z_out.writestr(zinfo, content, compress_type=zipfile.ZIP_DEFLATED, compresslevel=6)

    file_size = os.path.getsize(output_sup)
    print("\n" + "=" * 70)
    print(f"🎉 Arquivo corrigido: {output_sup}")
    print(f"📦 Tamanho: {file_size:,} bytes ({file_size/1024:.2f} KB)")
    print("=" * 70)

if __name__ == '__main__':
    # Usar arquivo BASE (sem as correções anteriores) para evitar duplicações
    input_path = '/home/lucas-junges/Documents/clientes/w&co/ihm/sups/CLP_COMPLETO_10_ROTINAS_FINAL.sup'
    output_path = '/home/lucas-junges/Documents/clientes/w&co/ihm/CLP_COMPLETO_10_ROTINAS_FINAL_CORRIGIDO.sup'

    if not os.path.exists(input_path):
        print(f"❌ ERRO: Arquivo não encontrado: {input_path}")
        exit(1)

    fix_sup_file(input_path, output_path)

    print("\n✅ CONCLUÍDO! Arquivo pronto para usar no Winsup 2")
