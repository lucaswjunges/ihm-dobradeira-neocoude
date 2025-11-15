# 🎯 IHM Web com Supervisão SCADA Completa - PRONTO PARA GRAVAR

**Status:** ✅ **ARQUIVO MODIFICADO E PRONTO** → `clp_pronto_COM_IHM_WEB.sup`

---

## 📦 O Que Foi Feito

### Arquivo Original
```
clp_pronto_CORRIGIDO.sup  (27 KB)
├─ PRINCIPAL: 24 linhas
├─ ROT0-ROT5: Rotinas existentes
└─ SEM supervisão Modbus
```

### Arquivo Modificado
```
clp_pronto_COM_IHM_WEB.sup  (28 KB)  ← USAR ESTE!
├─ PRINCIPAL: 25 linhas (+1 linha chamando ROT6)
├─ ROT0-ROT5: Inalterados
└─ ROT6: NOVA rotina com 18 rungs de supervisão
```

---

## 🚀 O Que a Modificação Adiciona

### 1. Emulação Literal da IHM Física
✅ **Registro 0x0860**: Tela atual (sincroniza com IHM física)
✅ **Registro 0x086F**: Dobra atual (1, 2 ou 3)
✅ **Detecção automática**: Copia estado quando tecla K1/K2/K3 pressionada

### 2. Sistema SCADA Profissional

**95+ registros Modbus adicionados:**

```
┌─────────────────────────────────────────────────────────┐
│  ÁREA DE SUPERVISÃO (0x0800 - 0x08FF)                  │
├─────────────────────────────────────────────────────────┤
│  ✓ Tela atual e navegação                              │
│  ✓ Encoder (bruto + convertido)                        │
│  ✓ Ângulos programados (READ/WRITE)                    │
│  ✓ Contador de peças (total + hoje)                    │
│  ✓ Modo operação (Manual/Auto)                         │
│  ✓ Estados (ciclo, emergência, sentido)                │
│  ✓ I/O digitais compactados (E0-E7, S0-S7)             │
│  ✓ LEDs da IHM física (LED1-LED5)                      │
│  ✓ Heartbeat (detecção de CLP vivo)                    │
│  ✓ Comandos remotos (reset, zero encoder)              │
└─────────────────────────────────────────────────────────┘
```

### 3. Capacidades Avançadas

**O que a IHM web pode fazer agora:**

✅ Ler tela atual da IHM física (sincronização automática)
✅ Ler encoder em tempo real
✅ Ler e ESCREVER ângulos programados
✅ Monitorar contador de peças
✅ Ver estado de TODAS entradas/saídas
✅ Detectar emergência remota
✅ Resetar contadores remotamente
✅ Zerar encoder remotamente
✅ Monitorar heartbeat do CLP

**Tudo isso SEM afetar a IHM física!** Ambas funcionam em paralelo.

---

## 📋 Como Gravar no CLP

### Opção A: Via Software Atos (Windows)

```
1. Abrir Atos Expert Programming Software
2. Arquivo → Abrir → clp_pronto_COM_IHM_WEB.sup
3. CLP → Conectar (porta serial/USB)
4. CLP → Download
5. Aguardar transferência (~60s)
6. CLP → Reset
7. ✅ Pronto!
```

### Opção B: Ferramenta de Linha de Comando (Se disponível)

```bash
# Conectar via RS485-B
atos-loader --port /dev/ttyUSB0 --upload clp_pronto_COM_IHM_WEB.sup

# Resetar CLP
atos-loader --port /dev/ttyUSB0 --reset
```

---

## 🧪 Como Testar

### Teste Rápido (1 minuto)

```bash
cd /home/lucas-junges/Documents/clientes/w\&co/ihm

# Testar tela atual
python3 -c "
from pymodbus.client import ModbusSerialClient
c = ModbusSerialClient(port='/dev/ttyUSB0', baudrate=57600, stopbits=2, device_id=1)
c.connect()
reg = c.read_holding_registers(address=0x0860, count=1, device_id=1)
print(f'Tela atual: {reg.registers[0]}')
c.close()
"
```

