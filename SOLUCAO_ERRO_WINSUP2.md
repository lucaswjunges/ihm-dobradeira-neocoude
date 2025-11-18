# SOLUÇÃO DO ERRO WINSUP 2

**Data**: 2025-11-11
**Status**: ✅ PROBLEMA IDENTIFICADO E CORRIGIDO

---

## 🐛 O PROBLEMA

O WinSup 2 rejeitava os arquivos `clp_FINAL_COM_ROT5.sup` e `clp_FINAL_COM_ROT5_V2.sup` com erro ao abrir o projeto.

### Hipóteses Iniciais (INCORRETAS)

1. ❌ ROT4 muito grande (26KB vs 8.4KB original)
2. ❌ WinSup 2 não permite modificações em ROT4
3. ❌ WinSup 2 não permite 5ª rotina (ROT5)
4. ❌ Problema de line endings (CRLF vs LF)
5. ❌ Problema de compressão ZIP

### Problema Real (CORRETO)

✅ **Erro de sintaxe no formato Ladder Atos**: Instruções `Out:` foram incorretamente duplicadas dentro de seções `[Branch]`.

---

## 🔍 ANÁLISE DETALHADA

### Formato Ladder Correto (Atos)

```
[LineXXXXX]
  [Features]
    Branchs:02
    Out:MOVK    T:0029 Size:003 E:0A01 E:0000  ← ÚNICA vez que Out: aparece!
  [Branch01]
    {0;00;0190;-1;-1;-1;-1;00}  ← Apenas o contato
    ###  ← NENHUM Out: aqui!
  [Branch02]
    {0;00;0191;-1;-1;-1;-1;00}  ← Apenas o contato
    ###  ← NENHUM Out: aqui!
```

### Formato Errado Gerado (Versões V1 e V2)

```
[LineXXXXX]
  [Features]
    Out:MOVK    T:0029 Size:003 E:0A01 E:0000
  [Branch01]
    {0;00;0190;-1;-1;-1;-1;00}
    Out:MOVK    T:0029 Size:003 E:0A01 E:0000  ← ❌ ERRO!
    ###
```

**Consequência**: WinSup 2 detecta sintaxe inválida e rejeita o arquivo.

---

## ✅ ARQUIVO FINAL CORRIGIDO

**Arquivo**: `clp_FINAL_COM_ROT5_V3_CORRIGIDO.sup`

**Localização**: `/home/lucas-junges/Documents/clientes/w&co/`

**Tamanho**: 24,103 bytes

**Conteúdo**:
- Base: TESTE_BASE_SEM_MODIFICACAO.sup (testado ✅)
- ROT4 expandido: 21 → 32 linhas ladder
- Sintaxe validada: 0 erros
- 10 linhas ROT5 integradas (Lines 00023-00032)

---

## 🎯 FUNCIONALIDADES "BACKDOOR"

### 1. Espelhamento LCD → Modbus (Leitura)

| Dado | Original | Shadow |
|------|----------|--------|
| Modo | 0190/0191 | 0A01 |
| Encoder MSW | 04D6 | 0A0C |
| Encoder LSW | 04D7 | 0A0D |

### 2. Emulação de Teclas (Escrita)

| Tecla | Bit Modbus | Bit HMI |
|-------|------------|---------|
| K1 | 03E1 (993) | 00A0 (160) |
| S1 | 03EA (1002) | 00DC (220) |
| ENTER | 03EE (1006) | 0025 (37) |

### 3. Virtualização Botões (Lógica OR)

| Botão | Físico | Modbus | Flag Virtual |
|-------|--------|--------|--------------|
| AVANÇAR | E2 (0102) | 03F2 | 03FC (1020) |
| PARADA | E3 (0103) | 03F4 | 03FD (1021) |
| RECUAR | E4 (0104) | 03F3 | 03FE (1022) |

**Lógica**: `FLAG = Físico OR Modbus`

### 4. Heartbeat

| Modbus | Status | Função |
|--------|--------|--------|
| 03F7 | 03FF | Alive |

---

## 📊 COMPARAÇÃO

| Versão | Ladder Lines | Erros | WinSup 2 |
|--------|-------------|-------|----------|
| Original | 21 | 0 | ✅ |
| V1 | 55 | 11 | ❌ |
| V2 | 32 | 10 | ❌ |
| **V3 CORRIGIDO** | **32** | **0** | **❓ Testar** |

---

## 🧪 TESTE NO WINSUP 2

1. Copiar `clp_FINAL_COM_ROT5_V3_CORRIGIDO.sup` para Windows
2. Abrir WinSup 2
3. Arquivo → Abrir Projeto
4. **Expectativa**: Deve abrir sem erro ✅

---

**Data**: 2025-11-11 16:30  
**Status**: Aguardando teste
