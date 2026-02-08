# DESCOBERTA CRÍTICA - ESCALA 2048 (12 BITS)
## Data: 02 de Janeiro de 2026

---

## 🔍 DESCOBERTA

Durante teste ao lado da máquina dobradeira, descobrimos que:

### **O CLP armazena ângulos em escala de 2048 (12 bits)**

- **90° na IHM Web** → **0x0200 (512 decimal)** no CLP
- **45° na IHM Web** → **0x0100 (256 decimal)** no CLP

---

## 📊 CONVERSÕES

### Fórmula Principal:

```
valor_clp = (graus / 360) × 2048
graus = (valor_clp / 2048) × 360
```

### ESCRITA (IHM → CLP)

Quando o usuário digita o ângulo:

1. **Usuário digita**: 90° (ângulo desejado)
2. **Converter para escala CLP**: (90 / 360) × 2048 = **512**
3. **Gravar no CLP**: 512 decimal no endereço 2560, 2562 ou 2564
4. **No CLP aparece**: 0x0200 (512 em hexa) ✓

### LEITURA (CLP → IHM)

Quando o sistema lê ângulos do CLP:

1. **CLP retorna**: 512 (0x0200 em hexa)
2. **Converter para graus**: (512 / 2048) × 360 = **90°**
3. **Mostrar ao usuário**: "Dobra 1: 90°"

---

## 🔢 TABELA DE REFERÊNCIA

| Ângulo | Valor CLP (dec) | Valor CLP (hexa) | Uso Típico |
|--------|----------------|------------------|------------|
| 22.5°  | 128            | 0x0080           | Dobra mínima |
| 45°    | **256**        | **0x0100**       | Dobra pequena |
| 90°    | **512**        | **0x0200**       | Dobra padrão (esquadro) |
| 120°   | 683            | 0x02AB           | Dobra comum |
| 135°   | 768            | 0x0300           | Dobra grande |
| 180°   | 1024           | 0x0400           | Meia volta |
| 270°   | 1536           | 0x0600           | 3/4 de volta |
| 360°   | 2048           | 0x0800           | Volta completa |

---

## 📍 ENDEREÇOS

### Ângulos Programados (DECIMAL)

**LEITURA** (onde o ladder armazena):
- Dobra 1: **2114** (0x0842)
- Dobra 2: **2116** (0x0844)
- Dobra 3: **2118** (0x0846)

**ESCRITA** (onde a IHM grava):
- Dobra 1: **2560** (0x0A00)
- Dobra 2: **2562** (0x0A02)
- Dobra 3: **2564** (0x0A04)

### Encoder (SEPARADO!)

- **Endereço**: 1238 (0x04D6)
- **Range**: 0-400 pulsos (DECIMAL)
- **Conversão**: (pulsos / 400) × 360 = graus
- **Uso**: Posição em tempo real da máquina

⚠️ **IMPORTANTE**: Encoder usa escala **400**, ângulos programados usam escala **2048**!

---

## ✅ VALIDAÇÃO

Executado `test_angle_conversion.py`:

```
✅ OK  Original:   45.0° → CLP:  256 (0x0100) → Lido:   45.0°
✅ OK  Original:   90.0° → CLP:  512 (0x0200) → Lido:   90.0°
✅ OK  Original:  135.0° → CLP:  768 (0x0300) → Lido:  135.0°
✅ OK  Original:  180.0° → CLP: 1024 (0x0400) → Lido:  180.0°

✅ TODAS AS CONVERSÕES VALIDADAS COM SUCESSO!
```

---

## 🛠️ IMPLEMENTAÇÃO

### Funções Criadas em `modbus_map.py`:

1. **`real_angle_to_clp(degrees)`**
   - Entrada: ângulo real (ex: 90.0)
   - Saída: valor CLP (ex: 512)
   - Fórmula: `(graus / 360) × 2048`

2. **`clp_to_real_angle(clp_value)`**
   - Entrada: valor lido do CLP (ex: 512)
   - Saída: ângulo real (ex: 90.0)
   - Fórmula: `(valor / 2048) × 360`

3. **`clp_to_degrees(pulses)`** *(para encoder)*
   - Converte pulsos do encoder → graus
   - Escala: 400 pulsos/volta
   - Fórmula: `(pulsos / 400) × 360`

4. **`degrees_to_clp(degrees)`** *(para encoder)*
   - Converte graus → pulsos do encoder
   - Escala: 400 pulsos/volta
   - Fórmula: `(graus / 360) × 400`

### Arquivos Atualizados:

- ✅ `modbus_map.py` - Funções `real_angle_to_clp()` e `clp_to_real_angle()`
- ✅ `modbus_client.py` - `write_bend_angle()` e `read_bend_angle()`
- ✅ `state_manager.py` - `read_angles()` aplica conversão correta
- ✅ `test_angle_conversion.py` - Teste de validação

---

## 📌 LOGS EM DECIMAL E HEXA

Os logs mostram **ambos** formatos para clareza:

```
✎ Gravando Dobra 1: 90.0° → valor 512 (0x0200) → endereço 2560
  ✓ Dobra 1 gravada: 90.0° = 512 (0x0200)

📖 Lendo Dobra 1 de endereço 2114: 512 (0x0200) → 90.0°
```

---

## 🎯 EXEMPLO DE USO

### Gravar ângulo via Python:

```python
# Usuário quer dobrar em 90°
client.write_bend_angle(1, 90.0)

# Log:
# ✎ Gravando Dobra 1: 90.0° → valor 512 (0x0200) → endereço 2560
# ✓ Dobra 1 gravada: 90.0° = 512 (0x0200)
```

### Ler ângulo via Python:

```python
# Ler ângulo programado
angle = client.read_bend_angle(1)
print(f"Dobra 1: {angle}°")

# Log:
# 📖 Lendo Dobra 1 de endereço 2114: 512 (0x0200) → 90.0°
# Dobra 1: 90.0°
```

### Ler encoder em tempo real:

```python
# Encoder usa escala DIFERENTE (400 pulsos/volta)
pulses = client.read_register(1238)  # Endereço 04D6
degrees = mm.clp_to_degrees(pulses)  # Conversão: (pulsos/400) × 360
print(f"Encoder: {pulses} pulsos = {degrees:.1f}°")

# Saída:
# Encoder: 157 pulsos = 141.3°
```

---

## ⚠️ IMPORTANTE

1. **Ângulos programados**: Escala **2048** (12 bits)
   - 90° = 512 (0x0200)
   - Endereços: 2114, 2116, 2118

2. **Encoder (posição)**: Escala **400** (pulsos/volta)
   - 90° = 100 pulsos
   - Endereço: 1238

3. **NÃO confundir as duas escalas!**
   - Ângulos programados: `real_angle_to_clp()` / `clp_to_real_angle()`
   - Encoder em tempo real: `degrees_to_clp()` / `clp_to_degrees()`

4. **Fórmulas corretas**:
   - Ângulos: `valor = (graus / 360) × 2048`
   - Encoder: `pulsos = (graus / 360) × 400`

---

## 📚 REFERÊNCIAS

- Teste de validação: `test_angle_conversion.py`
- Funções de conversão: `modbus_map.py:486-553`
- Cliente Modbus: `modbus_client.py:762-894`
- Gerenciador de estado: `state_manager.py:360-421`

---

**Descoberto por**: Lucas William Junges
**Local**: Ao lado da máquina dobradeira NEOCOUDE-HD-15
**Data**: 02 de Janeiro de 2026
**Status**: ✅ VALIDADO E IMPLEMENTADO

**Observação**: Valor visto no CLP em hexa (0x0200) = 512 em decimal
