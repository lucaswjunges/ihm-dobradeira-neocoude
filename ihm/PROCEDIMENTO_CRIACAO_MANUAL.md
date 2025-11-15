# PROCEDIMENTO: Criação Manual do Projeto no WinSUP 2

Data: 12/11/2025
Status: SOLUÇÃO DEFINITIVA após falha de todas as correções de arquivo

---

## POR QUE CRIAR MANUALMENTE

Após 8 iterações de correção do arquivo .sup:
- v1-v6: Correção de endereços e simplificação de ROT10
- v7: Remoção de metadados
- v8: Substituição por metadados funcionais

**TODAS falharam** porque o WinSUP interpreta incorretamente instruções MOVK como SFR/ADSUB, indicando:
1. Corrupção estrutural do .sup original
2. Incompatibilidade de versão/checksums internos
3. Cache corrompido do WinSUP

**Criar projeto novo garante**:
- Metadados gerados corretamente pelo WinSUP
- Estrutura interna válida
- Sem corrupção de reempacotamento

---

## PASSO 1: Preparar Arquivos de Referência

Extraia o conteúdo do arquivo original funcional:

```bash
cd /home/lucas-junges/Documents/clientes/w&co/ihm
unzip -o clp_pronto.sup -d clp_pronto_ref/
```

Você usará as rotinas ROT0-ROT9 (EXCETO ROT5) como referência.

---

## PASSO 2: Criar Novo Projeto no WinSUP 2

1. **Abra WinSUP 2**
2. **Arquivo → Novo Projeto**
3. **Configure**:
   - Nome: `NEOCOUDE_HD15_NOVO`
   - Modelo CLP: MPC4004
   - Tipo: Programa ladder
4. **Salve** o projeto novo

---

## PASSO 3: Configurar Estrutura de Rotinas

No WinSUP, crie as seguintes rotinas:

| Rotina      | Prioridade | Descrição                          |
|-------------|------------|------------------------------------|
| Principal   | 1          | Rotina principal (já criada)      |
| ROT0        | 2          | Lógica original                   |
| ROT1        | 3          | Lógica original                   |
| ROT2        | 4          | Lógica original                   |
| ROT3        | 5          | Lógica original                   |
| ROT4        | 6          | Lógica original                   |
| ROT5        | 7          | **CRIAR DO ZERO** (ver abaixo)    |
| ROT6        | 8          | Lógica original                   |
| ROT7        | 9          | Lógica original (corrigida)       |
| ROT8        | 10         | Lógica original (corrigida)       |
| ROT9        | 11         | Lógica original                   |
| ROT10       | 12         | **CRIAR MÍNIMA** (ver abaixo)     |

---

## PASSO 4: Copiar Rotinas ROT0-ROT4, ROT6, ROT9

Para cada rotina (ROT0, ROT1, ROT2, ROT3, ROT4, ROT6, ROT9):

1. Abra o arquivo `.txt` correspondente em `clp_pronto_ref/`
   - Exemplo: `clp_pronto_ref/ROT0.txt`

2. **No WinSUP**, abra a rotina e **copie manualmente** a lógica:
   - Use a interface gráfica do WinSUP
   - Arraste instruções (contatos, bobinas, funções)
   - Configure endereços conforme .txt original

3. **Salve** cada rotina após copiar

**IMPORTANTE**: NÃO copie ROT5, ROT7, ROT8 ainda - elas precisam de correções.

---

## PASSO 5: Criar ROT7 Corrigida

ROT7 tinha problemas com operandos CMP fora do range.

**Lógica corrigida** (do arquivo v6):

```
Linha 1: CMP E:0420 >= E:0421
         Branch: E:0003
         Out: SETR E:0005

Linha 2: CMP E:0420 <= E:0422
         Branch: E:0004
         Out: SETR E:0006

Linha 3: END
```

**No WinSUP**:
1. Abra ROT7
2. Adicione instrução CMP (Compare)
3. Configure registros:
   - E:0420, E:0421, E:0422 (área Timer/Counter 0x0400-0x047F)
   - Estados E:0003, E:0004, E:0005, E:0006
4. Salve

---

## PASSO 6: Criar ROT8 Corrigida

ROT8 tinha problemas com SCL2G usando estados em vez de registros.

**Lógica corrigida** (do arquivo v6):

```
Linha 1: SCL2G E:0520 E:0401 E:0400
         Out: E:0430

Linha 2: SCL2G E:0521 E:0401 E:0400
         Out: E:0431

Linha 3-15: Instruções MOV/MOVK copiando valores
            (use registros 0x0430-0x043E, 0x0520-0x0524)

Linha 16: END
```

**Registros críticos**:
- E:0400 = 0 (constante)
- E:0401 = 1 (constante)
- E:0430-E:043E = variáveis de trabalho
- E:0520-E:0524 = setpoints de escala

**No WinSUP**:
1. Abra ROT8
2. Adicione instruções MOVK para inicializar E:0400=0, E:0401=1
3. Adicione instruções SCL2G com operandos REGISTROS (não estados!)
4. Copie restante da lógica original
5. Salve

---

## PASSO 7: Criar ROT5 do Zero

ROT5 tinha problemas com SDAT2 em endereço alto (0x0700 → 0x0300).

**Lógica mínima funcional** (do arquivo v6):

```
Linha 1: SETR T:0043 E:00A0
         Branch: E:0300

Linha 2: SETR T:0043 E:00DC
         Branch: E:03EA

Linha 3: SETR T:0043 E:0025
         Branch: E:03EE

Linha 4: SETR T:0043 E:03F1
         Branch01: E:0102
         Branch02: E:0300

Linha 5: SETR T:0043 E:03F2
         Branch01: E:0104
         Branch02: E:03E3

Linha 6: SETR T:0043 E:03F3
         Branch01: E:0103
         Branch02: E:03E2

Linha 7: SDAT2 T:0042 E:0300
         Branch: E:0191

Linha 8: SETR T:0043 E:03FF
         Branch: E:00BE
```

