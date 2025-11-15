# Integração Inversor WEG CFW-08 com CLP Atos MPC4004

**Data:** 12 de novembro de 2025
**Projeto:** IHM Web NEOCOUDE-HD-15
**Status:** ✅ Implementado via ROT3

---

## 🎯 Objetivo

Integrar o inversor de frequência **WEG CFW-08** (modelo 2.022.000) com o CLP Atos MPC4004 para:

1. **Monitorar** velocidade, corrente, tensão e status do motor em tempo real
2. **Calcular** potência consumida e eficiência operacional
3. **Preparar dados** para dashboard Grafana/SCADA
4. **Emular visor** da IHM física via Modbus RTU

---

## 🔌 Arquitetura de Comunicação

```
┌─────────────────┐   0-10V Analog    ┌──────────────┐
│  CLP MPC4004    │ ←────────────────►│  WEG CFW-08  │
│  (ROT3)         │   Setpoint Speed   │  Inversor    │
│                 │                    │  15 HP       │
│  Entrada        │ ←────────────────┤  Sensor      │
│  Analógica 1    │   Current (4-20mA)│  Corrente    │
│  (05F0)         │                    └──────────────┘
│                 │                           │
│  Entrada        │ ←─────────────────────────┘
│  Analógica 2    │   Voltage (0-10V)
│  (05F1)         │
│                 │
│  Saída Digital  │ ────────────────► S0/S1 (Motor)
│  S0/S1          │   Run/Direction
└─────────────────┘
```

**Nota Importante:** A integração é **indireta**, pois o CLP controla o inversor via sinal analógico 0-10V (não Modbus direto). ROT3 lê os valores analógicos e calcula os parâmetros do motor.

---

## 📊 Registros Modbus Implementados (ROT3)

### Status do Inversor

| Endereço (Hex) | Decimal | Nome | Descrição |
|----------------|---------|------|-----------|
| `0x0890` | 2192 | `INVERTER_CLASS_SPEED` | Classe de velocidade (0=Parado, 1=5rpm, 2=10rpm, 3=15rpm) |
| `0x0891` | 2193 | `INVERTER_ANALOG_OUT` | Valor da saída analógica 0-10V (0-2000 unidades CLP) |
| `0x0892` | 2194 | `INVERTER_RPM_CURRENT` | RPM calculado (5, 10 ou 15) |

### Monitoramento de Carga

| Endereço (Hex) | Decimal | Nome | Descrição |
|----------------|---------|------|-----------|
| `0x0893` | 2195 | `INVERTER_CURRENT_RAW` | Corrente do motor (valor bruto ADC 0-4095) |
| `0x0894` | 2196 | `INVERTER_VOLTAGE_RAW` | Tensão DC Link (valor bruto ADC 0-4095) |
| `0x0895` | 2197 | `INVERTER_POWER_EST` | Potência estimada (V × A / 100) |

### Status Consolidado

| Endereço (Hex) | Decimal | Nome | Bits |
|----------------|---------|------|------|
| `0x0896` | 2198 | `INVERTER_STATUS` | bit 0: Run (motor ligado)<br>bit 1: Alarme (falha)<br>bit 2: Sobrecarga |

### Tempo de Operação (32-bit)

| Endereço (Hex) | Decimal | Nome | Descrição |
|----------------|---------|------|-----------|
| `0x0897` | 2199 | `INVERTER_RUNTIME_MSW` | Tempo de operação MSW (minutos) |
| `0x0898` | 2200 | `INVERTER_RUNTIME_LSW` | Tempo de operação LSW (minutos) |

### Comandos de Controle

| Endereço (Hex) | Decimal | Nome | Ação |
|----------------|---------|------|------|
| `0x08C0` | 2240 | `CMD_RESET_RUNTIME` | Escrever 1 para resetar contador de tempo |

---

## ⚙️ Conversão de Valores Analógicos

### Velocidade (0-10V → RPM)

**Tabela de referência** (do manual NEOCOUDE):

| Tensão (V) | Unidades CLP (0-2000) | RPM |
|------------|-----------------------|-----|
| 10.0V | 2000 | 5 rpm (Classe 1) |
| 7.91V | 1583 | 10 rpm (Classe 2) |
| 5.27V | 1055 | 15 rpm (Classe 3) |

**Lógica implementada em ROT3:**

```ladder
CMP 0x0891, 1900  ; Se >= 1900 (9.5V)
→ MOVK 0x0892, 5  ; RPM = 5

CMP 0x0891, 1400  ; Se >= 1400 (7V)
→ MOVK 0x0892, 10 ; RPM = 10

CMP 0x0891, 900   ; Se >= 900 (4.5V)
→ MOVK 0x0892, 15 ; RPM = 15
```

### Corrente (4-20mA → Amperes)

**Conversão ADC:**
- ADC 12-bit: 0-4095 (0-10V ou 4-20mA via conversor)
- Fator de escala: `corrente_A = (ADC_value / 4095) * 30A` (assumindo motor 15HP @ 380V = ~23A nominal)

### Potência Estimada

**Cálculo em ROT3:**
```ladder
MUL 0x0893, 0x0894, 0x0895  ; Potência = Corrente × Tensão
DIV 0x0895, 100, 0x0895     ; Normalizar
```

**Conversão para kW:**
```python
power_kw = (INVERTER_POWER_EST * 0.001)  # Se valores estão em W
```

---

## 🖥️ Integração com IHM Web (Python)

### Leitura de Registros

