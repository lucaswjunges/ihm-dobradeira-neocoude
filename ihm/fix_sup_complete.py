#!/usr/bin/env python3
"""
Corrige .SUP com TODAS as especificações do Winsup 2:
- Ordem correta de arquivos
- Timestamp DOS padrão (1980-01-01 00:00)
- Compressão Deflate nível 6
- Atributos MS-DOS corretos
"""

import zipfile
import sys
from pathlib import Path

def fix_sup_complete(input_sup: str, output_sup: str):
    """
    Extrai .sup e recria com TODAS as especificações Winsup 2

    Args:
        input_sup: Caminho do .sup com problemas
        output_sup: Caminho do .sup corrigido
    """

    # Ordem CORRETA dos arquivos
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

    print(f"📦 Corrigindo arquivo: {input_sup}")
    print(f"🎯 Saída: {output_sup}\n")

    # 1. Ler todos os arquivos do .sup original
    files_data = {}
    with zipfile.ZipFile(input_sup, 'r') as z_in:
        for name in z_in.namelist():
            files_data[name] = z_in.read(name)
            print(f"   ✓ Lido: {name} ({len(files_data[name])} bytes)")

    print(f"\n📝 Total de arquivos lidos: {len(files_data)}\n")

    # 2. Criar novo .sup com especificações EXATAS do Winsup 2
    with zipfile.ZipFile(output_sup, 'w', compression=zipfile.ZIP_DEFLATED) as z_out:

        # Timestamp padrão DOS (1980-01-01 00:00:00)
        DOS_DATE = (1980, 1, 1, 0, 0, 0)

        written_count = 0

        for filename in CORRECT_ORDER:
            if filename not in files_data:
                print(f"   ⚠️  AVISO: {filename} não encontrado")
                continue

            # Criar ZipInfo com especificações MS-DOS
            zinfo = zipfile.ZipInfo(filename=filename, date_time=DOS_DATE)
            zinfo.compress_type = zipfile.ZIP_DEFLATED

            # Atributos MS-DOS (arquivo normal)
            # Bit 5 = Archive bit (0x20)
            zinfo.external_attr = 0x20

            # Flag para indicar que é texto ASCII (opcional)
            zinfo.flag_bits = 0

            # Escrever no novo ZIP com compressão nível 6
            z_out.writestr(
                zinfo,
                files_data[filename],
                compress_type=zipfile.ZIP_DEFLATED,
                compresslevel=6
            )

            written_count += 1

            # Verificar tamanho descomprimido vs comprimido
            info = z_out.getinfo(filename)
            ratio = 100 - int(info.compress_size * 100 / info.file_size) if info.file_size > 0 else 0

            print(f"   {written_count:02d}. ✅ {filename}")
            print(f"       Original: {info.file_size} bytes")
            print(f"       Comprimido: {info.compress_size} bytes ({ratio}% redução)")

    # 3. Verificação final
    output_size = Path(output_sup).stat().st_size
    print(f"\n🎉 Arquivo corrigido criado!")
    print(f"📦 Tamanho: {output_size:,} bytes")
    print(f"📄 Arquivos: {written_count}\n")

    # 4. Verificar detalhes técnicos
    print("🔧 VERIFICAÇÃO TÉCNICA:\n")
    with zipfile.ZipFile(output_sup, 'r') as z:
        for name in ['Principal.lad', 'ROT5.lad', 'ROT6.lad']:
            if name not in z.namelist():
                continue

            info = z.getinfo(name)
            content = z.read(name)

            # Contar linhas CRLF
            crlf_count = content.count(b'\r\n')

            # Verificar cabeçalho Lines:
            first_line = content.split(b'\r\n')[0].decode('latin-1')

            print(f"   {name}:")
            print(f"      Data: {info.date_time}")
            print(f"      Compress type: {info.compress_type}")
            print(f"      External attr: {info.external_attr:#010x}")
            print(f"      CRLF count: {crlf_count}")
            print(f"      Header: {first_line}")
            print()

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Uso: python3 fix_sup_complete.py arquivo.sup [saida.sup]")
        sys.exit(1)

    input_file = sys.argv[1]

    if len(sys.argv) >= 3:
        output_file = sys.argv[2]
    else:
        # Nome padrão: adiciona "_FIXED"
        input_path = Path(input_file)
        output_file = str(input_path.parent / f"{input_path.stem}_FIXED{input_path.suffix}")

    fix_sup_complete(input_file, output_file)