**CRÍTICO**:
- Linha 7 usa **E:0300** (não 0x0700!)
- Todos os endereços são CONTATOS (0x0000-0x03FF)
- SDAT2 requer contato como destino

**No WinSUP**:
1. Abra ROT5
2. Adicione 6 instruções SETR com branches
3. Adicione instrução SDAT2 na linha 7 com **E:0300**
4. Adicione SETR final
5. Salve

---

## PASSO 8: Criar ROT10 Mínima

ROT10 foi a rotina mais problemática. Versão MÍNIMA funcional:

```
Linha 1: MOVK E:0450 = 0
         Branch: E:0300

Linha 2: MOVK E:0451 = 1
         Branch01: E:0190
         Branch02: E:0191

Linha 3: MOVK E:0452 = 1
         Branch: E:00F7

Linha 4: END
```

**Registros usados**:
- E:0450 (1104): Work register zerado
- E:0451 (1105): Flag 1
- E:0452 (1106): Flag 2

**No WinSUP**:
1. Abra ROT10
2. Adicione 3 instruções MOVK (Move Constant)
3. Configure endereços E:0450, E:0451, E:0452
4. Configure valores: 0, 1, 1
5. Adicione branches conforme acima
6. Adicione END
7. Salve

**NOTA**: Esta versão é absolutamente mínima. Se funcionar sem erros, você pode adicionar mais funcionalidade gradualmente.

---

## PASSO 9: Compilar e Verificar

1. **No WinSUP**: Menu **Compilar → Compilar Projeto**
2. **Verificar janela de erros**:
   - ✅ **0 erros**: SUCESSO! Vá para Passo 10
   - ⚠️ **1-3 erros**: Verifique endereços específicos e corrija
   - ❌ **4+ erros**: Revise rotinas problemáticas

3. **Se houver erros**:
   - Anote qual rotina e linha
   - Verifique se usou REGISTROS (0x0400+) para SCL2G/CMP
   - Verifique se usou CONTATOS (0x0000-0x03FF) para SDAT2
   - Verifique se ROT10 só tem MOVK (não MOV)

---

## PASSO 10: Salvar Projeto Funcional

1. **Menu Arquivo → Salvar Como**
2. **Nome**: `NEOCOUDE_HD15_FUNCIONAL.sup`
3. **Localização**: `/home/lucas-junges/Documents/clientes/w&co/ihm/`
4. Salve

---

## PASSO 11: Testar no CLP

1. **Conecte** cabo RS485 ao CLP
2. **No WinSUP**: Menu **Comunicação → Enviar Programa**
3. **Aguarde** upload completo
4. **Teste** funcionamento básico:
   - Encoder responde
   - Botões K0-K9 funcionam
   - Ciclos automáticos executam

---

## TROUBLESHOOTING

### "Erro ao criar rotina"
- Verifique se nome não tem caracteres especiais
- Use apenas ROT0-ROT10

### "Instrução não encontrada"
- Verifique biblioteca de instruções do WinSUP
- SDAT2/SCL2G podem estar em submenu "Funções Especiais"

### "Endereço inválido"
- Confirme range:
  - Contatos: 0x0000-0x03FF (0-1023)
  - Registros: 0x0400-0x0FFF (1024-4095)

### "SDAT2 ainda dá erro"
- Certifique-se que destino é CONTATO (não registro)
- Use E:0300 (decimal 768)

### "MOVK interpretado como SFR"
- Isso NÃO deve acontecer em projeto novo!
- Se ocorrer:
  1. Feche WinSUP
  2. Delete cache: `~/.winsup/cache/` (se Linux) ou `%APPDATA%\WinSUP\cache\` (Windows)
  3. Reabra projeto

---

## QUANDO ADICIONAR FUNCIONALIDADE

Após projeto compilar SEM ERROS:

1. **Teste básico**: Envie para CLP e teste encoder/botões
2. **Adicione lógica em Principal.lad** (não em ROT10!)
3. **Use apenas**:
   - Registros 0x0400-0x047F (Timer/Counter)
   - Estados 0x0000-0x03FF
   - Instruções MOVK, SETR, RSTR (evite MOV complexo)
4. **Compile após cada adição** para identificar problemas cedo

---

## RESUMO

✅ Criar projeto NOVO no WinSUP (não editar .sup)
✅ Copiar ROT0-ROT4, ROT6, ROT9 do original
✅ Criar ROT7/ROT8 com endereços corrigidos
✅ Criar ROT5 com SDAT2 E:0300
✅ Criar ROT10 mínima (3 MOVK + END)
✅ Compilar e verificar 0 erros
✅ Salvar como novo .sup
✅ Testar no CLP

---

## TEMPO ESTIMADO

- Preparação: 5 min
- Criação das 11 rotinas: 30-45 min
- Compilação e correção: 10-15 min
- **Total**: ~1 hora

---

## ARQUIVOS DE REFERÊNCIA

- Original funcional: `clp_pronto.sup`
- ROT10 mínima: `temp_extract/ROT10.lad` (do v6)
- ROT5 corrigida: `temp_extract/ROT5.lad` (do v6)
- Este guia: `PROCEDIMENTO_CRIACAO_MANUAL.md`

---

**BOA SORTE!** 🎯

Se após seguir este procedimento ainda houver erros, o problema pode ser:
1. Versão do WinSUP incompatível com MPC4004
2. Licença/configuração do WinSUP incorreta
3. Necessidade de atualização de firmware do WinSUP
