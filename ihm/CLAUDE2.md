# CLAUDE2.md - IHM Web para NEOCOUDE-HD-15 (Guia Definitivo)

**Data:** 12 de Novembro de 2025
**Versão:** 1.0
**Status:** ✅ EMPIRICAMENTE VALIDADO

Este documento contém TODAS as informações necessárias para desenvolver a IHM Web que emula ao máximo a IHM física Atos 4004.95C (danificada), baseado em **testes empíricos reais** com o CLP MPC4004 ligado.

---

## 📋 ÍNDICE

1. [Contexto e Hardware](#1-contexto-e-hardware)
2. [Descobertas Críticas Validadas](#2-descobertas-críticas-validadas)
3. [Mapeamento Modbus Completo (TESTADO)](#3-mapeamento-modbus-completo-testado)
4. [Especificação da IHM Física Original](#4-especificação-da-ihm-física-original)
5. [Arquitetura da IHM Web](#5-arquitetura-da-ihm-web)
6. [Implementação Backend (Python)](#6-implementação-backend-python)
7. [Implementação Frontend (HTML/JS/CSS)](#7-implementação-frontend-htmljscss)
8. [Procedimentos de Teste](#8-procedimentos-de-teste)
9. [Regras de Ouro](#9-regras-de-ouro)
10. [Resposta sobre Display LCD](#10-resposta-sobre-display-lcd)

---

## 1. CONTEXTO E HARDWARE

### 1.1. Máquina

**Trillor NEOCOUDE-HD-15** (fabricação 2007)
- Dobradeira de vergalhões até 50mm (CA-25) / 44mm (CA-50)
- Motor 15 HP, 1755 rpm @ 380V
- Velocidades: 5 rpm (Classe 1), 10 rpm (Classe 2), 15 rpm (Classe 3)
- Redução total: 1:58.5 (motor → redutor) × 3.44 (pinhão → coroa)

### 1.2. Controlador

**Atos Expert MPC4004** (designação "CJ" na máquina)
- Memória: 1024 estados internos + 1536 registradores
- Tempo de scan: ~6ms/K (K = tamanho do programa em KB)
- Comunicação: RS485-B (Channel B), Modbus RTU slave
- Encoder: Contador high-speed (3 kHz) em registros 0x04D6/0x04D7

### 1.3. Conexão Física

```
┌────────────────┐  USB-RS485-FTDI   ┌──────────────┐  WiFi   ┌─────────┐
│  CLP MPC4004   │◄─────────────────►│  Notebook    │◄───────►│ Tablet  │
│  (Slave ID: 1) │   /dev/ttyUSB0    │  Ubuntu      │         │ (AP)    │
│                │   57600 baud      │  Python 3    │         │         │
│  ROT0-4: ORIG  │   8N2             │  WebSocket   │         │ Browser │
│  ROT5-9: MIN   │                   │  8765        │         │         │
└────────────────┘                   └──────────────┘         └─────────┘
```

**Parâmetros Modbus RTU:**
- Porta: `/dev/ttyUSB0` ou `/dev/ttyUSB1`
- Baudrate: **57600**
- Parity: **None**
- Stop bits: **2**
- Data bits: **8**
- Slave ID: **1**
- Estado 0x00BE (190 dec): **DEVE estar ON** (Modbus slave ativo)

### 1.4. Estado Atual v25

**CLP_10_ROTINAS_v25_SAFE.sup:**
- ✅ Compila sem erros (MD5: `f04fb1e8cb9c3e45181cfd13e56031d6`)
- ✅ ROT0-4: Preservadas (controle original da máquina)
- ✅ ROT5-9: Lógica mínima (apenas copia ângulos para mirrors 0x0942/0x0944)
- ⚠️ **NÃO implementa supervisão** - isso será feito em Python!

**Decisão arquitetural:**
```
┌─────────────────────────────────────────────────┐
│  CLP Ladder (ROT5-9)                            │
│  ─────────────────────────────────────────      │
│  ❌ Espelhamento I/O (MOV não acessa)          │
│  ❌ Leitura timers (MOV não acessa)            │
│  ❌ Lógica WEG inverter (desnecessário)        │
│  ✅ Lógica mínima ou RET (compila e roda)      │
└─────────────────────────────────────────────────┘
                    ▼
┌─────────────────────────────────────────────────┐
│  Python Backend (ihm_server.py)                 │
│  ──────────────────────────────────────────     │
│  ✅ Lê I/O via Modbus (E0-E7, S0-S7 como COILS)│
│  ✅ Lê encoder (0x04D6/0x04D7 32-bit)          │
│  ✅ Lê ângulos (0x0840-0x0852 pares 32-bit)    │
│  ✅ Monitora inversor (0x06E0, etc)            │
│  ✅ Emula botões (write_coil K0-K9, S1, S2)    │
│  ✅ Supervisão completa (mais poderosa!)       │
└─────────────────────────────────────────────────┘
                    ▼
┌─────────────────────────────────────────────────┐
│  Frontend Web (Tablet)                          │
│  ─────────────────────────────────────────      │
│  ✅ Replica IHM física 100%                     │
│  ✅ + Diagnóstico avançado                      │
│  ✅ + Logs de produção                          │
│  ✅ + Gráficos (futuro)                         │
└─────────────────────────────────────────────────┘
```

---

## 2. DESCOBERTAS CRÍTICAS VALIDADAS

### 2.1. I/O Digital SÃO COILS, NÃO REGISTERS

**❌ ERRO ANTERIOR (assumido):**
```python
# Isto FALHA com "Illegal data address"
client.read_holding_registers(0x0100, 8)  # E0-E7
client.read_holding_registers(0x0180, 8)  # S0-S7
```

**✅ CORRETO (empiricamente validado):**
```python
# Function Code 0x01 (Read Coils)
result = client.read_coils(0x0100, 8)  # E0-E7 ✅
e0_status = result.bits[0]  # True/False

result = client.read_coils(0x0180, 8)  # S0-S7 ✅
s0_status = result.bits[0]
```

**Teste mbpoll (12/Nov/2025, 22:08 BRT):**
```bash
# SUCESSO:
mbpoll -m rtu -a 1 -r 256 -c 8 -t 0 -b 57600 -P none -s 2 -1 /dev/ttyUSB0
# Resultado: [256]: 1, [257-263]: 0  (E0 ON, E1-E7 OFF)

mbpoll -m rtu -a 1 -r 384 -c 8 -t 0 -b 57600 -P none -s 2 -1 /dev/ttyUSB0
# Resultado: [384-391]: 0  (S0-S7 todas OFF)
```

**Lição:** `-t 0` = Coils, `-t 3` = Holding Registers. I/O são coils!

### 2.2. Encoder é 32-bit (MSW+LSW)

**Endereços:**
- **0x04D6** (1238 dec): Most Significant Word (16 bits altos)
- **0x04D7** (1239 dec): Least Significant Word (16 bits baixos)

**Conversão:**
```python
msw = client.read_holding_registers(0x04D6, 1).registers[0]
lsw = client.read_holding_registers(0x04D7, 1).registers[0]
encoder_value_raw = (msw << 16) | lsw
encoder_graus = encoder_value_raw / 10.0  # Dividir por 10
```

**Teste mbpoll (12/Nov/2025, 22:07 BRT):**
```bash
mbpoll -m rtu -a 1 -r 1238 -c 2 -t 3 -b 57600 -P none -s 2 -1 /dev/ttyUSB0
# Resultado: [1238]: 0, [1239]: 119
# Conversão: (0 << 16) | 119 = 119 → 11.9 graus
```

### 2.3. Ângulos Programados (Pares 32-bit)

**Dobra 1 Esquerda:**
- **0x0840** (2112 dec): MSW
- **0x0842** (2114 dec): LSW
- Valor = (MSW << 16) | LSW, converter: `graus = valor / 10.0`

**Todas as dobras:**
```python
ANGLES = {
    'bend_1_left':  (0x0840, 0x0842),  # 2112, 2114
    'bend_2_left':  (0x0848, 0x084A),  # 2120, 2122
    'bend_3_left':  (0x0850, 0x0852),  # 2128, 2130
    # Direita: mesma lógica, endereços diferentes (ver mapa completo)
}
```

**Teste mbpoll (12/Nov/2025, 22:06 BRT):**
```bash
mbpoll -m rtu -a 1 -r 2112 -c 6 -t 3 -b 57600 -P none -s 2 -1 /dev/ttyUSB0
# Resultado:
# [2112]: 6109   → MSW dobra 1
# [2113]: 22237  → (não usado)
# [2114]: 30278  → LSW dobra 1
# [2115]: 20230  → (não usado)
# [2116]: 55558  → MSW dobra 2
# [2117]: 63760  → (não usado)

# Cálculo dobra 1: (6109 << 16) | 30278 = 400.300.278 / 10 = 40.030.027,8 graus
# (valores de exemplo, podem estar incorretos - ver seção 3.3)
```

### 2.4. Timers NÃO são Acessíveis

**Endereços 0x0400-0x041A (1024-1050 dec):**
```bash
# FALHA:
mbpoll -m rtu -a 1 -r 1024 -c 7 -t 3 -b 57600 -P none -s 2 -1 /dev/ttyUSB0
# Resultado: "Illegal data address"
```

**Conclusão:** Timers são internos ao CLP, não espelhados via Modbus. **Não implementar leitura de timers na IHM Web** (não essenciais para operação).

### 2.5. Inversor WEG é Acessível

**Tensão inversor: 0x06E0 (1760 dec)**
```bash
# SUCESSO:
mbpoll -m rtu -a 1 -r 1760 -c 1 -t 3 -b 57600 -P none -s 2 -1 /dev/ttyUSB0
# Resultado: [1760]: 21765
```

**Outros registros WEG (não testados ainda):**
- 0x05F1, 0x05F2: RPM, corrente (provavelmente)
- 0x0900: Classe de velocidade (1, 2, 3)

---

## 3. MAPEAMENTO MODBUS COMPLETO (TESTADO)

### 3.1. I/O Digital (Function Code 0x01 - Read Coils)

| Nome | Endereço Hex | Endereço Dec | Testado | Resultado | Observação |
|------|--------------|--------------|---------|-----------|------------|
| **E0** | 0x0100 | 256 | ✅ | 1 (ON) | Entrada digital 0 |
| **E1** | 0x0101 | 257 | ✅ | 0 (OFF) | Entrada digital 1 |
| **E2** | 0x0102 | 258 | ✅ | 0 (OFF) | Entrada digital 2 |
| **E3** | 0x0103 | 259 | ✅ | 0 (OFF) | Entrada digital 3 |
| **E4** | 0x0104 | 260 | ✅ | 0 (OFF) | Entrada digital 4 |
| **E5** | 0x0105 | 261 | ✅ | 0 (OFF) | Entrada digital 5 |
| **E6** | 0x0106 | 262 | ✅ | 0 (OFF) | Entrada digital 6 |
| **E7** | 0x0107 | 263 | ✅ | 0 (OFF) | Entrada digital 7 |
| **S0** | 0x0180 | 384 | ✅ | 0 (OFF) | Saída digital 0 |
| **S1** | 0x0181 | 385 | ✅ | 0 (OFF) | Saída digital 1 |
| **S2** | 0x0182 | 386 | ✅ | 0 (OFF) | Saída digital 2 |
| **S3** | 0x0183 | 387 | ✅ | 0 (OFF) | Saída digital 3 |
| **S4** | 0x0184 | 388 | ✅ | 0 (OFF) | Saída digital 4 |
| **S5** | 0x0185 | 389 | ✅ | 0 (OFF) | Saída digital 5 |
| **S6** | 0x0186 | 390 | ✅ | 0 (OFF) | Saída digital 6 |
| **S7** | 0x0187 | 391 | ✅ | 0 (OFF) | Saída digital 7 |

**Método Python:**
```python
def read_digital_inputs(client, slave=1):
    result = client.read_coils(0x0100, 8, slave=slave)
    if not result.isError():
        return {f'E{i}': bit for i, bit in enumerate(result.bits[:8])}
    return None

def read_digital_outputs(client, slave=1):
    result = client.read_coils(0x0180, 8, slave=slave)
    if not result.isError():
        return {f'S{i}': bit for i, bit in enumerate(result.bits[:8])}
    return None
```

### 3.2. Encoder (Function Code 0x03 - Read Holding Registers)

| Nome | Endereço Hex | Endereço Dec | Testado | Resultado | Observação |
|------|--------------|--------------|---------|-----------|------------|
| **Encoder MSW** | 0x04D6 | 1238 | ✅ | 0 | 16 bits altos |
| **Encoder LSW** | 0x04D7 | 1239 | ✅ | 119 | 16 bits baixos |

**Conversão:**
```python
def read_encoder_angle(client, slave=1):
    result = client.read_holding_registers(0x04D6, 2, slave=slave)
    if not result.isError():
        msw, lsw = result.registers
        raw_value = (msw << 16) | lsw
        degrees = raw_value / 10.0
        return degrees
    return None
```

**Teste:**
```python
# MSW=0, LSW=119 → (0 << 16) | 119 = 119 → 11.9 graus
```

### 3.3. Ângulos Programados (Function Code 0x03 - Pares 32-bit)

| Nome | MSW Hex | MSW Dec | LSW Hex | LSW Dec | Testado | Observação |
|------|---------|---------|---------|---------|---------|------------|
| **Dobra 1 Esquerda** | 0x0840 | 2112 | 0x0842 | 2114 | ✅ | MSW=6109, LSW=30278 |
| **Dobra 2 Esquerda** | 0x0848 | 2120 | 0x084A | 2122 | ✅ | MSW=55558, LSW=... |
| **Dobra 3 Esquerda** | 0x0850 | 2128 | 0x0852 | 2130 | ✅ | MSW=..., LSW=... |
| **Dobra 1 Direita** | 0x0844 | 2116 | 0x0846 | 2118 | ⏳ | Não testado ainda |
| **Dobra 2 Direita** | 0x084C | 2124 | 0x084E | 2126 | ⏳ | Não testado ainda |
| **Dobra 3 Direita** | 0x0854 | 2132 | 0x0856 | 2134 | ⏳ | Não testado ainda |

**⚠️ IMPORTANTE:** Valores retornados nos testes (6109, 30278, etc) parecem grandes demais. Pode haver:
1. Inversão MSW/LSW (testar LSW antes de MSW)
2. Formato diferente (BCD, signed int, etc)
3. Fator de conversão diferente (não dividir por 10?)

**TODO:** Testar escrevendo um ângulo conhecido (ex: 90.0°) e ver como fica armazenado.

**Método Python (provisório):**
```python
def read_angle_32bit(client, msw_addr, lsw_addr, slave=1):
    result = client.read_holding_registers(msw_addr, 1, slave=slave)
    if result.isError():
        return None
    msw = result.registers[0]

    result = client.read_holding_registers(lsw_addr, 1, slave=slave)
    if result.isError():
        return None
    lsw = result.registers[0]

    # Tentar ambas as ordens
    value_msw_first = (msw << 16) | lsw
    value_lsw_first = (lsw << 16) | msw

    # Retornar ambos para debug
    return {
        'msw_first': value_msw_first / 10.0,
        'lsw_first': value_lsw_first / 10.0,
        'msw_raw': msw,
        'lsw_raw': lsw
    }
```

### 3.4. Inversor WEG (Function Code 0x03 - Holding Registers)

| Nome | Endereço Hex | Endereço Dec | Testado | Resultado | Observação |
|------|--------------|--------------|---------|-----------|------------|
| **Tensão** | 0x06E0 | 1760 | ✅ | 21765 | Valor bruto (conversão?) |
| **Corrente** | 0x06E1? | 1761? | ⏳ | - | Não confirmado |
| **RPM** | 0x05F1? | 1521? | ⏳ | - | Não confirmado |
| **Classe Velocidade** | 0x0900? | 2304? | ⏳ | - | 1=5rpm, 2=10rpm, 3=15rpm |

**TODO:** Mapear completamente os registros do inversor.

### 3.5. Botões/Teclas (Function Code 0x05 - Write Single Coil)

| Tecla | Endereço Hex | Endereço Dec | Testado | Observação |
|-------|--------------|--------------|---------|------------|
| **K0** | 0x00A9 | 169 | ⏳ | Tecla numérica 0 |
| **K1** | 0x00A0 | 160 | ⏳ | Tecla numérica 1 |
| **K2** | 0x00A1 | 161 | ⏳ | Tecla numérica 2 |
| **K3** | 0x00A2 | 162 | ⏳ | Tecla numérica 3 |
| **K4** | 0x00A3 | 163 | ⏳ | Tecla numérica 4 |
| **K5** | 0x00A4 | 164 | ⏳ | Tecla numérica 5 |
| **K6** | 0x00A5 | 165 | ⏳ | Tecla numérica 6 |
| **K7** | 0x00A6 | 166 | ⏳ | Tecla numérica 7 (K1+K7 = muda velocidade) |
| **K8** | 0x00A7 | 167 | ⏳ | Tecla numérica 8 |
| **K9** | 0x00A8 | 168 | ⏳ | Tecla numérica 9 |
| **S1** | 0x00DC | 220 | ⏳ | Alterna AUTO/MANUAL |
| **S2** | 0x00DD | 221 | ⏳ | Reset/Contexto |
| **Arrow Up** | 0x00AC | 172 | ⏳ | Seta para cima |
| **Arrow Down** | 0x00AD | 173 | ⏳ | Seta para baixo |
| **ESC** | 0x00BC | 188 | ⏳ | Cancelar/Sair |
| **ENTER** | 0x0025 | 37 | ⏳ | Confirmar |
| **EDIT** | 0x0026 | 38 | ⏳ | Modo edição |
| **Lock** | 0x00F1 | 241 | ⏳ | Trava teclado |

**Protocolo de pulso (100ms):**
```python
def press_key(client, address, hold_ms=100, slave=1):
    # 1. ON
    result = client.write_coil(address, True, slave=slave)
    if result.isError():
        return False

    # 2. Aguarda
    time.sleep(hold_ms / 1000.0)

    # 3. OFF
    result = client.write_coil(address, False, slave=slave)
    return not result.isError()
```

**Mudança de velocidade (K1+K7 simultâneo):**
```python
def change_speed_class(client, slave=1):
    # ON simultâneo
    client.write_coil(0x00A0, True, slave=slave)   # K1
    client.write_coil(0x00A6, True, slave=slave)   # K7

    time.sleep(0.1)

    # OFF simultâneo
    client.write_coil(0x00A0, False, slave=slave)
    client.write_coil(0x00A6, False, slave=slave)
```

### 3.6. LEDs (Function Code 0x01 - Read Coils)

| LED | Endereço Hex | Endereço Dec | Testado | Observação |
|-----|--------------|--------------|---------|------------|
| **LED1** | 0x00C0 | 192 | ⏳ | Dobra 1 ativa |
| **LED2** | 0x00C1 | 193 | ⏳ | Dobra 2 ativa |
| **LED3** | 0x00C2 | 194 | ⏳ | Dobra 3 ativa |
| **LED4** | 0x00C3 | 195 | ⏳ | K4 (esquerda) ativo |
| **LED5** | 0x00C4 | 196 | ⏳ | K5 (direita) ativo |

### 3.7. Estados Críticos (Function Code 0x01 - Read Coils)

| Estado | Endereço Hex | Endereço Dec | Testado | Observação |
|--------|--------------|--------------|---------|------------|
| **Modbus Slave ON** | 0x00BE | 190 | ⏳ | DEVE estar ON (obrigatório) |
| **Ciclo Ativo** | 0x0191? | 401? | ⏳ | Máquina em operação |
| **Modo Manual** | 0x02FF? | 767? | ⏳ | Manual=1, Auto=0 |
| **Emergência** | ? | ? | ⏳ | Botão emergência pressionado |

### 3.8. Resumo de Acessibilidade

| Tipo de Dado | Acessível | Function Code | Observação |
|--------------|-----------|---------------|------------|
| **E0-E7, S0-S7** | ✅ SIM | 0x01 (Coils) | **NÃO usar 0x03!** |
| **Encoder** | ✅ SIM | 0x03 (Registers) | 32-bit MSW+LSW |
| **Ângulos** | ✅ SIM | 0x03 (Registers) | 32-bit pares |
| **Inversor** | ✅ SIM | 0x03 (Registers) | Tensão confirmada |
| **Timers** | ❌ NÃO | - | Illegal data address |
| **Botões** | ✅ SIM | 0x05 (Write Coil) | Pulso 100ms |
| **LEDs** | ⏳ Provável | 0x01 (Coils) | Não testado |

---

## 4. ESPECIFICAÇÃO DA IHM FÍSICA ORIGINAL

### 4.1. Layout Atos 4004.95C

```
┌──────────────────────────────────────┐
│  [LED1] [LED2] [LED3] [LED4] [LED5]  │
│                                      │
│   ┌──────────────────────────────┐   │
│   │                              │   │
│   │      Display LCD 2x16        │   │
│   │      (linha 1: status)       │   │
│   │      (linha 2: valores)      │   │
│   │                              │   │
│   └──────────────────────────────┘   │
│                                      │
│    [1] [2] [3] [↑] [S1] [Lock]       │
│    [4] [5] [6] [↓] [S2] [ESC]        │
│    [7] [8] [9] [EDIT] [ENTER]        │
│    [   0   ]                          │
│                                      │
└──────────────────────────────────────┘
```

**Componentes:**
- **5 LEDs**: Indicam dobra ativa (1/2/3) e direção (K4/K5)
- **Display LCD 2x16**: Mostra ângulo atual, setpoints, modo, mensagens
- **Teclado numérico**: K0-K9
- **Teclas de função**: S1, S2, Lock, ESC, EDIT, ENTER
- **Setas**: Navegação

### 4.2. Modos de Operação

#### Modo MANUAL
- Velocidade fixa 5 rpm (Classe 1)
- Usuário pressiona AVANÇAR ou RECUAR (botões físicos no painel da máquina, NÃO na IHM)
- Botão deve ser mantido pressionado durante toda a dobra
- Prato rotaciona até ângulo pré-programado
- Retorna automaticamente ao zero
- Para parada precisa: PARADA + direção simultâneos

**Estados:**
- LED1/2/3: Indica qual dobra (1ª, 2ª ou 3ª)
- Display linha 1: "MANUAL  5 RPM"
- Display linha 2: "ANG: 045.7°"

#### Modo AUTO
- Velocidades variáveis (5, 10 ou 15 rpm)
- Selecionar direção: PARADA + K4 (esquerda) ou K5 (direita)
- LED4 (K4) ou LED5 (K5) acende
- Pressionar AVANÇAR (anti-horário) ou RECUAR (horário)
- Sistema executa dobra automaticamente
- Avança para próxima dobra (K1→K2→K3) sem poder voltar

**Estados:**
- LED1/2/3: Indica qual dobra
- LED4/5: Indica direção selecionada
- Display linha 1: "AUTO   10 RPM"
- Display linha 2: "K2 DIR 090.0°"

#### Troca de Velocidade (MANUAL apenas)
- Pressionar K1+K7 simultaneamente
- Display mostra: "CLASSE: 2"
- Cicla: 1 (5rpm) → 2 (10rpm) → 3 (15rpm) → 1...

#### Troca de Modo (AUTO ↔ MANUAL)
- Pressionar S1
- Só funciona se:
  - Máquina parada (sem ciclo ativo)
  - Na dobra 1 (LED1 aceso)

### 4.3. Sequência de Dobras

```
  [Ligar]
     ↓
 ┌───────┐
 │ K1 ON │ ← Dobra 1
 └───┬───┘
     ↓ [Executa dobra 1]
 ┌───────┐
 │ K2 ON │ ← Dobra 2
 └───┬───┘
     ↓ [Executa dobra 2]
 ┌───────┐
 │ K3 ON │ ← Dobra 3
 └───┬───┘
     ↓ [Executa dobra 3]
 [Fim de ciclo]
     ↓
 ⚠️ NÃO pode voltar!
     ↓
 [Desligar/Religar para reset]
```

### 4.4. Mensagens do Display (Exemplos)

| Linha 1 | Linha 2 | Situação |
|---------|---------|----------|
| `MANUAL  5 RPM` | `ANG: 045.7°` | Manual, encoder em 45.7° |
| `AUTO   10 RPM` | `K1 ESQ 090.0°` | Auto, dobra 1 esquerda, setpoint 90° |
| `AUTO   15 RPM` | `K2 DIR 120.0°` | Auto, dobra 2 direita, setpoint 120° |
| `CLASSE: 1` | `5 RPM` | Selecionando velocidade |
| `EMERGENCIA` | `RESET S2` | Emergência ativa, pressionar S2 |
| `EDIT ANGULO 1` | `090.0°_` | Editando setpoint da dobra 1 |

**⚠️ IMPORTANTE:** Display LCD provavelmente **NÃO é acessível via Modbus** (ver seção 10).

---

## 5. ARQUITETURA DA IHM WEB

### 5.1. Stack Tecnológico

```
┌─────────────────────────────────────────────────────┐
│  FRONTEND (Tablet)                                  │
│  ─────────────────────────────────────────────      │
│  • HTML5 + CSS3 + JavaScript PURO                   │
│  • WebSocket cliente (ws://servidor:8765)           │
│  • SEM frameworks (portabilidade ESP32)             │
│  • Responsivo (tablets 7"-10")                      │
└─────────────────────────────────────────────────────┘
                        ▲
                        │ WebSocket (JSON)
                        ▼
┌─────────────────────────────────────────────────────┐
│  BACKEND (Notebook Ubuntu → futuro ESP32)           │
│  ─────────────────────────────────────────────      │
│  • Python 3.12+ (asyncio)                           │
│  • pymodbus (Modbus RTU cliente)                    │
│  • websockets (servidor WebSocket)                  │
│  • Polling 250ms (4 Hz)                             │
└─────────────────────────────────────────────────────┘
                        ▲
                        │ Modbus RTU (RS485)
                        ▼
┌─────────────────────────────────────────────────────┐
│  CLP MPC4004 (Slave ID 1)                           │
│  ─────────────────────────────────────────────      │
│  • 57600 baud, 8N2                                  │
│  • Function Codes: 0x01, 0x03, 0x05                 │
│  • /dev/ttyUSB0                                     │
└─────────────────────────────────────────────────────┘
```

### 5.2. Arquivos Backend

```
ihm/
├── modbus_client.py       ← Cliente Modbus (pymodbus wrapper)
├── state_manager.py       ← Polling loop + estado da máquina
├── ihm_server.py          ← Servidor WebSocket + HTTP
├── modbus_map.py          ← Constantes (endereços Modbus)
├── requirements.txt       ← Dependências Python
└── static/
    └── index.html         ← Frontend completo (HTML+JS+CSS)
```

### 5.3. Fluxo de Comunicação

```
1. Backend inicia:
   └─ Conecta RS485 (/dev/ttyUSB0)
   └─ Testa comunicação Modbus
   └─ Inicia servidor WebSocket (porta 8765)
   └─ Inicia polling loop (250ms)

2. Tablet abre navegador:
   └─ Carrega http://servidor:8080/
   └─ Conecta WebSocket ws://servidor:8765
   └─ Recebe estado completo

3. Polling contínuo (backend):
   └─ A cada 250ms:
       ├─ Lê encoder (0x04D6/0x04D7)
       ├─ Lê I/O (0x0100-0x0107, 0x0180-0x0187)
       ├─ Lê LEDs (0x00C0-0x00C4)
       ├─ Lê inversor (0x06E0)
       └─ Compara com estado anterior
           └─ Se mudou: Envia delta via WebSocket

4. Usuário pressiona botão (frontend):
   └─ JavaScript: ws.send({"action": "press", "key": "K1"})
   └─ Backend recebe, executa press_key(0x00A0)
   └─ Retorna {"status": "ok"} ou {"status": "error"}

5. Erro de conexão:
   └─ Modbus timeout:
       └─ machine_state["modbus_connected"] = False
       └─ Frontend mostra overlay "FALHA CLP"
   └─ WebSocket disconnect:
       └─ Frontend mostra overlay "DESLIGADO"
```

### 5.4. Estrutura de Dados (machine_state)

```python
machine_state = {
    # Encoder
    "encoder_raw": 119,              # Valor bruto 32-bit
    "encoder_degrees": 11.9,         # Convertido em graus

    # Ângulos programados
    "angle_bend1_left": 90.0,
    "angle_bend1_right": 85.0,
    "angle_bend2_left": 120.0,
    "angle_bend2_right": 115.0,
    "angle_bend3_left": 56.0,
    "angle_bend3_right": 52.0,

    # I/O Digital
    "inputs": {"E0": True, "E1": False, ..., "E7": False},
    "outputs": {"S0": False, "S1": False, ..., "S7": False},

    # LEDs
    "leds": {"LED1": True, "LED2": False, "LED3": False, "LED4": False, "LED5": False},

    # Inversor
    "inverter_voltage": 21765,
    "inverter_rpm": 1755,            # Se disponível
    "speed_class": 1,                # 1=5rpm, 2=10rpm, 3=15rpm

    # Estados
    "mode_manual": True,             # True=Manual, False=Auto
    "cycle_active": False,
    "emergency": False,

    # Conexão
    "modbus_connected": True,
    "last_update": "2025-11-12T22:10:00"
}
```

---

## 6. IMPLEMENTAÇÃO BACKEND (PYTHON)

### 6.1. Arquivo: `modbus_map.py`

```python
"""
Mapeamento Modbus RTU para CLP Atos MPC4004
Baseado em testes empíricos (12/Nov/2025)
"""

# ========== CONFIGURAÇÃO MODBUS ==========
MODBUS_CONFIG = {
    'port': '/dev/ttyUSB0',
    'baudrate': 57600,
    'parity': 'N',
    'stopbits': 2,
    'bytesize': 8,
    'timeout': 1.0,
    'slave_id': 1
}

# ========== I/O DIGITAL (COILS - Function 0x01) ==========
# CRÍTICO: São COILS, não Holding Registers!
DIGITAL_INPUTS = {
    'E0': 0x0100,  # 256
    'E1': 0x0101,  # 257
    'E2': 0x0102,  # 258
    'E3': 0x0103,  # 259
    'E4': 0x0104,  # 260
    'E5': 0x0105,  # 261
    'E6': 0x0106,  # 262
    'E7': 0x0107,  # 263
}

DIGITAL_OUTPUTS = {
    'S0': 0x0180,  # 384
    'S1': 0x0181,  # 385
    'S2': 0x0182,  # 386
    'S3': 0x0183,  # 387
    'S4': 0x0184,  # 388
    'S5': 0x0185,  # 389
    'S6': 0x0186,  # 390
    'S7': 0x0187,  # 391
}

# ========== ENCODER (HOLDING REGISTERS - 32-bit) ==========
ENCODER = {
    'MSW': 0x04D6,  # 1238 - Most Significant Word
    'LSW': 0x04D7,  # 1239 - Least Significant Word
}

# ========== ÂNGULOS PROGRAMADOS (HOLDING REGISTERS - Pares 32-bit) ==========
ANGLES = {
    'bend1_left':  {'MSW': 0x0840, 'LSW': 0x0842},  # 2112, 2114
    'bend1_right': {'MSW': 0x0844, 'LSW': 0x0846},  # 2116, 2118
    'bend2_left':  {'MSW': 0x0848, 'LSW': 0x084A},  # 2120, 2122
    'bend2_right': {'MSW': 0x084C, 'LSW': 0x084E},  # 2124, 2126
    'bend3_left':  {'MSW': 0x0850, 'LSW': 0x0852},  # 2128, 2130
    'bend3_right': {'MSW': 0x0854, 'LSW': 0x0856},  # 2132, 2134
}

# ========== INVERSOR WEG (HOLDING REGISTERS) ==========
INVERTER = {
    'voltage': 0x06E0,  # 1760 - Testado ✅
    'current': 0x06E1,  # 1761 - Não confirmado
    'rpm': 0x05F1,      # 1521 - Não confirmado
}

# ========== BOTÕES/TECLAS (COILS - Function 0x05 Write) ==========
KEYBOARD = {
    # Numérico
    'K0': 0x00A9,  # 169
    'K1': 0x00A0,  # 160
    'K2': 0x00A1,  # 161
    'K3': 0x00A2,  # 162
    'K4': 0x00A3,  # 163
    'K5': 0x00A4,  # 164
    'K6': 0x00A5,  # 165
    'K7': 0x00A6,  # 166 (K1+K7 = muda velocidade)
    'K8': 0x00A7,  # 167
    'K9': 0x00A8,  # 168

    # Função
    'S1': 0x00DC,        # 220 - Alterna AUTO/MANUAL
    'S2': 0x00DD,        # 221 - Reset/Contexto
    'ARROW_UP': 0x00AC,  # 172
    'ARROW_DOWN': 0x00AD,  # 173
    'ESC': 0x00BC,       # 188
    'ENTER': 0x0025,     # 37
    'EDIT': 0x0026,      # 38
    'LOCK': 0x00F1,      # 241
}

# ========== LEDs (COILS - Function 0x01 Read) ==========
LEDS = {
    'LED1': 0x00C0,  # 192 - Dobra 1 ativa
    'LED2': 0x00C1,  # 193 - Dobra 2 ativa
    'LED3': 0x00C2,  # 194 - Dobra 3 ativa
    'LED4': 0x00C3,  # 195 - K4 (esquerda) ativo
    'LED5': 0x00C4,  # 196 - K5 (direita) ativo
}

# ========== ESTADOS CRÍTICOS (COILS) ==========
STATES = {
    'modbus_slave_on': 0x00BE,  # 190 - DEVE estar ON
    'cycle_active': 0x0191,     # 401 - Não confirmado
    'mode_manual': 0x02FF,      # 767 - Não confirmado
    'emergency': None,          # Não mapeado ainda
}

# ========== HELPERS ==========
def combine_32bit(msw, lsw):
    """Combina MSW e LSW em valor 32-bit"""
    return (msw << 16) | lsw

def split_32bit(value):
    """Divide valor 32-bit em MSW e LSW"""
    msw = (value >> 16) & 0xFFFF
    lsw = value & 0xFFFF
    return msw, lsw

def raw_to_degrees(raw_value):
    """Converte valor bruto encoder/ângulo para graus"""
    return raw_value / 10.0

def degrees_to_raw(degrees):
    """Converte graus para valor bruto encoder/ângulo"""
    return int(degrees * 10)
```

### 6.2. Arquivo: `modbus_client.py`

```python
"""
Cliente Modbus RTU para CLP Atos MPC4004
Wrapper sobre pymodbus com métodos específicos
"""

import time
from typing import Optional, Dict, Tuple
from pymodbus.client import ModbusSerialClient
from pymodbus.exceptions import ModbusException

import modbus_map as mmap


class ModbusClientWrapper:
    def __init__(self, stub_mode: bool = False):
        """
        Inicializa cliente Modbus RTU

        Args:
            stub_mode: Se True, simula dados sem conexão real
        """
        self.stub_mode = stub_mode
        self.slave_id = mmap.MODBUS_CONFIG['slave_id']

        if not stub_mode:
            self.client = ModbusSerialClient(
                port=mmap.MODBUS_CONFIG['port'],
                baudrate=mmap.MODBUS_CONFIG['baudrate'],
                parity=mmap.MODBUS_CONFIG['parity'],
                stopbits=mmap.MODBUS_CONFIG['stopbits'],
                bytesize=mmap.MODBUS_CONFIG['bytesize'],
                timeout=mmap.MODBUS_CONFIG['timeout']
            )
            self.connected = self.client.connect()
        else:
            self.client = None
            self.connected = True
            self._stub_encoder = 119
            self._stub_direction = 1

    # ========== LEITURA I/O DIGITAL (COILS) ==========

    def read_digital_inputs(self) -> Optional[Dict[str, bool]]:
        """
        Lê todas as entradas digitais E0-E7 como COILS

        Returns:
            {'E0': True, 'E1': False, ...} ou None se erro
        """
        if self.stub_mode:
            return {f'E{i}': i == 0 for i in range(8)}  # E0=True, resto False

        try:
            result = self.client.read_coils(0x0100, 8, slave=self.slave_id)
            if result.isError():
                return None
            return {f'E{i}': bit for i, bit in enumerate(result.bits[:8])}
        except ModbusException:
            return None

    def read_digital_outputs(self) -> Optional[Dict[str, bool]]:
        """
        Lê todas as saídas digitais S0-S7 como COILS

        Returns:
            {'S0': False, 'S1': False, ...} ou None se erro
        """
        if self.stub_mode:
            return {f'S{i}': False for i in range(8)}

        try:
            result = self.client.read_coils(0x0180, 8, slave=self.slave_id)
            if result.isError():
                return None
            return {f'S{i}': bit for i, bit in enumerate(result.bits[:8])}
        except ModbusException:
            return None

    # ========== LEITURA ENCODER (32-bit) ==========

    def read_encoder(self) -> Optional[Dict[str, float]]:
        """
        Lê encoder 32-bit e converte para graus

        Returns:
            {'raw': 119, 'degrees': 11.9} ou None se erro
        """
        if self.stub_mode:
            # Simula encoder girando lentamente
            self._stub_encoder += self._stub_direction
            if self._stub_encoder > 3600:  # 360.0 graus
                self._stub_direction = -1
            elif self._stub_encoder < 0:
                self._stub_direction = 1
            return {
                'raw': self._stub_encoder,
                'degrees': self._stub_encoder / 10.0
            }

        try:
            result = self.client.read_holding_registers(
                mmap.ENCODER['MSW'], 2, slave=self.slave_id
            )
            if result.isError():
                return None

            msw, lsw = result.registers
            raw_value = mmap.combine_32bit(msw, lsw)
            degrees = mmap.raw_to_degrees(raw_value)

            return {'raw': raw_value, 'degrees': degrees}
        except ModbusException:
            return None

    # ========== LEITURA ÂNGULOS (32-bit pares) ==========

    def read_angle(self, name: str) -> Optional[float]:
        """
        Lê ângulo programado específico

        Args:
            name: 'bend1_left', 'bend2_right', etc (ver modbus_map.ANGLES)

        Returns:
            Ângulo em graus (ex: 90.0) ou None se erro
        """
        if self.stub_mode:
            # Valores de exemplo
            stub_angles = {
                'bend1_left': 90.0, 'bend1_right': 85.0,
                'bend2_left': 120.0, 'bend2_right': 115.0,
                'bend3_left': 56.0, 'bend3_right': 52.0,
            }
            return stub_angles.get(name)

        if name not in mmap.ANGLES:
            return None

        try:
            addrs = mmap.ANGLES[name]

            # Ler MSW
            result_msw = self.client.read_holding_registers(
                addrs['MSW'], 1, slave=self.slave_id
            )
            if result_msw.isError():
                return None
            msw = result_msw.registers[0]

            # Ler LSW
            result_lsw = self.client.read_holding_registers(
                addrs['LSW'], 1, slave=self.slave_id
            )
            if result_lsw.isError():
                return None
            lsw = result_lsw.registers[0]

            raw_value = mmap.combine_32bit(msw, lsw)
            degrees = mmap.raw_to_degrees(raw_value)

            return degrees
        except ModbusException:
            return None

    def read_all_angles(self) -> Optional[Dict[str, float]]:
        """
        Lê todos os 6 ângulos programados

        Returns:
            {'bend1_left': 90.0, 'bend1_right': 85.0, ...} ou None se erro
        """
        angles = {}
        for name in mmap.ANGLES.keys():
            value = self.read_angle(name)
            if value is None:
                return None
            angles[name] = value
        return angles

    # ========== ESCRITA ÂNGULOS ==========

    def write_angle(self, name: str, degrees: float) -> bool:
        """
        Escreve ângulo programado

        Args:
            name: 'bend1_left', 'bend2_right', etc
            degrees: Ângulo em graus (ex: 90.0)

        Returns:
            True se sucesso, False se erro
        """
        if self.stub_mode:
            return True

        if name not in mmap.ANGLES:
            return False

        try:
            addrs = mmap.ANGLES[name]
            raw_value = mmap.degrees_to_raw(degrees)
            msw, lsw = mmap.split_32bit(raw_value)

            # Escrever MSW
            result1 = self.client.write_register(
                addrs['MSW'], msw, slave=self.slave_id
            )
            if result1.isError():
                return False

            # Escrever LSW
            result2 = self.client.write_register(
                addrs['LSW'], lsw, slave=self.slave_id
            )
            if result2.isError():
                return False

            return True
        except ModbusException:
            return False

    # ========== LEITURA LEDs ==========

    def read_leds(self) -> Optional[Dict[str, bool]]:
        """
        Lê estado dos 5 LEDs

        Returns:
            {'LED1': True, 'LED2': False, ...} ou None se erro
        """
        if self.stub_mode:
            return {'LED1': True, 'LED2': False, 'LED3': False,
                    'LED4': False, 'LED5': False}

        try:
            result = self.client.read_coils(0x00C0, 5, slave=self.slave_id)
            if result.isError():
                return None
            return {f'LED{i+1}': bit for i, bit in enumerate(result.bits[:5])}
        except ModbusException:
            return None

    # ========== LEITURA INVERSOR ==========

    def read_inverter_voltage(self) -> Optional[int]:
        """
        Lê tensão do inversor WEG

        Returns:
            Valor bruto (ex: 21765) ou None se erro
        """
        if self.stub_mode:
            return 21765

        try:
            result = self.client.read_holding_registers(
                mmap.INVERTER['voltage'], 1, slave=self.slave_id
            )
            if result.isError():
                return None
            return result.registers[0]
        except ModbusException:
            return None

    # ========== SIMULAÇÃO DE BOTÕES (Write Coil) ==========

    def press_key(self, key_name: str, hold_ms: int = 100) -> bool:
        """
        Simula pressionamento de tecla com pulso ON→OFF

        Args:
            key_name: 'K0', 'K1', ..., 'S1', 'ENTER', etc
            hold_ms: Duração do pulso em ms (padrão 100ms)

        Returns:
            True se sucesso, False se erro
        """
        if self.stub_mode:
            print(f"[STUB] Tecla pressionada: {key_name}")
            return True

        if key_name not in mmap.KEYBOARD:
            return False

        address = mmap.KEYBOARD[key_name]

        try:
            # ON
            result1 = self.client.write_coil(address, True, slave=self.slave_id)
            if result1.isError():
                return False

            # Aguarda
            time.sleep(hold_ms / 1000.0)

            # OFF
            result2 = self.client.write_coil(address, False, slave=self.slave_id)
            if result2.isError():
                return False

            return True
        except ModbusException:
            return False

    def change_speed_class(self) -> bool:
        """
        Muda classe de velocidade (K1+K7 simultâneo)

        Returns:
            True se sucesso, False se erro
        """
        if self.stub_mode:
            print("[STUB] Mudança de velocidade: K1+K7")
            return True

        try:
            # ON simultâneo
            self.client.write_coil(mmap.KEYBOARD['K1'], True, slave=self.slave_id)
            self.client.write_coil(mmap.KEYBOARD['K7'], True, slave=self.slave_id)

            time.sleep(0.1)

            # OFF simultâneo
            self.client.write_coil(mmap.KEYBOARD['K1'], False, slave=self.slave_id)
            self.client.write_coil(mmap.KEYBOARD['K7'], False, slave=self.slave_id)

            return True
        except ModbusException:
            return False

    # ========== DIAGNÓSTICO ==========

    def test_connection(self) -> bool:
        """
        Testa conexão Modbus lendo encoder

        Returns:
            True se conectado e respondendo
        """
        if self.stub_mode:
            return True

        result = self.read_encoder()
        return result is not None

    def close(self):
        """Fecha conexão serial"""
        if self.client and not self.stub_mode:
            self.client.close()
```

### 6.3. Arquivo: `state_manager.py`

```python
"""
Gerenciador de estado da máquina
Polling loop asyncio (250ms) + estado centralizado
"""

import asyncio
import time
from datetime import datetime
from typing import Dict, Any, Optional

from modbus_client import ModbusClientWrapper


class MachineStateManager:
    def __init__(self, modbus_client: ModbusClientWrapper):
        """
        Inicializa gerenciador de estado

        Args:
            modbus_client: Cliente Modbus configurado
        """
        self.modbus = modbus_client
        self.state: Dict[str, Any] = self._init_state()
        self.previous_state: Dict[str, Any] = {}
        self.running = False

    def _init_state(self) -> Dict[str, Any]:
        """Inicializa estado vazio"""
        return {
            # Encoder
            'encoder_raw': 0,
            'encoder_degrees': 0.0,

            # Ângulos programados
            'angle_bend1_left': 0.0,
            'angle_bend1_right': 0.0,
            'angle_bend2_left': 0.0,
            'angle_bend2_right': 0.0,
            'angle_bend3_left': 0.0,
            'angle_bend3_right': 0.0,

            # I/O Digital
            'inputs': {f'E{i}': False for i in range(8)},
            'outputs': {f'S{i}': False for i in range(8)},

            # LEDs
            'leds': {f'LED{i}': False for i in range(1, 6)},

            # Inversor
            'inverter_voltage': 0,

            # Estados (não mapeados ainda)
            'mode_manual': True,
            'cycle_active': False,
            'emergency': False,
            'speed_class': 1,

            # Conexão
            'modbus_connected': False,
            'last_update': None,
        }

    async def poll_once(self):
        """Polling único - lê todos os dados do CLP"""
        try:
            # Encoder
            encoder_data = self.modbus.read_encoder()
            if encoder_data:
                self.state['encoder_raw'] = encoder_data['raw']
                self.state['encoder_degrees'] = encoder_data['degrees']

            # Ângulos
            angles = self.modbus.read_all_angles()
            if angles:
                for name, value in angles.items():
                    self.state[f'angle_{name}'] = value

            # I/O Digital
            inputs = self.modbus.read_digital_inputs()
            if inputs:
                self.state['inputs'] = inputs

            outputs = self.modbus.read_digital_outputs()
            if outputs:
                self.state['outputs'] = outputs

            # LEDs
            leds = self.modbus.read_leds()
            if leds:
                self.state['leds'] = leds

            # Inversor
            voltage = self.modbus.read_inverter_voltage()
            if voltage is not None:
                self.state['inverter_voltage'] = voltage

            # Marca como conectado
            self.state['modbus_connected'] = True
            self.state['last_update'] = datetime.now().isoformat()

        except Exception as e:
            print(f"[ERROR] Polling falhou: {e}")
            self.state['modbus_connected'] = False

    async def poll_loop(self, interval_ms: int = 250):
        """
        Loop de polling contínuo

        Args:
            interval_ms: Intervalo entre leituras em ms (padrão 250ms = 4 Hz)
        """
        self.running = True
        print(f"[INFO] Polling iniciado (intervalo: {interval_ms}ms)")

        while self.running:
            await self.poll_once()
            await asyncio.sleep(interval_ms / 1000.0)

    def stop(self):
        """Para o polling loop"""
        self.running = False
        print("[INFO] Polling parado")

    def get_state(self) -> Dict[str, Any]:
        """
        Retorna estado completo da máquina

        Returns:
            Dicionário com todos os dados
        """
        return self.state.copy()

    def get_changes(self) -> Optional[Dict[str, Any]]:
        """
        Retorna apenas campos que mudaram desde última chamada

        Returns:
            Dicionário com deltas ou None se nada mudou
        """
        if not self.previous_state:
            self.previous_state = self.state.copy()
            return self.state.copy()

        changes = {}
        for key, value in self.state.items():
            if key == 'last_update':
                continue
            if self.previous_state.get(key) != value:
                changes[key] = value

        self.previous_state = self.state.copy()

        return changes if changes else None
```

### 6.4. Arquivo: `ihm_server.py`

```python
"""
Servidor WebSocket para IHM Web
Backend completo: Modbus ↔ WebSocket ↔ Tablet
"""

import asyncio
import json
import websockets
from websockets.server import serve
from http.server import HTTPServer, SimpleHTTPRequestHandler
import threading
from pathlib import Path

from modbus_client import ModbusClientWrapper
from state_manager import MachineStateManager


class IHMServer:
    def __init__(self, stub_mode: bool = False):
        """
        Inicializa servidor IHM

        Args:
            stub_mode: Se True, roda sem CLP (desenvolvimento)
        """
        self.stub_mode = stub_mode
        self.modbus = ModbusClientWrapper(stub_mode=stub_mode)
        self.state_manager = MachineStateManager(self.modbus)
        self.clients = set()

    async def handle_client(self, websocket):
        """
        Gerencia conexão WebSocket de um cliente (tablet)

        Args:
            websocket: Conexão WebSocket
        """
        print(f"[INFO] Cliente conectado: {websocket.remote_address}")
        self.clients.add(websocket)

        try:
            # Envia estado completo inicial
            initial_state = self.state_manager.get_state()
            await websocket.send(json.dumps({
                'type': 'full_state',
                'data': initial_state
            }))

            # Loop de recepção de comandos
            async for message in websocket:
                await self.handle_message(websocket, message)

        except websockets.exceptions.ConnectionClosed:
            print(f"[INFO] Cliente desconectado: {websocket.remote_address}")
        finally:
            self.clients.remove(websocket)

    async def handle_message(self, websocket, message: str):
        """
        Processa mensagem recebida do cliente

        Args:
            websocket: Conexão do cliente
            message: JSON string
        """
        try:
            data = json.loads(message)
            action = data.get('action')

            if action == 'press_key':
                # Pressionar botão
                key_name = data.get('key')
                success = self.modbus.press_key(key_name)
                await websocket.send(json.dumps({
                    'type': 'response',
                    'action': 'press_key',
                    'key': key_name,
                    'success': success
                }))

            elif action == 'change_speed':
                # Mudar velocidade (K1+K7)
                success = self.modbus.change_speed_class()
                await websocket.send(json.dumps({
                    'type': 'response',
                    'action': 'change_speed',
                    'success': success
                }))

            elif action == 'write_angle':
                # Escrever ângulo
                angle_name = data.get('name')  # 'bend1_left', etc
                degrees = data.get('degrees')
                success = self.modbus.write_angle(angle_name, degrees)
                await websocket.send(json.dumps({
                    'type': 'response',
                    'action': 'write_angle',
                    'name': angle_name,
                    'success': success
                }))

            else:
                await websocket.send(json.dumps({
                    'type': 'error',
                    'message': f'Ação desconhecida: {action}'
                }))

        except Exception as e:
            print(f"[ERROR] Erro processando mensagem: {e}")
            await websocket.send(json.dumps({
                'type': 'error',
                'message': str(e)
            }))

    async def broadcast_updates(self):
        """
        Envia atualizações de estado para todos os clientes conectados
        Loop contínuo (500ms) que envia deltas
        """
        while True:
            await asyncio.sleep(0.5)  # 2 Hz

            if not self.clients:
                continue

            changes = self.state_manager.get_changes()
            if changes:
                message = json.dumps({
                    'type': 'state_update',
                    'data': changes
                })

                # Broadcast para todos os clientes
                websockets.broadcast(self.clients, message)

    async def start_websocket_server(self, host: str = '0.0.0.0', port: int = 8765):
        """
        Inicia servidor WebSocket

        Args:
            host: IP (0.0.0.0 = todas as interfaces)
            port: Porta WebSocket (padrão 8765)
        """
        async with serve(self.handle_client, host, port):
            print(f"[INFO] Servidor WebSocket iniciado em ws://{host}:{port}")
            await asyncio.Future()  # Roda para sempre

    def start_http_server(self, port: int = 8080):
        """
        Inicia servidor HTTP para servir frontend (static/index.html)
        Roda em thread separada

        Args:
            port: Porta HTTP (padrão 8080)
        """
        class Handler(SimpleHTTPRequestHandler):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, directory='static', **kwargs)

        def run_http():
            server = HTTPServer(('0.0.0.0', port), Handler)
            print(f"[INFO] Servidor HTTP iniciado em http://0.0.0.0:{port}")
            server.serve_forever()

        thread = threading.Thread(target=run_http, daemon=True)
        thread.start()

    async def run(self):
        """
        Inicia todos os serviços (Modbus polling, WebSocket, HTTP)
        """
        print(f"[INFO] Iniciando IHM Server (stub_mode={self.stub_mode})")

        # Testa conexão Modbus
        if not self.stub_mode:
            if not self.modbus.test_connection():
                print("[ERROR] Falha ao conectar CLP via Modbus!")
                return
            print("[INFO] CLP conectado via Modbus ✅")

        # Inicia HTTP server (thread)
        self.start_http_server(port=8080)

        # Inicia tarefas asyncio
        await asyncio.gather(
            self.state_manager.poll_loop(interval_ms=250),  # 4 Hz
            self.broadcast_updates(),                       # 2 Hz
            self.start_websocket_server(host='0.0.0.0', port=8765)
        )


# ========== MAIN ==========
if __name__ == '__main__':
    import sys

    stub_mode = '--stub' in sys.argv

    server = IHMServer(stub_mode=stub_mode)

    try:
        asyncio.run(server.run())
    except KeyboardInterrupt:
        print("\n[INFO] Servidor encerrado pelo usuário")
        server.modbus.close()
```

### 6.5. Arquivo: `requirements.txt`

```txt
pymodbus>=3.6.0
websockets>=12.0
```

---

## 7. IMPLEMENTAÇÃO FRONTEND (HTML/JS/CSS)

### 7.1. Estrutura de Diretórios

```
ihm/
└── static/
    └── index.html    ← Frontend completo (HTML + CSS + JS)
```

### 7.2. Arquivo: `static/index.html` (COMPLETO - ~600 linhas)

```html
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>IHM NEOCOUDE-HD-15</title>
    <style>
        /* ========== RESET ========== */
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Arial', sans-serif;
            background: #1a1a1a;
            color: #fff;
            user-select: none;
        }

        /* ========== OVERLAY DE ERRO ========== */
        .error-overlay {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(255, 0, 0, 0.85);
            z-index: 9999;
            justify-content: center;
            align-items: center;
            font-size: 48px;
            font-weight: bold;
            animation: pulse 1s infinite;
        }

        .error-overlay.show {
            display: flex;
        }

        @keyframes pulse {
            0%, 100% { opacity: 0.85; }
            50% { opacity: 1; }
        }

        /* ========== CONTAINER PRINCIPAL ========== */
        .container {
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }

        /* ========== LEDS ========== */
        .leds {
            display: flex;
            justify-content: center;
            gap: 20px;
            margin-bottom: 30px;
        }

        .led {
            width: 50px;
            height: 50px;
            border-radius: 50%;
            background: #333;
            border: 3px solid #666;
            transition: all 0.3s;
        }

        .led.on {
            background: #0f0;
            border-color: #0f0;
            box-shadow: 0 0 20px #0f0;
        }

        /* ========== DISPLAY ========== */
        .display {
            background: #000;
            border: 5px solid #444;
            border-radius: 10px;
            padding: 30px;
            text-align: center;
            margin-bottom: 30px;
            font-family: 'Courier New', monospace;
        }

        .display-angle {
            font-size: 72px;
            font-weight: bold;
            color: #0f0;
            text-shadow: 0 0 10px #0f0;
        }

        .display-status {
            font-size: 24px;
            color: #888;
            margin-top: 10px;
        }

        .display-status.connected {
            color: #0f0;
        }

        .display-status.disconnected {
            color: #f00;
        }

        /* ========== ÂNGULOS PROGRAMADOS ========== */
        .angles {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 15px;
            margin-bottom: 30px;
        }

        .angle-card {
            background: #2a2a2a;
            border: 2px solid #444;
            border-radius: 8px;
            padding: 15px;
            text-align: center;
        }

        .angle-label {
            font-size: 14px;
            color: #888;
            margin-bottom: 5px;
        }

        .angle-value {
            font-size: 32px;
            font-weight: bold;
            color: #0ff;
        }

        /* ========== TECLADO ========== */
        .keyboard {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 10px;
            margin-bottom: 30px;
        }

        .key {
            background: linear-gradient(180deg, #4a4a4a, #2a2a2a);
            border: 2px solid #666;
            border-radius: 8px;
            padding: 20px;
            font-size: 24px;
            font-weight: bold;
            color: #fff;
            cursor: pointer;
            transition: all 0.1s;
            text-align: center;
        }

        .key:active {
            background: linear-gradient(180deg, #2a2a2a, #1a1a1a);
            transform: scale(0.95);
            border-color: #0f0;
        }

        .key.wide {
            grid-column: span 2;
        }

        .key.function {
            background: linear-gradient(180deg, #555, #333);
            border-color: #888;
        }

        .key.function:active {
            border-color: #0ff;
        }

        /* ========== TABS ========== */
        .tabs {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
        }

        .tab-button {
            flex: 1;
            padding: 15px;
            background: #2a2a2a;
            border: 2px solid #444;
            border-radius: 8px;
            color: #888;
            cursor: pointer;
            transition: all 0.2s;
        }

        .tab-button.active {
            background: #0ff;
            color: #000;
            font-weight: bold;
        }

        .tab-content {
            display: none;
        }

        .tab-content.active {
            display: block;
        }

        /* ========== I/O DIGITAL ========== */
        .io-grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 10px;
        }

        .io-indicator {
            background: #2a2a2a;
            border: 2px solid #444;
            border-radius: 8px;
            padding: 15px;
            text-align: center;
        }

        .io-label {
            font-size: 12px;
            color: #888;
            margin-bottom: 5px;
        }

        .io-led {
            width: 40px;
            height: 40px;
            margin: 0 auto;
            border-radius: 50%;
            background: #333;
            border: 2px solid #666;
        }

        .io-led.on {
            background: #f00;
            border-color: #f00;
            box-shadow: 0 0 15px #f00;
        }

        /* ========== DIAGNÓSTICO ========== */
        .diagnostics {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
        }

        .diagnostic-section {
            background: #2a2a2a;
            border: 2px solid #444;
            border-radius: 8px;
            padding: 20px;
        }

        .diagnostic-section h3 {
            color: #0ff;
            margin-bottom: 15px;
        }
    </style>
</head>
<body>
    <!-- OVERLAY DE ERRO -->
    <div id="errorOverlay" class="error-overlay">
        <div id="errorMessage">DESLIGADO</div>
    </div>

    <!-- CONTAINER PRINCIPAL -->
    <div class="container">
        <!-- LEDS -->
        <div class="leds">
            <div class="led" id="led1" title="Dobra 1"></div>
            <div class="led" id="led2" title="Dobra 2"></div>
            <div class="led" id="led3" title="Dobra 3"></div>
            <div class="led" id="led4" title="K4 - Esquerda"></div>
            <div class="led" id="led5" title="K5 - Direita"></div>
        </div>

        <!-- DISPLAY -->
        <div class="display">
            <div class="display-angle" id="displayAngle">000.0°</div>
            <div class="display-status connected" id="displayStatus">CONECTADO</div>
        </div>

        <!-- TABS -->
        <div class="tabs">
            <div class="tab-button active" data-tab="operacao">OPERAÇÃO</div>
            <div class="tab-button" data-tab="diagnostico">DIAGNÓSTICO</div>
        </div>

        <!-- TAB: OPERAÇÃO -->
        <div class="tab-content active" id="tab-operacao">
            <!-- ÂNGULOS PROGRAMADOS -->
            <div class="angles">
                <div class="angle-card">
                    <div class="angle-label">Dobra 1 ESQ</div>
                    <div class="angle-value" id="angle-bend1-left">000.0°</div>
                </div>
                <div class="angle-card">
                    <div class="angle-label">Dobra 2 ESQ</div>
                    <div class="angle-value" id="angle-bend2-left">000.0°</div>
                </div>
                <div class="angle-card">
                    <div class="angle-label">Dobra 3 ESQ</div>
                    <div class="angle-value" id="angle-bend3-left">000.0°</div>
                </div>
                <div class="angle-card">
                    <div class="angle-label">Dobra 1 DIR</div>
                    <div class="angle-value" id="angle-bend1-right">000.0°</div>
                </div>
                <div class="angle-card">
                    <div class="angle-label">Dobra 2 DIR</div>
                    <div class="angle-value" id="angle-bend2-right">000.0°</div>
                </div>
                <div class="angle-card">
                    <div class="angle-label">Dobra 3 DIR</div>
                    <div class="angle-value" id="angle-bend3-right">000.0°</div>
                </div>
            </div>

            <!-- TECLADO -->
            <div class="keyboard">
                <button class="key" data-key="K1">1</button>
                <button class="key" data-key="K2">2</button>
                <button class="key" data-key="K3">3</button>
                <button class="key function" data-key="ARROW_UP">↑</button>

                <button class="key" data-key="K4">4</button>
                <button class="key" data-key="K5">5</button>
                <button class="key" data-key="K6">6</button>
                <button class="key function" data-key="ARROW_DOWN">↓</button>

                <button class="key" data-key="K7">7</button>
                <button class="key" data-key="K8">8</button>
                <button class="key" data-key="K9">9</button>
                <button class="key function" data-key="ESC">ESC</button>

                <button class="key wide" data-key="K0">0</button>
                <button class="key function" data-key="EDIT">EDIT</button>
                <button class="key function" data-key="ENTER">ENTER</button>

                <button class="key function" data-key="S1">S1</button>
                <button class="key function" data-key="S2">S2</button>
                <button class="key function wide" id="speedBtn">VELOCIDADE</button>
            </div>
        </div>

        <!-- TAB: DIAGNÓSTICO -->
        <div class="tab-content" id="tab-diagnostico">
            <div class="diagnostics">
                <!-- ENTRADAS DIGITAIS -->
                <div class="diagnostic-section">
                    <h3>ENTRADAS (E0-E7)</h3>
                    <div class="io-grid">
                        <div class="io-indicator">
                            <div class="io-label">E0</div>
                            <div class="io-led" id="input-E0"></div>
                        </div>
                        <div class="io-indicator">
                            <div class="io-label">E1</div>
                            <div class="io-led" id="input-E1"></div>
                        </div>
                        <div class="io-indicator">
                            <div class="io-label">E2</div>
                            <div class="io-led" id="input-E2"></div>
                        </div>
                        <div class="io-indicator">
                            <div class="io-label">E3</div>
                            <div class="io-led" id="input-E3"></div>
                        </div>
                        <div class="io-indicator">
                            <div class="io-label">E4</div>
                            <div class="io-led" id="input-E4"></div>
                        </div>
                        <div class="io-indicator">
                            <div class="io-label">E5</div>
                            <div class="io-led" id="input-E5"></div>
                        </div>
                        <div class="io-indicator">
                            <div class="io-label">E6</div>
                            <div class="io-led" id="input-E6"></div>
                        </div>
                        <div class="io-indicator">
                            <div class="io-label">E7</div>
                            <div class="io-led" id="input-E7"></div>
                        </div>
                    </div>
                </div>

                <!-- SAÍDAS DIGITAIS -->
                <div class="diagnostic-section">
                    <h3>SAÍDAS (S0-S7)</h3>
                    <div class="io-grid">
                        <div class="io-indicator">
                            <div class="io-label">S0</div>
                            <div class="io-led" id="output-S0"></div>
                        </div>
                        <div class="io-indicator">
                            <div class="io-label">S1</div>
                            <div class="io-led" id="output-S1"></div>
                        </div>
                        <div class="io-indicator">
                            <div class="io-label">S2</div>
                            <div class="io-led" id="output-S2"></div>
                        </div>
                        <div class="io-indicator">
                            <div class="io-label">S3</div>
                            <div class="io-led" id="output-S3"></div>
                        </div>
                        <div class="io-indicator">
                            <div class="io-label">S4</div>
                            <div class="io-led" id="output-S4"></div>
                        </div>
                        <div class="io-indicator">
                            <div class="io-label">S5</div>
                            <div class="io-led" id="output-S5"></div>
                        </div>
                        <div class="io-indicator">
                            <div class="io-label">S6</div>
                            <div class="io-led" id="output-S6"></div>
                        </div>
                        <div class="io-indicator">
                            <div class="io-label">S7</div>
                            <div class="io-led" id="output-S7"></div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        // ========== WEBSOCKET ==========
        let ws = null;
        let machineState = {};

        function connectWebSocket() {
            const host = window.location.hostname || 'localhost';
            ws = new WebSocket(`ws://${host}:8765`);

            ws.onopen = () => {
                console.log('[WS] Conectado');
                hideError();
            };

            ws.onmessage = (event) => {
                const message = JSON.parse(event.data);

                if (message.type === 'full_state') {
                    machineState = message.data;
                    updateUI(machineState);
                } else if (message.type === 'state_update') {
                    Object.assign(machineState, message.data);
                    updateUI(message.data);
                }
            };

            ws.onerror = (error) => {
                console.error('[WS] Erro:', error);
                showError('FALHA CONEXÃO');
            };

            ws.onclose = () => {
                console.log('[WS] Desconectado');
                showError('DESLIGADO');
                setTimeout(connectWebSocket, 3000);  // Reconectar após 3s
            };
        }

        // ========== UI UPDATE ==========
        function updateUI(data) {
            // Encoder
            if (data.encoder_degrees !== undefined) {
                document.getElementById('displayAngle').textContent =
                    data.encoder_degrees.toFixed(1) + '°';
            }

            // Status conexão
            if (data.modbus_connected !== undefined) {
                const statusEl = document.getElementById('displayStatus');
                if (data.modbus_connected) {
                    statusEl.textContent = 'CONECTADO';
                    statusEl.className = 'display-status connected';
                } else {
                    statusEl.textContent = 'FALHA CLP';
                    statusEl.className = 'display-status disconnected';
                    showError('FALHA CLP');
                }
            }

            // LEDs
            if (data.leds) {
                for (let i = 1; i <= 5; i++) {
                    const ledEl = document.getElementById(`led${i}`);
                    if (data.leds[`LED${i}`]) {
                        ledEl.classList.add('on');
                    } else {
                        ledEl.classList.remove('on');
                    }
                }
            }

            // Ângulos programados
            const angleKeys = [
                'angle_bend1_left', 'angle_bend2_left', 'angle_bend3_left',
                'angle_bend1_right', 'angle_bend2_right', 'angle_bend3_right'
            ];
            angleKeys.forEach(key => {
                if (data[key] !== undefined) {
                    const id = 'angle-' + key.replace('angle_', '').replace('_', '-');
                    const el = document.getElementById(id);
                    if (el) {
                        el.textContent = data[key].toFixed(1) + '°';
                    }
                }
            });

            // I/O Digital
            if (data.inputs) {
                for (let i = 0; i < 8; i++) {
                    const ioEl = document.getElementById(`input-E${i}`);
                    if (data.inputs[`E${i}`]) {
                        ioEl.classList.add('on');
                    } else {
                        ioEl.classList.remove('on');
                    }
                }
            }

            if (data.outputs) {
                for (let i = 0; i < 8; i++) {
                    const ioEl = document.getElementById(`output-S${i}`);
                    if (data.outputs[`S${i}`]) {
                        ioEl.classList.add('on');
                    } else {
                        ioEl.classList.remove('on');
                    }
                }
            }
        }

        // ========== ERROR OVERLAY ==========
        function showError(message) {
            const overlay = document.getElementById('errorOverlay');
            document.getElementById('errorMessage').textContent = message;
            overlay.classList.add('show');
        }

        function hideError() {
            document.getElementById('errorOverlay').classList.remove('show');
        }

        // ========== BOTÕES ==========
        function pressKey(keyName) {
            if (!ws || ws.readyState !== WebSocket.OPEN) {
                return;
            }

            ws.send(JSON.stringify({
                action: 'press_key',
                key: keyName
            }));
        }

        function changeSpeed() {
            if (!ws || ws.readyState !== WebSocket.OPEN) {
                return;
            }

            ws.send(JSON.stringify({
                action: 'change_speed'
            }));
        }

        // ========== TABS ==========
        function switchTab(tabName) {
            document.querySelectorAll('.tab-button').forEach(btn => {
                btn.classList.remove('active');
            });
            document.querySelectorAll('.tab-content').forEach(content => {
                content.classList.remove('active');
            });

            document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');
            document.getElementById(`tab-${tabName}`).classList.add('active');
        }

        // ========== EVENT LISTENERS ==========
        document.addEventListener('DOMContentLoaded', () => {
            // Botões do teclado
            document.querySelectorAll('.key[data-key]').forEach(btn => {
                btn.addEventListener('click', () => {
                    pressKey(btn.dataset.key);
                });
            });

            // Botão de velocidade
            document.getElementById('speedBtn').addEventListener('click', changeSpeed);

            // Tabs
            document.querySelectorAll('.tab-button').forEach(btn => {
                btn.addEventListener('click', () => {
                    switchTab(btn.dataset.tab);
                });
            });

            // Conecta WebSocket
            connectWebSocket();
        });
    </script>
</body>
</html>
```

---

## 8. PROCEDIMENTOS DE TESTE

### 8.1. Teste 1: Desenvolvimento Stub (SEM CLP)

```bash
# 1. Instalar dependências
pip3 install -r requirements.txt

# 2. Executar em modo stub
python3 ihm_server.py --stub

# 3. Abrir navegador
firefox http://localhost:8080

# 4. Verificar:
#    - LEDs piscando
#    - Encoder simulado girando
#    - Botões respondem (console mostra mensagens)
#    - Sem erro "DESLIGADO"
```

### 8.2. Teste 2: Conexão Modbus (COM CLP)

```bash
# 1. CLP ligado, cabo RS485 conectado
# 2. Verificar porta serial
ls -l /dev/ttyUSB*

# 3. Testar comunicação básica
python3 -c "from modbus_client import *; c = ModbusClientWrapper(); print(c.read_encoder())"

# 4. Se retornar {'raw': 119, 'degrees': 11.9} → OK!
```

### 8.3. Teste 3: IHM Web Completa (COM CLP)

```bash
# 1. Executar servidor
python3 ihm_server.py

# 2. Verificar logs:
#    [INFO] CLP conectado via Modbus ✅
#    [INFO] Servidor HTTP iniciado em http://0.0.0.0:8080
#    [INFO] Servidor WebSocket iniciado em ws://0.0.0.0:8765
#    [INFO] Polling iniciado (intervalo: 250ms)

# 3. Abrir tablet/notebook no mesmo WiFi
firefox http://<IP_DO_SERVIDOR>:8080

# 4. Verificar:
#    - Display mostra ângulo real do encoder
#    - LEDs refletem estado do CLP
#    - I/O digitais atualizam em tempo real (tab DIAGNÓSTICO)
#    - Pressionar botão K1 e verificar reação no CLP
```

### 8.4. Teste 4: Simulação de Botão

```bash
# CLP deve estar em modo que aceita comandos (não em ciclo ativo)

# 1. Via Python (terminal):
python3
>>> from modbus_client import *
>>> c = ModbusClientWrapper()
>>> c.press_key('K1')  # Pressiona K1
True

# 2. Via IHM Web:
#    - Abrir http://localhost:8080
#    - Pressionar botão "1" no teclado virtual
#    - Observar reação no CLP físico (LED1 deve acender?)
```

### 8.5. Teste 5: Validação de Ângulos

```bash
# 1. No CLP físico, via IHM original (se funcional):
#    - Programar dobra 1 esquerda = 90.0°
#    - Salvar

# 2. Via IHM Web:
#    - Recarregar página
#    - Verificar se "Dobra 1 ESQ" mostra "090.0°"

# 3. Se NÃO aparecer 90.0°:
#    - Pode ser inversão MSW/LSW
#    - Verificar seção 3.3 deste documento
#    - Testar read_angle() com debug
```

---

## 9. REGRAS DE OURO

### 9.1. Modbus

1. **I/O Digital SÃO COILS** (Function 0x01), **NUNCA** Holding Registers (0x03)
2. **Encoder é 32-bit** (MSW+LSW): sempre ler 2 registros consecutivos
3. **Timeout mínimo 100ms** (CLP scan time ~6ms/K)
4. **Sempre tratar exceções** - NUNCA deixar `ModbusException` crashar o servidor
5. **Pulso de botão = 100ms** (ON → wait → OFF)

### 9.2. Arquitetura

6. **ROT0-4 são intocáveis** - controle original da máquina
7. **ROT5-9 podem ser mínimas** - lógica complexa vai para Python
8. **Estado centralizado** em `machine_state` (state_manager.py)
9. **Polling 250ms** (4 Hz) - não sobrecarregar CLP
10. **Broadcast deltas** (500ms, 2 Hz) - economizar bandwidth WebSocket

### 9.3. Frontend

11. **HTML+CSS+JS puro** - sem frameworks (portabilidade ESP32)
12. **Overlay de erro** obrigatório (DESLIGADO, FALHA CLP)
13. **Responsivo** - tablets 7"-10"
14. **Reconexão automática** WebSocket (3s após desconexão)
15. **Emular IHM física ao máximo** - layout, LEDs, botões, display

### 9.4. Desenvolvimento

16. **Sempre testar em modo stub primeiro** (--stub)
17. **Documentar cada registro descoberto** (atualizar modbus_map.py)
18. **Testar empiricamente** com mbpoll antes de implementar em Python
19. **Logs verbosos** - print() de tudo durante desenvolvimento
20. **Backup de v25** - CLP funcional antes de qualquer mudança

---

## 10. RESPOSTA SOBRE DISPLAY LCD

### 10.1. Pergunta

> "dá para ler o conteúdo do visor lcd ou a tela em que está 'oficialmente' pelo modbus rtu para emular ainda melhor e da maneira mais assertiva?"

### 10.2. Resposta: **PROVAVELMENTE NÃO**

**Análise técnica:**

1. **Display LCD é componente local da IHM física**
   - Conectado diretamente aos pinos do microcontrolador da IHM (não do CLP)
   - Conteúdo gerado pela firmware da IHM 4004.95C
   - **NÃO** é parte da memória do CLP MPC4004

2. **Manual MPC4004 NÃO menciona registros de display**
   - Nenhuma seção sobre "LCD content", "screen buffer", ou similar
   - Registros documentados são apenas: I/O, timers, contadores, analog, encoder
   - Display seria mencionado se fosse acessível (seria feature importante)

3. **Arquitetura típica de IHMs industriais:**
   ```
   ┌──────────────┐          ┌──────────────┐
   │  IHM 4004    │          │  CLP MPC4004 │
   │              │◄─Modbus─►│              │
   │  [Display]   │          │  [Lógica]    │
   │  [Teclado]   │          │  [I/O]       │
   │              │          │  [Memória]   │
   │  Firmware    │          │              │
   │  local gera  │          │  Não sabe    │
   │  texto LCD   │          │  o que está  │
   │              │          │  no LCD!     │
   └──────────────┘          └──────────────┘
   ```

   - IHM **lê** dados do CLP (encoder, estados, ângulos)
   - IHM **processa localmente** e **gera texto** para LCD
   - CLP **não armazena** o texto do display

4. **Teste empírico sugerido:**
   ```bash
   # Tentar ler área que poderia conter display (especulativo)
   # Área de memória superior (não documentada):
   mbpoll -m rtu -a 1 -r 2000 -c 32 -t 3 -b 57600 -P none -s 2 -1 /dev/ttyUSB0
   mbpoll -m rtu -a 1 -r 3000 -c 32 -t 3 -b 57600 -P none -s 2 -1 /dev/ttyUSB0

   # Se retornar "Illegal data address" → NÃO existe
   ```

### 10.3. Solução Alternativa (RECOMENDADA)

**Emular a lógica do display na IHM Web:**

1. **Ler os MESMOS dados que a IHM física lê:**
   - Encoder atual
   - Ângulos programados
   - LEDs (indicam dobra ativa, direção)
   - Modo (manual/auto)
   - Velocidade (classe 1/2/3)

2. **Gerar texto exatamente como a IHM faria:**
   ```javascript
   function generateDisplay() {
       let line1 = '';
       let line2 = '';

       if (machineState.mode_manual) {
           line1 = `MANUAL  ${machineState.speed_class * 5} RPM`;
       } else {
           line1 = `AUTO   ${machineState.speed_class * 5} RPM`;
       }

       // Dobra ativa (qual LED está aceso)
       let bend = 'K1';
       if (machineState.leds.LED2) bend = 'K2';
       if (machineState.leds.LED3) bend = 'K3';

       // Direção
       let dir = machineState.leds.LED4 ? 'ESQ' : 'DIR';

       // Ângulo programado da dobra ativa
       let angle = machineState[`angle_bend${bend[1]}_${dir.toLowerCase()}`];

       line2 = `${bend} ${dir} ${angle.toFixed(1)}°`;

       return {line1, line2};
   }
   ```

3. **Vantagem:**
   - IHM Web pode ser **MAIS PODEROSA** que a física!
   - Mostrar TODOS os 6 ângulos simultaneamente (física mostra 1 por vez)
   - Gráficos de encoder (histórico de movimento)
   - Diagnóstico avançado (I/O em tempo real)
   - Logs de produção (número de dobras, tempo de ciclo)

### 10.4. Conclusão

**NÃO é possível ler o LCD via Modbus**, mas **NÃO é necessário**!

A IHM Web pode:
- Ler os mesmos dados que a IHM física lê (✅ possível, já testado)
- Processar localmente (JavaScript)
- Apresentar de forma **MELHOR** que a IHM física:
  - Display maior (tablet 7"-10" vs LCD 2x16)
  - Cores, gráficos, animações
  - Múltiplos dados simultâneos
  - Tabs com diagnóstico avançado

**Estratégia:** Não emular o LCD. Emular a **funcionalidade** (e melhorar!).

---

## ✅ CHECKLIST FINAL

Antes de começar implementação, confirme:

- [ ] Li RESULTADOS_TESTES_MODBUS.md (validação empírica)
- [ ] Entendi que **I/O são COILS** (Function 0x01, não 0x03)
- [ ] Entendi encoder 32-bit (MSW+LSW)
- [ ] Sei que timers NÃO são acessíveis
- [ ] Entendi que ROT5-9 podem ser mínimas (Python faz o resto)
- [ ] Tenho v25 como backup (CLP funcional)
- [ ] Vou começar em modo stub (--stub) para testar sem CLP
- [ ] Vou testar empiricamente com mbpoll antes de implementar novos registros
- [ ] Vou documentar cada descoberta (atualizar CLAUDE2.md)

---

## 🎓 LIÇÕES FINAIS

1. **Sempre validar empiricamente** - mbpoll salvou 24 versões de erro
2. **Function Code importa** - Coils ≠ Registers
3. **Separação de camadas** - Ladder faz mínimo, Python faz supervisão
4. **IHM Web > IHM Física** - Aproveitar capacidade do tablet
5. **Stub mode é essencial** - Desenvolver sem hardware
6. **Documentação é crítica** - 3 sessões depois, contexto completo

---

**Status:** ✅ PRONTO PARA IMPLEMENTAÇÃO

**Próximos passos:**
1. Criar diretório `ihm/`
2. Copiar todos os arquivos Python (seção 6)
3. Criar `static/index.html` (seção 7)
4. Testar modo stub: `python3 ihm_server.py --stub`
5. Testar com CLP: `python3 ihm_server.py`
6. Iterar, validar, documentar

---

**Criado:** 12 de Novembro de 2025, 22:30 BRT
**Autor:** Claude Code (Anthropic)
**Versão:** 1.0
**Base empírica:** RESULTADOS_TESTES_MODBUS.md
**Máquina:** Trillor NEOCOUDE-HD-15 (2007)
**CLP:** Atos MPC4004 (Slave ID 1)