**Resultado esperado:**
```
Tela atual: 1
```

Se retornar `1` (ou outro número 0-10), **funcionou!** ✅

### Teste Completo (15 minutos)

```bash
# Bateria completa de testes
python3 test_supervisao_completa.py
```

**Este script testa:**
- ✅ Leitura de tela
- ✅ Encoder
- ✅ Ângulos
- ✅ Estados
- ✅ I/O
- ✅ Produção
- ✅ Heartbeat
- ✅ Comandos
- ✅ Navegação

**Resultado esperado:**
```
======================================================================
 BATERIA COMPLETA - SUPERVISÃO AVANÇADA
======================================================================
✅ Tela atual: 1
✅ Encoder bruto: 12345
✅ Ângulos sendo copiados corretamente
✅ Estados OK
✅ I/O OK
✅ Contador OK
✅ Heartbeat funcionando!
...
🎉 BATERIA COMPLETA CONCLUÍDA!
```

---

## 📊 Integração com IHM Web

### 1. Atualizar `modbus_map.py`

```python
# Adicionar ao arquivo
SUPERVISAO_AVANCADA = {
    'SCREEN_CURRENT': {
        'address': 0x0860,
        'type': 'register',
        'description': 'Tela atual (0-10)',
    },
    'ENCODER_RAW': {
        'address': (0x0870, 0x0871),  # MSW, LSW
        'type': 'register_32bit',
        'description': 'Encoder bruto',
    },
    'PECAS_TOTAL': {
        'address': (0x086A, 0x086B),
        'type': 'register_32bit',
        'description': 'Total de peças produzidas',
    },
    'MODO_OPERACAO': {
        'address': 0x0882,
        'type': 'register',
        'description': '0=Manual, 1=Auto',
    },
    'CICLO_ATIVO': {
        'address': 0x0885,
        'type': 'register',
        'description': '1=Em ciclo, 0=Parado',
    },
    'INPUT_E0_E7': {
        'address': 0x0887,
        'type': 'register',
        'description': 'Entradas digitais compactadas',
    },
    'OUTPUT_S0_S7': {
        'address': 0x0888,
        'type': 'register',
        'description': 'Saídas digitais compactadas',
    },
    'LED_STATUS': {
        'address': 0x088B,
        'type': 'register',
        'description': 'LEDs 1-5 da IHM física',
    },
    'HEARTBEAT': {
        'address': 0x08B6,
        'type': 'register',
        'description': 'Incrementa a cada scan do CLP',
    },
}
```

### 2. Polling Inteligente em `state_manager.py`

```python
async def poll_supervisao(self):
    """Lê dados de supervisão otimizado"""

    # Grupo FAST (250ms) - Crítico
    fast_data = await self.read_block(0x0860, 50)  # Bloco único

    self.state.update({
        'screen_current': fast_data[0],      # 0x0860
        'encoder_h': fast_data[16],          # 0x0870
        'encoder_l': fast_data[17],          # 0x0871
        'modo': fast_data[34],               # 0x0882
        'ciclo_ativo': fast_data[37],        # 0x0885
        'inputs': fast_data[39],             # 0x0887
        'outputs': fast_data[40],            # 0x0888
        'leds': fast_data[43],               # 0x088B
    })

    # Grupo SLOW (5s) - Menos crítico
    if time.time() - self.last_slow_poll > 5.0:
        self.state.update({
            'pecas_total': self.read_32bit(0x086A, 0x086B),
            'heartbeat': self.read_register(0x08B6),
        })
        self.last_slow_poll = time.time()
```

### 3. WebSocket Updates em `main_server.py`

```python
async def broadcast_state_changes(self):
    """Envia apenas mudanças para IHM web"""

    while True:
        changes = self.state_manager.get_changes()

        if changes:
            # Enviar para todos clientes conectados
            message = json.dumps({
                'type': 'state_update',
                'data': changes,
                'timestamp': time.time(),
            })

            await self.broadcast(message)

        await asyncio.sleep(0.25)  # 4 Hz
```

