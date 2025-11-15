# Correções Aplicadas na ROT10 - CLP NEOCOUDE-HD-15

**Data**: 2025-11-12
**Arquivo Original**: `CLP_FINAL_11_ROTINAS_CORRIGIDO.sup`
**Arquivo Corrigido**: `CLP_FINAL_11_ROTINAS_CORRIGIDO_FIXED.sup`

---

## 🔍 Problemas Identificados

### ❌ Erro 1: Tipo de Instrução Incorreto
**Sintoma**: WinSUP2 reportava "registro OPx fora do range permitido"
**Causa**: ROT10 usava `T:0048 Size:001` para registros 32-bit

**Registros Afetados**:
- Encoder (04D6/04D7): Contador 32-bit de alta velocidade
- Ângulos (0840-0852): Setpoints de dobra (32-bit)

**Comparação**:
```
❌ ANTES: MOV T:0048 Size:001 E:04D6 E:0900
✅ DEPOIS: MOV T:0028 Size:003 E:04D6 E:0900
```

### ❌ Erro 2: MOV Direto em Registros de I/O
**Sintoma**: "registro OP1 fora do range permitido"
**Causa**: Tentativa de usar MOV para copiar registros de I/O digital

**Registros Afetados**:
- **Entradas**: 0x0100-0x0105 (E0-E5)
- **Saídas**: 0x0180-0x0181 (S0-S1)

**Solução**: Instruções MOV comentadas (preservadas como referência)

---

## ✅ Correções Aplicadas

### 1. Encoder (04D6/04D7) - 2 linhas
```diff
- Out:MOV     T:0048 Size:001 E:04D6 E:0900
+ Out:MOV     T:0028 Size:003 E:04D6 E:0900

- Out:MOV     T:0048 Size:001 E:04D7 E:0901
+ Out:MOV     T:0028 Size:003 E:04D7 E:0901
```

### 2. Ângulos de Dobra (084x/085x) - 6 linhas
```diff
Dobra 1 (Esquerda):
- Out:MOV     T:0048 Size:001 E:0842 E:0910
+ Out:MOV     T:0028 Size:003 E:0842 E:0910

- Out:MOV     T:0048 Size:001 E:0840 E:0911
+ Out:MOV     T:0028 Size:003 E:0840 E:0911

Dobra 2 (Esquerda):
- Out:MOV     T:0048 Size:001 E:084A E:0913
+ Out:MOV     T:0028 Size:003 E:084A E:0913

- Out:MOV     T:0048 Size:001 E:0848 E:0914
+ Out:MOV     T:0028 Size:003 E:0848 E:0914

Dobra 3 (Esquerda):
- Out:MOV     T:0048 Size:001 E:0852 E:0916
+ Out:MOV     T:0028 Size:003 E:0852 E:0916

- Out:MOV     T:0048 Size:001 E:0850 E:0917
+ Out:MOV     T:0028 Size:003 E:0850 E:0917
```

### 3. Registros de I/O - 8 linhas comentadas
```diff
Entradas Digitais (E0-E5):
- Out:MOV     T:0048 Size:001 E:0100 E:0930
+ # COMENTADO - Instrução inválida: Out:MOV     T:0048 Size:001 E:0100 E:0930

... (6 linhas similares para E:0101-0105)

Saídas Digitais (S0-S1):
- Out:MOV     T:0048 Size:001 E:0180 E:0940
+ # COMENTADO - Instrução inválida: Out:MOV     T:0048 Size:001 E:0180 E:0940

... (2 linhas similares para E:0181)
```

---

## 📊 Resumo das Correções

| Tipo de Correção | Quantidade | Status |
|-----------------|------------|--------|
| Encoder 32-bit | 2 | ✅ Corrigido |
| Ângulos 32-bit | 6 | ✅ Corrigido |
| I/O Digital | 8 | 🔧 Comentado |
| **TOTAL** | **16** | **Concluído** |

---

## 🔧 Próximos Passos

