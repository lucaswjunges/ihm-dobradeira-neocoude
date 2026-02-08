# DESCOBERTA CRÍTICA - ÂNGULOS DOBRADOS
## Data: 02 de Janeiro de 2026

---

## 🔍 DESCOBERTA

Durante teste ao lado da máquina dobradeira, descobrimos que:

### **Para dobrar vergalhão em 90°, a MÁQUINA GIRA 180°!**

Ou seja, os ângulos são gravados **DOBRADOS** no CLP.

---

## 📊 CONVERSÕES

### ESCRITA (IHM → CLP)

Quando o usuário digita o ângulo **REAL** da dobra:

1. **Usuário digita**: 90° (ângulo real do vergalhão)
2. **Converter para máquina**: 90° × 2 = **180°** (ângulo que a máquina gira)
3. **Converter para pulsos**: (180° / 360°) × 400 = **200 pulsos**
4. **Gravar no CLP**: 200 pulsos (DECIMAL) no endereço 2560, 2562 ou 2564

### LEITURA (CLP → IHM)

Quando o sistema lê ângulos do CLP:

1. **CLP retorna**: 200 pulsos (DECIMAL, nunca A/B/F)
2. **Converter para graus máquina**: (200 / 400) × 360 = **180°**
3. **Converter para ângulo real**: 180° ÷ 2 = **90°**
4. **Mostrar ao usuário**: "Dobra 1: 90°"

---

## 🔢 ENCODER E ENDEREÇOS - TUDO DECIMAL

### Encoder
- **Range**: 0 a 400 (DECIMAL)
- **Nunca mostra**: A, B, C, D, E, F (não é hexadecimal!)
- **Endereço**: 1238 (0x04D6)
- **Formato**: 16-bit (1 registro apenas)

### Endereços de Ângulos (DECIMAL)

**LEITURA** (onde o ladder armazena):
- Dobra 1: **2114** (0x0842)
- Dobra 2: **2116** (0x0844)
- Dobra 3: **2118** (0x0846)

**ESCRITA** (onde a IHM grava):
- Dobra 1: **2560** (0x0A00)
- Dobra 2: **2562** (0x0A02)
- Dobra 3: **2564** (0x0A04)

---

## 📋 TABELA DE REFERÊNCIA

| Ângulo Real | Ângulo Máquina | Pulsos CLP | Uso Típico |
|-------------|---------------|-----------|------------|
| 22.5°       | 45°           | 50        | Dobra mínima |
| 45°         | 90°           | 100       | Dobra pequena |
| 90°         | 180°          | 200       | Dobra padrão (esquadro) |
| 120°        | 240°          | 267       | Dobra comum |
| 135°        | 270°          | 300       | Dobra grande |
| 179.5°      | 359°          | 398-399   | **LIMITE MÁXIMO** |

⚠️ **ATENÇÃO**: 180° real = 360° máquina = 0 pulsos (volta completa). Limite prático é **179.5°**.

---

## ✅ VALIDAÇÃO

Executado `test_angle_conversion.py`:

```
✅ OK  Original:   45.0° → Pulsos: 100 → Lido:   45.0° (erro: 0.000°)
✅ OK  Original:   90.0° → Pulsos: 200 → Lido:   90.0° (erro: 0.000°)
✅ OK  Original:  135.0° → Pulsos: 300 → Lido:  135.0° (erro: 0.000°)
✅ OK  Original:  179.5° → Pulsos: 398 → Lido:  179.1° (erro: 0.400°)

✅ TODAS AS CONVERSÕES VALIDADAS COM SUCESSO!
```

---

## 🛠️ IMPLEMENTAÇÃO

### Funções Criadas em `modbus_map.py`:

1. **`real_angle_to_machine(degrees)`**
   - Entrada: ângulo real (ex: 90.0)
   - Saída: pulsos para gravar no CLP (ex: 200)
   - Usa multiplicação por 2

2. **`machine_angle_to_real(pulses)`**
   - Entrada: pulsos lidos do CLP (ex: 200)
   - Saída: ângulo real (ex: 90.0)
   - Usa divisão por 2

3. **`clp_to_degrees(pulses)`** *(NÃO alterada)*
   - Converte pulsos → graus da máquina (SEM divisão por 2)
   - Usada apenas para leitura do encoder em tempo real

4. **`degrees_to_clp(degrees)`** *(NÃO alterada)*
   - Converte graus da máquina → pulsos (SEM multiplicação por 2)
   - Função auxiliar, usar `real_angle_to_machine()` para dobras

### Arquivos Atualizados:

- ✅ `modbus_map.py` - Funções de conversão + documentação
- ✅ `modbus_client.py` - `write_bend_angle()` e `read_bend_angle()`
- ✅ `state_manager.py` - `read_angles()` aplica conversão
- ✅ `test_angle_conversion.py` - Teste de validação

---

## 📌 LOGS DEVEM SER EM DECIMAL

Todos os logs devem mostrar valores em **DECIMAL**, não hexadecimal:

**❌ ERRADO:**
```
Gravando Dobra 1: 90.0° → 0xC8 pulsos → 0x0A00
```

**✅ CORRETO:**
```
Gravando Dobra 1: 90.0° real → 180.0° máquina → 200 pulsos → endereço 2560
```

---

## 🎯 EXEMPLO DE USO

### Gravar ângulo via Python:

```python
# Usuário quer dobrar vergalhão em 90°
client.write_bend_angle(1, 90.0)

# Log:
# ✎ Gravando Dobra 1: 90.0° real → 180.0° máquina → 200 pulsos → endereço 2560
# ✓ Dobra 1 gravada: 90.0° real = 180.0° máquina = 200 pulsos
```

### Ler ângulo via Python:

```python
# Ler ângulo programado
angle = client.read_bend_angle(1)
print(f"Dobra 1: {angle}°")

# Log:
# 📖 Lendo Dobra 1 de endereço 2114: 200 pulsos → 180.0° máquina → 90.0° real
# Dobra 1: 90.0°
```

### Ler encoder em tempo real:

```python
# Encoder mostra posição da máquina (não precisa dividir por 2)
pulses = client.read_register(1238)  # Endereço 04D6
degrees = mm.clp_to_degrees(pulses)
print(f"Encoder: {pulses} pulsos = {degrees:.1f}° (máquina)")

# Saída:
# Encoder: 157 pulsos = 141.3° (máquina)
```

---

## ⚠️ IMPORTANTE

1. **Encoder mostra posição da MÁQUINA**, não o ângulo real da dobra
   - Se encoder = 180°, a máquina girou 180°
   - O vergalhão foi dobrado em 90° (180° ÷ 2)

2. **Ângulos programados são REAIS** (após conversão)
   - Usuário vê e digita ângulos reais
   - Sistema converte automaticamente

3. **Limite máximo**: 179.5° real (359° máquina, 399 pulsos)
   - Não usar 180° real (seria 360° máquina = 0 pulsos)

4. **Encoder NUNCA mostra letras** (A, B, C, D, E, F)
   - Range: 0-400 pulsos (DECIMAL)
   - Logs devem mostrar valores decimais

---

## 📚 REFERÊNCIAS

- Teste de validação: `test_angle_conversion.py`
- Funções de conversão: `modbus_map.py:486-551`
- Cliente Modbus: `modbus_client.py:762-899`
- Gerenciador de estado: `state_manager.py:360-418`

---

**Descoberto por**: Lucas William Junges
**Local**: Ao lado da máquina dobradeira NEOCOUDE-HD-15
**Data**: 02 de Janeiro de 2026
**Status**: ✅ VALIDADO E IMPLEMENTADO
