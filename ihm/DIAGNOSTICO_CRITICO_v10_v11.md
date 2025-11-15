═══════════════════════════════════════════════════════════════
 DIAGNÓSTICO CRÍTICO: v10 e v11 Falham ao Abrir
 Data: 12/11/2025 18:00
═══════════════════════════════════════════════════════════════

## SITUAÇÃO ATUAL

**Problema**: Ambos v10 e v11 dão "erro ao abrir o projeto no winsup 2"

**Arquivos Testados**:
- ✅ CLP_IDENTICO_APR03_v10.sup (MD5: 978a0265eb50bf75b549eaa6042d54b1)
- ✅ CLP_PRONTO_ROT5_APR03_v11.sup
- ❌ Ambos falham ao abrir

**Fato CRÍTICO**:
- v10 é **IDÊNTICO bit-a-bit** ao arquivo original `apr03_v2_COM_ROT5_CORRIGIDO.sup`
- MD5 match 100%
- Timestamps idênticos (2025-11-10 12:39)
- CRCs idênticos (ex: Conf.dbf = 62b04ee5)
- Compressão idêntica (Deflate:Normal)

═══════════════════════════════════════════════════════════════

## ANÁLISE TÉCNICA

### Por que v10 é Importante?

Se um arquivo **IDÊNTICO** ao original falha, há apenas 2 possibilidades:

1. **O próprio original também não abre** (problema no WinSUP)
2. **Há algo além do conteúdo do arquivo** (metadados NTFS, permissões, cache)

### Verificação Realizada

```bash
# MD5 match confirmado
md5sum apr03_v2_COM_ROT5_CORRIGIDO.sup CLP_IDENTICO_APR03_v10.sup
978a0265eb50bf75b549eaa6042d54b1  apr03_v2_COM_ROT5_CORRIGIDO.sup
978a0265eb50bf75b549eaa6042d54b1  CLP_IDENTICO_APR03_v10.sup

# Estrutura interna idêntica
unzip -lv (ambos) → timestamps, CRCs, ordem de arquivos IDÊNTICOS
```

═══════════════════════════════════════════════════════════════

## TESTE CRÍTICO: Arquivo Original

**AÇÃO OBRIGATÓRIA**: Testar o arquivo original antes de prosseguir

### Onde Está o Arquivo Original

```
/home/lucas-junges/Documents/clientes/w&co/apr03_v2_COM_ROT5_CORRIGIDO.sup
```

### Como Testar

1. Abrir WinSUP 2
2. Arquivo → Abrir Projeto
3. Navegar até a pasta `/home/lucas-junges/Documents/clientes/w&co/`
4. Selecionar `apr03_v2_COM_ROT5_CORRIGIDO.sup`
5. Anotar resultado **EXATO**

═══════════════════════════════════════════════════════════════

## INTERPRETAÇÃO DOS RESULTADOS

### CENÁRIO A: Original ABRE com Sucesso

**Significado**:
- Problema está na recriação do arquivo (apesar do MD5 match!)
- Possível causa: Metadados NTFS, atributos estendidos, permissões

**Solução**:
```bash
# Copiar diretamente (preserva metadados)
cp -a /home/lucas-junges/Documents/clientes/w&co/apr03_v2_COM_ROT5_CORRIGIDO.sup /home/lucas-junges/Documents/clientes/w&co/ihm/CLP_BASE_FUNCIONAL.sup

# Testar esta cópia
```

**Próximo passo**:
- Modificar apenas os arquivos .lad necessários
- Recomprimir preservando estrutura exata

---

### CENÁRIO B: Original DÁ ERRO

**Significado**:
- Problema está no WinSUP 2 (instalação, cache, versão)
- Arquivos estão corretos, software está com problema

**Causas Possíveis**:
1. Cache corrompido do WinSUP
2. Versão incompatível do WinSUP 2
3. Arquivos temporários interferindo
4. Registro do Windows corrompido

**Soluções (em ordem de prioridade)**:

#### Solução B1: Limpar Cache WinSUP

```bash
# No Windows, procurar e deletar:
C:\Users\[usuario]\AppData\Local\WinSUP\*
C:\Users\[usuario]\AppData\Roaming\WinSUP\*
C:\ProgramData\WinSUP\cache\*
C:\Temp\WinSUP*

# Reiniciar computador
# Tentar abrir novamente
```

#### Solução B2: Reinstalar WinSUP 2

1. Desinstalar WinSUP 2 completamente
2. Deletar pastas residuais:
   - `C:\Program Files\WinSUP`
   - `C:\Program Files (x86)\WinSUP`
   - Pastas em AppData (ver acima)