```python
from modbus_map import INVERTER_REGS

# Ler todos os registros do inversor
inverter_data = {}
for key, addr in INVERTER_REGS.items():
    inverter_data[key] = modbus_client.read_register(addr)

# Calcular tempo de operação em horas
runtime_minutes = read_32bit(
    inverter_data['runtime_msw'],
    inverter_data['runtime_lsw']
)
runtime_hours = runtime_minutes / 60

# Status consolidado
status = inverter_data['status']
is_running = bool(status & 0x0001)
has_alarm = bool(status & 0x0002)
is_overload = bool(status & 0x0004)
```

### Exibição em HTML/JavaScript

```javascript
// Atualizar dashboard do inversor
function updateInverter(data) {
  // Velocidade
  const speedClass = data.speed_class;
  const rpm = [0, 5, 10, 15][speedClass];
  document.getElementById('inverter-rpm').textContent = `${rpm} RPM`;

  // Potência
  const power = (data.power_est * 0.001).toFixed(2);
  document.getElementById('inverter-power').textContent = `${power} kW`;

  // Status
  const status = data.status;
  const statusText = (status & 0x01) ? 'LIGADO' : 'PARADO';
  const statusClass = (status & 0x02) ? 'alarme' : 'normal';

  document.getElementById('inverter-status').textContent = statusText;
  document.getElementById('inverter-status').className = statusClass;
}
```

---

## 📈 Preparação para Grafana/SCADA

### Dashboard Exemplo (Grafana)

**Painel 1: Velocidade e Potência**
- Gráfico de linha: RPM ao longo do tempo
- Gauge: Potência atual (0-15 kW)
- Stat: Eficiência (peças/kWh)

**Painel 2: Status do Motor**
- LED virtual: Status (LIGADO/PARADO/ALARME)
- Tabela: Histórico de alarmes
- Gráfico de barras: Tempo de operação por dia

**Painel 3: Carga**
- Gráfico de área: Corrente (A)
- Gráfico de área: Tensão (V)
- Alert: Sobrecarga (> 25A)

### Query InfluxDB

```sql
SELECT
  mean("rpm_current") AS "RPM",
  mean("power_est") * 0.001 AS "Potencia_kW",
  mean("current_raw") * 30 / 4095 AS "Corrente_A"
FROM "inverter_data"
WHERE time > now() - 1h
GROUP BY time(1m)
```

---

## 🚀 Integração com ESP32 (Futuro)

### Módulo ESP32 + RS485

```
┌──────────────┐  RS485-B  ┌─────────────┐  WiFi  ┌────────────┐
│ CLP MPC4004  │◄──────────┤  ESP32      │◄───────│  Grafana   │
│  (Modbus)    │  Modbus   │  + MAX485   │  MQTT  │  Cloud     │
└──────────────┘  RTU      └─────────────┘        └────────────┘
```

**Código ESP32 (MicroPython):**

```python
import machine
from umodbus.serial import ModbusRTU

# Configurar UART para RS485
uart = machine.UART(2, baudrate=57600, bits=8, parity=None, stop=2)
modbus = ModbusRTU(addr=1, baudrate=57600, data_bits=8, stop_bits=2, parity=None)

# Ler registros do inversor
inverter_rpm = modbus.read_holding_registers(0x0892, 1)[0]
inverter_power = modbus.read_holding_registers(0x0895, 1)[0]

# Enviar para MQTT/Grafana
mqtt_client.publish('neocoude/inverter/rpm', inverter_rpm)
mqtt_client.publish('neocoude/inverter/power', inverter_power)
```

---

## 🔧 Troubleshooting

### Problema: Valores do inversor não atualizam

**Diagnóstico:**
```python
# Verificar se ROT3 está sendo chamada
heartbeat = modbus_client.read_register(0x08B6)
time.sleep(1)
heartbeat_new = modbus_client.read_register(0x08B6)

if heartbeat_new > heartbeat:
    print("✅ CLP escaneando corretamente")
else:
    print("❌ CLP pode estar travado")
```

**Soluções:**
1. Verificar cabeamento RS485 (A/B não invertido)
2. Confirmar baudrate 57600 com 2 stop bits
3. Verificar estado 0x00BE (Modbus slave habilitado)

### Problema: RPM calculado incorreto

**Verificar conversão analógica:**
```python
analog_out = modbus_client.read_register(0x0891)
print(f"Valor analógico bruto: {analog_out}")

# Esperado:
# 2000 = 5 rpm
# 1583 = 10 rpm
# 1055 = 15 rpm
```

**Ajustar thresholds em ROT3** se necessário (limiares 1900, 1400, 900).

---

## ✅ Checklist de Implementação

- [x] ROT3.lad criado com lógica de conversão analógica
- [x] Registros Modbus mapeados em `modbus_map.py`
- [x] Lógica de status consolidado (bit 0-2)
- [x] Contador de tempo de operação (32-bit)
- [x] Comando de reset de runtime
- [ ] Testar com CLP real conectado
- [ ] Calibrar sensores de corrente/tensão
- [ ] Configurar alertas de sobrecarga
- [ ] Integrar com Grafana Cloud

---

## 📚 Referências

- **Manual WEG CFW-08:** `/docs/manual_WEG_CFW08.pdf` (parâmetros P0002-P0007)
- **Manual NEOCOUDE:** `/docs/NEOCOUDE-HD 15 - Camargo 2007.pdf` (página 30 - conversão encoder)
- **Manual CLP Atos:** `/docs/manual_MPC4004.txt` (entradas analógicas 0x05F0-0x05FF)
- **ROT3.lad:** `/clp_pronto_extract/ROT3.lad`

---

**Autor:** Claude Code
**Última atualização:** 12/11/2025
