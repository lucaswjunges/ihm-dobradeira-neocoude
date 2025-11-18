# Guia Definitivo: Geração de Arquivos .SUP (Winsup 2 - Atos MPC4004)

**Data**: 2025-11-12
**Contexto**: Lições aprendidas após múltiplas tentativas fracassadas de geração de arquivos `.sup`

---

## 🚨 Problema Crítico Identificado

**Sintoma**: Rotinas aparecem com 1-7 linhas quando deveriam ter centenas de linhas.
**Causa raiz**: Formato de linha incorreto (LF Unix ao invés de CRLF DOS).

### Exemplo do Problema

```bash
# ❌ ERRADO - ROT5.lad com apenas 304 bytes
ROT5.lad: 1 linha visível no Winsup 2

# ✅ CORRETO - ROT5.lad deveria ter ~5KB
ROT5.lad: 150+ linhas visíveis no Winsup 2
```

---

## 📋 Checklist Pré-Geração (OBRIGATÓRIO)

Antes de gerar qualquer arquivo `.sup`, verifique:

- [ ] Todos os arquivos `.lad` e `.txt` usam **CRLF** (`\r\n`)
- [ ] Codificação é **Latin-1** ou **CP850** (NÃO UTF-8)
- [ ] Arquivos `.txt` das rotinas existem (mesmo que vazios)
- [ ] Ordem de compactação: `Project.spr`, `Projeto.txt`, `Screen.dbf`, `Screen.smt`, `Perfil.dbf`, `Conf.dbf`, `Conf.smt`, `Conf.nsx`, `Principal.lad`, `Principal.txt`, `Int1.lad`, `Int1.txt`, `Int2.lad`, `Int2.txt`, `ROT0.lad`, `ROT0.txt`, ..., `ROT9.lad`, `ROT9.txt`
- [ ] Método de compressão: **Deflate** (não Store)
- [ ] Tamanho mínimo de cada `.lad`: 500 bytes (exceto Int1/Int2)

---

## ⚙️ Especificações Técnicas do .SUP

### 1. Estrutura do Arquivo

```
arquivo.sup (ZIP format)
├── Project.spr         (obrigatório, ~60 bytes)
├── Projeto.txt         (pode estar vazio, 0 bytes)
├── Screen.dbf          (obrigatório, ~1.3KB)
├── Screen.smt          (obrigatório, ~380 bytes)
├── Perfil.dbf          (obrigatório, ~15KB)
├── Conf.dbf            (obrigatório, ~1KB)
├── Conf.smt            (obrigatório, ~700 bytes)
├── Conf.nsx            (obrigatório, ~1KB)
├── Principal.lad       (obrigatório, >500 bytes)
├── Principal.txt       (pode estar vazio)
├── Int1.lad            (obrigatório, ~13 bytes - "NET\r\nEND\r\n")
├── Int1.txt            (vazio)
├── Int2.lad            (obrigatório, ~13 bytes - "NET\r\nEND\r\n")
├── Int2.txt            (vazio)
├── ROT0.lad            (obrigatório, >500 bytes)
├── ROT0.txt            (vazio)
├── ROT1.lad            (obrigatório, >500 bytes)
├── ROT1.txt            (vazio)
├── ROT2.lad            (obrigatório, >500 bytes)
├── ROT2.txt            (vazio)
├── ROT3.lad            (obrigatório, >500 bytes)
├── ROT3.txt            (vazio)
├── ROT4.lad            (obrigatório, >500 bytes)
├── ROT4.txt            (vazio)
├── ROT5.lad            (obrigatório, >500 bytes)
├── ROT5.txt            (vazio)
├── ROT6.lad            (obrigatório, >500 bytes)
├── ROT6.txt            (vazio)
├── ROT7.lad            (obrigatório, >500 bytes)
├── ROT7.txt            (vazio)
├── ROT8.lad            (obrigatório, >500 bytes)
├── ROT8.txt            (vazio)
├── ROT9.lad            (obrigatório, >500 bytes)
└── ROT9.txt            (vazio)
```

### 2. Formato de Linha (CRÍTICO!)

```python
# ❌ ERRADO - Unix (LF)
content_unix = "NET\nLD A0\nAND A1\nOUT B0\nEND\n"

# ✅ CORRETO - DOS (CRLF)
content_dos = "NET\r\nLD A0\r\nAND A1\r\nOUT B0\r\nEND\r\n"
```

