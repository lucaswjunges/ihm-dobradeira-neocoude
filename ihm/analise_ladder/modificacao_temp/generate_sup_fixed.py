#!/usr/bin/env python3
"""
Gerador de arquivo .SUP com encoding correto - VERSÃO CORRIGIDA
Inclui Pseudo.lad que estava faltando
"""

import zipfile
import os
from datetime import datetime

def normalize_line_endings(text: str) -> str:
    """Converte para CRLF (DOS)"""
    return text.replace('\r\n', '\n').replace('\n', '\r\n')

def convert_file_to_crlf(filepath: str):
    """Converte arquivo para CRLF"""
    with open(filepath, 'rb') as f:
        content = f.read()

    # Decode, normalize, encode
    text = content.decode('latin-1', errors='replace')
    text_crlf = normalize_line_endings(text)
    content_crlf = text_crlf.encode('latin-1', errors='replace')

    with open(filepath, 'wb') as f:
        f.write(content_crlf)

    print(f"✅ {os.path.basename(filepath)}: convertido para CRLF ({len(content_crlf)} bytes)")

def create_sup_file(output_path: str, source_dir: str):
    """Cria arquivo .SUP com todos os arquivos necessários"""

    # Timestamp único para todos os arquivos
    now = datetime.now()
    date_time = (now.year, now.month, now.day, now.hour, now.minute, now.second)

    # Converter todos os .lad para CRLF ANTES de compactar
    lad_files = [
        'Principal.lad', 'Int1.lad', 'Int2.lad',
        'ROT0.lad', 'ROT1.lad', 'ROT2.lad', 'ROT3.lad', 'ROT4.lad', 'ROT5.lad',
        'Pseudo.lad'  # ADICIONADO!
    ]

    for lad_file in lad_files:
        filepath = os.path.join(source_dir, lad_file)
        if os.path.exists(filepath):
            convert_file_to_crlf(filepath)

    # Lista de arquivos na ordem EXATA (crítico!)
    file_order = [
        'Project.spr', 'Projeto.txt',
        'Screen.dbf', 'Screen.smt', 'Perfil.dbf',
        'Conf.dbf', 'Conf.smt', 'Conf.nsx',
        'Principal.lad', 'Principal.txt',
        'Int1.lad', 'Int1.txt', 'Int2.lad', 'Int2.txt',
        'ROT0.lad', 'ROT0.txt', 'ROT1.lad', 'ROT1.txt',
        'ROT2.lad', 'ROT2.txt', 'ROT3.lad', 'ROT3.txt',
        'ROT4.lad', 'ROT4.txt', 'ROT5.lad', 'ROT5.txt',
        'Pseudo.lad',  # ADICIONADO! (sem .txt correspondente)
    ]

    with zipfile.ZipFile(output_path, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        for filename in file_order:
            filepath = os.path.join(source_dir, filename)

            if os.path.exists(filepath):
                # Criar ZipInfo com timestamp correto
                zinfo = zipfile.ZipInfo(filename=filename, date_time=date_time)
                zinfo.compress_type = zipfile.ZIP_DEFLATED
                zinfo.external_attr = 0o644 << 16

                with open(filepath, 'rb') as f:
                    content = f.read()

                z.writestr(zinfo, content, compress_type=zipfile.ZIP_DEFLATED, compresslevel=6)
                print(f"✅ {filename}: {len(content)} bytes")
            else:
                print(f"⚠️  {filename}: NÃO ENCONTRADO")

    # Verificação final
    file_size = os.path.getsize(output_path)
    print(f"\n🎉 Arquivo {output_path} criado com sucesso!")
    print(f"📦 Tamanho: {file_size:,} bytes")

    if file_size < 50000:
        print(f"⚠️  ATENÇÃO: Arquivo pequeno ({file_size} bytes). Esperado > 50KB")

    return file_size

if __name__ == '__main__':
    source_dir = '.'
    output_path = 'clp_MODIFICADO_IHM_WEB.sup'

    print("="*70)
    print("🔧 GERADOR DE ARQUIVO .SUP - ATOS MPC4004 (VERSÃO CORRIGIDA)")
    print("="*70)
    print()

    create_sup_file(output_path, source_dir)

    print("\n" + "="*70)
    print("✅ PRONTO! Arquivo gerado:")
    print(f"   {os.path.abspath(output_path)}")
    print("="*70)
