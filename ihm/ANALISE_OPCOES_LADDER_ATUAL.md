# 🔍 ANÁLISE COMPLETA - SITUAÇÃO ATUAL DO CLP

**Data:** 16/Nov/2025 12:30
**CLP Conectado:** ✅ SIM (`/dev/ttyUSB0 @ 57600 bps`)
**Arquivo Atual:** `clp_pronto_CORRIGIDO.sup` (27KB, modificado 11/Nov)

---

## 📊 TESTE EXECUTADO AGORA (RESULTADOS REAIS)

```
✅ CLP Conectado OK
✅ Encoder funcionando: 11.9° (leitura em tempo real)
❌ Ângulos NÃO PERSISTEM:
   - Escrevi: 450 (45.0°)
   - Li após 500ms: 39280 (3928.0°)
   - Conclusão: LADDER SOBRESCREVE IMEDIATAMENTE!

✅ E6 (entrada crítica): OFF
   - S0/S1 teoricamente podem ligar (condição E6=OFF satisfeita)

❌ Motor S0/S1: Ambos OFF (não testado write ainda)
```

---

## 🧐 HISTÓRICO DO QUE JÁ FOI TENTADO

### 1. Modificações de Ladder (v12 → v17)

**Documentação encontrada:**
- `README_v17_TUDO_CORRIGIDO.md` - Tentativas de adicionar ROT6-ROT9
- `MODIFICACAO_LADDER_EMULACAO_IHM.md` - Proposta registro espelho 0x0860
- `ANALISE_S0_S1_LADDER.md` - Descoberta bloqueio E6 em S0/S1

**Problemas identificados:**
1. ❌ Project.spr com rotinas incompletas
2. ❌ Principal.lad com linhas duplicadas
3. ❌ ROT6.lad com cabeçalho errado (Lines:00035 vs 18 reais)
4. ❌ Compilação falhando no WinSUP

**Resultado:** Versões v12-v17 criadas mas **NUNCA gravadas no CLP**

### 2. Estado Atual do CLP

```
clp_pronto_CORRIGIDO.sup contém:
├─ ROT0-ROT5: ✅ Funcionais (base original)
├─ ROT6: ❌ Existe no .sup mas NÃO está em Project.spr
├─ ROT7-ROT9: ❌ Não existem
└─ Principal.lad: ✅ Original (sem modificações avançadas)
```

**Confirmação:** Arquivo atual **NÃO TEM** as modificações das versões v12-v17!

---

## ⚠️ PROBLEMA RAIZ IDENTIFICADO

### 🔴 **REGISTROS DE ÂNGULOS SÃO READ-ONLY VIA MODBUS**

**Endereços Testados:**
- 0x0840/0x0842 (Dobra 1) - PRINCIPAL.lad:Line00008
- 0x0846/0x0848 (Dobra 2) - PRINCIPAL.lad:Line00009
- 0x0850/0x0852 (Dobra 3) - PRINCIPAL.lad:Line00010

**Lógica do Ladder:**
```ladder
Line00008: Out:SUB T:0048 Size:004 E:0858 E:0842 E:0840
Line00009: Out:SUB T:0048 Size:004 E:0858 E:0848 E:0846
Line00010: Out:SUB T:0048 Size:004 E:0858 E:0852 E:0850
```

**Interpretação:**
- Ladder **CALCULA** ângulos a cada scan (~6-12ms)
- Usa SUB (subtração): `0858 = 0842 - 0840`
- Qualquer valor escrito via Modbus é **sobrescrito imediatamente**
- Não há INPUT de ângulos via Modbus no ladder atual!

### 🔍 Onde a IHM Física Original Escrevia?

**Hipóteses:**
1. **NVRAM (0x0500-0x053F)** - Área não-volátil para ângulos iniciais
2. **Registros dedicados de entrada** - Ainda não mapeados
3. **IHM escrevia diretamente na memória do CLP** - Via protocolo proprietário

**Teste de varredura anterior:** `test_find_writable_registers.py`
- Resultado: **0 candidatos encontrados** em 168 pares testados
- Todas as áreas testadas são sobrescritas pelo ladder

---

## 🎯 OPÇÕES DISPONÍVEIS (ANÁLISE TÉCNICA)

### OPÇÃO A: 🟢 **IHM HÍBRIDA** (Monitoramento Apenas)

**Descrição:**
Aceitar que IHM web é **somente leitura**, mantendo painel físico para configuração.

**O que funciona:**
- ✅ Leitura encoder em tempo real
- ✅ Leitura de estados (E0-E7, S0-S7)
- ✅ Leitura de ângulos **programados** (0x0840-0x0852)
- ✅ Visualização de LEDs, status, alarmes
- ✅ Dashboards Grafana/SCADA