### 1. Teste no WinSUP2
1. Abra o arquivo `CLP_FINAL_11_ROTINAS_CORRIGIDO_FIXED.sup` no WinSUP2
2. Execute a verificação de checagem (lista de erros)
3. Confirme que os erros "registro fora do range" foram resolvidos

### 2. Resolva os Registros de I/O Comentados

As 8 instruções MOV para registros de I/O foram **comentadas** porque não é permitido usar MOV direto para esses endereços. Você tem 3 opções:

#### Opção A: Usar Instruções Apropriadas (Recomendado)
Substitua por instruções SETR ou CTCPU (verificar manual):
```
# Para saídas digitais (0x0180-0x0187):
Out:SETR    T:0043 Size:003 E:0180

# Para entradas digitais (0x0100-0x0107):
Out:CTCPU   T:0016 Size:004 E:0800 E:0000 E:0100
```

#### Opção B: Acessar via States (Coils)
Os registros de I/O também podem ser acessados como bits:
- E0-E7: States 0x0100-0x0107
- S0-S7: States 0x0180-0x0187

Use instruções de manipulação de bits se só precisa do status ON/OFF.

#### Opção C: Remover se Desnecessário
Se a ROT10 não precisa realmente copiar esses valores, simplesmente remova os blocos comentados.

### 3. Compile e Teste
1. Recompile o programa no WinSUP2
2. Faça download para o CLP
3. Teste as funcionalidades que dependem da ROT10

---

## 📚 Referências Técnicas

### Formato de Tipos de Instrução (T:XXXX)
- **T:0028**: Operação com registros 32-bit (MSW+LSW)
- **T:0043**: Set Register (para I/O digital)
- **T:0044**: Move Constant (MOVK)
- **T:0048**: Move 16-bit single register (não suportado para I/O)

### Formato de Size
- **Size:001**: 16-bit single register
- **Size:003**: 32-bit register pair (MSW+LSW)
- **Size:004**: Operação especial ou múltiplos operandos

### Memória do MPC4004
| Faixa | Descrição | Acesso |
|-------|-----------|--------|
| 0x0000-0x03FF | Internal States (1024 bits) | Read/Write via coil instructions |
| 0x0100-0x0107 | Digital Inputs E0-E7 | ⚠️ Somente leitura, não MOV direto |
| 0x0180-0x0187 | Digital Outputs S0-S7 | ⚠️ Usar SETR, não MOV direto |
| 0x0400-0x0FFF | Registers (1536 x 16-bit) | Read/Write via MOV |
| 0x04D6-0x04D7 | High-Speed Counter (32-bit) | ✅ MOV T:0028 Size:003 |
| 0x0840-0x0852 | Angle Setpoints (32-bit) | ✅ MOV T:0028 Size:003 |

---

## 🛠️ Script de Correção

O script `fix_rot10.py` foi criado para automatizar correções futuras:

```bash
# Uso básico:
python3 fix_rot10.py

# Aplica correções em:
# 1. Tipo T:0048 → T:0028 para registros 32-bit
# 2. Size:001 → Size:003 para registros 32-bit
# 3. Comenta instruções MOV inválidas para I/O
```

---

## ⚠️ Avisos Importantes

1. **Backup**: O arquivo original foi preservado como `ROT10_ORIGINAL.lad` no diretório `sup_extracted/`
2. **Teste Antes de Usar em Produção**: Valide todas as correções no WinSUP2 e teste em bancada
3. **I/O Comentados**: As instruções de I/O precisam ser reimplementadas corretamente
4. **Compatibilidade**: Estas correções são específicas para o CLP Atos MPC4004

---

## 📞 Contato

Para dúvidas sobre implementação ou erros adicionais, consulte:
- `CLAUDE.md`: Documentação completa do projeto
- Manual MPC4004: `manual_MPC4004.pdf`
- Análise de registros: `ANALISE_COMPLETA_REGISTROS_PRINCIPA.md`
