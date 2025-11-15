# 📊 MAPA MODBUS - ÁREA 08xx (IHM Web)

**Versão**: v19_COMPLETO
**Data**: 12/11/2025
**Propósito**: Integração IHM Web com CLP MPC4004

---

## 🎯 VISÃO GERAL

A área **08xx** (2176-2304 decimal) é dedicada à comunicação entre o CLP e a IHM Web via Modbus RTU.

**Organização**:
- `08C0-08C5`: Heartbeat/Comunicação (ROT5)
- `0860-0871`: Espelhamento I/O (ROT6)
- `0880-0889`: Inversor WEG (ROT7)
- `08A0-08B1`: Estatísticas (ROT8)
- `08C0-08D3`: Emulação de teclas (ROT9)

**Acesso**:
- **Leitura**: Function Code 0x03 (Read Holding Registers)
- **Escrita**: Function Code 0x06 (Write Single Register) ou 0x05 (Write Single Coil)

---

## 📡 ROT5: HEARTBEAT/COMUNICAÇÃO (08C0-08C5)

| Endereço | Hex | Decimal | Tipo | R/W | Descrição |
|----------|-----|---------|------|-----|-----------|
| 08C0 | 0x08C0 | 2240 | Bit | R | **Heartbeat** - Oscila ON/OFF a cada scan (~6ms) |
| 08C1 | 0x08C1 | 2241 | Bit | R | **Modbus slave ativo** - Cópia de 00BE |
| 08C2 | 0x08C2 | 2242 | Bit | R | **Ciclo ativo** - Cópia de 0191 (hipótese) |
| 08C3 | 0x08C3 | 2243 | Bit | R | **Modo manual** - Cópia de 02FF (hipótese) |
| 08C4 | 0x08C4 | 2244 | 16-bit | R | **Watchdog MSW** - Contador 32-bit (parte alta) |
| 08C5 | 0x08C5 | 2245 | 16-bit | R | **Watchdog LSW** - Contador 32-bit (parte baixa) |

### Uso Típico

```python
# Verificar conexão CLP (heartbeat deve oscilar)
heartbeat = client.read_coil(0x08C0)

# Ler watchdog (32-bit)
watchdog_msw = client.read_register(0x08C4)
watchdog_lsw = client.read_register(0x08C5)
watchdog = (watchdog_msw << 16) | watchdog_lsw

# Detectar travamento (watchdog não incrementa em 2 scans)
if watchdog == last_watchdog_2_scans_ago:
    print("⚠️ CLP pode estar travado!")
```

---

## 🔌 ROT6: ESPELHAMENTO I/O (0860-0871)

### Entradas Digitais E0-E7

| Endereço | Hex | Decimal | Origem | Descrição |
|----------|-----|---------|--------|-----------|
| 0860 | 0x0860 | 2144 | 0100 | **E0** - Entrada digital 0 |
| 0861 | 0x0861 | 2145 | 0101 | **E1** - Entrada digital 1 |
| 0862 | 0x0862 | 2146 | 0102 | **E2** - Entrada digital 2 |
| 0863 | 0x0863 | 2147 | 0103 | **E3** - Emergência (hipótese) |
| 0864 | 0x0864 | 2148 | 0104 | **E4** - Entrada digital 4 |
| 0865 | 0x0865 | 2149 | 0105 | **E5** - Entrada digital 5 |
| 0866 | 0x0866 | 2150 | 0106 | **E6** - Entrada digital 6 |
| 0867 | 0x0867 | 2151 | 0107 | **E7** - Alarme inversor (hipótese) |

### Saídas Digitais S0-S7

