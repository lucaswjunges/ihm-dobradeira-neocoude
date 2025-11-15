#!/usr/bin/env python3
"""
Gerador de arquivo .SUP com 10 rotinas (ROT0-ROT9)
Base: clp_pronto_CORRIGIDO.sup (funciona 100%)
Adiciona: ROT6-ROT9 do CLP_FINAL_10_ROTINAS

Segue TODAS as especificações do GUIA_DEFINITIVO_GERACAO_SUP.md
"""

import zipfile
import os
from datetime import datetime

def normalize_line_endings(content: bytes) -> bytes:
    """Converte para CRLF (DOS) - aceita bytes"""
    # Remove CR existentes e reconverte
    content_str = content.decode('latin-1', errors='replace')
    content_str = content_str.replace('\r\n', '\n').replace('\n', '\r\n')
    return content_str.encode('latin-1', errors='replace')

def verify_crlf(content: bytes, filename: str) -> bool:
    """Verifica se arquivo tem CRLF"""
    has_crlf = b'\r\n' in content
    has_only_lf = b'\n' in content and not has_crlf

    if has_only_lf:
        print(f"  ⚠️  {filename}: Usa LF (Unix) - SERÁ CONVERTIDO")
        return False
    elif has_crlf:
        print(f"  ✅ {filename}: Usa CRLF (DOS) - OK")
        return True
    else:
        print(f"  ⚠️  {filename}: Sem quebras de linha ou binário")
        return True  # Arquivos binários são OK

def create_sup_from_bases(
    base_sup_path: str,
    rot6_9_sup_path: str,
    output_sup_path: str
):
    """
    Cria novo arquivo .SUP combinando:
    - Base (ROT0-ROT5): clp_pronto_CORRIGIDO.sup
    - ROT6-ROT9: CLP_FINAL_10_ROTINAS_20251112_102801.sup
    """

    print("=" * 60)
    print("GERADOR DE ARQUIVO .SUP COM 10 ROTINAS")
    print("=" * 60)

    # Timestamp único
    now = datetime.now()
    date_time = (now.year, now.month, now.day, now.hour, now.minute, now.second)

    # Ordem correta de arquivos no ZIP (CRÍTICO!)
    file_order = [
        'Project.spr',
        'Projeto.txt',
        'Screen.dbf',
        'Screen.smt',
        'Perfil.dbf',
        'Conf.dbf',
        'Conf.smt',
        'Conf.nsx',
        'Principal.lad',
        'Principal.txt',
        'Int1.lad',
        'Int1.txt',
        'Int2.lad',
        'Int2.txt',
    ]

    # Adiciona ROT0-ROT9
    for i in range(10):
        file_order.append(f'ROT{i}.lad')
        file_order.append(f'ROT{i}.txt')

    # Adiciona Pseudo.lad no final
    file_order.append('Pseudo.lad')

    # Extrai arquivos da base (ROT0-ROT5)
    print("\n📦 Lendo arquivo BASE (clp_pronto_CORRIGIDO.sup)...")
    base_files = {}
    with zipfile.ZipFile(base_sup_path, 'r') as z_base:
        for name in z_base.namelist():
            content = z_base.read(name)
            base_files[name] = content

            # Verifica CRLF em arquivos .lad
            if name.endswith('.lad'):
                verify_crlf(content, name)

    print(f"  ✅ {len(base_files)} arquivos lidos da base")

    # Extrai ROT6-ROT9 do segundo arquivo
    print("\n📦 Lendo arquivo com ROT6-ROT9 (CLP_FINAL_10_ROTINAS)...")
    rot6_9_files = {}
    with zipfile.ZipFile(rot6_9_sup_path, 'r') as z_rot:
        for name in z_rot.namelist():
            if name.startswith('ROT') and int(name[3]) >= 6:  # ROT6, ROT7, ROT8, ROT9
                content = z_rot.read(name)

                # Normaliza CRLF se for .lad
                if name.endswith('.lad'):
                    if not verify_crlf(content, name):
                        content = normalize_line_endings(content)
                        print(f"    🔧 {name}: Convertido para CRLF")

                rot6_9_files[name] = content

    print(f"  ✅ {len(rot6_9_files)} arquivos lidos (ROT6-ROT9)")

    # Combina os arquivos
    print("\n🔨 Criando arquivo .SUP final...")
    all_files = {**base_files, **rot6_9_files}

    # Cria novo ZIP na ordem correta
    with zipfile.ZipFile(output_sup_path, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=6) as z_out:

        written_count = 0

        for filename in file_order:
            if filename in all_files:
                content = all_files[filename]

                # Cria ZipInfo com timestamp
                zinfo = zipfile.ZipInfo(filename=filename, date_time=date_time)
                zinfo.compress_type = zipfile.ZIP_DEFLATED

                # Escreve no ZIP
                z_out.writestr(zinfo, content, compress_type=zipfile.ZIP_DEFLATED, compresslevel=6)

                size_kb = len(content) / 1024
                print(f"  ✅ {filename}: {size_kb:.2f} KB")
                written_count += 1
            else:
                print(f"  ⚠️  {filename}: NÃO ENCONTRADO")

    # Verificação final
    file_size = os.path.getsize(output_sup_path)
    print("\n" + "=" * 60)
    print(f"🎉 Arquivo criado: {output_sup_path}")
    print(f"📦 Tamanho: {file_size:,} bytes ({file_size/1024:.2f} KB)")
    print(f"📄 Arquivos: {written_count}")
    print("=" * 60)

    # Validações
    if file_size < 50000:
        print(f"⚠️  ATENÇÃO: Arquivo pequeno (< 50 KB)! Pode estar incompleto.")
    else:
        print(f"✅ Tamanho OK (> 50 KB)")

    if written_count < 34:
        print(f"⚠️  ATENÇÃO: Esperados 34 arquivos, encontrados {written_count}")
    else:
        print(f"✅ Todos os {written_count} arquivos incluídos")

    # Lista final
    print("\n📋 Conteúdo final do .SUP:")
    with zipfile.ZipFile(output_sup_path, 'r') as z:
        for info in z.infolist():
            print(f"  {info.filename:20s} {info.file_size:8d} bytes")

if __name__ == '__main__':
    # Caminhos dos arquivos
    base_path = '/home/lucas-junges/Documents/clientes/w&co/ihm/sups/clp_pronto_CORRIGIDO.sup'
    rot6_9_path = '/home/lucas-junges/Documents/clientes/w&co/ihm/CLP_FINAL_10_ROTINAS_20251112_102801.sup'
    output_path = '/home/lucas-junges/Documents/clientes/w&co/ihm/sups/CLP_COMPLETO_10_ROTINAS_FINAL.sup'

    # Verifica se arquivos base existem
    if not os.path.exists(base_path):
        print(f"❌ ERRO: Arquivo base não encontrado: {base_path}")
        exit(1)

    if not os.path.exists(rot6_9_path):
        print(f"❌ ERRO: Arquivo com ROT6-ROT9 não encontrado: {rot6_9_path}")
        exit(1)

    # Gera o arquivo
    create_sup_from_bases(base_path, rot6_9_path, output_path)

    print("\n✅ CONCLUÍDO! Arquivo pronto para usar no Winsup 2")
