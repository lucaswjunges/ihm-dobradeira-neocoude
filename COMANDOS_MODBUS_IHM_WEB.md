# 📡 COMANDOS MODBUS - IHM WEB → CLP

## 🎯 ESPECIFICAÇÕES DE COMUNICAÇÃO

### Configuração Modbus RTU

```
Protocolo: Modbus RTU
Porta: /dev/ttyUSB0 ou /dev/ttyUSB1
Baudrate: 57600
Paridade: None
Data bits: 8
Stop bits: 2 ⚠️ CRÍTICO (testado: 1 stop bit retorna erro)
Slave ID: 1
Timeout: 200ms (mínimo 100ms)
```

### Funções Modbus Suportadas

| Função | Código | Nome | Uso |
|--------|--------|------|-----|
| **0x01** | 01 | Read Coil Status | Ler bits (estados) |
| **0x02** | 02 | Read Input Status | Ler entradas |
| **0x03** | 03 | Read Holding Registers | **Ler registros (usado para encoder, ângulos)** |
| **0x05** | 05 | Force Single Coil | **Escrever 1 bit (usado para teclas)** |
| **0x06** | 06 | Preset Single Register | **Escrever 1 registro (usado para ângulos)** |
| 0x0F | 15 | Force Multiple Coils | Escrever múltiplos bits |
| 0x10 | 16 | Preset Multiple Registers | Escrever múltiplos registros |

---

## 🔑 MAPEAMENTO DE MEMÓRIA

### Área de Estados (Coils/Bits) - 0x0000 a 0x03FF

Endereços em **HEXADECIMAL** (0-1023 decimal)

**Estrutura**: 1024 bits (estados internos)
**Acesso**: Função 0x01 (Read) ou 0x05 (Write Single) ou 0x0F (Write Multiple)

### Área de Registros - 0x0400 em diante

Endereços em **HEXADECIMAL** (1024+ decimal)

**Estrutura**: Registros de 16 bits cada
**Acesso**: Função 0x03 (Read) ou 0x06 (Write Single) ou 0x10 (Write Multiple)

---

## 📝 COMANDOS PARA ENVIAR - TECLAS

### Protocolo de Acionamento de Tecla

**IMPORTANTE**: Cada tecla deve ser enviada como PULSO:

1. **Escrever bit = ON** (0xFF00)
2. **Aguardar 100ms**
3. **Escrever bit = OFF** (0x0000)

### Função Modbus: 0x05 (Force Single Coil)

**Formato do comando**:
```
[Slave ID][0x05][Endereço High][Endereço Low][Valor High][Valor Low][CRC Low][CRC High]
```

**Valores**:
- ON: `0xFF 0x00` (forçar coil ON)
- OFF: `0x00 0x00` (forçar coil OFF)

---

### Tabela de Teclas (Endereços em DECIMAL)

| Tecla | Hex | **Dec** | Descrição | Código Modbus (ON) | Código Modbus (OFF) |
|-------|-----|---------|-----------|-------------------|---------------------|
| **K1** | 00A0 | **160** | Número 1 / Tela 4 | `01 05 00 A0 FF 00 [CRC]` | `01 05 00 A0 00 00 [CRC]` |
| **K2** | 00A1 | **161** | Número 2 / Tela 5 | `01 05 00 A1 FF 00 [CRC]` | `01 05 00 A1 00 00 [CRC]` |
| **K3** | 00A2 | **162** | Número 3 / Tela 6 | `01 05 00 A2 FF 00 [CRC]` | `01 05 00 A2 00 00 [CRC]` |
| **K4** | 00A3 | **163** | Número 4 / Esq | `01 05 00 A3 FF 00 [CRC]` | `01 05 00 A3 00 00 [CRC]` |
| **K5** | 00A4 | **164** | Número 5 / Dir | `01 05 00 A4 FF 00 [CRC]` | `01 05 00 A4 00 00 [CRC]` |
| **K6** | 00A5 | **165** | Número 6 | `01 05 00 A5 FF 00 [CRC]` | `01 05 00 A5 00 00 [CRC]` |
| **K7** | 00A6 | **166** | Número 7 / Vel | `01 05 00 A6 FF 00 [CRC]` | `01 05 00 A6 00 00 [CRC]` |
| **K8** | 00A7 | **167** | Número 8 | `01 05 00 A7 FF 00 [CRC]` | `01 05 00 A7 00 00 [CRC]` |
| **K9** | 00A8 | **168** | Número 9 | `01 05 00 A8 FF 00 [CRC]` | `01 05 00 A8 00 00 [CRC]` |
| **K0** | 00A9 | **169** | Número 0 | `01 05 00 A9 FF 00 [CRC]` | `01 05 00 A9 00 00 [CRC]` |
| **↑** | 00AC | **172** | Seta CIMA | `01 05 00 AC FF 00 [CRC]` | `01 05 00 AC 00 00 [CRC]` |
| **↓** | 00AD | **173** | Seta BAIXO | `01 05 00 AD FF 00 [CRC]` | `01 05 00 AD 00 00 [CRC]` |
| **ESC** | 00BC | **188** | Cancelar | `01 05 00 BC FF 00 [CRC]` | `01 05 00 BC 00 00 [CRC]` |
| **ENTER** | 0025 | **37** | Confirmar | `01 05 00 25 FF 00 [CRC]` | `01 05 00 25 00 00 [CRC]` |
| **EDIT** | 0026 | **38** | Modo edição | `01 05 00 26 FF 00 [CRC]` | `01 05 00 26 00 00 [CRC]` |
| **S1** | 00DC | **220** | Tecla S1 | `01 05 00 DC FF 00 [CRC]` | `01 05 00 DC 00 00 [CRC]` |
| **S2** | 00DD | **221** | Tecla S2 | `01 05 00 DD FF 00 [CRC]` | `01 05 00 DD 00 00 [CRC]` |
| **LOCK** | 00F1 | **241** | Travar teclado | `01 05 00 F1 FF 00 [CRC]` | `01 05 00 F1 00 00 [CRC]` |

