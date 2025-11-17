# ⚡ Guia Rápido de Referência

**IHM Web Dobradeira NEOCOUDE-HD-15**
**Última atualização**: 16/Nov/2025

---

## 🎯 Comandos Mais Usados

### Ângulos de Dobra (0x0500-0x0504)

```bash
# GRAVAR Dobra 1: 90°
mbpoll -a 1 -b 57600 -P none -s 2 -r 1280 -t 4 -1 /dev/ttyUSB0 900

# GRAVAR Dobra 2: 120°
mbpoll -a 1 -b 57600 -P none -s 2 -r 1282 -t 4 -1 /dev/ttyUSB0 1200

# GRAVAR Dobra 3: 45°
mbpoll -a 1 -b 57600 -P none -s 2 -r 1284 -t 4 -1 /dev/ttyUSB0 450

# LER todas as 3 dobras
mbpoll -a 1 -b 57600 -P none -s 2 -r 1280 -t 4 -c 3 -1 /dev/ttyUSB0
```

### Velocidade (0x094C)

```bash
# GRAVAR 5 rpm
mbpoll -a 1 -b 57600 -P none -s 2 -r 2380 -t 4 -1 /dev/ttyUSB0 5

# GRAVAR 10 rpm
mbpoll -a 1 -b 57600 -P none -s 2 -r 2380 -t 4 -1 /dev/ttyUSB0 10

# GRAVAR 15 rpm
mbpoll -a 1 -b 57600 -P none -s 2 -r 2380 -t 4 -1 /dev/ttyUSB0 15

# LER velocidade atual
mbpoll -a 1 -b 57600 -P none -s 2 -r 2380 -t 4 -c 1 -1 /dev/ttyUSB0
```

### Encoder (0x04D6/0x04D7)

```bash
# LER posição angular (32-bit)
mbpoll -a 1 -b 57600 -P none -s 2 -r 1238 -t 4 -c 2 -1 /dev/ttyUSB0
# Resultado: [MSW] [LSW] → converter: (MSW << 16 | LSW) / 10
```

### Botões (Pulso 100ms)

```bash
# PRESSIONAR K1
mbpoll -a 1 -b 57600 -P none -s 2 -r 160 -t 0 -1 /dev/ttyUSB0 1
sleep 0.1
mbpoll -a 1 -b 57600 -P none -s 2 -r 160 -t 0 -1 /dev/ttyUSB0 0

# PRESSIONAR S1 (AUTO/MANUAL)
mbpoll -a 1 -b 57600 -P none -s 2 -r 220 -t 0 -1 /dev/ttyUSB0 1
sleep 0.1
mbpoll -a 1 -b 57600 -P none -s 2 -r 220 -t 0 -1 /dev/ttyUSB0 0
```

### I/O Digital

```bash
# LER entradas E0-E7
mbpoll -a 1 -b 57600 -P none -s 2 -r 256 -t 0 -c 8 -1 /dev/ttyUSB0

# LER saídas S0-S7
mbpoll -a 1 -b 57600 -P none -s 2 -r 384 -t 0 -c 8 -1 /dev/ttyUSB0

# LER LEDs 1-5
mbpoll -a 1 -b 57600 -P none -s 2 -r 192 -t 0 -c 5 -1 /dev/ttyUSB0
```

---

## 🐍 Python Rápido

### Ângulos

```python
from modbus_client import ModbusClientWrapper

client = ModbusClientWrapper(port='/dev/ttyUSB0')

# Gravar
client.write_bend_angle(1, 90.0)   # Dobra 1: 90°
client.write_bend_angle(2, 120.0)  # Dobra 2: 120°
client.write_bend_angle(3, 45.5)   # Dobra 3: 45.5°

# Ler
angle1 = client.read_bend_angle(1)
print(f"Dobra 1: {angle1}°")

# Ler todas
angles = client.read_all_bend_angles()
print(angles)  # {'bend_1': 90.0, 'bend_2': 120.0, 'bend_3': 45.5}
```

### Velocidade

```python
# Gravar
client.write_speed_class(5)    # 5 rpm
client.write_speed_class(10)   # 10 rpm
client.write_speed_class(15)   # 15 rpm

# Ler
speed = client.read_speed_class()
print(f"Velocidade: {speed} rpm")
```

### Encoder

```python
import modbus_map as mm

value = client.read_32bit(
    mm.ENCODER['ANGLE_MSW'],
    mm.ENCODER['ANGLE_LSW']
)
degrees = value / 10.0
print(f"Posição: {degrees}°")
```

