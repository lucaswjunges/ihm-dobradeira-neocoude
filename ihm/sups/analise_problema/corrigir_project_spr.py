#!/usr/bin/env python3
"""
Corrige o arquivo .SUP adicionando ROT5-ROT9 no Project.spr
e as chamadas CALL no Principal.lad
"""

import zipfile
import os
from datetime import datetime

def update_project_spr(original_content: bytes) -> bytes:
    """
    Atualiza Project.spr para incluir ROT5-ROT9
    Original: ROT0 ;~!@ROT1 ;~!@ROT2 ;~!@ROT3 ;~!@ROT4 ;~!@
    Novo:     ROT0 ;~!@ROT1 ;~!@ROT2 ;~!@ROT3 ;~!@ROT4 ;~!@ROT5 ;~!@ROT6 ;~!@ROT7 ;~!@ROT8 ;~!@ROT9 ;~!@
    """
    content_str = original_content.decode('latin-1')

    # Encontra a linha com ROT0-ROT4
    if 'ROT0 ;~!@' in content_str:
        # Adiciona ROT5-ROT9
        old_line = 'ROT0 ;~!@ROT1 ;~!@ROT2 ;~!@ROT3 ;~!@ROT4 ;~!@'
        new_line = 'ROT0 ;~!@ROT1 ;~!@ROT2 ;~!@ROT3 ;~!@ROT4 ;~!@ROT5 ;~!@ROT6 ;~!@ROT7 ;~!@ROT8 ;~!@ROT9 ;~!@'

        content_str = content_str.replace(old_line, new_line)
        print(f"  ✅ Project.spr: Adicionadas ROT5-ROT9")
    elif 'ROT5 ;~!@' in content_str:
        # Já tem ROT5, adiciona apenas ROT6-ROT9
        old_line = 'ROT0 ;~!@ROT1 ;~!@ROT2 ;~!@ROT3 ;~!@ROT4 ;~!@ROT5 ;~!@'
        new_line = 'ROT0 ;~!@ROT1 ;~!@ROT2 ;~!@ROT3 ;~!@ROT4 ;~!@ROT5 ;~!@ROT6 ;~!@ROT7 ;~!@ROT8 ;~!@ROT9 ;~!@'

        content_str = content_str.replace(old_line, new_line)
        print(f"  ✅ Project.spr: Adicionadas ROT6-ROT9")
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
    has_rot5 = 'E:ROT5' in content_str
    has_rot6 = 'E:ROT6' in content_str
    has_rot7 = 'E:ROT7' in content_str
    has_rot8 = 'E:ROT8' in content_str
    has_rot9 = 'E:ROT9' in content_str

    # Conta o número de linhas existentes
    import re
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

    if not has_rot5:
        additions.append((5, next_line_num))
        next_line_num += 1

    if not has_rot6:
        additions.append((6, next_line_num))
        next_line_num += 1

    if not has_rot7:
        additions.append((7, next_line_num))
        next_line_num += 1

    if not has_rot8:
        additions.append((8, next_line_num))
        next_line_num += 1

    if not has_rot9:
        additions.append((9, next_line_num))
        next_line_num += 1

    if additions:
        # Adiciona as novas linhas no final (antes de fechar o arquivo)
        new_calls = ""
        for rot_num, line_num in additions:
            new_calls += call_template.format(line_num=line_num, rot_num=rot_num)
            print(f"  ✅ Principal.lad: Adicionada CALL ROT{rot_num}")

        # Insere antes do final do arquivo (geralmente tem apenas \r\n no final)
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
    Corrige o arquivo .SUP adicionando ROT5-ROT9 onde necessário
    """
    print("=" * 70)
    print("CORREÇÃO DE ARQUIVO .SUP - ADICIONANDO ROT5-ROT9")
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
    input_path = '/home/lucas-junges/Documents/clientes/w&co/ihm/sups/CLP_COMPLETO_10_ROTINAS_FINAL.sup'
    output_path = '/home/lucas-junges/Documents/clientes/w&co/ihm/sups/CLP_COMPLETO_10_ROTINAS_FINAL_V2.sup'

    if not os.path.exists(input_path):
        print(f"❌ ERRO: Arquivo não encontrado: {input_path}")
        exit(1)

    fix_sup_file(input_path, output_path)

    print("\n✅ CONCLUÍDO! Arquivo pronto para usar no Winsup 2")
