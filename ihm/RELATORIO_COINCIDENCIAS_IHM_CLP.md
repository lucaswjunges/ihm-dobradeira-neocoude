# 🔬 RELATÓRIO DE COINCIDÊNCIAS - IHM vs CLP

**Data:** 18 de Novembro de 2025, 06:15
**Método:** Análise de coincidências via API ESP32 + Análise do ladder PRINCIPAL.lad
**Objetivo:** Verificar se valores mostrados na IHM coincidem com setpoints oficiais do CLP

---

## ❓ PERGUNTA DO USUÁRIO

> "Mas quero saber se existe coincidência entre os dados dos setpoints (oficiais) e os dados apresentados, nem que seja olhando no ladder para dizer"

---

## ✅ RESPOSTA DIRETA

**Há coincidência entre IHM e setpoints do CLP?**
⚠️ **SIM, PARCIALMENTE (67% - 2 de 3 dobras)**

**Detalhamento:**
- ✅ **Dobra 1 (45.0°)**: COINCIDE com registro 0x0500 do CLP
- ⚠️ **Dobra 2 (51.0°)**: CLP retorna `null` no registro 0x0502
- ✅ **Dobra 3 (90.0°)**: COINCIDE com registro 0x0504 do CLP

---

## 📚 ANÁLISE DO LADDER (PRINCIPAL.lad)

### Setpoints Oficiais Conforme Ladder

Conforme análise de `ANALISE_COMPLETA_REGISTROS_PRINCIPA.md`:

#### Registros Shadow 32-bit (usados pelo ladder):

| Dobra | Esquerda | Direita |
|-------|----------|---------|
| **Dobra 1** | 0x0840/0x0842 (2112/2114) | 0x0844/0x0846 (2116/2118) |
| **Dobra 2** | 0x0848/0x084A (2120/2122) | 0x084C/0x084E (2124/2126) |
| **Dobra 3** | 0x0850/0x0852 (2128/2130) | 0x0854/0x0856 (2132/2134) |

**Instrução ladder (PRINCIPAL.lad):**
```
Line00008: Out:SUB T:0048 Size:004 E:0858 E:0842 E:0840  // Dobra 1
Line00009: Out:SUB T:0048 Size:004 E:0858 E:0848 E:0846  // Dobra 2
Line00010: Out:SUB T:0048 Size:004 E:0858 E:0852 E:0850  // Dobra 3
```

### Área de Setpoints Manual MPC4004

Conforme manual MPC4004 (página 85):
- **0x0500-0x053F** (1280-1343): Área oficial de setpoints de ângulos

---

## 🧪 TESTES EXECUTADOS VIA API ESP32

### Teste 1: Valores Atuais da IHM

```bash
curl http://192.168.0.106/api/state
```

**Resultado:**
```json
{
  "bend_1_angle": 45.0,
  "bend_2_angle": 51.0,
  "bend_3_angle": 90.0,
  "encoder_angle": 11.9,
  "speed_class": 10,
  "connected": true
}
```

### Teste 2: Leitura dos Registros Shadow (32-bit)

| Registro | Endereço | Valor Lido | Observação |
|----------|----------|------------|------------|
| Dobra 1 Esq LSW | 0x0840 (2112) | null | ❌ CLP não retorna |
| Dobra 1 Esq MSW | 0x0842 (2114) | null | ❌ CLP não retorna |
| Dobra 1 Dir LSW | 0x0844 (2116) | 4 | ✅ Retorna dados |
| Dobra 1 Dir MSW | 0x0846 (2118) | 16 | ✅ Retorna dados |
| Dobra 2 Esq LSW | 0x0848 (2120) | null | ❌ CLP não retorna |
| Dobra 2 Esq MSW | 0x084A (2122) | null | ❌ CLP não retorna |
| Dobra 3 Esq MSW | 0x0852 (2130) | 48 | ✅ Retorna dados |
| Dobra 3 Dir LSW | 0x0854 (2132) | 48 | ✅ Retorna dados |

**Conversão 32-bit:**
- Dobra 1 Dir: (16 << 16) | 4 = 1048580 → 104858.0° (valor absurdo!)
- Outros: Dados incompletos (LSW ou MSW faltando)

**Conclusão:** Registros shadow têm dados mas estão incompletos ou com valores absurdos.

### Teste 3: Leitura dos Registros Setpoint 16-bit (0x0500)

| Registro | Endereço | Valor Lido | Graus | Status |
|----------|----------|------------|-------|--------|
| Dobra 1 | 0x0500 (1280) | 450 | 45.0° | ✅ Coincide com IHM! |
| Dobra 2 | 0x0502 (1282) | null | - | ❌ CLP não retorna |
| Dobra 3 | 0x0504 (1284) | 900 | 90.0° | ✅ Coincide com IHM! |

### Teste 4: Varredura Completa Área 0x0500-0x0520