---

### Exemplo Python - Enviar Tecla K1

```python
import time
from pymodbus.client import ModbusSerialClient

# Configurar cliente
client = ModbusSerialClient(
    port='/dev/ttyUSB0',
    baudrate=57600,
    parity='N',
    stopbits=2,  # CRÍTICO!
    bytesize=8,
    timeout=0.2
)

def press_key(address):
    """
    Simula pressionar uma tecla com pulso ON/OFF

    Args:
        address: Endereço decimal da tecla (ex: 160 para K1)
    """
    # ON - Força coil para TRUE (0xFF00)
    client.write_coil(address, True, slave=1)

    # Aguardar 100ms
    time.sleep(0.1)

    # OFF - Força coil para FALSE (0x0000)
    client.write_coil(address, False, slave=1)

# Exemplo: Pressionar K1
press_key(160)  # K1

# Exemplo: Pressionar S1
press_key(220)  # S1

# Exemplo: Pressionar ENTER
press_key(37)   # ENTER
```

---

## 📊 COMANDOS PARA LEITURA - REGISTROS

### Função Modbus: 0x03 (Read Holding Registers)

**Formato do comando**:
```
[Slave ID][0x03][Endereço High][Endereço Low][Qtd High][Qtd Low][CRC Low][CRC High]
```

### Tabela de Leitura

| Dado | Registros (Hex) | **Registros (Dec)** | Qtd | Tipo | Descrição |
|------|-----------------|---------------------|-----|------|-----------|
| **Encoder** | 04D6/04D7 | **1238/1239** | 2 | 32-bit | Posição angular atual |
| **Ângulo 1 (AJ)** | 0842/0840 | **2114/2112** | 2 | 32-bit | Setpoint ângulo 1 |
| **Ângulo 2 (AJ)** | 0848/0846 | **2120/2118** | 2 | 32-bit | Setpoint ângulo 2 |
| **Ângulo 3 (AJ)** | 0852/0850 | **2130/2128** | 2 | 32-bit | Setpoint ângulo 3 |
| **Velocidade** | 06E0 | **1760** | 1 | 16-bit | Saída analógica (RPM) |
| **Classe Vel** | 0900 | **2304** | 1 | 16-bit | Classe atual (1/2/3) |
| **Entrada E0** | 0100 | **256** | 1 | 16-bit | Bit 0 = status E0 |
| **Entrada E1** | 0101 | **257** | 1 | 16-bit | Bit 0 = status E1 |
| **Entrada E2** | 0102 | **258** | 1 | 16-bit | Bit 0 = status E2 |
| **Entrada E3** | 0103 | **259** | 1 | 16-bit | Bit 0 = status E3 |
| **Entrada E4** | 0104 | **260** | 1 | 16-bit | Bit 0 = status E4 |
| **Entrada E5** | 0105 | **261** | 1 | 16-bit | Bit 0 = status E5 |
| **Entrada E6** | 0106 | **262** | 1 | 16-bit | Bit 0 = status E6 |
| **Entrada E7** | 0107 | **263** | 1 | 16-bit | Bit 0 = status E7 |
| **Saída S0** | 0180 | **384** | 1 | 16-bit | Bit 0 = status S0 |
| **Saída S1** | 0181 | **385** | 1 | 16-bit | Bit 0 = status S1 |
| **Saída S2** | 0182 | **386** | 1 | 16-bit | Bit 0 = status S2 |
| **Saída S3** | 0183 | **387** | 1 | 16-bit | Bit 0 = status S3 |
| **Saída S4** | 0184 | **388** | 1 | 16-bit | Bit 0 = status S4 |
| **Saída S5** | 0185 | **389** | 1 | 16-bit | Bit 0 = status S5 |
| **Saída S6** | 0186 | **390** | 1 | 16-bit | Bit 0 = status S6 |
| **Saída S7** | 0187 | **391** | 1 | 16-bit | Bit 0 = status S7 |

