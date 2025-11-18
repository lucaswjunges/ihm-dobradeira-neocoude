# 🔄 Análise: Migração para ESP32 / Raspberry Pi Pico W2

## 📊 Comparação Técnica

| Critério | Notebook Ubuntu | ESP32 | Raspberry Pi Pico W2 |
|----------|----------------|-------|---------------------|
| **Processador** | Intel/AMD (GHz) | Xtensa 240MHz | RP2350 150MHz |
| **RAM** | 8-16GB | 520KB | 520KB |
| **Python** | CPython 3.x | MicroPython | MicroPython |
| **Custo** | R$ 2.000+ | R$ 40-80 | R$ 80-120 |
| **Consumo** | 30-60W | 0.5-1W | 0.3-0.8W |
| **WiFi integrado** | Sim (via USB) | Sim | Sim |
| **RS485** | USB-FTDI | Nativo (UART) | Nativo (UART) |
| **Confiabilidade** | Alta (mas é PC) | Muito Alta | Muito Alta |
| **Tamanho** | Grande | 5x3cm | 2x5cm |

---

## ✅ OPÇÃO 1: ESP32 (RECOMENDADO)

### Hardware Sugerido
**ESP32-WROOM-32D ou ESP32-DevKit V1**
- Preço: R$ 40-60
- WiFi 802.11 b/g/n
- 3x UART (pode usar UART2 para RS485)
- 4MB Flash
- 520KB RAM

**Módulo RS485:**
- MAX485 ou MAX3485 (R$ 8-15)
- Conexão direta nas GPIOs do ESP32

**Alimentação:**
- Fonte 5V 2A (R$ 15-25)
- **OU** alimentar direto do painel 24V DC com conversor buck (R$ 10)

### 🔧 Esforço de Migração: **MÉDIO (3-5 dias)**

#### O que FUNCIONA sem mudanças:
1. ✅ **HTML/CSS/JavaScript** → 100% compatível (serve como arquivo estático)
2. ✅ **WebSocket** → MicroPython tem `websockets` ou `uasyncio`
3. ✅ **Modbus RTU** → Biblioteca `umodbus` disponível

#### O que PRECISA adaptar:

**1. pymodbus → umodbus (2h trabalho)**
```python
# Código atual (pymodbus)
from pymodbus.client import ModbusSerialClient
client = ModbusSerialClient(port='/dev/ttyUSB0', baudrate=57600)

# MicroPython (umodbus)
from umodbus.serial import Serial as ModbusRTUMaster
client = ModbusRTUMaster(uart_id=2, baudrate=57600, tx_pin=17, rx_pin=16)
```

**2. asyncio → uasyncio (1h trabalho)**
```python
# Código atual
import asyncio
await asyncio.sleep(0.5)

# MicroPython
import uasyncio as asyncio  # Apenas trocar import!
await asyncio.sleep_ms(500)
```

**3. aiohttp → microdot (4h trabalho)**
```python
# Código atual (aiohttp)
from aiohttp import web
app = web.Application()
app.router.add_get('/', handler)

# MicroPython (microdot)
from microdot import Microdot
app = Microdot()
@app.route('/')
def handler(request):
    return send_file('index.html')
```

**4. Reduzir logs verbosos (1h)**
- Remover prints DEBUG
- RAM limitada: não pode logar tudo

**5. Configuração WiFi (1h)**
```python
import network
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect('SSID_FABRICA', 'senha')
```

### 📦 Bibliotecas MicroPython Necessárias:
```bash
# Instalar via upip (gerenciador do MicroPython)
upip.install('microdot')           # Web server
upip.install('umodbus')             # Modbus RTU
upip.install('uasyncio')            # Async (já vem no core)
upip.install('ujson')               # JSON (já vem no core)
```

### ⚙️ Configuração Pinos ESP32:
```python
# RS485
UART_TX = 17  # TX do ESP32 → DI do MAX485
UART_RX = 16  # RX do ESP32 → RO do MAX485
RS485_DE = 4  # Direction Enable → DE/RE do MAX485

# LEDs (opcional)
LED_STATUS = 2  # LED interno
LED_WIFI = 5
LED_MODBUS = 18
```