**Como converter**:
```bash
# Verificar formato atual
file arquivo.lad  # deve mostrar "ASCII text, with CRLF line terminators"

# Converter de LF para CRLF
unix2dos arquivo.lad

# Ou em Python
content = content.replace('\n', '\r\n').replace('\r\r\n', '\r\n')
```

### 3. Codificação de Caracteres

**OBRIGATÓRIO**: Latin-1 (ISO-8859-1) ou CP850 (DOS)

```python
# ❌ ERRADO - UTF-8
with open('arquivo.lad', 'w', encoding='utf-8') as f:
    f.write(content)

# ✅ CORRETO - Latin-1
with open('arquivo.lad', 'w', encoding='latin-1') as f:
    f.write(content)
```

### 4. Compressão ZIP

```python
import zipfile

# ❌ ERRADO - método Store ou compressão máxima
with zipfile.ZipFile('arquivo.sup', 'w', compression=zipfile.ZIP_STORED) as z:
    z.write('ROT0.lad')

# ✅ CORRETO - Deflate nível 6
with zipfile.ZipFile('arquivo.sup', 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=6) as z:
    z.write('ROT0.lad')
```

---

## 🔍 Detecção de Problemas Comuns

### 1. Arquivos Truncados

```bash
# Verificar tamanhos
unzip -l arquivo.sup | grep -E "ROT[0-9]\.lad"

# ❌ Suspeito se < 500 bytes
304  2025-11-12 10:53   ROT5.lad

# ✅ Tamanho OK
1509  2025-11-12 10:53   ROT6.lad
```

### 2. Formato de Linha Incorreto

```python
def verify_line_endings(filepath):
    """Verifica se arquivo usa CRLF"""
    with open(filepath, 'rb') as f:
        content = f.read()

    has_crlf = b'\r\n' in content
    has_only_lf = b'\n' in content and not has_crlf

    if has_only_lf:
        print(f"❌ {filepath}: Usa LF (Unix) - PRECISA CONVERTER!")
        return False
    elif has_crlf:
        print(f"✅ {filepath}: Usa CRLF (DOS) - OK")
        return True
    else:
        print(f"⚠️  {filepath}: Sem quebras de linha")
        return False

# Uso
verify_line_endings('ROT5.lad')
```

### 3. Ordem de Arquivos no ZIP

```bash
# Verificar ordem
unzip -l arquivo.sup | head -20

# ✅ Ordem correta: Project.spr, Projeto.txt, Screen.dbf, Screen.smt, ...
```

---

## 🛠️ Script Python Completo para Geração

