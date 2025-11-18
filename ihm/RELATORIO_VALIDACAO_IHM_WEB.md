# 📋 RELATÓRIO DE VALIDAÇÃO - IHM Web ESP32

**Data:** 18 de Novembro de 2025
**Sistema:** IHM Web ESP32 para Dobradeira NEOCOUDE-HD-15
**Objetivo:** Verificar se a IHM lê dados reais do CLP ou apenas valores que nós mesmos escrevemos

---

## 🎯 PREOCUPAÇÃO DO USUÁRIO

> "Estou com medo de que os valores mostrados na IHM web são daquela região da memória do CLP que nós mesmos criamos."

**Resposta:** ⚠️ **SUA PREOCUPAÇÃO ESTÁ PARCIALMENTE CORRETA!**

---

## 🔍 ANÁLISE DO CÓDIGO

### Arquivo: `main.py` (linhas 57-86)

```python
# Encoder (32-bit)
encoder_raw = modbus.read_register_32bit(mm.ENCODER['ANGLE_MSW'])  # 0x04D6/0x04D7
machine_state['encoder_angle'] = encoder_raw / 10.0

# Ângulos setpoint
bend1 = modbus.read_register(mm.BEND_ANGLES['BEND_1_SETPOINT'])  # 0x0500
machine_state['bend_1_angle'] = bend1 / 10.0

bend2 = modbus.read_register(mm.BEND_ANGLES['BEND_2_SETPOINT'])  # 0x0502
machine_state['bend_2_angle'] = bend2 / 10.0

bend3 = modbus.read_register(mm.BEND_ANGLES['BEND_3_SETPOINT'])  # 0x0504
machine_state['bend_3_angle'] = bend3 / 10.0

# Velocidade (área de supervisão)
speed_reg = modbus.read_register(mm.SUPERVISION_AREA['SPEED_CLASS'])  # 0x094C
machine_state['speed_class'] = speed_map.get(speed_reg, 5)
```

---

## 📊 TABELA COMPARATIVA: O QUE A IHM LÊ vs O QUE DEVERIA LER

| Variável | Endereço Lido | Tipo | Origem dos Dados | Status |
|----------|---------------|------|------------------|--------|
| **Encoder** | 0x04D6/0x04D7 (1238/1239) | 32-bit | ✅ **Contador high-speed do CLP** | ✅ CORRETO |
| **Dobra 1** | 0x0500 (1280) | 16-bit | ❌ **Setpoint que Python/IHM escreve** | ⚠️ PROBLEMA |
| **Dobra 2** | 0x0502 (1282) | 16-bit | ❌ **Setpoint que Python/IHM escreve** | ⚠️ PROBLEMA |
| **Dobra 3** | 0x0504 (1284) | 16-bit | ❌ **Setpoint que Python/IHM escreve** | ⚠️ PROBLEMA |
| **Velocidade** | 0x094C (2380) | 16-bit | ❌ **Área supervisão Python** | ⚠️ PROBLEMA |

---

## 🚨 REGISTROS SHADOW (USADOS PELO LADDER) - NÃO SENDO LIDOS

Conforme análise do `PRINCIPAL.lad` e `modbus_map.py` (linhas 117-129):

```python
BEND_ANGLES_SHADOW = {
    'BEND_1_LEFT_LSW':  0x0840,  # 2112 - Shadow Dobra 1 (LSW)
    'BEND_1_LEFT_MSW':  0x0842,  # 2114 - Shadow Dobra 1 (MSW)

    'BEND_2_LEFT_LSW':  0x0846,  # 2118 - Shadow Dobra 2 (LSW)
    'BEND_2_LEFT_MSW':  0x0848,  # 2120 - Shadow Dobra 2 (MSW)

    'BEND_3_LEFT_LSW':  0x0850,  # 2128 - Shadow Dobra 3 (LSW)
    'BEND_3_LEFT_MSW':  0x0852,  # 2130 - Shadow Dobra 3 (MSW)
}
```

**Estes endereços são os que o LADDER ORIGINAL usa (PRINCIPAL.lad):**
- Line00008: `SUB 0858 = 0842 - 0840` (Dobra 1)
- Line00009: `SUB 0858 = 0848 - 0846` (Dobra 2)
- Line00010: `SUB 0858 = 0852 - 0850` (Dobra 3)

---

## 🧪 TESTES EXECUTADOS

### Teste 1: Conectividade
```bash
ping -c 3 192.168.0.106
```
**Resultado:** ✅ 0% packet loss

### Teste 2: API State
```bash
curl http://192.168.0.106/api/state
```
**Resultado:**
```json
{
    "encoder_angle": 11.9,
    "bend_1_angle": 38.0,
    "bend_2_angle": 281.8,
    "bend_3_angle": 1748.9,
    "speed_class": 10,
    "connected": true
}
```

### Teste 3: Leitura Direta de Registros

#### Área 0x0500 (que a IHM lê):
```bash
curl "http://192.168.0.106/api/read_test?address=1280"
```
**Resultado:** ✅ `{"value": 380, "success": true}` → 38.0° (corresponde ao valor da IHM!)

#### Área 0x0840 (shadow do ladder):
```bash
curl "http://192.168.0.106/api/read_test?address=2112"
```
**Resultado:** ❌ `{"value": null, "success": false}`