### 🎯 Vantagens ESP32:
1. ✅ **Embarcado**: Monta dentro do painel elétrico
2. ✅ **Barato**: R$ 50 total (ESP32 + MAX485)
3. ✅ **Confiável**: Sem OS, boot em 2s
4. ✅ **Industrial**: Faixa temperatura -40°C a +85°C
5. ✅ **Baixo consumo**: 0.5W vs 40W do notebook
6. ✅ **RS485 nativo**: Sem USB-FTDI (mais estável)

### ⚠️ Desvantagens ESP32:
1. ❌ **RAM limitada**: 520KB (vs 8GB do PC)
   - **Solução:** Não carregar tudo na RAM, usar streaming
2. ❌ **Debugar é mais difícil**: Sem IDE completo
   - **Solução:** Thonny IDE + REPL via USB
3. ❌ **Primeira vez é mais trabalhosa**: Configurar ambiente
   - **Solução:** Já está tudo mapeado aqui!

---

## ✅ OPÇÃO 2: Raspberry Pi Pico W2

### Hardware
**Raspberry Pi Pico W2**
- Preço: R$ 80-120
- WiFi 802.11n
- RP2350 (150MHz dual-core)
- 2MB Flash
- 520KB RAM

**Módulo RS485:**
- Mesmo MAX485 (R$ 8-15)

### 🔧 Esforço de Migração: **MÉDIO-ALTO (4-6 dias)**

#### Vantagens sobre ESP32:
1. ✅ **Dual-core**: Pode separar Modbus e WebSocket em cores diferentes
2. ✅ **Mais RAM disponível**: 520KB mas gerenciamento melhor
3. ✅ **Documentação melhor**: Raspberry Pi Foundation
4. ✅ **Debug mais fácil**: Thonny + USB drag-and-drop

#### Desvantagens sobre ESP32:
1. ❌ **Mais caro**: R$ 80-120 vs R$ 40-60
2. ❌ **Menos bibliotecas Modbus**: Comunidade menor que ESP32
3. ❌ **Pinos 3.3V**: Precisa level shifter para RS485 (ESP32 aguenta 5V)

### Veredicto Pico W2:
**Funciona, mas ESP32 é melhor custo-benefício para este projeto.**

---

## ❌ OPÇÃO 3: Manter Notebook (Atual)

### Vantagens:
1. ✅ **Já está funcionando**: Zero trabalho adicional
2. ✅ **Debug fácil**: Terminal, logs completos
3. ✅ **Python completo**: Todas as bibliotecas disponíveis
4. ✅ **Prototipação**: Ideal para ajustes rápidos

### Desvantagens:
1. ❌ **Não é solução permanente**: Notebook pode ser necessário em outro lugar
2. ❌ **Consumo alto**: 40W contínuo
3. ❌ **Frágil**: Disco, ventoinhas, tela podem quebrar
4. ❌ **Custo oportunidade**: Notebook vale R$ 2.000+

### Recomendação:
**Use notebook para validação/homologação (1-2 semanas), depois migra para ESP32.**

---

## 🎯 PLANO RECOMENDADO: Migração Gradual

### FASE 1: Homologação com Notebook (HOJE)
- ✅ Instalar na fábrica
- ✅ Validar com operadores (1-2 semanas)
- ✅ Ajustes finos baseados no uso real
- ✅ Confirmar estabilidade

### FASE 2: Migração para ESP32 (Depois de validado)
**Tempo estimado: 3-5 dias de trabalho**

**Dia 1: Setup Hardware**
- Comprar ESP32 + MAX485 + fonte
- Montar protótipo em protoboard
- Testar comunicação RS485 básica
- Piscar LED

**Dia 2: Porta Modbus Client**
- Instalar MicroPython no ESP32
- Portar `modbus_client.py` para `umodbus`
- Testar leitura de registros 0x04D6, 0x0500, 0x094C
- Validar escrita de ângulos

**Dia 3: Porta State Manager + WebSocket**
- Portar `state_manager.py` para `uasyncio`
- Implementar WebSocket com `microdot-websocket`
- Testar broadcast de estado

**Dia 4: Porta Web Server**
- Implementar servidor HTTP com `microdot`
- Servir `index.html` da Flash
- Configurar WiFi AP (ponto de acesso próprio)
- Testar conexão tablet → ESP32

**Dia 5: Testes Integrados**
- Montar em caixa DIN rail
- Instalar no painel
- Testes de stress (24h ligado)
- Validação final com operadores

### FASE 3: Produção (Permanente)
- ESP32 instalado no painel
- Tablet conecta direto no ESP32 (sem notebook)
- Backup do firmware em pendrive

---