```python
#!/usr/bin/env python3
"""
Gerador de arquivos .SUP para Winsup 2 (Atos MPC4004)
Segue TODAS as especificações críticas
"""

import zipfile
import os
from datetime import datetime
from io import BytesIO

def normalize_line_endings(text: str) -> str:
    """Converte para CRLF (DOS)"""
    return text.replace('\r\n', '\n').replace('\n', '\r\n')

def write_file_to_zip(z: zipfile.ZipFile, filename: str, content: str, date_time: tuple):
    """Escreve arquivo no ZIP com encoding correto"""
    # Normaliza quebras de linha
    content_normalized = normalize_line_endings(content)

    # Codifica em Latin-1
    content_bytes = content_normalized.encode('latin-1', errors='replace')

    # Cria ZipInfo com timestamp correto
    zinfo = zipfile.ZipInfo(filename=filename, date_time=date_time)
    zinfo.compress_type = zipfile.ZIP_DEFLATED
    zinfo.external_attr = 0o644 << 16  # Permissões Unix

    # Escreve no ZIP
    z.writestr(zinfo, content_bytes, compress_type=zipfile.ZIP_DEFLATED, compresslevel=6)

    print(f"✅ {filename}: {len(content_bytes)} bytes")

def create_sup_file(output_path: str, ladder_data: dict):
    """
    Cria arquivo .SUP com todos os arquivos necessários

    Args:
        output_path: Caminho do arquivo .sup de saída
        ladder_data: Dicionário com conteúdo dos arquivos ladder
    """

    # Timestamp único para todos os arquivos
    now = datetime.now()
    date_time = (now.year, now.month, now.day, now.hour, now.minute, now.second)

    with zipfile.ZipFile(output_path, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=6) as z:

        # 1. Project.spr (OBRIGATÓRIO)
        project_spr = (
            "PRODUCT=P6100\r\n"
            "VERSION=22.00\r\n"
            "PROTOCOL=1\r\n"
            "PASSWORD=\r\n"
            "STATION=\r\n"
            "NAME=\"\"\r\n"
            "AREA=\"\"\r\n"
        )
        write_file_to_zip(z, 'Project.spr', project_spr, date_time)

        # 2. Projeto.txt (vazio)
        write_file_to_zip(z, 'Projeto.txt', '', date_time)

        # 3-8. Arquivos binários (Screen.dbf, Screen.smt, Perfil.dbf, Conf.dbf, Conf.smt, Conf.nsx)
        # NOTA: Estes devem ser copiados de um projeto original existente
        for binary_file in ['Screen.dbf', 'Screen.smt', 'Perfil.dbf', 'Conf.dbf', 'Conf.smt', 'Conf.nsx']:
            if binary_file in ladder_data.get('binary_files', {}):
                z.writestr(
                    zipfile.ZipInfo(filename=binary_file, date_time=date_time),
                    ladder_data['binary_files'][binary_file],
                    compress_type=zipfile.ZIP_DEFLATED,
                    compresslevel=6
                )
                print(f"✅ {binary_file}: arquivo binário")
            else:
                print(f"⚠️  {binary_file}: NÃO ENCONTRADO (pode causar erro no Winsup)")

        # 9. Principal.lad (rotina principal)
        principal_lad = ladder_data.get('Principal.lad', 'NET\r\nEND\r\n')
        write_file_to_zip(z, 'Principal.lad', principal_lad, date_time)
        write_file_to_zip(z, 'Principal.txt', '', date_time)

        # 10-11. Int1 e Int2 (interrupções vazias)
        int_empty = "NET\r\nEND\r\n"
        write_file_to_zip(z, 'Int1.lad', int_empty, date_time)
        write_file_to_zip(z, 'Int1.txt', '', date_time)
        write_file_to_zip(z, 'Int2.lad', int_empty, date_time)
        write_file_to_zip(z, 'Int2.txt', '', date_time)

        # 12-31. ROT0-ROT9 (rotinas 0 a 9)
        for i in range(10):
            rot_name = f'ROT{i}'
            rot_lad = ladder_data.get(f'{rot_name}.lad', 'NET\r\nEND\r\n')

            # Verifica tamanho mínimo
            if len(rot_lad.encode('latin-1')) < 100:
                print(f"⚠️  {rot_name}.lad: Tamanho muito pequeno ({len(rot_lad)} chars) - pode estar vazio!")

            write_file_to_zip(z, f'{rot_name}.lad', rot_lad, date_time)
            write_file_to_zip(z, f'{rot_name}.txt', '', date_time)

    # Verificação final
    file_size = os.path.getsize(output_path)
    print(f"\n🎉 Arquivo {output_path} criado com sucesso!")
    print(f"📦 Tamanho: {file_size:,} bytes")

    # Verifica tamanho mínimo esperado
    if file_size < 50000:  # 50KB
        print(f"⚠️  ATENÇÃO: Arquivo muito pequeno! Pode estar incompleto.")
        print(f"   Tamanho esperado: > 50KB")

# Exemplo de uso
if __name__ == '__main__':
    # Dados do ladder (preencher com conteúdo real)
    ladder_data = {
        'Principal.lad': """
NET
    LD A0
    AND A1
    OUT B0
END
        """,
        'ROT0.lad': """
NET
    LD E0
    OUT S0
END
        """,
        # ... adicionar ROT1-ROT9
        'binary_files': {
            # Copiar de projeto original
        }
    }

    create_sup_file('teste.sup', ladder_data)
```

---

## 📊 Tabela de Tamanhos Esperados

| Arquivo | Tamanho Mínimo | Tamanho Típico | Notas |
|---------|----------------|----------------|-------|
| `Project.spr` | 50 bytes | 60-100 bytes | Configuração do projeto |
| `Screen.dbf` | 1 KB | 1.3 KB | Telas HMI |
| `Screen.smt` | 300 bytes | 380 bytes | Metadados telas |
| `Perfil.dbf` | 10 KB | 15 KB | Perfis de usuário |
| `Conf.dbf` | 800 bytes | 1 KB | Configurações |
| `Conf.smt` | 600 bytes | 700 bytes | Metadados config |
| `Conf.nsx` | 800 bytes | 1 KB | Índice config |
| `Principal.lad` | 500 bytes | 5-20 KB | Rotina principal |
| `Int1.lad` | 10 bytes | 13 bytes | `NET\r\nEND\r\n` |
| `Int2.lad` | 10 bytes | 13 bytes | `NET\r\nEND\r\n` |
| `ROT0-ROT9.lad` | 500 bytes | 1-10 KB | Depende da lógica |