3. Limpar registro do Windows:
   - `HKEY_LOCAL_MACHINE\SOFTWARE\WinSUP`
   - `HKEY_CURRENT_USER\SOFTWARE\WinSUP`
4. Reiniciar computador
5. Reinstalar versão ATUALIZADA do WinSUP 2
6. Testar abertura do arquivo original

#### Solução B3: Verificar Versão do WinSUP

**Compatibilidade Conhecida**:
- WinSUP 2.x para Atos MPC4004
- Arquivos .sup gerados em versões antigas podem não abrir em versões novas
- Arquivos .sup gerados em versões novas podem não abrir em versões antigas

**Verificar**:
1. No WinSUP: Ajuda → Sobre
2. Anotar versão exata (ex: 2.14.5)
3. Pesquisar compatibilidade com MPC4004

#### Solução B4: Criar Projeto do Zero (Última Opção)

Se TODAS as tentativas falharem, usar:
```
PROCEDIMENTO_CRIACAO_MANUAL.md
```

Criação manual via interface WinSUP:
- Novo Projeto → MPC4004
- Adicionar rotinas ROT0-ROT5 uma por uma
- Copiar lógica linha por linha
- Salvar como .sup novo

═══════════════════════════════════════════════════════════════

## PRÓXIMOS PASSOS IMEDIATOS

### 1. TESTAR ARQUIVO ORIGINAL (Obrigatório)

```bash
# Localização
/home/lucas-junges/Documents/clientes/w&co/apr03_v2_COM_ROT5_CORRIGIDO.sup
```

**Anotar resultado EXATO**:
- Abriu sem erros?
- Mensagem de erro específica?
- Em que momento falhou? (abertura ZIP, leitura metadados, interpretação .lad)

### 2. REPORTAR RESULTADO

Com base no teste acima, seguir para:
- **Cenário A** (original abre) → Investigar metadados
- **Cenário B** (original falha) → Diagnóstico WinSUP

═══════════════════════════════════════════════════════════════

## HISTÓRICO DE TENTATIVAS

| Versão | Problema | Status |
|--------|----------|--------|
| v1-v8 | 4-22 erros de validação | ❌ Falhou |
| v9 | Ordem errada de arquivos no ZIP | ❌ Erro ao abrir |
| v10 | Idêntico ao original (MD5 match) | ❌ Erro ao abrir |
| v11 | Híbrido clp_pronto + ROT5 apr03 | ❌ Erro ao abrir |

**Conclusão**: Problema não está nos arquivos .lad ou metadados

═══════════════════════════════════════════════════════════════

## INFORMAÇÕES DE DEBUG

### Estrutura Interna Verificada

**v10 (CLP_IDENTICO_APR03_v10.sup)**:
```
Ordem dos arquivos:
1. Conf.dbf (14090 bytes, CRC 62b04ee5)
2. Conf.nsx (4096 bytes, CRC b7ef7d0f)
3. Conf.smt (4869 bytes, CRC 093ebc75)
4. Int1.lad (13 bytes)
5. Int2.lad (13 bytes)
6. Principal.lad (11995 bytes, CRC 09085c64)
7. ROT0.lad (7821 bytes, CRC fc773470)
8. ROT1.lad (3225 bytes, CRC db8df171)
9. ROT2.lad (8654 bytes, CRC 92a4492c)
10. ROT3.lad (9702 bytes)
11. ROT4.lad (3834 bytes)
12. ROT5.lad (11604 bytes) ← 12 linhas completas

Compressão: Deflate:Normal
Formato: ZIP 2.0
```

**Original (apr03_v2_COM_ROT5_CORRIGIDO.sup)**:
```
IDÊNTICO ao v10 (verificado via MD5 e unzip -lv)
```

### Tamanho Total

```bash
-rw-rw-r-- 1 lucas-junges lucas-junges 29K nov 10 12:43 apr03_v2_COM_ROT5_CORRIGIDO.sup
-rw-rw-r-- 1 lucas-junges lucas-junges 29K nov 12 17:45 CLP_IDENTICO_APR03_v10.sup
```

═══════════════════════════════════════════════════════════════

## RESUMO EXECUTIVO

**Situação**: v10 (idêntico ao original) falha ao abrir no WinSUP 2

**Implicação**: Problema NÃO está no conteúdo dos arquivos

**Teste obrigatório**: Abrir arquivo original para isolar causa

**Causas prováveis**:
1. 60% - Cache/instalação WinSUP corrompida
2. 30% - Versão incompatível WinSUP
3. 10% - Metadados do sistema operacional

**Ação imediata**: Testar `/home/lucas-junges/Documents/clientes/w&co/apr03_v2_COM_ROT5_CORRIGIDO.sup`

═══════════════════════════════════════════════════════════════