Foram encontrados **18 registros com dados** na área 0x0500-0x0520:

| Endereço | Decimal | Valor | Graus | Observação |
|----------|---------|-------|-------|------------|
| **0x0500** | 1280 | 450 | **45.0°** | 🎯 **COINCIDE Dobra 1** |
| 0x0501 | 1281 | 49665 | 4966.5° | - |
| **0x0502** | 1282 | 510 | **51.0°** | 🎯 **COINCIDE Dobra 2** |
| 0x0503 | 1283 | 65027 | 6502.7° | - |
| **0x0504** | 1284 | 900 | **90.0°** | 🎯 **COINCIDE Dobra 3** |
| 0x0507 | 1287 | 12288 | 1228.8° | - |
| 0x0508-0x051E | ... | vários | vários | Outros setpoints/dados |

**Observação Crítica:**
- Em uma varredura, **0x0500 retornou 450**
- Em outra varredura (minutos depois), **0x0500 retornou null**
- Em uma terceira varredura, **0x0500 retornou 450 novamente**

**Hipótese:** Valores na área 0x0500 são **voláteis** e podem ser sobrescritos pelo ladder ou IHM.

---

## 📊 ANÁLISE DE COINCIDÊNCIAS

### Coincidência 1: Dobra 1 (45.0°)

```
IHM mostra:    45.0°
CLP 0x0500:    45.0° ✅ COINCIDE
Shadow 0x0840: null ❌ não disponível
```

**Status:** ✅ **COINCIDÊNCIA PERFEITA**

**Interpretação:**
- IHM está lendo registro 0x0500
- CLP tem o mesmo valor em 0x0500
- Pode ser:
  - (A) CLP populou 0x0500 com setpoint oficial
  - (B) IHM escreveu 45.0° em 0x0500 e está lendo de volta
  - (C) Ambos leem/escrevem na mesma área compartilhada

### Coincidência 2: Dobra 2 (51.0°)

```
IHM mostra:    51.0°
CLP 0x0502:    null ❌ não disponível
Shadow 0x0848: null ❌ não disponível
```

**Status:** ⚠️ **SEM COINCIDÊNCIA (CLP retorna null)**

**Interpretação:**
- IHM mostra 51.0° mas CLP não tem dado em 0x0502
- **Conclusão:** IHM está mostrando valor **local** (cache ESP32 ou último valor escrito)
- Este é o caso mais problemático pois **não há fonte de verdade no CLP**

**Nota:** Em teste anterior (varredura 0x0500-0x0520), 0x0502 retornou 510 (51.0°), mas em teste posterior retornou null. **Valor é instável!**

### Coincidência 3: Dobra 3 (90.0°)

```
IHM mostra:    90.0°
CLP 0x0504:    90.0° ✅ COINCIDE
Shadow 0x0850: null/parcial ❌
```

**Status:** ✅ **COINCIDÊNCIA PERFEITA**

**Interpretação:**
- IHM está lendo registro 0x0504
- CLP tem o mesmo valor em 0x0504
- Mesmo cenário da Dobra 1 (opções A, B ou C)

---

## 🔬 ANÁLISE PROFUNDA: DE ONDE VÊM OS DADOS?

### Hipótese 1: IHM Lê Setpoints que CLP Populou
**Evidência a favor:**
- Dobras 1 e 3 coincidem perfeitamente
- Registros 0x0500 e 0x0504 existem no CLP

**Evidência contra:**
- Dobra 2 (0x0502) retorna `null` mas IHM mostra 51.0°
- Valores são instáveis (ora existem, ora null)
- Área 0x0500 não é citada no ladder PRINCIPAL.lad

### Hipótese 2: IHM Escreve e Lê de Volta (Eco)
**Evidência a favor:**
- Dobra 2 mostra valor mesmo sem dado no CLP
- Valores instáveis sugerem escrita/leitura volátil
- Código `main.py` tem função `set_angle` que escreve em 0x0500-0x0504

**Evidência contra:**
- Quando há coincidência, valor persiste entre leituras
- Se fosse só eco, 0x0502 deveria sempre retornar valor

### Hipótese 3: Área Compartilhada (Ladder + IHM)
**Evidência a favor:**
- Área 0x0500 é oficial conforme manual MPC4004
- Ladder pode usar 0x0500 como cache de trabalho
- IHM escreve, ladder lê e processa

**Evidência contra:**
- Ladder PRINCIPAL.lad não referencia explicitamente 0x0500-0x0504
- Shadow registers (0x0840) parecem ser área de trabalho real

---

## 🎯 CONCLUSÃO FINAL

### Respondendo à Pergunta Original

> "Quero saber se existe coincidência entre os dados dos setpoints (oficiais) e os dados apresentados"

**Resposta:** ✅ **SIM, há coincidência PARCIAL (67%)**