**O que NÃO funciona:**
- ❌ Configuração de ângulos via web
- ❌ Controle de motor (AVANÇAR/RECUAR) via web
- ❌ Substituição 100% do painel físico

**Vantagens:**
- 🟢 Zero risco (não mexe em ladder)
- 🟢 Implementação imediata (código já existe)
- 🟢 Máquina continua operando normal
- 🟢 Útil para supervisão/diagnóstico remoto

**Desvantagens:**
- 🔴 Não atende objetivo original (substituir IHM física)
- 🔴 Operador precisa do painel físico

**Esforço:** ⏱️ 0 horas (já implementado!)

---

### OPÇÃO B: 🟡 **MODIFICAÇÃO LADDER CONTROLADA**

**Descrição:**
Modificar ladder para criar **registros de entrada Modbus** dedicados.

#### B.1: Criar Área de Input (0x0A00-0x0A10)

**Lógica proposta:**
```ladder
[Line00025] NOVO - Cópia de inputs Modbus
  [Features]
    Comment: "Copia ângulos escritos via Modbus para área de trabalho"

  ; Dobra 1
  [Branch01]
    In:LDP  E:0A00  ; Detecta mudança em 0A00 (Modbus escreveu)
    Out:MOV E:0A02 E:0840  ; Copia LSW para área oficial
    Out:MOV E:0A00 E:0842  ; Copia MSW para área oficial
    ###

  ; Dobra 2
  [Branch02]
    In:LDP  E:0A04
    Out:MOV E:0A06 E:0846
    Out:MOV E:0A04 E:0848
    ###

  ; Dobra 3
  [Branch03]
    In:LDP  E:0A08
    Out:MOV E:0A0C E:0850
    Out:MOV E:0A08 E:0852
    ###
```

**Atualização Python:**
```python
# modbus_map.py
BEND_ANGLES_INPUT = {
    'BEND_1_MSW': 0x0A00,  # IHM web escreve aqui
    'BEND_1_LSW': 0x0A02,
    'BEND_2_MSW': 0x0A04,
    'BEND_2_LSW': 0x0A06,
    'BEND_3_MSW': 0x0A08,
    'BEND_3_LSW': 0x0A0A,
}
```

**Vantagens:**
- 🟢 Solução definitiva e elegante
- 🟢 IHM web pode configurar ângulos
- 🟢 Não quebra lógica existente
- 🟢 Retrocompatível (IHM física continua funcionando)

**Desvantagens:**
- 🔴 Requer WinSUP (Windows)
- 🔴 Risco de erro humano ao editar ladder
- 🔴 Precisa gravar no CLP (máquina para ~5min)
- 🔴 Rollback necessário se der errado

**Esforço:** ⏱️ 2-3 horas (na fábrica, segunda-feira)

**Checklist existente:** `CHECKLIST_SEGUNDA_MODIFICACAO_LADDER.md` ✅

---

#### B.2: Usar NVRAM (0x0500-0x053F)

**Lógica proposta:**
```ladder
; Verificar se ladder JÁ copia de 0x0500
; Se sim, basta IHM web escrever lá!

; BUSCAR no ladder:
; MOV E:0500 → 0840
; MOV E:0502 → 0842
```

**Se ladder já usar NVRAM:**
- 🟢 Nenhuma modificação necessária!
- 🟢 Apenas atualizar `modbus_map.py`

**Se ladder NÃO usar:**
- Adicionar lógica similar a B.1

**Esforço:** ⏱️ 1-2 horas (se já existir) ou 2-3 horas (se criar)

---

### OPÇÃO C: 🔴 **ENGENHARIA REVERSA COMPLETA**

**Descrição:**
Analisar **todo** o ladder (ROT0-ROT5 + Principal) para entender onde IHM física original escrevia.

**Ferramentas:**
- WinSUP (abrir clp_pronto_CORRIGIDO.sup no Windows)
- Análise de fluxo de dados (cross-reference)
- Testes exaustivos com mbpoll

**Vantagens:**
- 🟢 Solução "nativa" (usa mesmos endereços da IHM original)
- 🟢 Máximo aproveitamento do ladder existente

**Desvantagens:**
- 🔴 Muito tempo (8-16 horas de análise)
- 🔴 Ladder pode **não ter** inputs Modbus (IHM via serial proprietária)
- 🔴 Alto risco de não encontrar nada

**Esforço:** ⏱️ 8-16 horas + modificação (se necessário)

---

### OPÇÃO D: 🟣 **EMULAÇÃO VIA ROT6-ROT9** (Experimental)

**Descrição:**
Adicionar rotinas ROT6-ROT9 com lógica Modbus avançada (conforme tentativas anteriores).

**Arquivos base:**
- `CLP_10_ROTINAS_v17_TUDO_CORRIGIDO.sup` (359KB)
- ROT6: 18 linhas (integração Modbus)
- ROT7: 12 linhas (inversor WEG)
- ROT8: 15 linhas (estatísticas)
- ROT9: 20 linhas (emulação teclas)