| Endereço | Hex | Decimal | Origem | Descrição |
|----------|-----|---------|--------|-----------|
| 0868 | 0x0868 | 2152 | 0180 | **S0** - Saída digital 0 (Run inversor) |
| 0869 | 0x0869 | 2153 | 0181 | **S1** - Saída digital 1 |
| 086A | 0x086A | 2154 | 0182 | **S2** - Saída digital 2 |
| 086B | 0x086B | 2155 | 0183 | **S3** - Saída digital 3 |
| 086C | 0x086C | 2156 | 0184 | **S4** - Saída digital 4 |
| 086D | 0x086D | 2157 | 0185 | **S5** - Saída digital 5 |
| 086E | 0x086E | 2158 | 0186 | **S6** - Saída digital 6 |
| 086F | 0x086F | 2159 | 0187 | **S7** - Saída digital 7 |

### Encoder (32-bit)

| Endereço | Hex | Decimal | Origem | Descrição |
|----------|-----|---------|--------|-----------|
| 0870 | 0x0870 | 2160 | 04D6 | **Encoder MSW** - Posição angular (parte alta) |
| 0871 | 0x0871 | 2161 | 04D7 | **Encoder LSW** - Posição angular (parte baixa) |

### Uso Típico

```python
# Ler entradas
emergencia = client.read_register(0x0863) & 0x0001

# Ler saídas
run_inversor = client.read_register(0x0868) & 0x0001

# Ler encoder (32-bit)
encoder_msw = client.read_register(0x0870)
encoder_lsw = client.read_register(0x0871)
encoder_raw = (encoder_msw << 16) | encoder_lsw
angulo_graus = encoder_raw / 10.0

# Display digital twin
for i in range(8):
    e = client.read_register(0x0860 + i) & 0x0001
    s = client.read_register(0x0868 + i) & 0x0001
    print(f"E{i}: {e}  S{i}: {s}")
```

---

## ⚡ ROT7: INVERSOR WEG (0880-0889)

| Endereço | Hex | Decimal | Tipo | R/W | Descrição |
|----------|-----|---------|------|-----|-----------|
| 0880 | 0x0880 | 2176 | 16-bit | R | **Tensão inversor** - Saída analógica 0 (06E0) |
| 0881 | 0x0881 | 2177 | 16-bit | R | **Classe velocidade** - 1=5rpm, 2=10rpm, 3=15rpm |
| 0882 | 0x0882 | 2178 | 16-bit | R | **Corrente motor** - Entrada analógica 1 (05F1) |
| 0883 | 0x0883 | 2179 | 16-bit | R | **Tensão motor** - Entrada analógica 2 (05F2) |
| 0884 | 0x0884 | 2180 | 16-bit | R | **Potência estimada** - (I × V) / 100 |
| 0885 | 0x0885 | 2181 | Bit | R | **Status Run** - Inversor em operação (cópia S0) |
| 0886 | 0x0886 | 2182 | Bit | R | **Alarme inversor** - Cópia E7 (hipótese) |
| 0887 | 0x0887 | 2183 | 16-bit | R | **Tempo operação MSW** - Segundos (parte alta) |
| 0888 | 0x0888 | 2184 | 16-bit | R | **Tempo operação LSW** - Segundos (parte baixa) |
| 0889 | 0x0889 | 2185 | Bit | W | **Reset tempo** - Zera contador 0887/0888 |

### Uso Típico

```python
# Ler parâmetros inversor
tensao = client.read_register(0x0880)
classe = client.read_register(0x0881)
corrente = client.read_register(0x0882)
potencia = client.read_register(0x0884)

rpm = [5, 10, 15][classe - 1]
print(f"Inversor: {rpm} RPM, {potencia}W, {corrente}A")

# Ler tempo operação (32-bit)
tempo_msw = client.read_register(0x0887)
tempo_lsw = client.read_register(0x0888)
tempo_segundos = (tempo_msw << 16) | tempo_lsw
horas = tempo_segundos / 3600

# Reset tempo (ex: após manutenção)
client.write_coil(0x0889, True)
time.sleep(0.1)
client.write_coil(0x0889, False)
```

---

## 📈 ROT8: ESTATÍSTICAS (08A0-08B1)