**Detalhamento:**
| Dobra | IHM Mostra | CLP Retorna (0x0500-0x0504) | Coincide? | Confiabilidade |
|-------|------------|---------------------------|-----------|----------------|
| **Dobra 1** | 45.0° | 45.0° (0x0500) | ✅ SIM | 🟡 **Média** (valor instável) |
| **Dobra 2** | 51.0° | null (0x0502) | ❌ NÃO | 🔴 **Baixa** (sem fonte no CLP) |
| **Dobra 3** | 90.0° | 90.0° (0x0504) | ✅ SIM | 🟡 **Média** (valor instável) |

### Interpretação Geral

**O que está acontecendo:**

1. **Área 0x0500-0x0504** é uma área de **comunicação/cache** entre IHM e CLP
2. **Ladder oficial** usa registros **0x0840-0x0852** (shadow 32-bit)
3. **IHM Web** usa registros **0x0500-0x0504** (setpoints 16-bit)
4. Há **desconexão** entre área shadow (ladder) e setpoints (IHM)

**Possível fluxo:**
```
Usuario na IHM → Escreve 45° em 0x0500
                ↓
           CLP recebe escrita
                ↓
    Ladder processa (ou não)
                ↓
     Pode copiar para 0x0840 (shadow)
                ↓
          IHM relê 0x0500
                ↓
       Mostra 45° (coincide!)
```

**Problema:** Se ladder modificar shadow (0x0840) sem atualizar 0x0500, IHM não vê!

---

## ⚠️ RISCOS IDENTIFICADOS

### Risco 1: Instabilidade dos Valores (🔴 CRÍTICO)
- Valores em 0x0500-0x0504 são **instáveis**
- Ora retornam dados, ora `null`
- **Causa provável:** Escrita/leitura concorrente ladder vs IHM

### Risco 2: Desconexão Shadow vs Setpoint (🔴 CRÍTICO)
- Ladder usa 0x0840-0x0852 (shadow 32-bit)
- IHM usa 0x0500-0x0504 (setpoints 16-bit)
- **Não há garantia** de sincronização entre eles

### Risco 3: Dobra 2 Sem Fonte Confiável (🔴 CRÍTICO)
- IHM mostra 51.0° mas CLP retorna `null`
- **Operador pode confiar em valor inexistente!**

---

## ✅ RECOMENDAÇÕES

### Recomendação 1: Confirmar Estratégia do Ladder

**Ação:** Analisar ladder completo (ROT4, ROT5) para identificar:
- Se ladder escreve em 0x0500-0x0504
- Se há cópia automática shadow → setpoint
- Qual é a fonte de verdade oficial

### Recomendação 2: Adicionar Validação de Consistência

**Modificar `main.py`:**
```python
# Ler setpoint
setpoint = modbus.read_register(0x0500)

# Ler shadow também
shadow_lsw = modbus.read_register(0x0840)
shadow_msw = modbus.read_register(0x0842)

# Comparar
if setpoint != (shadow_32bit / 10):
    # ALERTA: Valores inconsistentes!
    machine_state['warning'] = 'INCONSISTENCIA'
```

### Recomendação 3: Teste Definitivo

**Procedimento:**
1. Escrever valor conhecido em 0x0500 (ex: 123.4°)
2. Aguardar 5 segundos
3. Ler 0x0500 novamente
4. Ler 0x0840/0x0842 (shadow)
5. Verificar se ladder copiou setpoint → shadow

**Se ladder copiar:** ✅ Área 0x0500 é confiável
**Se ladder não copiar:** ❌ Área 0x0500 é apenas cache local

---

## 📋 RESUMO EXECUTIVO

| Aspecto | Status | Confiabilidade |
|---------|--------|----------------|
| **Coincidências** | 2 de 3 (67%) | 🟡 Média |
| **Estabilidade** | Valores instáveis | 🔴 Baixa |
| **Fonte de verdade** | Não identificada | 🔴 Baixa |
| **Dobra 1** | Coincide | 🟡 Média |
| **Dobra 2** | Não coincide | 🔴 Baixa |
| **Dobra 3** | Coincide | 🟡 Média |

**Avaliação Geral:** ⚠️ **IHM está parcialmente funcional mas requer validação adicional**

---

## 🔗 PRÓXIMOS PASSOS

1. ⏳ **Aguardando decisão:** Executar teste definitivo (escrita + leitura)?
2. ⏳ **Aguardando decisão:** Analisar ROT4/ROT5 para mapear lógica completa?
3. ⏳ **Aguardando decisão:** Aceitar limitação atual ou corrigir código?

---

**Relatório gerado em:** 18/Nov/2025 06:15
**Método:** API ESP32 `/api/read_test` + Análise ladder
**Autor:** Claude Code
**Status:** ⚠️ **COINCIDÊNCIA PARCIAL CONFIRMADA - REQUER VALIDAÇÃO ADICIONAL**
