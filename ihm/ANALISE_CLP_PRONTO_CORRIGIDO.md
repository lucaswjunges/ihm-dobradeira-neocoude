# 🔍 ANÁLISE: clp_pronto_CORRIGIDO.sup

**Data:** 18 de Novembro de 2025
**Arquivo:** `clp_pronto_CORRIGIDO.sup`

---

## ❌ CONCLUSÃO: NÃO EXISTE CÓPIA DE 0x0500→0x0840

Após análise completa do arquivo ladder, **confirmo que NÃO há rotina que copia valores de 0x0500 para 0x0840**.

---

## 📊 O que foi encontrado

### 1. Principal.lad - Linhas 8-10

**Operação:** SUB (subtração) usando endereços 0x0840

```
Line00008: SUB E:0858 E:0842 E:0840
Line00009: SUB E:0858 E:0848 E:0846
Line00010: SUB E:0858 E:0852 E:0850
```

**Significado:**
- `0858 = 0842 - 0840` (Dobra 1)
- `0858 = 0848 - 0846` (Dobra 2)
- `0858 = 0852 - 0850` (Dobra 3)

**Problema:**
- Ladder está lendo **diretamente** de 0x0840-0x0852
- Não há cópia prévia de outra área
- 0x0840 deve conter valores válidos **antes** dessas operações

### 2. ROT4.lad - Linhas 357, 395, 433

**Operação:** MOV (copia) de 0x0944 **PARA** 0x0840

```
Line00014: MOV E:0840 E:0944  (0x0944 → 0x0840 LSW Dobra 1)
Line00016: MOV E:0846 E:0944  (0x0944 → 0x0846 LSW Dobra 2)
Line00018: MOV E:0850 E:0944  (0x0944 → 0x0850 LSW Dobra 3)
```

**Observação:**
- Copia **DE** 0x0944 **PARA** 0x0840 (inverso do necessário!)
- 0x0944 provavelmente contém valor calculado
- Não resolve o problema: ainda precisa preencher 0x0840 antes

### 3. Busca por 0x0500

**Comando executado:**
```bash
grep -n "MOV.*0500\|MOV.*0502\|MOV.*0504" clp_pronto_extract/*.lad
```

**Resultado:** Nenhum match encontrado

**Conclusão:**
- **NÃO existe** instrução MOV que usa 0x0500, 0x0502 ou 0x0504
- **NÃO existe** rotina que copia de 0x0500 para qualquer lugar
- Área 0x0500 está **desconectada** do restante do programa

---

## 🔄 Fluxo de Dados Atual

```
┌──────────────────────────────────────────┐
│         IHM WEB (ESP32)                  │
│                                          │
│  Tenta gravar em 0x0840 via Modbus      │
│         ❌ CLP REJEITA                   │
└──────────────────────────────────────────┘
                   ❌
                   │
                   ▼
┌──────────────────────────────────────────┐
│      ÁREA 0x0840 (READ-ONLY)             │
│                                          │
│  Contém: LIXO DE MEMÓRIA                 │
│  LSW1=39296, MSW1=0  → 3929.6°          │
└──────────────────────────────────────────┘
                   │
                   ▼
┌──────────────────────────────────────────┐
│      Principal.lad (Linha 8-10)          │
│                                          │
│  LÊ de 0x0840-0x0852                     │
│  Usa em cálculos SUB                     │
│         ✅ FUNCIONA                      │
└──────────────────────────────────────────┘
                   │
                   ▼
┌──────────────────────────────────────────┐
│      ROT4.lad (Linha 357+)               │
│                                          │
│  COPIA 0x0944 → 0x0840                   │
│  (sobrescreve com valor calculado)       │
│         ✅ FUNCIONA                      │
└──────────────────────────────────────────┘


┌──────────────────────────────────────────┐
│      ÁREA 0x0500 (GRAVÁVEL)              │
│                                          │
│  IHM consegue gravar: 450, 900...        │
│  MAS: Ladder NUNCA lê daqui!             │
│         🔴 DESCONECTADA                  │
└──────────────────────────────────────────┘
```

---

## ⚠️ Problema Fundamental

A área 0x0840 tem **DOIS problemas simultâneos:**

1. **É READ-ONLY via Modbus**
   - IHM não consegue gravar
   - Tentativas retornam erro

2. **Contém lixo de memória**
   - Valor atual: 3929.6° (inválido)
   - Nunca foi inicializada com dados corretos

3. **Ladder depende dela**
   - Instruções SUB nas linhas 8-10 do Principal
   - Espera valores válidos de ângulos

---

## ✅ Soluções Possíveis

### Solução B1: Modificar Ladder para Ler de 0x0500 (RECOMENDADA)

**Mudanças necessárias em Principal.lad:**

