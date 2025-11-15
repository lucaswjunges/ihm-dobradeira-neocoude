#!/usr/bin/env python3
"""
Validador de arquivos .SUP para Winsup 2
Segue as especificações do GUIA_DEFINITIVO_GERACAO_SUP.md
"""

import zipfile
import sys

def test_line_endings(sup_file):
    """Verifica se todos os .lad têm CRLF"""
    print("\n🔍 Teste 1: Verificando formato de linha (CRLF)...")
    passed = True

    with zipfile.ZipFile(sup_file, 'r') as z:
        for name in z.namelist():
            if name.endswith('.lad'):
                content = z.read(name)

                has_crlf = b'\r\n' in content
                has_only_lf = b'\n' in content and not has_crlf

                if has_only_lf:
                    print(f"  ❌ {name}: Usa LF (Unix) - ERRO!")
                    passed = False
                elif has_crlf:
                    line_count = content.count(b'\r\n')
                    print(f"  ✅ {name}: CRLF correto ({line_count} linhas)")
                elif len(content) == 0:
                    print(f"  ⚠️  {name}: Arquivo vazio")
                else:
                    print(f"  ⚠️  {name}: Sem quebras de linha")

    return passed

def test_file_sizes(sup_file):
    """Verifica tamanhos mínimos"""
    print("\n🔍 Teste 2: Verificando tamanhos mínimos...")

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

    passed = True

    with zipfile.ZipFile(sup_file, 'r') as z:
        for name, min_size in min_sizes.items():
            try:
                info = z.getinfo(name)
                if info.file_size < min_size:
                    print(f"  ❌ {name}: {info.file_size} bytes < {min_size} bytes mínimos")
                    passed = False
                else:
                    print(f"  ✅ {name}: {info.file_size} bytes OK")
            except KeyError:
                print(f"  ❌ {name}: ARQUIVO NÃO ENCONTRADO!")
                passed = False

    return passed

def test_complete_structure(sup_file):
    """Verifica se todos os arquivos obrigatórios existem"""
    print("\n🔍 Teste 3: Verificando estrutura completa...")

    required_files = [
        'Project.spr', 'Projeto.txt',
        'Screen.dbf', 'Screen.smt', 'Perfil.dbf',
        'Conf.dbf', 'Conf.smt', 'Conf.nsx',
        'Principal.lad', 'Principal.txt',
        'Int1.lad', 'Int1.txt', 'Int2.lad', 'Int2.txt'
    ]

    # Adiciona ROT0-ROT9
    for i in range(10):
        required_files.extend([f'ROT{i}.lad', f'ROT{i}.txt'])

    with zipfile.ZipFile(sup_file, 'r') as z:
        existing = set(z.namelist())
        missing = set(required_files) - existing

        if missing:
            print(f"  ❌ Arquivos faltando: {missing}")
            return False

        print(f"  ✅ Estrutura completa ({len(required_files)} arquivos obrigatórios)")

        # Verifica ordem
        expected_order = [
            'Project.spr', 'Projeto.txt',
            'Screen.dbf', 'Screen.smt', 'Perfil.dbf',
            'Conf.dbf', 'Conf.smt', 'Conf.nsx',
            'Principal.lad', 'Principal.txt',
            'Int1.lad', 'Int1.txt', 'Int2.lad', 'Int2.txt'
        ]

        # Adiciona ROT0-ROT9
        for i in range(10):
            expected_order.append(f'ROT{i}.lad')
            expected_order.append(f'ROT{i}.txt')

        actual_order = [name for name in z.namelist()]

        # Compara primeiros 34 arquivos (ignora Pseudo.lad)
        if actual_order[:34] == expected_order[:34]:
            print(f"  ✅ Ordem dos arquivos está correta")
        else:
            print(f"  ⚠️  Ordem dos arquivos pode estar incorreta")
            print(f"     Esperado: {expected_order[:5]}...")
            print(f"     Real:     {actual_order[:5]}...")

    return True

def test_binary_files(sup_file):
    """Verifica arquivos binários obrigatórios"""
    print("\n🔍 Teste 4: Verificando arquivos binários...")

    binary_files = {
        'Screen.dbf': 40000,  # ~40 KB
        'Screen.smt': 10000,  # ~10 KB
        'Perfil.dbf': 150000,  # ~150 KB
        'Conf.dbf': 10000,  # ~10 KB
        'Conf.smt': 3000,  # ~3 KB
        'Conf.nsx': 3000,  # ~3 KB
    }

    passed = True

    with zipfile.ZipFile(sup_file, 'r') as z:
        for name, min_size in binary_files.items():
            try:
                info = z.getinfo(name)
                if info.file_size < min_size:
                    print(f"  ⚠️  {name}: {info.file_size} bytes (esperado > {min_size})")
                else:
                    print(f"  ✅ {name}: {info.file_size} bytes OK")
            except KeyError:
                print(f"  ❌ {name}: ARQUIVO NÃO ENCONTRADO!")
                passed = False

    return passed

def validate_sup_file(sup_file_path):
    """Executa todos os testes"""
    print("=" * 70)
    print(f"VALIDADOR DE ARQUIVO .SUP")
    print(f"Arquivo: {sup_file_path}")
    print("=" * 70)

    results = {
        'line_endings': test_line_endings(sup_file_path),
        'file_sizes': test_file_sizes(sup_file_path),
        'structure': test_complete_structure(sup_file_path),
        'binary_files': test_binary_files(sup_file_path),
    }

    # Resumo final
    print("\n" + "=" * 70)
    print("RESUMO DA VALIDAÇÃO")
    print("=" * 70)

    all_passed = all(results.values())

    for test_name, passed in results.items():
        status = "✅ PASSOU" if passed else "❌ FALHOU"
        print(f"  {test_name:20s}: {status}")

    print("=" * 70)

    if all_passed:
        print("🎉 VALIDAÇÃO COMPLETA: Arquivo pronto para usar no Winsup 2!")
        return 0
    else:
        print("❌ VALIDAÇÃO FALHOU: Corrija os problemas antes de usar")
        return 1

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Uso: python3 validar_sup.py <arquivo.sup>")
        sys.exit(1)

    sup_file = sys.argv[1]

    try:
        exit_code = validate_sup_file(sup_file)
        sys.exit(exit_code)
    except FileNotFoundError:
        print(f"❌ ERRO: Arquivo não encontrado: {sup_file}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ ERRO: {e}")
        sys.exit(1)
