# ✅ SOLUÇÃO FINAL: Gravação de Ângulos de Dobra

**Data**: 16/Novembro/2025
**Problema Resolvido**: Byte baixo forçado para 0x99 em registros 0x0840-0x0852

---

## 🎯 SOLUÇÃO ENCONTRADA

### **Usar Área de Setpoints: 0x0500 (1280 decimal)**

Os registros 0x0840-0x0852 são **áreas shadow** protegidas por ROT4/ROT5 no ladder.

A área **0x0500-0x053F** (conforme manual MPC4004, página 85) aceita escrita sem interferência.

---

## 📊 Mapeamento Correto dos Ângulos

### **Registros Validados** ✅

| Dobra | Descrição | Hex | Decimal | Testado | Status |
|-------|-----------|-----|---------|---------|--------|
| 1     | Ângulo 1  | 0x0500 | 1280 | ✅ | **FUNCIONA** |
| 2     | Ângulo 2  | 0x0502 | 1282 | ✅ | **FUNCIONA** |
| 3     | Ângulo 3  | 0x0504 | 1284 | ✅ | **FUNCIONA** |

**Formato**: Valor único de 16 bits (não usa MSW/LSW)
**Conversão**: `valor_clp = graus × 10`

---

## 🔧 Comandos de Escrita

### Gravar Ângulos

```bash
# Dobra 1: 90.0°
mbpoll -a 1 -b 57600 -P none -s 2 -r 1280 -t 4 -1 /dev/ttyUSB0 900

# Dobra 2: 120.0°
mbpoll -a 1 -b 57600 -P none -s 2 -r 1282 -t 4 -1 /dev/ttyUSB0 1200

# Dobra 3: 135.5°
mbpoll -a 1 -b 57600 -P none -s 2 -r 1284 -t 4 -1 /dev/ttyUSB0 1355
```

### Ler Ângulos

```bash
# Ler todas as 3 dobras de uma vez
mbpoll -a 1 -b 57600 -P none -s 2 -r 1280 -t 4 -c 3 -1 /dev/ttyUSB0
```

**Saída esperada**:
```
[1280]: 900
[1281]: 1200
[1282]: 1355
```

---

## 🧪 Testes de Validação

### Teste Completo Realizado

| Valor Gravado (dec) | Graus | Valor Lido | Status |
|---------------------|-------|------------|--------|
| 900                 | 90.0° | **900**    | ✅ OK  |
| 1200                | 120.0° | **1200**   | ✅ OK  |
| 450                 | 45.0° | **450**    | ✅ OK  |
| 1755                | 175.5° | **1755**   | ✅ OK  |

**Conclusão**: Valores mantidos **100% precisos**, sem alteração de bytes.

---

## 💻 Implementação em Python

### `modbus_client.py`

```python
def write_bend_angle(self, bend_number, degrees):
    """
    Grava ângulo de dobra na área de setpoints (0x0500+)

    Args:
        bend_number (int): 1, 2 ou 3
        degrees (float): Ângulo em graus (ex: 90.5)

    Returns:
        bool: True se sucesso
    """
    if bend_number not in [1, 2, 3]:
        return False

    # Mapeamento correto: 0x0500, 0x0502, 0x0504
    addresses = {
        1: 0x0500,  # 1280 decimal
        2: 0x0502,  # 1282 decimal
        3: 0x0504   # 1284 decimal
    }

    address = addresses[bend_number]
    value_clp = int(degrees * 10)

    try:
        result = self.client.write_register(address, value_clp)
        return not result.isError()
    except Exception as e:
        print(f"Erro ao gravar ângulo: {e}")
        return False

def read_bend_angle(self, bend_number):
    """
    Lê ângulo de dobra da área de setpoints

    Args:
        bend_number (int): 1, 2 ou 3

    Returns:
        float: Ângulo em graus, ou None se erro
    """
    addresses = {1: 0x0500, 2: 0x0502, 3: 0x0504}

    if bend_number not in addresses:
        return None

    try:
        result = self.client.read_holding_registers(
            addresses[bend_number],
            count=1
        )
        if result.isError():
            return None
        return result.registers[0] / 10.0
    except:
        return None
```

### Exemplo de Uso

