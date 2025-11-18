# TODO - Migração ESP32

## ✅ FASE 1: Estrutura Base (CONCLUÍDA)

- [x] Criar pasta `ihm_esp32/`
- [x] Criar `CLAUDE.md` (documentação completa)
- [x] Criar `README.md` (guia rápido)
- [x] Copiar `modbus_map.py` (100% compatível)
- [x] Copiar `static/index.html` (100% compatível)
- [x] Criar `boot.py` (configuração WiFi)

---

## ⏳ FASE 2: Código MicroPython (PENDENTE)

### Arquivos a Criar

#### 2.1 `modbus_client_esp32.py`
**Complexidade:** Média (2h)
**Baseado em:** `../ihm/modbus_client.py`

**Mudanças necessárias:**
```python
# Ubuntu
from pymodbus.client import ModbusSerialClient
client = ModbusSerialClient(port='/dev/ttyUSB0', baudrate=57600)

# ESP32
from machine import UART, Pin
uart = UART(2, baudrate=57600, tx=17, rx=16, timeout=500)
# Usar biblioteca umodbus
```

**Checklist:**
- [ ] Importar `machine.UART`
- [ ] Configurar pinos GPIO17/16
- [ ] Pino DE/RE (GPIO4) para controle de direção RS485
- [ ] Adaptar `read_register()` para umodbus
- [ ] Adaptar `write_register()` para umodbus
- [ ] Adaptar `read_coil()` para umodbus
- [ ] Adaptar `write_coil()` para umodbus
- [ ] Remover logs DEBUG verbose (economia de RAM)
- [ ] Testar leitura encoder (0x04D6/0x04D7)

#### 2.2 `state_manager_esp32.py`
**Complexidade:** Baixa (1h)
**Baseado em:** `../ihm/state_manager.py`

**Mudanças necessárias:**
```python
# Ubuntu
import asyncio
await asyncio.sleep(0.5)

# ESP32
import uasyncio as asyncio
await asyncio.sleep_ms(500)
```

**Checklist:**
- [ ] Trocar `import asyncio` por `import uasyncio as asyncio`
- [ ] Trocar `asyncio.sleep(X)` por `asyncio.sleep_ms(X*1000)`
- [ ] Remover prints DEBUG
- [ ] Ajustar intervalo de polling (250ms → 500ms para economia)
- [ ] Adicionar `gc.collect()` após cada poll (garbage collector)

#### 2.3 `main.py`
**Complexidade:** Média (2-3h)
**Baseado em:** `../ihm/main_server.py`

**Mudanças necessárias:**
```python
# Ubuntu
from aiohttp import web
app = web.Application()

# ESP32
from microdot import Microdot, send_file
from microdot.websocket import with_websocket
app = Microdot()
```

**Checklist:**
- [ ] Importar `microdot` e `microdot_websocket`
- [ ] Adaptar rotas HTTP:
  - `@app.route('/')` para servir index.html
  - `@app.route('/ws')` para WebSocket
- [ ] Adaptar handler WebSocket:
  - `@with_websocket` decorator
  - `await ws.send()` para enviar JSON
  - `await ws.receive()` para receber comandos
- [ ] Remover módulo `argparse` (não disponível)
- [ ] Simplificar inicialização (sem argumentos CLI)
- [ ] Adicionar LED de status (GPIO2)
- [ ] Implementar watchdog timer (opcional)

---

## ⏳ FASE 3: Bibliotecas Externas (PENDENTE)

### 3.1 Microdot (Web Server)

**Download:**
```bash
cd /home/lucas-junges/Documents/clientes/w\&co/ihm_esp32

# Microdot core
wget https://raw.githubusercontent.com/miguelgrinberg/microdot/main/src/microdot/microdot.py -O lib/microdot.py

# WebSocket support
wget https://raw.githubusercontent.com/miguelgrinberg/microdot/main/src/microdot/microdot_websocket.py -O lib/microdot_websocket.py
```

**Checklist:**
- [ ] Baixar `microdot.py`
- [ ] Baixar `microdot_websocket.py`
- [ ] Verificar imports no código
- [ ] Testar servidor básico (hello world)

### 3.2 uModbus (Modbus RTU)

**Opção A: Repositório PycomOfficial**
```bash
git clone https://github.com/pycom/pycom-modbus.git /tmp/pycom-modbus
cp -r /tmp/pycom-modbus/umodbus lib/
rm -rf /tmp/pycom-modbus
```

**Opção B: Minimal (criar manualmente)**
Criar arquivo simplificado baseado na documentação MicroPython.

**Checklist:**
- [ ] Escolher opção (A recomendado)
- [ ] Copiar arquivos para `lib/umodbus/`
- [ ] Verificar estrutura:
  - `lib/umodbus/__init__.py`
  - `lib/umodbus/serial.py`
  - `lib/umodbus/functions.py`
- [ ] Testar import: `from umodbus.serial import Serial`