---

### Formato 32-bit (MSW/LSW)

**IMPORTANTE**: Valores de 32 bits usam 2 registros consecutivos:

```
Registro PAR (MSW) = Most Significant Word (bits 31-16)
Registro ÍMPAR (LSW) = Least Significant Word (bits 15-0)
```

**Exemplo - Encoder em 90°**:
```
Registro 1238 (MSW) = 0x0000 = 0
Registro 1239 (LSW) = 0x005A = 90

Valor final = (0x0000 << 16) | 0x005A = 90
```

**Exemplo - Ângulo em 180°**:
```
Registro 2114 (MSW) = 0x0000 = 0
Registro 2112 (LSW) = 0x00B4 = 180

Valor final = (0x0000 << 16) | 0x00B4 = 180
```

---

### Exemplo Python - Ler Encoder (32-bit)

```python
def read_encoder():
    """
    Lê o encoder (registros 1238/1239) como valor 32-bit

    Returns:
        int: Valor do encoder em graus (0-360+)
    """
    # Ler 2 registros consecutivos começando em 1238
    result = client.read_holding_registers(1238, 2, slave=1)

    if result.isError():
        return None

    # Extrair MSW e LSW
    msw = result.registers[0]  # Registro 1238
    lsw = result.registers[1]  # Registro 1239

    # Combinar em 32-bit
    encoder_value = (msw << 16) | lsw

    return encoder_value

# Uso
encoder = read_encoder()
print(f"Encoder: {encoder}°")
```

---

### Exemplo Python - Ler Entrada Digital E0

```python
def read_input_e0():
    """
    Lê o status da entrada digital E0

    Returns:
        bool: True se ativada, False se desativada
    """
    # Ler registro 256 (entrada E0)
    result = client.read_holding_registers(256, 1, slave=1)

    if result.isError():
        return None

    # Bit 0 contém o status (LSB)
    status = bool(result.registers[0] & 0x0001)

    return status

# Uso
e0_status = read_input_e0()
print(f"Entrada E0: {'ATIVA' if e0_status else 'INATIVA'}")
```

---

## ✍️ COMANDOS PARA ESCRITA - REGISTROS

### Função Modbus: 0x06 (Preset Single Register)

**Formato do comando**:
```
[Slave ID][0x06][Endereço High][Endereço Low][Valor High][Valor Low][CRC Low][CRC High]
```

### Tabela de Escrita

| Dado | Registros (Hex) | **Registros (Dec)** | Tipo | Faixa | Descrição |
|------|-----------------|---------------------|------|-------|-----------|
| **Ângulo 1 MSW** | 0842 | **2114** | 16-bit | 0-65535 | Parte alta do ângulo 1 |
| **Ângulo 1 LSW** | 0840 | **2112** | 16-bit | 0-65535 | Parte baixa do ângulo 1 |
| **Ângulo 2 MSW** | 0848 | **2120** | 16-bit | 0-65535 | Parte alta do ângulo 2 |
| **Ângulo 2 LSW** | 0846 | **2118** | 16-bit | 0-65535 | Parte baixa do ângulo 2 |
| **Ângulo 3 MSW** | 0852 | **2130** | 16-bit | 0-65535 | Parte alta do ângulo 3 |
| **Ângulo 3 LSW** | 0850 | **2128** | 16-bit | 0-65535 | Parte baixa do ângulo 3 |

**IMPORTANTE**: Para valores até 360°, MSW sempre será 0x0000.

---

### Exemplo Python - Escrever Ângulo 1 = 90°