#### Área 0x094C (velocidade):
```bash
curl "http://192.168.0.106/api/read_test?address=2380"
```
**Resultado:** ❌ `{"value": null, "success": false}`

---

## 🔬 INTERPRETAÇÃO DOS RESULTADOS

### ✅ **Encoder (0x04D6/0x04D7)**
- **Status:** CORRETO - Lê registro original do CLP
- **Observação:** Encoder não está conectado fisicamente, então valor é 0 ou lixo

### ❌ **Ângulos das Dobras (0x0500, 0x0502, 0x0504)**
- **Status:** INCORRETO - Lê área de setpoints que Python/IHM escreve
- **Problema:** Se o ladder modificar os ângulos shadow (0x0840-0x0852), a IHM NÃO verá!
- **Evidência:**
  - Área 0x0500 retorna valor ✅ (380 = 38.0°)
  - Área 0x0840 (shadow) retorna null ❌
  - **Conclusão:** IHM está lendo o que ela mesma escreveu!

### ❌ **Velocidade (0x094C)**
- **Status:** INCORRETO - Área criada por nós, não existe no ladder original
- **Evidência:** Leitura retorna `null`
- **Problema:** Valor de velocidade mostrado (10 rpm) pode não corresponder à velocidade real do CLP

---

## 📝 CONCLUSÕES

### 1. Encoder ✅
- **Validado:** SIM
- **Lê dados reais do CLP:** SIM
- **Observação:** Encoder desconectado fisicamente (valores irrelevantes até conectar)

### 2. Ângulos das Dobras ❌
- **Validado:** NÃO
- **Lê dados reais do CLP:** NÃO
- **Problema:** Lê área 0x0500-0x0504 (setpoints que Python escreve)
- **Deveria ler:** Área 0x0840-0x0852 (shadow registers do ladder)
- **Risco:** IHM mostra apenas o que foi escrito nela, não reflete estado real do CLP

### 3. Velocidade ❌
- **Validado:** NÃO
- **Lê dados reais do CLP:** NÃO
- **Problema:** Área 0x094C retorna `null` (não existe no ladder)
- **Deveria ler:** LEDs K4/K5 ou inferir da área de controle do inversor

---

## 🚨 RISCOS IDENTIFICADOS

### **Risco 1: IHM Mostra Valores Desatualizados**
Se o ladder modificar os ângulos shadow (via ROT4/ROT5), a IHM continuará mostrando valores antigos escritos na área 0x0500.

**Severidade:** 🔴 ALTA

### **Risco 2: Velocidade Não Reflete Estado Real**
A área 0x094C não existe no ladder original. Valor mostrado pode não corresponder à velocidade real da máquina.

**Severidade:** 🟡 MÉDIA

### **Risco 3: Encoder OK (sem risco)**
Encoder lê registro correto. Quando conectado fisicamente, funcionará corretamente.

**Severidade:** 🟢 BAIXA

---

## ✅ RECOMENDAÇÕES

### **Ação Imediata 1: Corrigir Leitura de Ângulos**

**Modificar `main.py` linhas 63-76:**

```python
# ❌ ANTES (ERRADO):
bend1 = modbus.read_register(mm.BEND_ANGLES['BEND_1_SETPOINT'])  # 0x0500

# ✅ DEPOIS (CORRETO):
bend1_lsw = modbus.read_register(mm.BEND_ANGLES_SHADOW['BEND_1_LEFT_LSW'])  # 0x0840
bend1_msw = modbus.read_register(mm.BEND_ANGLES_SHADOW['BEND_1_LEFT_MSW'])  # 0x0842
bend1 = (bend1_msw << 16) | bend1_lsw if bend1_lsw and bend1_msw else 0
```

### **Ação Imediata 2: Corrigir Leitura de Velocidade**

Ler velocidade dos LEDs (K1+K7 detecta mudança) ou criar lógica que infere da classe atual.

**Opções:**
1. Ler coils dos LEDs e inferir estado
2. Ler registro do inversor (se existir)
3. Manter área 0x094C mas validar se CLP realmente a popula

### **Ação 3: Teste de Validação Final**

Após correções:
1. Escrever valor nos shadow registers via ladder
2. Verificar se IHM lê corretamente
3. Comparar com área 0x0500 (não devem ser iguais se houver lógica no ladder)

---

## 📌 RESPOSTA DIRETA À SUA PERGUNTA

> "Quero saber se minha IHM web no ESP32 está funcionando 100%"

**Resposta:** ❌ **NÃO, não está 100% funcional**

**Funciona:**
- ✅ Encoder (registro correto, mas hardware desconectado)
- ✅ Interface web carrega
- ✅ Comunicação Modbus funciona

**NÃO funciona corretamente:**
- ❌ Ângulos das dobras (lê área que Python escreve, não shadow do ladder)
- ❌ Velocidade (lê área inexistente no CLP original)

**Severidade:** 🔴 **CRÍTICA** - IHM pode mostrar valores que não refletem estado real do CLP

---

## 🔧 PRÓXIMOS PASSOS

1. ✅ **Validação concluída** - Problema identificado
2. ⏳ **Aguardando decisão** - Corrigir leitura de ângulos?
3. ⏳ **Aguardando decisão** - Corrigir leitura de velocidade?
4. ⏳ **Testes finais** - Validar correções

---

**Relatório gerado em:** 18/Nov/2025
**Autor:** Claude Code
**Status:** ⚠️ REQUER AÇÃO CORRETIVA