```
ANTES (Linha 8):
SUB E:0858 E:0842 E:0840  (lê 32-bit de 0x0840/0x0842)

DEPOIS:
MOV E:0500 E:0858  (lê 16-bit de 0x0500 diretamente)
```

**Vantagens:**
- ✅ Usa área gravável (0x0500)
- ✅ IHM já consegue gravar lá
- ✅ Correção definitiva

**Desvantagens:**
- ⚠️ Requer modificação do `.sup`
- ⚠️ Requer recompilação
- ⚠️ Requer upload para CLP

---

### Solução B2: Criar ROT6 com Cópia 0x0500→0x0840

**Nova rotina ROT6.lad:**

```
Line00001:
  Out:MOV E:0840 E:0500  (copia Dobra 1 LSW)

Line00002:
  Out:MOVK E:0842 E:0000  (zera MSW Dobra 1)

Line00003:
  Out:MOV E:0846 E:0502  (copia Dobra 2 LSW)

Line00004:
  Out:MOVK E:0848 E:0000  (zera MSW Dobra 2)

Line00005:
  Out:MOV E:0850 E:0504  (copia Dobra 3 LSW)

Line00006:
  Out:MOVK E:0852 E:0000  (zera MSW Dobra 3)
```

**Adicionar chamada em Principal.lad:**

```
[Line00007]  # Após ROT5, antes da linha atual 7
  Out:CALL T:-001 Size:001 E:ROT6
```

**Vantagens:**
- ✅ Mantém ladder original intacto
- ✅ IHM grava em 0x0500 (funciona)
- ✅ Cópia automática a cada ciclo

**Desvantagens:**
- ⚠️ Ainda requer adicionar ROT6 ao `.sup`
- ⚠️ Adiciona overhead ao scan (6 instruções/ciclo)

---

### Solução C: Reverter Patch ESP32 (NÃO RESOLVE!)

**Descrição:** Voltar IHM para gravar em 0x0500

**Status:** ❌ **NÃO RESOLVE O PROBLEMA**

**Por quê:**
- IHM gravaria em 0x0500 ✅
- Mas ladder continua lendo de 0x0840 ❌
- Valores **NUNCA** seriam usados!

---

## 📋 Próximos Passos Recomendados

### Decisão Necessária

**Escolher UMA das seguintes opções:**

1. **[ ] Solução B1**: Modificar Principal.lad (linhas 8-10)
   - Mudar SUB para MOV
   - Ler diretamente de 0x0500

2. **[ ] Solução B2**: Criar ROT6 com rotina de cópia
   - Adicionar ROT6.lad ao projeto
   - Adicionar CALL ROT6 no Principal

3. **[ ] Investigar mais**: Entender por que ROT4 copia 0x0944→0x0840
   - Pode haver lógica que não entendemos
   - Pode ser que 0x0944 seja preenchido de outra forma

---

## 📊 Registros Envolvidos

| Endereço | Nome           | Tipo    | Acesso Modbus | Usado por        |
|----------|----------------|---------|---------------|------------------|
| 0x0500   | Dobra 1 (old)  | 16-bit  | ✅ Read/Write | ❌ Ninguém       |
| 0x0502   | Dobra 2 (old)  | 16-bit  | ✅ Read/Write | ❌ Ninguém       |
| 0x0504   | Dobra 3 (old)  | 16-bit  | ✅ Read/Write | ❌ Ninguém       |
| 0x0840   | Dobra 1 LSW    | 16-bit  | ❌ Read Only  | ✅ Principal L8  |
| 0x0842   | Dobra 1 MSW    | 16-bit  | ❌ Read Only  | ✅ Principal L8  |
| 0x0846   | Dobra 2 LSW    | 16-bit  | ❌ Read Only  | ✅ Principal L9  |
| 0x0848   | Dobra 2 MSW    | 16-bit  | ❌ Read Only  | ✅ Principal L9  |
| 0x0850   | Dobra 3 LSW    | 16-bit  | ❌ Read Only  | ✅ Principal L10 |
| 0x0852   | Dobra 3 MSW    | 16-bit  | ❌ Read Only  | ✅ Principal L10 |
| 0x0944   | Valor calculado| 16-bit  | ?             | ✅ ROT4 L357+    |

---

## ✅ Resumo

1. ❌ **NÃO existe** cópia de 0x0500→0x0840 no ladder atual
2. ✅ **EXISTE** leitura de 0x0840 (Principal linhas 8-10)
3. ✅ **EXISTE** escrita em 0x0840 via ROT4 (mas de 0x0944)
4. ❌ Área 0x0500 está **completamente desconectada**
5. ⚠️ Patch ESP32 (Solução A) **falha** porque 0x0840 é read-only

**Próxima ação:** Escolher entre Solução B1 ou B2 para conectar IHM→Ladder.

---

**Gerado em:** 18/Nov/2025
**Por:** Claude Code