```python
def write_angle_1(angle_degrees):
    """
    Escreve o ângulo 1 (setpoint AJ)

    Args:
        angle_degrees: Ângulo em graus (0-360)

    Returns:
        bool: True se sucesso, False se erro
    """
    # Validar
    if angle_degrees < 0 or angle_degrees > 360:
        print("Ângulo fora da faixa (0-360)!")
        return False

    # Converter para 32-bit
    msw = (angle_degrees >> 16) & 0xFFFF  # Sempre 0 para valores até 360
    lsw = angle_degrees & 0xFFFF

    # Escrever MSW (registro 2114)
    result_msw = client.write_register(2114, msw, slave=1)
    if result_msw.isError():
        print("Erro ao escrever MSW!")
        return False

    # Escrever LSW (registro 2112)
    result_lsw = client.write_register(2112, lsw, slave=1)
    if result_lsw.isError():
        print("Erro ao escrever LSW!")
        return False

    print(f"Ângulo 1 escrito: {angle_degrees}°")
    return True

# Exemplo: Escrever 90°
write_angle_1(90)

# Exemplo: Escrever 120°
write_angle_1(120)

# Exemplo: Escrever 45°
write_angle_1(45)
```

---

### Exemplo Python - Escrever Ângulo 2 = 120°

```python
def write_angle_2(angle_degrees):
    """Escreve ângulo 2"""
    if angle_degrees < 0 or angle_degrees > 360:
        return False

    msw = (angle_degrees >> 16) & 0xFFFF
    lsw = angle_degrees & 0xFFFF

    # Registros 2120 (MSW) e 2118 (LSW)
    client.write_register(2120, msw, slave=1)
    client.write_register(2118, lsw, slave=1)

    return True
```

---

### Exemplo Python - Escrever Ângulo 3 = 45°

```python
def write_angle_3(angle_degrees):
    """Escreve ângulo 3"""
    if angle_degrees < 0 or angle_degrees > 360:
        return False

    msw = (angle_degrees >> 16) & 0xFFFF
    lsw = angle_degrees & 0xFFFF

    # Registros 2130 (MSW) e 2128 (LSW)
    client.write_register(2130, msw, slave=1)
    client.write_register(2128, lsw, slave=1)

    return True
```

---

## 🔄 POLLING - LEITURA PERIÓDICA

### Dados a Ler a Cada 250ms

```python
import asyncio

async def poll_clp_data():
    """Polling periódico de dados do CLP"""
    while True:
        # 1. Ler encoder (32-bit, 2 registros)
        encoder = read_encoder()

        # 2. Ler ângulos (opcional, para confirmar valores escritos)
        angle1 = read_angle_1()
        angle2 = read_angle_2()
        angle3 = read_angle_3()

        # 3. Ler entradas digitais E0-E7
        inputs = []
        for i in range(8):
            reg_addr = 256 + i  # E0=256, E1=257, ..., E7=263
            result = client.read_holding_registers(reg_addr, 1, slave=1)
            if not result.isError():
                inputs.append(bool(result.registers[0] & 0x0001))
            else:
                inputs.append(False)

        # 4. Ler saídas digitais S0-S7
        outputs = []
        for i in range(8):
            reg_addr = 384 + i  # S0=384, S1=385, ..., S7=391
            result = client.read_holding_registers(reg_addr, 1, slave=1)
            if not result.isError():
                outputs.append(bool(result.registers[0] & 0x0001))
            else:
                outputs.append(False)

        # 5. Ler classe de velocidade
        result_vel = client.read_holding_registers(2304, 1, slave=1)
        velocidade_classe = result_vel.registers[0] if not result_vel.isError() else 0

        # Enviar dados ao frontend via WebSocket
        data = {
            'encoder': encoder,
            'angle1': angle1,
            'angle2': angle2,
            'angle3': angle3,
            'inputs': inputs,
            'outputs': outputs,
            'velocidade_classe': velocidade_classe
        }

        await broadcast_to_clients(data)

        # Aguardar 250ms
        await asyncio.sleep(0.25)
```

---

## 🎮 FUNÇÕES ESPECIAIS DESCOBERTAS NO LADDER

### 1. Mudança de Velocidade (K1 + K7 simultâneo)

**Observado em ROT2.lad**:

| Classe | Valor em 06E0 (Dec) | Valor em 06E0 (Hex) | RPM |
|--------|---------------------|---------------------|-----|
| 1 | 527 | 0x020F | 5 RPM |
| 2 | 1583 | 0x062F | 10 RPM |
| 3 | 1055 | 0x041F | 15 RPM |

**NOTA**: Esta função é gerenciada pelo LADDER, NÃO pela IHM diretamente!

