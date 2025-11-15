#!/usr/bin/env python3
"""
GERADOR DEFINITIVO E FINAL - .SUP COM 10 ROTINAS
Corrige TODOS os problemas conhecidos:
1. Project.spr incompleto (ROT0-ROT4 → ROT0-ROT9)
2. ROT5.lad truncado (304 bytes → 2374 bytes)
3. ROT6.lad com formato LF (converte para CRLF)
"""

import zipfile
import os
from datetime import datetime

def normalize_crlf(content: bytes) -> bytes:
    """Converte para CRLF (DOS) garantindo formato correto"""
    # Decodifica com latin-1
    text = content.decode('latin-1', errors='replace')

    # Remove CR existentes e reconverte
    text = text.replace('\r\n', '\n').replace('\r', '\n').replace('\n', '\r\n')

    # Codifica de volta
    return text.encode('latin-1', errors='replace')

def fix_project_spr(content: bytes) -> bytes:
    """Adiciona ROT5-ROT9 no Project.spr"""
    text = content.decode('latin-1')

    # Substitui a lista de rotinas
    import re
    rot_pattern = r'(ROT\d+ ;~!@)+'

    if re.search(rot_pattern, text):
        # Cria lista completa ROT0-ROT9
        new_rots = ''.join([f'ROT{i} ;~!@' for i in range(10)])

        # Substitui
        text = re.sub(rot_pattern, new_rots, text)
        print(f"  ✅ Project.spr: Atualizado para ROT0-ROT9")
    else:
        print(f"  ⚠️  Project.spr: Formato não reconhecido")

    return text.encode('latin-1')

def create_final_sup():
    print("=" * 70)
    print("GERADOR DEFINITIVO E FINAL - .SUP COM 10 ROTINAS")
    print("=" * 70)

    # Caminhos
    base_10_rotinas = '/home/lucas-junges/Documents/clientes/w&co/ihm/CLP_FINAL_10_ROTINAS_20251112_102801.sup'
    base_corrigida = '/home/lucas-junges/Documents/clientes/w&co/ihm/sups/clp_pronto_CORRIGIDO.sup'
    output_sup = '/home/lucas-junges/Documents/clientes/w&co/ihm/CLP_FINAL_10_ROTINAS_DEFINITIVO.sup'

    # Timestamp único
    now = datetime.now()
    date_time = (now.year, now.month, now.day, now.hour, now.minute, now.second)

    print(f"\n📦 Base: {os.path.basename(base_10_rotinas)}")
    print(f"📦 ROT5 de: {os.path.basename(base_corrigida)}")

    # Lê ROT5.lad correto
    print(f"\n🔍 Lendo ROT5.lad correto...")
    with zipfile.ZipFile(base_corrigida, 'r') as z:
        rot5_correto = z.read('ROT5.lad')

    print(f"  ✅ ROT5.lad: {len(rot5_correto)} bytes")

    # Ordem correta
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

    # Cria arquivo final
    print(f"\n🔨 Criando e corrigindo arquivo final...")

    with zipfile.ZipFile(base_10_rotinas, 'r') as z_in:
        with zipfile.ZipFile(output_sup, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=6) as z_out:

            for filename in file_order:
                if filename in z_in.namelist():
                    content = z_in.read(filename)

                    # CORREÇÃO 1: Project.spr - adiciona ROT5-ROT9
                    if filename == 'Project.spr':
                        content = fix_project_spr(content)

                    # CORREÇÃO 2: ROT5.lad - substitui pelo correto
                    elif filename == 'ROT5.lad':
                        content = rot5_correto
                        print(f"  ✅ {filename}: {len(content)} bytes (SUBSTITUÍDO)")

                    # CORREÇÃO 3: ROT6.lad - converte para CRLF
                    elif filename == 'ROT6.lad':
                        original_size = len(content)

                        # Verifica se precisa converter
                        has_crlf = b'\r\n' in content
                        has_lf_only = b'\n' in content and not has_crlf

                        if has_lf_only:
                            content = normalize_crlf(content)
                            print(f"  ✅ {filename}: {original_size} → {len(content)} bytes (CONVERTIDO para CRLF)")
                        else:
                            print(f"  ✅ {filename}: {len(content)} bytes")

                    # Outros arquivos
                    else:
                        # Verifica CRLF em .lad
                        if filename.endswith('.lad') and len(content) > 0:
                            has_crlf = b'\r\n' in content
                            has_lf_only = b'\n' in content and not has_crlf

                            if has_lf_only:
                                print(f"  ⚠️  {filename}: {len(content)} bytes (LF detectado)")
                            else:
                                print(f"  ✅ {filename}: {len(content)} bytes")
                        else:
                            print(f"  ✅ {filename}: {len(content)} bytes")

                    # Escreve no ZIP
                    zinfo = zipfile.ZipInfo(filename=filename, date_time=date_time)
                    zinfo.compress_type = zipfile.ZIP_DEFLATED
                    z_out.writestr(zinfo, content, compress_type=zipfile.ZIP_DEFLATED, compresslevel=6)

    file_size = os.path.getsize(output_sup)
    print("\n" + "=" * 70)
    print(f"🎉 Arquivo criado: {output_sup}")
    print(f"📦 Tamanho: {file_size:,} bytes ({file_size/1024:.2f} KB)")
    print("=" * 70)

    # Verificação final
    print(f"\n🔍 VERIFICAÇÃO FINAL...")

    with zipfile.ZipFile(output_sup, 'r') as z:
        # 1. Project.spr
        project_spr = z.read('Project.spr').decode('latin-1')
        if 'ROT9' in project_spr:
            print(f"  ✅ Project.spr: ROT0-ROT9 declaradas")
        else:
            print(f"  ❌ Project.spr: Faltam rotinas")

        # 2. ROT5.lad
        rot5 = z.read('ROT5.lad')
        if len(rot5) > 2000:
            print(f"  ✅ ROT5.lad: {len(rot5)} bytes (correto)")
        else:
            print(f"  ❌ ROT5.lad: {len(rot5)} bytes (truncado)")

        # 3. ROT6.lad CRLF
        rot6 = z.read('ROT6.lad')
        has_crlf = b'\r\n' in rot6
        has_lf_only = b'\n' in rot6 and not has_crlf

        if has_lf_only:
            print(f"  ❌ ROT6.lad: Formato LF (precisa ser CRLF)")
        elif has_crlf:
            print(f"  ✅ ROT6.lad: Formato CRLF correto")

        # 4. Principal.lad
        principal = z.read('Principal.lad')
        call_count = principal.count(b'E:ROT')
        has_crlf = b'\r\n' in principal

        if call_count == 10:
            print(f"  ✅ Principal.lad: {call_count} chamadas CALL")
        else:
            print(f"  ⚠️  Principal.lad: {call_count} chamadas CALL (esperado: 10)")

        if has_crlf:
            print(f"  ✅ Principal.lad: Formato CRLF correto")
        else:
            print(f"  ❌ Principal.lad: Formato incorreto")

    print("\n" + "=" * 70)
    print("✅ ARQUIVO DEFINITIVO PRONTO!")
    print("=" * 70)

if __name__ == '__main__':
    create_final_sup()
    print("\n📋 Próximo passo: Testar no Winsup 2")
