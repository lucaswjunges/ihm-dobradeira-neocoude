#!/usr/bin/env python3
"""
Corrige ordem dos arquivos em .SUP para formato Winsup 2
Extrai .sup existente e recria com ordem correta
"""

import zipfile
import sys
from pathlib import Path
from datetime import datetime

def fix_sup_order(input_sup: str, output_sup: str):
    """
    Extrai .sup e recria com ordem correta de arquivos

    Args:
        input_sup: Caminho do .sup com ordem errada
        output_sup: Caminho do .sup corrigido
    """

    # Ordem CORRETA dos arquivos (segundo GUIA_DEFINITIVO_GERACAO_SUP.md)
    CORRECT_ORDER = [
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
        CORRECT_ORDER.extend([f'ROT{i}.lad', f'ROT{i}.txt'])

    print(f"📦 Corrigindo ordem do arquivo: {input_sup}")
    print(f"🎯 Saída: {output_sup}\n")

    # 1. Ler todos os arquivos do .sup original
    files_data = {}
    with zipfile.ZipFile(input_sup, 'r') as z_in:
        for name in z_in.namelist():
            files_data[name] = z_in.read(name)
            print(f"   ✓ Lido: {name} ({len(files_data[name])} bytes)")

    print(f"\n📝 Total de arquivos lidos: {len(files_data)}\n")

    # 2. Criar novo .sup com ordem correta
    with zipfile.ZipFile(output_sup, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=6) as z_out:

        # Timestamp único para todos os arquivos
        now = datetime.now()
        date_time = (now.year, now.month, now.day, now.hour, now.minute, now.second)

        written_count = 0

        for filename in CORRECT_ORDER:
            if filename not in files_data:
                print(f"   ⚠️  AVISO: {filename} não encontrado no .sup original")
                continue

            # Criar ZipInfo com timestamp correto
            zinfo = zipfile.ZipInfo(filename=filename, date_time=date_time)
            zinfo.compress_type = zipfile.ZIP_DEFLATED
            zinfo.external_attr = 0o644 << 16  # Permissões Unix

            # Escrever no novo ZIP
            z_out.writestr(zinfo, files_data[filename], compress_type=zipfile.ZIP_DEFLATED, compresslevel=6)

            written_count += 1
            print(f"   {written_count:02d}. ✅ {filename} ({len(files_data[filename])} bytes)")

    # 3. Verificação final
    output_size = Path(output_sup).stat().st_size
    print(f"\n🎉 Arquivo corrigido criado com sucesso!")
    print(f"📦 Tamanho: {output_size:,} bytes")
    print(f"📄 Total de arquivos: {written_count}\n")

    # 4. Mostrar comparação de ordem
    print("📊 COMPARAÇÃO DE ORDEM:\n")
    print("ANTES (ordem alfabética - ERRADO):")
    with zipfile.ZipFile(input_sup, 'r') as z:
        for i, name in enumerate(z.namelist()[:10], 1):
            print(f"   {i:2d}. {name}")

    print("\nDEPOIS (ordem correta - Winsup 2):")
    with zipfile.ZipFile(output_sup, 'r') as z:
        for i, name in enumerate(z.namelist()[:10], 1):
            print(f"   {i:2d}. {name}")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Uso: python3 fix_sup_order.py arquivo.sup [saida.sup]")
        sys.exit(1)

    input_file = sys.argv[1]

    if len(sys.argv) >= 3:
        output_file = sys.argv[2]
    else:
        # Nome padrão: adiciona "_CORRIGIDO"
        input_path = Path(input_file)
        output_file = str(input_path.parent / f"{input_path.stem}_CORRIGIDO{input_path.suffix}")

    fix_sup_order(input_file, output_file)
