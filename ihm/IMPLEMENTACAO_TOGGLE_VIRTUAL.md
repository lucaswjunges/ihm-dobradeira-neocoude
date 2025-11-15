# 🚀 IMPLEMENTAÇÃO: TOGGLE VIRTUAL AUTO/MANUAL

**Solução para quando E6 não está disponível**

Como E6 (sensor de segurança) não está ativo, vamos criar um **botão virtual** na IHM Web que escreve diretamente em **02FF**.

---

## 📝 CÓDIGO COMPLETO

### 1. Atualizar `modbus_map.py`

```python
# Adicionar ao final do arquivo

# BIT DE MODO REAL DO LADDER
MODE_BIT_REAL = {
    'MODE_02FF': 0x02FF,  # 767 - Bit REAL de modo
    # 02FF = False → MANUAL
    # 02FF = True  → AUTO
}

# Adicionar comentário em MODE_STATE
# MODE_STATE (0x0946) é escrito por Python para IHM Web
# Mas o bit REAL do ladder é 02FF!
```

### 2. Criar função em `modbus_client.py`

```python
def toggle_mode_direct(self) -> bool:
    """
    Toggle direto do bit de modo (02FF)
    Bypass do S1 + E6

    Returns:
        True se sucesso, False se falha
    """
    try:
        # Ler modo atual
        current_mode = self.read_coil(0x02FF)  # 767
        if current_mode is None:
            return False

        # Inverter
        new_mode = not current_mode

        # Escrever novo modo
        success = self.write_coil(0x02FF, new_mode)

        if success:
            mode_text = "AUTO" if new_mode else "MANUAL"
            print(f"✅ Modo alterado para: {mode_text} (02FF={new_mode})")

        return success
    except Exception as e:
        print(f"❌ Erro ao alternar modo: {e}")
        return False

def read_real_mode(self) -> str:
    """
    Lê o modo REAL do ladder (02FF)

    Returns:
        "AUTO", "MANUAL" ou "UNKNOWN"
    """
    try:
        mode_bit = self.read_coil(0x02FF)
        if mode_bit is None:
            return "UNKNOWN"
        return "AUTO" if mode_bit else "MANUAL"
    except:
        return "UNKNOWN"
```

### 3. Atualizar `state_manager.py`

```python
# No método poll_once(), adicionar:

def poll_mode_bits(self):
    """Lê bits de modo (REAL e Python)"""
    # Bit REAL do ladder
    mode_02ff = self.client.read_coil(0x02FF)  # 767
    self.machine_state['mode_real_02ff'] = mode_02ff
    self.machine_state['mode_text'] = "AUTO" if mode_02ff else "MANUAL"

    # Sincronizar com MODE_STATE (para compatibilidade)
    mode_state_value = 1 if mode_02ff else 0
    current_mode_state = self.client.read_register(mm.SUPERVISION_AREA['MODE_STATE'])

    # Se diferente, atualizar MODE_STATE
    if current_mode_state != mode_state_value:
        self.client.write_register(mm.SUPERVISION_AREA['MODE_STATE'], mode_state_value)

    self.machine_state['mode_state_0946'] = mode_state_value

# Chamar no poll_once():
async def poll_once(self):
    # ... código existente ...

    # Polling de modo
    self.poll_mode_bits()

    # ... resto do código ...
```

### 4. Adicionar handler em `main_server.py`

```python
async def handle_toggle_mode(self, websocket, data):
    """
    Handler para toggle de modo virtual (direct write em 02FF)
    Bypass de S1 + E6
    """
    print("🔄 Toggle de modo (direto em 02FF)...")

    # Ler modo atual
    mode_antes = self.modbus_client.read_real_mode()

    # Toggle
    success = self.modbus_client.toggle_mode_direct()

    if success:
        # Aguardar ladder processar
        await asyncio.sleep(0.3)

        # Ler modo novo
        mode_depois = self.modbus_client.read_real_mode()

        # Enviar atualização para TODOS os clientes
        update = {
            'type': 'mode_changed',
            'mode_antes': mode_antes,
            'mode_depois': mode_depois,
            'timestamp': time.time()
        }

        for client in self.clients:
            try:
                await client.send(json.dumps(update))
            except:
                pass

        print(f"✅ Modo alterado: {mode_antes} → {mode_depois}")
        return True
    else:
        await websocket.send(json.dumps({
            'type': 'error',
            'message': 'Falha ao alternar modo'
        }))
        return False

# No handle_client_message, adicionar:
async def handle_client_message(self, websocket, message: str):
    try:
        data = json.loads(message)
        action = data.get('action')

        # ... handlers existentes ...

        elif action == 'toggle_mode':
            await self.handle_toggle_mode(websocket, data)

        # ... resto do código ...
```