| Endereço | Hex | Decimal | Tipo | R/W | Descrição |
|----------|-----|---------|------|-----|-----------|
| 08A0 | 0x08A0 | 2208 | 16-bit | R | **Timestamp MSW** - Minutos desde power-on (parte alta) |
| 08A1 | 0x08A1 | 2209 | 16-bit | R | **Timestamp LSW** - Minutos desde power-on (parte baixa) |
| 08A2 | 0x08A2 | 2210 | 16-bit | R | **Último alarme** - 000=OK, 001=Emerg, 002=Inversor |
| 08AD | 0x08AD | 2221 | 16-bit | R | **Total peças MSW** - Contador produção (parte alta) |
| 08AE | 0x08AE | 2222 | 16-bit | R | **Total peças LSW** - Contador produção (parte baixa) |
| 08AF | 0x08AF | 2223 | 16-bit | R | **Tempo ciclo** - Duração ciclo atual (segundos) |
| 08B0 | 0x08B0 | 2224 | 16-bit | R | **Status consolidado** - Bits: 0=ciclo, 1=emerg, 2=manual |
| 08B1 | 0x08B1 | 2225 | Bit | W | **Reset estatísticas** - Zera contadores |

### Status Consolidado (08B0)

| Bit | Máscara | Descrição |
|-----|---------|-----------|
| 0 | 0x0001 | Ciclo ativo (dobrando) |
| 1 | 0x0002 | Emergência acionada |
| 2 | 0x0004 | Modo manual (vs automático) |
| 3-15 | - | Reservado |

### Uso Típico

```python
# Ler timestamp (32-bit)
ts_msw = client.read_register(0x08A0)
ts_lsw = client.read_register(0x08A1)
minutos = (ts_msw << 16) | ts_lsw
horas_uptime = minutos / 60

# Ler produção (32-bit)
pecas_msw = client.read_register(0x08AD)
pecas_lsw = client.read_register(0x08AE)
total_pecas = (pecas_msw << 16) | pecas_lsw

# Ler tempo ciclo
tempo_ciclo_seg = client.read_register(0x08AF)

# Decodificar status
status = client.read_register(0x08B0)
ciclo_ativo = bool(status & 0x0001)
emergencia = bool(status & 0x0002)
modo_manual = bool(status & 0x0004)

# Reset estatísticas (ex: fim do turno)
client.write_coil(0x08B1, True)
time.sleep(0.1)
client.write_coil(0x08B1, False)

# Dashboard
print(f"Produção: {total_pecas} peças")
print(f"Uptime: {horas_uptime:.1f}h")
print(f"Último alarme: {client.read_register(0x08A2):03d}")
```

---

## ⌨️ ROT9: EMULAÇÃO DE TECLAS (08C0-08D3)

### Teclas Numéricas K0-K9

| Endereço | Hex | Decimal | Tecla | Destino CLP |
|----------|-----|---------|-------|-------------|
| 08C0 | 0x08C0 | 2240 | K0 | 00A9 (169) |
| 08C1 | 0x08C1 | 2241 | K1 | 00A0 (160) |
| 08C2 | 0x08C2 | 2242 | K2 | 00A1 (161) |
| 08C3 | 0x08C3 | 2243 | K3 | 00A2 (162) |
| 08C4 | 0x08C4 | 2244 | K4 | 00A3 (163) |
| 08C5 | 0x08C5 | 2245 | K5 | 00A4 (164) |
| 08C6 | 0x08C6 | 2246 | K6 | 00A5 (165) |
| 08C7 | 0x08C7 | 2247 | K7 | 00A6 (166) |
| 08C8 | 0x08C8 | 2248 | K8 | 00A7 (167) |
| 08C9 | 0x08C9 | 2249 | K9 | 00A8 (168) |

### Teclas de Função

