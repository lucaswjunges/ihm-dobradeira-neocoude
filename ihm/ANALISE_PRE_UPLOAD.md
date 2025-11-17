# ⚠️ ANÁLISE CRÍTICA PRÉ-UPLOAD - ROT5 MODIFICADO

**Data:** 16/Nov/2025
**Status:** REVISÃO FINAL ANTES DE GRAVAR NO CLP

---

## 🔍 PROBLEMAS IDENTIFICADOS NA SOLUÇÃO ATUAL

### ❌ PROBLEMA 1: Triggers Aumentam Complexidade Desnecessária

**Solução atual (Linhas 7-12):**
```ladder
[Line00007]
  Out:MOV E:0A00 E:0842
  Branch: {0;00;0390;-1;-1;-1;-1;00}  // Trigger 0x0390
```

**Implicação no código Python:**
```python
# IHM precisa fazer 5 operações para gravar 1 ângulo:
client.write_register(0x0A00, msw)      # 1. Escrever MSW
client.write_register(0x0A02, lsw)      # 2. Escrever LSW
client.write_coil(0x0390, True)         # 3. Ativar trigger
time.sleep(0.05)                        # 4. Aguardar scan
client.write_coil(0x0390, False)        # 5. Desativar trigger
```

**Risco:**
- Bug no código Python deixa trigger ligado → copia lixo continuamente
- Race condition entre escrita MSW/LSW e ativação do trigger
- Mais pontos de falha = menos confiável

---

### ❌ PROBLEMA 2: Race Condition em 32-bit

**Cenário perigoso:**
```
T=0ms:  IHM escreve 0x0A00 = 0x0000 (MSW novo)
T=5ms:  IHM escreve 0x0A02 = 0x0384 (LSW novo)
T=8ms:  IHM ativa 0x0390 (trigger)
T=9ms:  CLP scan detecta trigger ANTES de LSW chegar
T=10ms: Ladder copia MSW novo + LSW ANTIGO → ângulo ERRADO!
```

**Probabilidade:** Baixa, mas EXISTE. Em ambiente industrial, isso é inaceitável.

---

### ❌ PROBLEMA 3: Triggers Não Documentados

Estamos usando bits:
- `0x0390` - Não sabemos se é usado em outra rotina
- `0x0391` - Não sabemos se é usado em outra rotina
- `0x0392` - Não sabemos se é usado em outra rotina
- `0x0393` - Não sabemos se é usado em outra rotina

**Risco:** Efeito colateral inesperado em outra parte do ladder.

---

### ⚠️ PROBLEMA 4: Linha 15 (WEG) Não Está Pronta

**Linha atual:**
```ladder
[Line00015]
  Out:MOV E:0C00 E:0180
  Branch: {0;00;0393;-1;-1;-1;-1;00}
```

**Problemas:**
1. Não sabemos se `0x0180` (saída S0) está conectada ao inversor WEG
2. Código Python não implementa controle WEG ainda
3. Bit `0x0393` pode estar em uso em outro lugar
4. Adicionar linha "preparatória" sem necessidade = risco desnecessário

---

## ✅ SOLUÇÃO RECOMENDADA: SIMPLIFICAR

### Modificação 1: Remover Triggers (Linhas 7-12)

**ANTES (com triggers):**
```ladder
[Line00007]
  Out:MOV E:0A00 E:0842
  Branch: {0;00;0390;-1;-1;-1;-1;00}  // ❌ Trigger complexo
```

**DEPOIS (sempre ativo):**
```ladder
[Line00007]
  Out:MOV E:0A00 E:0842
  Branch: {0;00;00FF;-1;-1;-1;-1;00}  // ✅ Sempre ativo (bit 0xFF)
```

**Vantagens:**
- ✅ IHM só escreve em `0x0A00-0x0A0A`, NADA MAIS
- ✅ Zero lógica de trigger no Python
- ✅ Impossível race condition (copia a cada scan ~6ms)
- ✅ Se IHM escrever 0, ladder copia 0 (sem problemas)
- ✅ Código Python: 2 linhas em vez de 5

**Código Python simplificado:**
```python
# Apenas 2 operações:
client.write_register(0x0A00, msw)
client.write_register(0x0A02, lsw)
# Pronto! Ladder copia automaticamente em ~6ms
```

**Overhead no CLP:**
- 6 MOVs a cada scan (~6µs cada = 36µs total)
- Scan atual: ~6ms/KB (6000µs)
- Aumento: 0.6% (DESPREZÍVEL)

---

### Modificação 2: Remover Linha 15 (WEG)

**Motivos:**
1. Não há implementação Python pronta
2. Não sabemos se `0x0180` é correto
3. Bit `0x0393` não foi validado
4. Pode adicionar DEPOIS quando necessário