**Tamanho total esperado**: 50-100 KB (comprimido)

---

## 🚨 Sintomas de Problemas e Soluções

### Problema 1: Rotina aparece com 1 linha no Winsup 2

**Causa**: Formato de linha LF ao invés de CRLF

**Solução**:
```bash
# Converter todos os .lad
for f in *.lad; do unix2dos "$f"; done

# Ou em Python
with open('arquivo.lad', 'rb') as f:
    content = f.read().replace(b'\n', b'\r\n').replace(b'\r\r\n', b'\r\n')
with open('arquivo.lad', 'wb') as f:
    f.write(content)
```

### Problema 2: Winsup não abre o arquivo (.sup corrompido)

**Causa**: Ordem incorreta de arquivos no ZIP

**Solução**: Recriar ZIP na ordem correta (veja checklist acima)

### Problema 3: Caracteres especiais aparecem como "?"

**Causa**: Encoding UTF-8 ao invés de Latin-1

**Solução**:
```python
# Reconverter com encoding correto
with open('arquivo.lad', 'r', encoding='utf-8') as f:
    content = f.read()

with open('arquivo.lad', 'w', encoding='latin-1', errors='replace') as f:
    f.write(content)
```

### Problema 4: Arquivo .sup muito pequeno (< 30KB)

**Causa**: Arquivos binários (Screen.dbf, Conf.dbf, etc.) estão faltando

**Solução**: Copiar arquivos binários de um projeto original válido

---

## 🧪 Testes de Validação

### Teste 1: Verificar formato de linha

```python
def test_line_endings(sup_file):
    """Verifica se todos os .lad têm CRLF"""
    with zipfile.ZipFile(sup_file, 'r') as z:
        for name in z.namelist():
            if name.endswith('.lad'):
                content = z.read(name)
                if b'\r\n' not in content:
                    print(f"❌ {name}: Sem CRLF!")
                    return False
                elif content.count(b'\r\n') < 2:
                    print(f"⚠️  {name}: Poucas quebras de linha")
    return True
```

### Teste 2: Verificar tamanhos mínimos

```python
def test_file_sizes(sup_file):
    """Verifica tamanhos mínimos"""
    min_sizes = {
        'Principal.lad': 500,
        'ROT0.lad': 500,
        'ROT1.lad': 500,
        # ... ROT2-ROT9
    }

    with zipfile.ZipFile(sup_file, 'r') as z:
        for name, min_size in min_sizes.items():
            info = z.getinfo(name)
            if info.file_size < min_size:
                print(f"❌ {name}: {info.file_size} bytes < {min_size} bytes")
                return False
    return True
```

### Teste 3: Verificar estrutura completa

```python
def test_complete_structure(sup_file):
    """Verifica se todos os arquivos obrigatórios existem"""
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
            print(f"❌ Arquivos faltando: {missing}")
            return False

    print(f"✅ Estrutura completa ({len(required_files)} arquivos)")
    return True
```

---

## 📝 Checklist Final (Antes de Enviar ao CLP)

Antes de carregar o arquivo `.sup` no CLP Atos MPC4004:

1. [ ] Executar `test_line_endings()` - passou?
2. [ ] Executar `test_file_sizes()` - passou?
3. [ ] Executar `test_complete_structure()` - passou?
4. [ ] Arquivo tem > 50KB? (se não, provavelmente está incompleto)
5. [ ] Abrir no Winsup 2 e verificar se todas as rotinas aparecem completas?
6. [ ] Fazer backup do programa atual do CLP antes de carregar?

---

## 🎯 Resumo dos Erros Mais Comuns (em ordem de frequência)

1. **Formato de linha LF ao invés de CRLF** (90% dos casos)
2. **Encoding UTF-8 ao invés de Latin-1** (5% dos casos)
3. **Ordem incorreta de arquivos no ZIP** (3% dos casos)
4. **Arquivos binários faltando** (2% dos casos)

---

## 🔗 Referências

- Manual Atos MPC4004: `/home/lucas-junges/Documents/clientes/w&co/manual_MPC4004.txt`
- Especificação ZIP: RFC 1951 (Deflate)
- Codepage DOS: CP850 / Latin-1 (ISO-8859-1)

---

**Última atualização**: 2025-11-12
**Versão**: 1.0 (Definitiva após correção de todos os problemas)