## 💰 Análise Financeira

| Item | Notebook (atual) | ESP32 (futuro) | Economia |
|------|------------------|----------------|----------|
| **Hardware** | R$ 0 (já tem) | R$ 80 | - |
| **Consumo/mês** | R$ 30 (40W × 730h × R$0.80/kWh) | R$ 0.30 | **R$ 29.70/mês** |
| **Manutenção/ano** | R$ 200 (risco) | R$ 10 | **R$ 190/ano** |
| **ROI** | - | 3 meses | ✅ |

**Break-even: 3 meses**
**Economia em 5 anos: R$ 1.800**

---

## 📋 Checklist de Compatibilidade do Código Atual

| Componente | Compatibilidade ESP32 | Esforço |
|------------|----------------------|---------|
| **modbus_map.py** | ✅ 100% (apenas constantes) | 0h |
| **modbus_client.py** | 🟡 80% (trocar pymodbus→umodbus) | 2h |
| **state_manager.py** | ✅ 95% (asyncio→uasyncio) | 1h |
| **main_server.py** | 🟡 70% (aiohttp→microdot) | 4h |
| **static/index.html** | ✅ 100% (navegador não muda) | 0h |
| **WebSocket protocol** | ✅ 100% (RFC 6455 padrão) | 0h |

**Total estimado: 7-10 horas de trabalho efetivo**

---

## 🔧 Código Exemplo: ESP32 (Resumido)

```python
# main.py para ESP32
import uasyncio as asyncio
from machine import UART, Pin
from microdot import Microdot
from microdot.websocket import with_websocket
from umodbus.serial import Serial as ModbusRTUMaster

# Configuração WiFi
import network
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect('WiFi_Fabrica', 'senha123')

# Configuração RS485
uart = UART(2, baudrate=57600, tx=17, rx=16, timeout=500)
rs485_de = Pin(4, Pin.OUT)
modbus = ModbusRTUMaster(uart=uart, ctrl_pin=rs485_de)

# Web server
app = Microdot()

@app.route('/')
def index(request):
    return send_file('index.html')

@app.route('/ws')
@with_websocket
async def websocket(request, ws):
    while True:
        # Ler encoder
        encoder_msw = modbus.read_holding_registers(1, 0x04D6, 1)[0]
        encoder_lsw = modbus.read_holding_registers(1, 0x04D7, 1)[0]
        encoder_raw = (encoder_msw << 16) | encoder_lsw
        
        # Enviar via WebSocket
        await ws.send(ujson.dumps({
            'type': 'state_update',
            'data': {'encoder_raw': encoder_raw, 'encoder_degrees': encoder_raw / 10.0}
        }))
        
        await asyncio.sleep_ms(500)

# Iniciar servidor
app.run(port=8080)
```

**Isso é 90% do código necessário!**

---

## 🎯 CONCLUSÃO E RECOMENDAÇÃO

### Para HOJE na fábrica:
✅ **Use o notebook** - está pronto, testado e funcional

### Para produção permanente (depois de 2 semanas):
✅ **Migre para ESP32** - melhor custo-benefício

**Esforço total: 3-5 dias de trabalho**
**Custo: R$ 80 (hardware)**
**Economia: R$ 30/mês (energia + confiabilidade)**
**Complexidade: Média (você tem experiência de embedded?)**

### Se você NÃO tem experiência com ESP32/MicroPython:
- Tempo real: 5-7 dias (inclui curva de aprendizado)
- **Alternativa:** Contratar alguém (R$ 500-1.000) para fazer migração
- **OU:** Raspberry Pi 4 com Raspbian (Python completo, R$ 400)

### Se você TEM experiência com ESP32/MicroPython:
- Tempo real: 3-4 dias
- **Faça você mesmo!** O código já está 70% pronto

---

**Resposta direta:** 
- ✅ ESP32 = **3-5 dias de trabalho** (melhor opção)
- ✅ Pico W2 = **4-6 dias de trabalho** (funciona, mas ESP32 é melhor)
- ❌ Sem mudanças = **impossível** (arquiteturas diferentes)

**Recomendação profissional:**
1. Hoje: Instala notebook na fábrica
2. Valida com operadores 1-2 semanas
3. Compra ESP32 (R$ 80)
4. Migra em 1 semana de trabalho
5. Instala ESP32 no painel permanentemente

**Quer que eu prepare o código base para ESP32?** Posso gerar os 4 arquivos principais adaptados.