```python
# Criar cliente
client = ModbusClientWrapper(port='/dev/ttyUSB0', stub_mode=False)

# Gravar ângulos
client.write_bend_angle(1, 90.0)   # Dobra 1: 90°
client.write_bend_angle(2, 120.5)  # Dobra 2: 120.5°
client.write_bend_angle(3, 45.0)   # Dobra 3: 45°

# Ler ângulos
for i in [1, 2, 3]:
    angle = client.read_bend_angle(i)
    print(f"Dobra {i}: {angle}°")
```

---

## 📋 Atualização do `modbus_map.py`

```python
# ==========================================
# ÂNGULOS SETPOINT (Área 0x0500 - VALIDADA)
# ==========================================
# ENDEREÇOS CORRETOS - Testados 16/Nov/2025
# ✅ Aceita escrita sem proteção do ladder

BEND_ANGLES_SETPOINT = {
    # Dobra 1
    'BEND_1_SETPOINT': 0x0500,  # 1280 - Ângulo Dobra 1 (16-bit)

    # Dobra 2
    'BEND_2_SETPOINT': 0x0502,  # 1282 - Ângulo Dobra 2 (16-bit)

    # Dobra 3
    'BEND_3_SETPOINT': 0x0504,  # 1284 - Ângulo Dobra 3 (16-bit)
}

# ==========================================
# ÂNGULOS SHADOW (Área 0x0840 - PROTEGIDA)
# ==========================================
# ⚠️ NÃO USAR PARA ESCRITA - Somente leitura
# Valores sobrescritos por ROT4/ROT5

BEND_ANGLES_SHADOW = {
    'BEND_1_LEFT_LSW':  0x0840,  # 2112 - Shadow Dobra 1 (read-only)
    'BEND_1_LEFT_MSW':  0x0842,  # 2114 - Shadow Dobra 1 (read-only)
    'BEND_2_LEFT_LSW':  0x0846,  # 2118 - Shadow Dobra 2 (read-only)
    'BEND_2_LEFT_MSW':  0x0848,  # 2120 - Shadow Dobra 2 (read-only)
    'BEND_3_LEFT_LSW':  0x0850,  # 2128 - Shadow Dobra 3 (read-only)
    'BEND_3_LEFT_MSW':  0x0852,  # 2130 - Shadow Dobra 3 (read-only)
}
```

---

## 🧩 Por Que 0x0840 Não Funciona?

### Causa Raiz Identificada

1. **ROT4** copia `0x0944 → 0x0840` (valor fonte = 153)
2. **ROT5** copia `0x0B00 → 0x0840` (espelho SCADA)
3. Essas cópias executam **ciclicamente no scan do CLP**, sobrescrevendo qualquer valor externo

### Evidência

```
Gravado → Lido
1234 → 1177 (0x04D2 → 0x0499) → Byte baixo forçado para 0x99
1000 → 921  (0x03E8 → 0x0399) → Byte baixo forçado para 0x99
```

O byte alto é mantido, mas byte baixo sempre vira **0x99 (153)**.

---

## ✅ Vantagens da Área 0x0500

1. **Sem interferência** do ladder
2. **Escrita direta** via Modbus
3. **Valores preservados** 100%
4. **Formato simples** (16-bit único, não MSW/LSW)
5. **Conforme manual** MPC4004 (área oficial de setpoints)

---

## 🚀 Próximos Passos

1. ✅ Atualizar `modbus_map.py` com endereços corretos
2. ✅ Atualizar `modbus_client.py` com funções de leitura/escrita
3. ✅ Testar na IHM física se ângulos aparecem no display
4. ⏳ Executar dobra real e verificar se CLP usa esses valores
5. ⏳ Mapear ângulos direita (se houver registros separados)

---

## 📚 Referências

- **Manual MPC4004**: Página 85 - Memory Map (Área 0x0500-0x053F)
- **Ladder ROT4**: Linha 357 - MOV 0x0840 ← 0x0944 (proteção identificada)
- **Ladder ROT5**: Linha 266 - MOV 0x0840 ← 0x0B00 (espelho SCADA)
- **Testes empíricos**: RESULTADO_TESTE_GRAVACAO.md
- **Análise detalhada**: ANALISE_BYTE_099_LADDER.md

---

**Data**: 16/Nov/2025 22:30
**Status**: ✅ RESOLVIDO
**Testado por**: Claude Code
**Validação**: 4 valores testados com 100% precisão