A IHM apenas envia:
1. Pulso em K1 (160)
2. Pulso em K7 (166)
3. Ladder detecta combinação e muda velocidade

**NÃO escrever diretamente em 06E0** - deixar ladder controlar!

---

### 2. Alternância AUTO/MANUAL (S1 na Tela 2)

**Observado em ROT1.lad linha 129**:

- Bit `00DC` (S1) é lido pelo ladder
- Ladder gerencia mudança de modo
- Bit `02FF` indica modo ativo

**IHM deve apenas**:
- Enviar pulso em S1 (220)
- Ler status do modo via bits do CLP (se disponível)

**NÃO tentar controlar modo diretamente** - ladder gerencia!

---

### 3. Reset Encoder (S2 na Tela 3)

**Observado em ROT1.lad linhas 47-48, 79-80**:

- Bit `00DD` (S2) é lido pelo ladder
- Ladder executa reset do encoder

**IHM deve apenas**:
- Enviar pulso em S2 (221)
- Ladder reseta registros 04D6/04D7 para zero

---

## ⚠️ REGRAS CRÍTICAS

### 1. SEMPRE Usar 2 Stop Bits

```python
# CORRETO
client = ModbusSerialClient(..., stopbits=2)

# INCORRETO - Vai dar erro "Illegal Function"
client = ModbusSerialClient(..., stopbits=1)
```

### 2. Teclas Sempre com Pulso ON/OFF

```python
# CORRETO
client.write_coil(160, True, slave=1)   # ON
time.sleep(0.1)
client.write_coil(160, False, slave=1)  # OFF

# INCORRETO - Tecla vai ficar "presa"
client.write_coil(160, True, slave=1)   # ON
# Sem OFF!
```

### 3. Valores 32-bit = 2 Registros

```python
# CORRETO - Escrever MSW e LSW
client.write_register(2114, msw, slave=1)  # Ângulo 1 MSW
client.write_register(2112, lsw, slave=1)  # Ângulo 1 LSW

# INCORRETO - Escrever só 1 registro
client.write_register(2112, angle, slave=1)  # Incompleto!
```

### 4. Validar Valores Antes de Escrever

```python
# CORRETO
if 0 <= angle <= 360:
    write_angle_1(angle)
else:
    print("Ângulo fora da faixa!")

# INCORRETO - Escrever sem validar
write_angle_1(999)  # Vai causar comportamento inesperado!
```

### 5. Tratar Erros Modbus

```python
# CORRETO
result = client.read_holding_registers(1238, 2, slave=1)
if result.isError():
    print("Erro Modbus!")
    return None
encoder = (result.registers[0] << 16) | result.registers[1]

# INCORRETO - Não verificar erro
result = client.read_holding_registers(1238, 2, slave=1)
encoder = result.registers[0]  # Pode crashar se erro!
```

---

## 📋 RESUMO DE ENDEREÇOS (Decimal)

### Teclas (Coils - Função 0x05)
- K1=160, K2=161, K3=162, K4=163, K5=164, K6=165, K7=166, K8=167, K9=168, K0=169
- S1=220, S2=221
- ↑=172, ↓=173
- ENTER=37, ESC=188, EDIT=38, LOCK=241

### Ângulos (Registros 32-bit - Função 0x06)
- Ângulo 1: MSW=2114, LSW=2112
- Ângulo 2: MSW=2120, LSW=2118
- Ângulo 3: MSW=2130, LSW=2128

### Encoder (Registro 32-bit - Função 0x03)
- Encoder: MSW=1238, LSW=1239

### I/Os (Registros 16-bit - Função 0x03)
- Entradas: E0=256, E1=257, E2=258, E3=259, E4=260, E5=261, E6=262, E7=263
- Saídas: S0=384, S1=385, S2=386, S3=387, S4=388, S5=389, S6=390, S7=391

### Velocidade (Registros 16-bit)
- Saída analógica: 1760 (RO - só leitura, ladder controla)
- Classe atual: 2304 (RO - só leitura, ladder controla)

---

## 🚀 PRÓXIMO PASSO

Com este documento, a implementação ficará:

1. **Backend**: Usa os endereços e funções Modbus exatos documentados aqui
2. **Frontend**: Chama backend via WebSocket com ações de alto nível
3. **CLP**: Recebe comandos Modbus exatamente como IHM Expert enviava

**Data**: 09/11/2025
**Status**: Especificação completa e pronta para implementação
**Testado**: Comunicação Modbus RTU com 2 stop bits funcionando
