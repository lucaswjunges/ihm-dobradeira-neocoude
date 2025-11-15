#!/usr/bin/env python3
"""
Gerador DEFINITIVO do arquivo .SUP com 10 rotinas
Estratégia: Usar CLP_FINAL_10_ROTINAS como base (tem Project.spr e Principal.lad corretos)
           Apenas substituir ROT5.lad truncado pelo correto do clp_pronto_CORRIGIDO.sup
"""

import zipfile
import os
from datetime import datetime

def create_final_sup():
    print("=" * 70)
    print("GERADOR DEFINITIVO - .SUP COM 10 ROTINAS")
    print("=" * 70)

    # Caminhos
    base_10_rotinas = '/home/lucas-junges/Documents/clientes/w&co/ihm/CLP_FINAL_10_ROTINAS_20251112_102801.sup'
    base_corrigida = '/home/lucas-junges/Documents/clientes/w&co/ihm/sups/clp_pronto_CORRIGIDO.sup'
    output_sup = '/home/lucas-junges/Documents/clientes/w&co/ihm/CLP_FINAL_10_ROTINAS_PRONTO.sup'

    # Timestamp único
    now = datetime.now()
    date_time = (now.year, now.month, now.day, now.hour, now.minute, now.second)

    print(f"\n📦 Base (10 rotinas): {os.path.basename(base_10_rotinas)}")
    print(f"📦 ROT5 correta de: {os.path.basename(base_corrigida)}")
    print(f"📦 Saída: {os.path.basename(output_sup)}")

    # Lê ROT5.lad correto
    print("\n🔍 Lendo ROT5.lad correto...")
    with zipfile.ZipFile(base_corrigida, 'r') as z:
        rot5_correto = z.read('ROT5.lad')
        rot5_txt = z.read('ROT5.txt')

    print(f"  ✅ ROT5.lad: {len(rot5_correto)} bytes (correto)")

    # Ordem correta de arquivos
    file_order = [
        'Project.spr', 'Projeto.txt',
        'Screen.dbf', 'Screen.smt', 'Perfil.dbf',
        'Conf.dbf', 'Conf.smt', 'Conf.nsx',
        'Principal.lad', 'Principal.txt',
        'Int1.lad', 'Int1.txt',
        'Int2.lad', 'Int2.txt',
    ]

    for i in range(10):
        file_order.append(f'ROT{i}.lad')
        file_order.append(f'ROT{i}.txt')

    # Cria novo SUP
    print(f"\n🔨 Criando arquivo final...")

    with zipfile.ZipFile(base_10_rotinas, 'r') as z_in:
        with zipfile.ZipFile(output_sup, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=6) as z_out:

            for filename in file_order:
                if filename in z_in.namelist():
                    # Substitui ROT5.lad pelo correto
                    if filename == 'ROT5.lad':
                        content = rot5_correto
                        print(f"  ✅ {filename}: {len(content)} bytes (SUBSTITUÍDO pelo correto)")
                    elif filename == 'ROT5.txt':
                        content = rot5_txt
                        print(f"  ✅ {filename}: {len(content)} bytes")
                    else:
                        content = z_in.read(filename)
                        size = len(content)

                        # Verifica CRLF em arquivos .lad
                        if filename.endswith('.lad') and size > 0:
                            has_crlf = b'\r\n' in content
                            has_lf_only = b'\n' in content and not has_crlf

                            if has_lf_only:
                                print(f"  ⚠️  {filename}: {size} bytes (AVISO: formato LF)")
                            else:
                                print(f"  ✅ {filename}: {size} bytes")
                        else:
                            print(f"  ✅ {filename}: {size} bytes")

                    # Escreve no ZIP
                    zinfo = zipfile.ZipInfo(filename=filename, date_time=date_time)
                    zinfo.compress_type = zipfile.ZIP_DEFLATED
                    z_out.writestr(zinfo, content, compress_type=zipfile.ZIP_DEFLATED, compresslevel=6)
                else:
                    print(f"  ⚠️  {filename}: NÃO ENCONTRADO")

    file_size = os.path.getsize(output_sup)
    print("\n" + "=" * 70)
    print(f"🎉 Arquivo criado: {output_sup}")
    print(f"📦 Tamanho: {file_size:,} bytes ({file_size/1024:.2f} KB)")
    print("=" * 70)

    # Verificação adicional
    print("\n🔍 Verificando arquivo criado...")
    with zipfile.ZipFile(output_sup, 'r') as z:
        # Verifica ROT5
        rot5_check = z.read('ROT5.lad')
        if len(rot5_check) > 2000:
            print(f"  ✅ ROT5.lad: {len(rot5_check)} bytes (OK)")
        else:
            print(f"  ❌ ROT5.lad: {len(rot5_check)} bytes (MUITO PEQUENO!)")

        # Verifica Project.spr
        project_spr = z.read('Project.spr').decode('latin-1')
        if 'ROT9' in project_spr:
            print(f"  ✅ Project.spr: ROT0-ROT9 declaradas")
        else:
            print(f"  ⚠️  Project.spr: Pode estar faltando ROT6-ROT9")

        # Verifica Principal.lad
        principal = z.read('Principal.lad')
        call_count = principal.count(b'E:ROT')
        print(f"  ✅ Principal.lad: {call_count} chamadas CALL")

        # Verifica formato
        has_crlf = b'\r\n' in principal
        has_lf_only = b'\n' in principal and not has_crlf

        if has_lf_only:
            print(f"  ⚠️  Principal.lad: AVISO - formato LF detectado")
        elif has_crlf:
            print(f"  ✅ Principal.lad: Formato CRLF correto")

if __name__ == '__main__':
    create_final_sup()
    print("\n✅ CONCLUÍDO! Teste no Winsup 2")