---

## ⏳ FASE 4: Testes (PENDENTE)

### 4.1 Teste Local (sem CLP)
**Objetivo:** Validar boot, WiFi e servidor HTTP

**Checklist:**
- [ ] Flash MicroPython no ESP32
- [ ] Upload `boot.py`
- [ ] Upload `main.py` (versão stub)
- [ ] Verificar WiFi AP ativo
- [ ] Conectar no WiFi "IHM_NEOCOUDE"
- [ ] Acessar http://192.168.4.1
- [ ] Ver index.html carregado

### 4.2 Teste Modbus (com CLP)
**Objetivo:** Validar comunicação RS485

**Checklist:**
- [ ] Conectar MAX485 (GPIO17/16/4)
- [ ] Conectar RS485-A/B no CLP
- [ ] Upload `modbus_client_esp32.py`
- [ ] Testar leitura encoder (0x04D6/0x04D7)
- [ ] Testar leitura ângulos (0x0500/0x0502/0x0504)
- [ ] Testar escrita ângulo
- [ ] Testar escrita velocidade (0x094C)

### 4.3 Teste Integrado
**Objetivo:** Sistema completo funcionando

**Checklist:**
- [ ] Tablet conecta no WiFi
- [ ] Interface carrega sem erros
- [ ] WebSocket conecta (WS ✓)
- [ ] Status CLP aparece (CLP ✓)
- [ ] Encoder atualiza em tempo real
- [ ] Botão de velocidade funciona
- [ ] Botão de ângulo funciona
- [ ] Motor liga/desliga via interface

---

## 🔧 FASE 5: Deploy em Produção (PENDENTE)

### 5.1 Hardware Final
**Checklist:**
- [ ] Comprar ESP32-WROOM-32 DevKit V1
- [ ] Comprar MAX485
- [ ] Comprar Buck 24V→5V 3A
- [ ] Montar protoboard de teste
- [ ] Soldar conexões permanentes (opcional)
- [ ] Montar em caixa DIN rail

### 5.2 Instalação no Painel
**Checklist:**
- [ ] Desligar máquina (chave geral)
- [ ] Identificar terminal 24V DC no painel
- [ ] Conectar Buck ao 24V
- [ ] Ajustar Buck para exatos 5.0V
- [ ] Alimentar ESP32
- [ ] Conectar RS485 no CLP
- [ ] Testar sistema completo
- [ ] Fechar painel
- [ ] Criar backup do firmware

### 5.3 Documentação para Cliente
**Checklist:**
- [ ] Anotar SSID e senha WiFi
- [ ] Anotar IP de acesso
- [ ] Tirar fotos das conexões
- [ ] Criar manual de operador
- [ ] Criar guia de troubleshooting
- [ ] Entregar backup do firmware

---

## 📊 Resumo de Progresso

| Fase | Itens | Concluídos | Progresso |
|------|-------|------------|-----------|
| 1. Estrutura Base | 6 | 6 | ✅ 100% |
| 2. Código MicroPython | 3 | 0 | ⏳ 0% |
| 3. Bibliotecas | 2 | 0 | ⏳ 0% |
| 4. Testes | 3 | 0 | ⏳ 0% |
| 5. Deploy | 3 | 0 | ⏳ 0% |
| **TOTAL** | **17** | **6** | **⏳ 35%** |

**Tempo estimado restante:** 5-7 horas de trabalho efetivo

---

## 🎯 Próximos Passos Imediatos

1. **Baixar bibliotecas** (15 min)
   ```bash
   cd /home/lucas-junges/Documents/clientes/w\&co/ihm_esp32
   ./download_libs.sh  # Criar este script
   ```

2. **Criar `modbus_client_esp32.py`** (2h)
   - Abrir `../ihm/modbus_client.py` lado a lado
   - Adaptar linha por linha
   - Testar cada função isoladamente

3. **Criar `state_manager_esp32.py`** (1h)
   - Mais simples: só trocar imports
   - Adicionar `gc.collect()`

4. **Criar `main.py`** (2-3h)
   - Parte mais trabalhosa
   - Seguir exemplos do Microdot
   - Adaptar rotas

5. **Testar sem CLP** (30min)
   - Boot + WiFi + HTTP
   - Interface carrega

6. **Testar com CLP** (1h)
   - Comunicação Modbus
   - Leituras funcionando

**Total: 6-8 horas até estar funcional**

---

## 💡 Dicas

- Use **Thonny IDE** para upload e debug (mais fácil que ampy)
- Teste **cada arquivo isoladamente** antes de integrar
- Use **console serial** (`screen /dev/ttyUSB0 115200`) para ver logs
- **Salve backups** do firmware funcionando
- Documentação Microdot: https://microdot.readthedocs.io/
- Documentação uModbus: https://github.com/pycom/pycom-modbus

---

**Quer que eu crie o script de download das bibliotecas automaticamente?**