**Vantagens:**
- 🟢 Funcionalidades avançadas (SCADA, Grafana, emulação)
- 🟢 Documentação já existe (README_v17)
- 🟢 Código ladder pronto (corrigido nas versões v12-v17)

**Desvantagens:**
- 🔴 Nunca foi testado no CLP real!
- 🔴 Complexidade alta (10 rotinas vs 6 atuais)
- 🔴 Pode ter bugs não descobertos
- 🔴 Risco de corromper programa funcionável

**Esforço:** ⏱️ 4-6 horas (gravar + testar extensivamente)

---

## 🚦 RECOMENDAÇÃO TÉCNICA

### Cenário 1: **Urgência Baixa + Risco Zero**
→ **OPÇÃO A** (IHM Híbrida)
Use para monitoramento e diagnóstico. Operador continua usando painel físico.

### Cenário 2: **Precisa de Controle Total + Tem WinSUP**
→ **OPÇÃO B.1** (Modificação Controlada - Área 0x0A00)
Solução profissional e segura. Seguir checklist existente.

### Cenário 3: **Quer Aproveitar Ladder Original**
→ **OPÇÃO B.2** (Verificar NVRAM 0x0500)
Testar primeiro se ladder já usa NVRAM. Se sim, ganho rápido!

### Cenário 4: **Projeto de Longo Prazo + Recursos**
→ **OPÇÃO C** (Engenharia Reversa)
Investimento alto mas solução "by the book".

### Cenário 5: **Exploratório/Experimental**
→ **OPÇÃO D** (ROT6-ROT9)
Apenas se tiver ambiente de testes e backup garantido.

---

## 📋 PRÓXIMO PASSO RECOMENDADO

### ✅ AÇÃO IMEDIATA (30 minutos)

**Verificar se ladder usa NVRAM:**

1. Abrir `clp_pronto_extract/Principal.lad` no editor de texto
2. Buscar: `0500`, `0502`, `0504` (endereços NVRAM)
3. Verificar se há instruções:
   ```
   MOV E:0500 → 0840  (ou similar)
   MOV E:0502 → 0842
   ```

4. **SE ENCONTRAR:**
   - ✅ Solução fácil! Basta atualizar `modbus_map.py`
   - Teste: escrever em 0x0500 via Modbus e verificar se persiste

5. **SE NÃO ENCONTRAR:**
   - Seguir OPÇÃO B.1 (adicionar área 0x0A00)

---

## 📞 SUPORTE DISPONÍVEL

**Documentação Pronta:**
- ✅ `GUIA_MODIFICACAO_LADDER_SEGUNDA.md` (passo-a-passo)
- ✅ `CHECKLIST_SEGUNDA_MODIFICACAO_LADDER.md` (printável)
- ✅ `MODIFICACAO_LADDER_EMULACAO_IHM.md` (referência técnica)
- ✅ `ANALISE_S0_S1_LADDER.md` (bloqueio motor)

**Testes Prontos:**
- ✅ `test_official_addresses_final.py` (validar ângulos)
- ✅ `test_find_writable_registers.py` (varredura completa)
- ✅ `test_alternative_angle_addresses.py` (motor)

---

## ⚙️ FERRAMENTAS NECESSÁRIAS

### Para OPÇÃO A (Híbrida):
- ✅ Nada! Código atual já funciona

### Para OPÇÃO B (Modificação Ladder):
- 🔧 WinSUP 2.x (Windows)
- 🔧 Cabo RS485 (USB-RS485)
- 🔧 Backup em pen drive
- 🔧 2-3 horas de parada da máquina

### Para OPÇÃO C (Engenharia Reversa):
- 🔧 WinSUP 2.x
- 🔧 Manual MPC4004 (já disponível)
- 🔧 8-16 horas de análise
- 🔧 mbpoll para testes

---

## 🏁 CONCLUSÃO

**Situação Atual:**
CLP funcional com ROT0-ROT5, mas **registros de ângulos são read-only via Modbus**.

**Problema Raiz:**
Ladder **não tem área de input** para ângulos via Modbus. Registros 0x0840-0x0852 são calculados, não inputs.

**Solução Mais Rápida:**
Verificar NVRAM (0x0500) - pode ser solução em 30min!

**Solução Mais Segura:**
Opção B.1 (área 0x0A00) - 2-3h na fábrica com checklist pronto.

**Opção Conservadora:**
Opção A (híbrida) - monitoramento funciona hoje, controle fica para depois.

---

**Gerado em:** 16/Nov/2025 12:45
**Por:** Claude Code (Anthropic)
**CLP Testado:** ✅ Atos MPC4004 @ /dev/ttyUSB0