### 5. Atualizar `static/index.html`

```html
<!-- Adicionar botão na interface -->
<div class="mode-control">
    <h3>Controle de Modo</h3>
    <div class="mode-display">
        <span id="mode-current">MANUAL</span>
    </div>
    <button id="btn-toggle-mode" class="btn-mode">
        🔄 Alternar AUTO/MANUAL
    </button>
    <p class="mode-info">
        Modo atual é lido do bit <strong>02FF</strong> (ladder)<br>
        Botão alterna diretamente (bypass de S1+E6)
    </p>
</div>

<style>
.mode-control {
    background: #f5f5f5;
    border: 2px solid #333;
    padding: 15px;
    margin: 10px 0;
    border-radius: 8px;
}

.mode-display {
    font-size: 24px;
    font-weight: bold;
    text-align: center;
    padding: 20px;
    margin: 10px 0;
    border-radius: 8px;
}

.mode-display[data-mode="AUTO"] {
    background: #4CAF50;
    color: white;
}

.mode-display[data-mode="MANUAL"] {
    background: #FF9800;
    color: white;
}

.btn-mode {
    width: 100%;
    padding: 15px;
    font-size: 18px;
    background: #2196F3;
    color: white;
    border: none;
    border-radius: 8px;
    cursor: pointer;
    margin: 10px 0;
}

.btn-mode:hover {
    background: #1976D2;
}

.btn-mode:active {
    background: #0D47A1;
}

.mode-info {
    font-size: 12px;
    color: #666;
    text-align: center;
    margin-top: 10px;
}
</style>

<script>
// Atualizar display de modo
function updateModeDisplay(state) {
    const modeElement = document.getElementById('mode-current');
    const modeDisplay = document.querySelector('.mode-display');

    const mode = state.mode_text || 'UNKNOWN';
    modeElement.textContent = mode;
    modeDisplay.setAttribute('data-mode', mode);
}

// Handler do botão toggle
document.getElementById('btn-toggle-mode').addEventListener('click', () => {
    console.log('🔄 Solicitando toggle de modo...');
    ws.send(JSON.stringify({ action: 'toggle_mode' }));
});

// Listener para mudanças de modo
ws.addEventListener('message', (event) => {
    const msg = JSON.parse(event.data);

    if (msg.type === 'mode_changed') {
        console.log(`✅ Modo alterado: ${msg.mode_antes} → ${msg.mode_depois}`);
        // Interface atualiza automaticamente via full_state
    }

    if (msg.type === 'full_state' || msg.type === 'state_update') {
        updateModeDisplay(msg.data);
    }
});
</script>
```

---

## 🧪 TESTE RÁPIDO

```python
#!/usr/bin/env python3
"""Teste do toggle virtual"""
from modbus_client import ModbusClientWrapper
import modbus_map as mm
import time

client = ModbusClientWrapper(port=mm.MODBUS_CONFIG['port'], stub_mode=False)

if client.connected:
    print("Modo inicial:", client.read_real_mode())

    print("\n Alternando...")
    client.toggle_mode_direct()
    time.sleep(0.5)

    print("Modo final:", client.read_real_mode())

    client.close()
```

---

## ✅ VANTAGENS DO TOGGLE VIRTUAL

1. **Funciona sem E6** - Não depende de sensor externo
2. **Resposta imediata** - Não precisa pulso de 100ms
3. **Menos complexo** - Escreve direto no bit
4. **Auditável** - Logs de todas as mudanças
5. **Sincronizado** - Atualiza MODE_STATE automaticamente

## ⚠️ DESVANTAGENS

1. **Bypass de segurança** - Ignora a condição E6
2. **Não segue lógica original** - S1 não é usado
3. **Pode conflitar** - Se S1 for pressionado fisicamente

## 📋 QUANDO USAR

- ✅ E6 não está disponível (sensor desconectado)
- ✅ IHM física não funciona
- ✅ Teste e desenvolvimento
- ✅ Operação remota sem painel

## ⛔ QUANDO **NÃO** USAR

- E6 é requisito de segurança crítico
- Operação em produção com painel físico ativo
- Máquina em movimento/ciclo ativo

---

**Status:** ✅ PRONTO PARA IMPLEMENTAR