---

## 📊 Tabela de Endereços

| Funcionalidade | Hex | Decimal | Tipo | R/W |
|----------------|-----|---------|------|-----|
| **Encoder MSW** | 0x04D6 | 1238 | 16-bit | R |
| **Encoder LSW** | 0x04D7 | 1239 | 16-bit | R |
| **Ângulo Dobra 1** | 0x0500 | 1280 | 16-bit | R/W |
| **Ângulo Dobra 2** | 0x0502 | 1282 | 16-bit | R/W |
| **Ângulo Dobra 3** | 0x0504 | 1284 | 16-bit | R/W |
| **Velocidade** | 0x094C | 2380 | 16-bit | R/W |
| **K0** | 0x00A9 | 169 | Coil | W |
| **K1** | 0x00A0 | 160 | Coil | W |
| **K2** | 0x00A1 | 161 | Coil | W |
| **K3** | 0x00A2 | 162 | Coil | W |
| **K4** | 0x00A3 | 163 | Coil | W |
| **K5** | 0x00A4 | 164 | Coil | W |
| **K6** | 0x00A5 | 165 | Coil | W |
| **K7** | 0x00A6 | 166 | Coil | W |
| **K8** | 0x00A7 | 167 | Coil | W |
| **K9** | 0x00A8 | 168 | Coil | W |
| **S1** | 0x00DC | 220 | Coil | W |
| **S2** | 0x00DD | 221 | Coil | W |
| **ENTER** | 0x0025 | 37 | Coil | W |
| **ESC** | 0x00BC | 188 | Coil | W |
| **EDIT** | 0x0026 | 38 | Coil | W |
| **LED1** | 0x00C0 | 192 | Coil | R |
| **LED2** | 0x00C1 | 193 | Coil | R |
| **LED3** | 0x00C2 | 194 | Coil | R |
| **LED4** | 0x00C3 | 195 | Coil | R |
| **LED5** | 0x00C4 | 196 | Coil | R |
| **E0-E7** | 0x0100-0x0107 | 256-263 | Coil | R |
| **S0-S7** | 0x0180-0x0187 | 384-391 | Coil | R |

---

## 🔄 Conversões

### Ângulos
```
Graus → CLP: valor_clp = graus × 10
CLP → Graus: graus = valor_clp ÷ 10

Exemplo:
90.0° → 900 (CLP)
135.5° → 1355 (CLP)
```

### Encoder (32-bit)
```
MSW + LSW → Valor:
value = (MSW << 16) | LSW

Valor → Graus:
graus = value / 10.0

Exemplo:
MSW=0, LSW=457 → 457 → 45.7°
MSW=1, LSW=2450 → 68018 → 6801.8°
```

---

## ⚠️ ATENÇÃO

### ❌ NÃO ESCREVER
- 0x0840-0x0852 (ângulos shadow - protegidos)
- 0x04D6/0x04D7 (encoder - read-only)
- 0x0100-0x0107 (entradas - read-only)
- 0x00C0-0x00C4 (LEDs - read-only)

### ✅ SEGURO ESCREVER
- 0x0500-0x0504 (ângulos setpoint)
- 0x094C (velocidade)
- 0x00A0-0x00DD (botões - pulso 100ms)

---

## 🧪 Testes Rápidos

### Menu Interativo
```bash
cd /home/lucas-junges/Documents/clientes/w\&co/ihm
./test_write_complete_mbpoll.sh
```

### Teste Python
```bash
# Ângulos
python3 test_new_angles.py

# Velocidade
python3 test_speed_rpm.py
```

---

## 🛠️ Troubleshooting

### Não conecta
```bash
# Verificar porta
ls -l /dev/ttyUSB*

# Testar
mbpoll -a 1 -b 57600 -P none -s 2 -r 190 -t 0 -c 1 /dev/ttyUSB0
```

### Timeout
```bash
# Adicionar timeout maior
mbpoll ... -T 2.00 ...  # 2 segundos
```

### Valores não gravam
- ✅ Usar 0x0500 para ângulos (NÃO 0x0840)
- ✅ Usar 0x094C para velocidade (NÃO K1+K7)

---

## 📖 Documentação Completa

- **CLAUDE.md** - Guia completo
- **INDEX.md** - Índice de todos os arquivos
- **RESUMO_VALIDACOES_16NOV2025.md** - Todas as validações

---

**Versão**: 2.0 - 16/Nov/2025
**Status**: ✅ 100% Validado
