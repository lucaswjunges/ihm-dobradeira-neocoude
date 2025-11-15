#!/usr/bin/env python3
"""
Validação completa de arquivo .SUP para Winsup 2
Baseado em GUIA_DEFINITIVO_GERACAO_SUP.md
"""

import zipfile
import sys
from pathlib import Path

def validate_sup(sup_file: str):
    """Executa todos os testes de validação"""

    print(f"🔍 VALIDAÇÃO DE ARQUIVO .SUP: {sup_file}\n")
    print("=" * 70)

    all_passed = True

    # TESTE 1: Verificar formato de linha (CRLF)
    print("\n📝 TESTE 1: Formato de Linha (CRLF)")
    print("-" * 70)

    with zipfile.ZipFile(sup_file, 'r') as z:
        lad_files = [name for name in z.namelist() if name.endswith('.lad')]

        for name in lad_files:
            content = z.read(name)

            has_crlf = b'\r\n' in content
            has_only_lf = b'\n' in content and b'\r\n' not in content

            if has_only_lf:
                print(f"   ❌ {name}: Usa LF (Unix) - PRECISA CONVERTER!")
                all_passed = False
            elif has_crlf:
                line_count = content.count(b'\r\n')
                print(f"   ✅ {name}: CRLF (DOS) - OK ({line_count} linhas)")
            else:
                print(f"   ⚠️  {name}: Sem quebras de linha ({len(content)} bytes)")

    # TESTE 2: Verificar tamanhos mínimos
    print("\n📏 TESTE 2: Tamanhos Mínimos")
    print("-" * 70)

    min_sizes = {
        'Principal.lad': 500,
        'ROT0.lad': 500,
        'ROT1.lad': 500,
        'ROT2.lad': 500,
        'ROT3.lad': 500,
        'ROT4.lad': 500,
        'ROT5.lad': 500,
        'ROT6.lad': 500,
        'ROT7.lad': 500,
        'ROT8.lad': 500,
        'ROT9.lad': 500,
    }

    with zipfile.ZipFile(sup_file, 'r') as z:
        for name, min_size in min_sizes.items():
            try:
                info = z.getinfo(name)
                if info.file_size < min_size:
                    print(f"   ⚠️  {name}: {info.file_size} bytes < {min_size} bytes (suspeito)")
                else:
                    print(f"   ✅ {name}: {info.file_size} bytes (OK)")
            except KeyError:
                print(f"   ❌ {name}: NÃO ENCONTRADO!")
                all_passed = False

    # TESTE 3: Verificar ordem correta
    print("\n📋 TESTE 3: Ordem de Arquivos")
    print("-" * 70)

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

    with zipfile.ZipFile(sup_file, 'r') as z:
        actual_order = z.namelist()

        order_correct = True
        for i, expected in enumerate(CORRECT_ORDER):
            if i >= len(actual_order):
                print(f"   ❌ {i+1:02d}. {expected}: FALTANDO!")
                all_passed = False
                order_correct = False
                continue

            actual = actual_order[i]
            if actual == expected:
                print(f"   ✅ {i+1:02d}. {expected}")
            else:
                print(f"   ❌ {i+1:02d}. Esperado: {expected}, Encontrado: {actual}")
                all_passed = False
                order_correct = False

    # TESTE 4: Verificar estrutura completa
    print("\n📦 TESTE 4: Estrutura Completa")
    print("-" * 70)

    required_files = set(CORRECT_ORDER)

    with zipfile.ZipFile(sup_file, 'r') as z:
        existing = set(z.namelist())
        missing = required_files - existing
        extra = existing - required_files

        if missing:
            print(f"   ❌ Arquivos faltando ({len(missing)}):")
            for name in sorted(missing):
                print(f"      - {name}")
            all_passed = False
        else:
            print(f"   ✅ Todos os arquivos obrigatórios presentes ({len(required_files)})")

        if extra:
            print(f"   ⚠️  Arquivos extras ({len(extra)}):")
            for name in sorted(extra):
                print(f"      - {name}")

    # TESTE 5: Verificar tamanho total
    print("\n💾 TESTE 5: Tamanho Total do Arquivo")
    print("-" * 70)

    file_size = Path(sup_file).stat().st_size
    print(f"   Tamanho: {file_size:,} bytes ({file_size / 1024:.1f} KB)")

    if file_size < 50000:  # 50KB
        print(f"   ⚠️  ATENÇÃO: Arquivo muito pequeno! Pode estar incompleto.")
        print(f"   Tamanho esperado: > 50KB")
    else:
        print(f"   ✅ Tamanho adequado (> 50KB)")

    # RESUMO FINAL
    print("\n" + "=" * 70)
    if all_passed:
        print("✅ TODOS OS TESTES PASSARAM!")
        print("🎯 Arquivo pronto para carregar no Winsup 2")
    else:
        print("❌ ALGUNS TESTES FALHARAM!")
        print("⚠️  Revisar problemas acima antes de carregar no CLP")

    print("=" * 70)

    return all_passed

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Uso: python3 validate_sup.py arquivo.sup")
        sys.exit(1)

    sup_file = sys.argv[1]
    success = validate_sup(sup_file)

    sys.exit(0 if success else 1)