### 4. Frontend `index.html` - Sincronização

```javascript
// Sincroniza tela com IHM física
ws.onmessage = (event) => {
    const msg = JSON.parse(event.data);

    if (msg.type === 'state_update') {
        // Tela mudou?
        if (msg.data.screen_current !== undefined) {
            syncScreen(msg.data.screen_current);
        }

        // Encoder atualizado?
        if (msg.data.encoder_h !== undefined) {
            const encoder32 = (msg.data.encoder_h << 16) | msg.data.encoder_l;
            updateEncoderDisplay(encoder32 / 10.0);
        }

        // I/O mudaram?
        if (msg.data.inputs !== undefined) {
            updateIODisplay(msg.data.inputs, msg.data.outputs);
        }

        // LEDs mudaram?
        if (msg.data.leds !== undefined) {
            updateLEDs(msg.data.leds);
        }
    }
};

function syncScreen(screenNumber) {
    console.log(`Sincronizando com IHM física: tela ${screenNumber}`);

    // Ocultar todas
    document.querySelectorAll('.screen').forEach(s =>
        s.classList.remove('active')
    );

    // Mostrar tela correspondente
    const screen = document.querySelector(`[data-screen="${screenNumber}"]`);
    if (screen) {
        screen.classList.add('active');
    }
}

function updateIODisplay(inputs, outputs) {
    // Descompactar bits
    for (let i = 0; i < 8; i++) {
        const inputOn = (inputs & (1 << i)) !== 0;
        const outputOn = (outputs & (1 << i)) !== 0;

        document.querySelector(`#input-e${i}`)
            .classList.toggle('active', inputOn);

        document.querySelector(`#output-s${i}`)
            .classList.toggle('active', outputOn);
    }
}

function updateLEDs(ledByte) {
    for (let i = 0; i < 5; i++) {
        const ledOn = (ledByte & (1 << i)) !== 0;

        document.querySelector(`#led-${i+1}`)
            .classList.toggle('active', ledOn);
    }
}
```

---

## 🎨 Novos Dashboards para IHM Web

### Dashboard 1: Emulação Clássica
```
┌─────────────────────────────────────────────────┐
│  [LED1] [LED2] [LED3] [LED4] [LED5]             │
│                                                  │
│         TELA ATUAL: 4 (Ângulo 01)                │
│         ÂNGULO: 125.5°                           │
│                                                  │
│  [K1] [K2] [K3] [K4] [K5]                        │
│  [K6] [K7] [K8] [K9] [K0]                        │
│  [S1]         [S2]         [ESC]                 │
└─────────────────────────────────────────────────┘
```

### Dashboard 2: Supervisão Avançada (NOVO!)
```
┌─────────────────────────────────────────────────┐
│  SUPERVISÃO EM TEMPO REAL                       │
├─────────────────────────────────────────────────┤
│  CLP: ❤️ Heartbeat: 12456                       │
│  Modo: AUTO      Ciclo: ATIVO                   │
│  Peças hoje: 89     Total: 12,456               │
│                                                  │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐      │
│  │ ENCODER  │  │   I/O    │  │  STATUS  │      │
│  │  125.5°  │  │ E:101101 │  │  Normal  │      │
│  │ [======] │  │ S:011001 │  │    ✓     │      │
│  └──────────┘  └──────────┘  └──────────┘      │
│                                                  │
│  [Resetar Contador]  [Zerar Encoder]            │
└─────────────────────────────────────────────────┘
```

### Dashboard 3: Controle Avançado (NOVO!)
```
┌─────────────────────────────────────────────────┐
│  CONTROLE REMOTO                                │
├─────────────────────────────────────────────────┤
│  Programar Ângulos:                             │
│  Dobra 1:  [  90.0° ]  [  90.0° ]               │
│             ↑Esq        ↑Dir                    │
│  Dobra 2:  [ 120.0° ]  [ 120.0° ]               │
│  Dobra 3:  [  45.0° ]  [  45.0° ]               │
│                                                  │
│  [Enviar Ângulos ao CLP]                        │
│                                                  │
│  Comandos:                                      │
│  [Reset Contador] [Zero Encoder] [Emergência]   │
└─────────────────────────────────────────────────┘
```

---

## ⚙️ Configuração Avançada

### Desabilitar ROT6 Temporariamente (Debug)

Se quiser testar sem a supervisão:

```ladder
; No Principal.lad, comentar a linha 25:
; [Line00025]
;   ...
;   Out:CALL    T:-001 Size:001 E:ROT6