| Endereço | Hex | Decimal | Tecla | Destino CLP |
|----------|-----|---------|-------|-------------|
| 08CA | 0x08CA | 2250 | S1 | 00DC (220) |
| 08CB | 0x08CB | 2251 | S2 | 00DD (221) |
| 08CC | 0x08CC | 2252 | ENTER | 0025 (37) |
| 08CD | 0x08CD | 2253 | ESC | 00BC (188) |
| 08CE | 0x08CE | 2254 | EDIT | 0026 (38) |
| 08CF | 0x08CF | 2255 | Arrow UP | 00AC (172) |
| 08D0 | 0x08D0 | 2256 | Arrow DOWN | 00AD (173) |

### Diagnóstico

| Endereço | Hex | Decimal | Tipo | R/W | Descrição |
|----------|-----|---------|------|-----|-----------|
| 08D1 | 0x08D1 | 2257 | 16-bit | R | **Contador comandos MSW** - Total teclas (parte alta) |
| 08D2 | 0x08D2 | 2258 | 16-bit | R | **Contador comandos LSW** - Total teclas (parte baixa) |
| 08D3 | 0x08D3 | 2259 | Bit | W | **Reset contador** - Zera 08D1/08D2 |

### Uso Típico

```python
# Simular pressão de tecla K1
client.write_coil(0x08C1, True)
time.sleep(0.1)
client.write_coil(0x08C1, False)

# Trocar modo (S1)
client.write_coil(0x08CA, True)
time.sleep(0.1)
client.write_coil(0x08CA, False)

# Editar ângulo (sequência: EDIT → K1 → K2 → K0 → ENTER)
def press_key(addr):
    client.write_coil(addr, True)
    time.sleep(0.1)
    client.write_coil(addr, False)
    time.sleep(0.05)

press_key(0x08CE)  # EDIT
press_key(0x08C1)  # K1
press_key(0x08C2)  # K2
press_key(0x08C0)  # K0
press_key(0x08CC)  # ENTER

# Ler contador comandos (32-bit)
cnt_msw = client.read_register(0x08D1)
cnt_lsw = client.read_register(0x08D2)
total_comandos = (cnt_msw << 16) | cnt_lsw
print(f"Total comandos enviados: {total_comandos}")
```

---

## 🔧 CONVERSÕES E FÓRMULAS

### Encoder → Graus

```python
encoder_raw = (msw << 16) | lsw
graus = encoder_raw / 10.0
```

### Potência Motor

```python
corrente = read_register(0x0882)  # Fator escala depende do sensor
tensao = read_register(0x0883)    # Fator escala depende do sensor
potencia = read_register(0x0884)  # Já calculado no CLP
# ou calcular manualmente:
potencia = (corrente * tensao) / 100
```

### Tempo → Horas

```python
# Tempo operação inversor (segundos)
tempo_seg = (msw << 16) | lsw
horas = tempo_seg / 3600

# Timestamp sistema (minutos)
minutos = (msw << 16) | lsw
horas_uptime = minutos / 60
```

### Eficiência

```python
pecas = (msw << 16) | lsw
horas_uptime = minutos / 60
pecas_por_hora = pecas / horas_uptime if horas_uptime > 0 else 0
```

---

## 🚨 CÓDIGOS DE ALARME (08A2)

| Código | Descrição | Origem |
|--------|-----------|--------|
| 000 | **OK** - Nenhum alarme ativo | - |
| 001 | **Emergência** - Botão emergência acionado | E3 (0103) |
| 002 | **Alarme inversor** - Falha no inversor WEG | E7 (0107) |
| 003+ | Reservado para expansão futura | - |

---

## 📚 EXEMPLOS DE INTEGRAÇÃO

### Python (modbus_map.py)