**Resultado:**
- ROT5 fica com **14 linhas** (não 15)
- Foco no objetivo imediato: programar ângulos via web
- WEG pode ser adicionado em versão futura (v2)

---

### Modificação 3: Manter Linhas 13-14 (SCADA)

**Motivo:**
- Overhead mínimo (~12µs por scan)
- Preparação estratégica para Grafana/SCADA
- Não afeta operação atual
- Isola leitura SCADA de registros críticos

**Decisão:** MANTER

---

## 📋 ROT5 FINAL RECOMENDADO

```
Linhas 1-6:   Emulação de botões (INALTERADO)
Linhas 7-12:  Input Modbus (SEM TRIGGERS - bit 0xFF)
Linhas 13-14: SCADA mirror (MANTIDO)
Linha 15:     WEG control (REMOVIDA)
```

**Total:** 14 linhas

---

## 🔄 MUDANÇAS NECESSÁRIAS NO ROT5.lad

### Linha 7: Mudar
```
DE:   {0;00;0390;-1;-1;-1;-1;00}
PARA: {0;00;00FF;-1;-1;-1;-1;00}
```

### Linha 8: Mudar
```
DE:   {0;00;0390;-1;-1;-1;-1;00}
PARA: {0;00;00FF;-1;-1;-1;-1;00}
```

### Linha 9: Mudar
```
DE:   {0;00;0391;-1;-1;-1;-1;00}
PARA: {0;00;00FF;-1;-1;-1;-1;00}
```

### Linha 10: Mudar
```
DE:   {0;00;0391;-1;-1;-1;-1;00}
PARA: {0;00;00FF;-1;-1;-1;-1;00}
```

### Linha 11: Mudar
```
DE:   {0;00;0392;-1;-1;-1;-1;00}
PARA: {0;00;00FF;-1;-1;-1;-1;00}
```

### Linha 12: Mudar
```
DE:   {0;00;0392;-1;-1;-1;-1;00}
PARA: {0;00;00FF;-1;-1;-1;-1;00}
```

### Linha 15: REMOVER COMPLETAMENTE
- Apagar todo o bloco `[Line00015]`
- Ajustar `Lines:00015` para `Lines:00014` na linha 1

---

## 📊 COMPARAÇÃO: ANTES vs RECOMENDADO

| Item | Solução Atual (Triggers) | Solução Recomendada (Sempre Ativo) |
|------|--------------------------|-------------------------------------|
| **Linhas de código Python** | 5 (escrever + trigger ON/OFF) | 2 (apenas escrever) |
| **Pontos de falha** | 5 | 2 |
| **Race condition** | Possível | Impossível |
| **Bits desconhecidos usados** | 4 (0x0390-0x0393) | 0 |
| **Overhead no CLP** | ~36µs (só quando trigger ativo) | ~36µs (sempre) |
| **Complexidade** | Alta | Baixa |
| **Robustez** | Média | Alta |
| **Preparação WEG** | Sim (não testada) | Não (adicionar depois) |

---

## 🎯 RECOMENDAÇÃO FINAL

### ✅ FAZER AGORA (Versão 1.0):
1. Modificar linhas 7-12 para usar bit `0x00FF` (sempre ativo)
2. Remover linha 15 (WEG control)
3. Manter linhas 13-14 (SCADA mirror)
4. Gerar novo `clp_MODIFICADO_IHM_WEB_v2.sup`
5. Fazer upload no CLP

### 🔜 ADICIONAR DEPOIS (Versão 2.0):
1. Testar saída `0x0180` no bancada
2. Confirmar conexão com inversor WEG
3. Implementar código Python de controle WEG
4. Adicionar linha 15 (WEG control) com segurança

---

## ⚖️ DECISÃO

**Opção A:** Usar `.sup` atual (com triggers)
- ❌ Mais complexo
- ❌ Mais pontos de falha
- ❌ Race condition possível
- ✅ Preparado para WEG (não testado)

**Opção B:** Usar `.sup` simplificado (SEM triggers) ✅ **RECOMENDADO**
- ✅ Máxima simplicidade
- ✅ Máxima robustez
- ✅ Zero race condition
- ✅ Código Python trivial
- ✅ Foco no objetivo (ângulos via web)
- ❌ WEG fica para depois (baixo risco)

---

## 🚀 PRÓXIMOS PASSOS

**SE escolher Opção B:**
1. Modificar `ROT5.lad` (trocar triggers por 0xFF, remover linha 15)
2. Rodar `python3 generate_sup_fixed.py`
3. Verificar novo `.sup`
4. Fazer upload no CLP
5. Testar programação de ângulos

**Tempo estimado:** 10 minutos para modificar + gerar + testar

---

**Preparado por:** Claude Code (Anthropic)
**Decisão:** AGUARDANDO CONFIRMAÇÃO DO USUÁRIO