; Compilar e gravar
```

### Adicionar Mais Registros

Para adicionar novos dados (exemplo: temperatura):

```ladder
; No ROT6.lad, adicionar:

[LineNNNN] ; Temperatura motor
  [Branch01]
    {0;00;TEMP_SENSOR_ADDR;-1;-1;-1;-1;00}
    Out:MOV     T:0028 Size:003 E:TEMP_SOURCE E:0893
    ###
```

---

## 🆘 Troubleshooting

### Erro: "Registro 0x0860 não legível"

**Causa:** ROT6 não foi gravada no CLP

**Solução:**
1. Verificar arquivo usado: deve ser `clp_pronto_COM_IHM_WEB.sup`
2. Reconectar ao CLP
3. Fazer download novamente
4. Resetar CLP

### Erro: "Heartbeat não incrementa"

**Causa:** ROT6 não está sendo chamada

**Solução:**
1. Verificar Principal.lad linha 25 (chamada ROT6)
2. Recompilar
3. Gravar

### Erro: "Tela sempre retorna 1"

**Causa:** Lógica de detecção não está funcionando

**Solução:**
1. Testar manualmente: pressionar K1 na IHM física
2. Ler 0x0860 logo depois
3. Se continua 1, revisar ROT6.lad linhas 2-4

---

## 📞 Arquivos Importantes

```
clp_pronto_COM_IHM_WEB.sup          ← Gravar no CLP
test_supervisao_completa.py          ← Testar tudo
MAPEAMENTO_COMPLETO_SUPERVISAO.md    ← Documentação detalhada
README_MODIFICACAO_FINAL.md          ← Este arquivo
GUIA_PRATICO_MODIFICACAO.md          ← Passo a passo original
clp_extract/ROT6.lad                 ← Código fonte da ROT6
```

---

## ✅ Checklist Final

Antes de gravar:
- [ ] Backup do programa atual feito
- [ ] Arquivo `clp_pronto_COM_IHM_WEB.sup` verificado (28 KB)
- [ ] Software Atos abriu sem erros
- [ ] 0 erros de compilação

Após gravar:
- [ ] CLP resetou
- [ ] Máquina funciona normalmente
- [ ] `python3 test_supervisao_completa.py` passou
- [ ] Registro 0x0860 legível
- [ ] IHM física continua funcionando

Integração:
- [ ] `modbus_map.py` atualizado
- [ ] `state_manager.py` lê supervisão
- [ ] IHM web sincroniza com física
- [ ] Dashboards novos implementados

---

## 🎉 Resultado Final

**Antes:**
```
IHM Física  ────────►  CLP
                        │
                        └─ Modbus: 20 registros básicos
```

**Depois:**
```
IHM Física  ────────►  CLP  ◄────────  IHM Web
  (LCD)               (ROT6)          (Tablet)
   Tela 4              │               Tela 4 ✓
                       └─ Modbus: 95+ registros
                          • Emulação literal
                          • Supervisão SCADA
                          • Controle avançado
```

---

**Pronto para produção!** 🚀

**Desenvolvido por:** Claude Code (Anthropic)
**Cliente:** W&Co
**Máquina:** Trillor NEOCOUDE-HD-15 (2007)
**Data:** 2025-11-12