```python
# Heartbeat/Comunicação
HEARTBEAT_BIT = 0x08C0
MODBUS_SLAVE_ACTIVE = 0x08C1
CYCLE_ACTIVE = 0x08C2
MANUAL_MODE = 0x08C3
WATCHDOG_MSW = 0x08C4
WATCHDOG_LSW = 0x08C5

# Espelhamento I/O
INPUT_E0 = 0x0860
OUTPUT_S0 = 0x0868
ENCODER_MSW = 0x0870
ENCODER_LSW = 0x0871

# Inversor WEG
INVERTER_VOLTAGE = 0x0880
SPEED_CLASS = 0x0881
MOTOR_CURRENT = 0x0882
MOTOR_VOLTAGE = 0x0883
MOTOR_POWER = 0x0884
INVERTER_RUN = 0x0885
INVERTER_ALARM = 0x0886
OPERATION_TIME_MSW = 0x0887
OPERATION_TIME_LSW = 0x0888
RESET_OPERATION_TIME = 0x0889

# Estatísticas
TIMESTAMP_MSW = 0x08A0
TIMESTAMP_LSW = 0x08A1
LAST_ALARM = 0x08A2
TOTAL_PIECES_MSW = 0x08AD
TOTAL_PIECES_LSW = 0x08AE
CYCLE_TIME = 0x08AF
STATUS_CONSOLIDATED = 0x08B0
RESET_STATS = 0x08B1

# Emulação teclas
KEY_K0 = 0x08C0
KEY_K1 = 0x08C1
KEY_S1 = 0x08CA
KEY_ENTER = 0x08CC
COMMAND_COUNTER_MSW = 0x08D1
COMMAND_COUNTER_LSW = 0x08D2
RESET_COUNTER = 0x08D3
```

### JavaScript (index.html)

```javascript
// Polling heartbeat
let lastHeartbeat = null;
setInterval(() => {
    if (machineState.heartbeat !== lastHeartbeat) {
        updateConnectionStatus('CONECTADO', 'green');
        lastHeartbeat = machineState.heartbeat;
    } else {
        updateConnectionStatus('SEM RESPOSTA', 'red');
    }
}, 500);

// Display encoder
function updateEncoderDisplay(msw, lsw) {
    const raw = (msw << 16) | lsw;
    const degrees = raw / 10.0;
    document.getElementById('angle').textContent = degrees.toFixed(1) + '°';
}

// Botão K1
document.getElementById('btn-k1').onclick = () => {
    websocket.send(JSON.stringify({
        action: 'press_key',
        address: 0x08C1
    }));
};

// Digital twin I/O
function updateDigitalTwin(state) {
    for (let i = 0; i < 8; i++) {
        document.getElementById(`e${i}`).classList.toggle('active', state[`e${i}`]);
        document.getElementById(`s${i}`).classList.toggle('active', state[`s${i}`]);
    }
}
```

---

## ⚠️ OBSERVAÇÕES IMPORTANTES

### Endereços Hipotéticos

Alguns endereços são **hipóteses** baseadas em análise parcial da ladder:
- `0191` (ciclo ativo)
- `02FF` (modo manual)
- `0103` (emergência)
- `0107` (alarme inversor)

**Ação necessária**: Analisar ROT0-4 no WinSUP para confirmar/corrigir.

### Debounce Automático

ROT9 usa instrução `SETR` que **seta** o bit sem resetar automaticamente.
O pulso deve ser gerenciado pelo software Python (100ms ON + OFF).

### Scan Time

CLP MPC4004 scan ~6ms/K (K = tamanho programa em KB).
Com 10 rotinas (~50K ladder), scan ~300ms típico.
**Polling recomendado**: 500ms (seguro) ou 250ms (agressivo).

### 32-bit Reads

Sempre ler MSW primeiro, depois LSW:
```python
msw = read_register(addr)
lsw = read_register(addr + 1)
value = (msw << 16) | lsw
```

---

═══════════════════════════════════════════════════════════════

**Versão**: v19_COMPLETO
**Arquivo**: `CLP_10_ROTINAS_v19_COMPLETO.sup`
**Status**: ✅ Pronto para produção

**Documentação complementar**:
- `STATUS_v19_COMPLETO.txt`
- `README_v19_COMPLETO.md`

═══════════════════════════════════════════════════════════════
