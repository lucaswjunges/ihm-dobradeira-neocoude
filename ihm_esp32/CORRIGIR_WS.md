# Correção: WS → HTTP na Interface

## 🎯 O Que Foi Alterado

O texto "WS" no canto superior direito foi alterado para **"HTTP"**.

**Arquivo alterado:**
- `static/index.html` - Linha 430

**Mudança:**
```html
<!-- Antes -->
<span id="wsText">WS</span>

<!-- Depois -->
<span id="wsText">HTTP</span>
```

---

## 📤 Como Fazer Upload Manual

### Opção 1: Via Thonny (RECOMENDADO)

1. **Abrir Thonny:**
   ```bash
   thonny &
   ```

2. **Conectar no ESP32:**
   - `Tools → Options → Interpreter`
   - Selecionar: `MicroPython (ESP32)`
   - Porta: `/dev/ttyACM0` (ou a que aparecer)
   - Clicar `OK`

3. **Fazer Upload:**
   - Abrir arquivo: `/home/lucas-junges/Documents/clientes/w&co/ihm_esp32/static/index.html`
   - `File → Save As → MicroPython device`
   - Navegar para pasta: `static/`
   - Salvar como: `index.html` (substituir)

4. **Resetar ESP32:**
   - No console do Thonny: Pressionar **CTRL+D**

5. **Testar:**
   - Acessar: `http://192.168.0.106` (ou `http://192.168.4.1`)
   - Verificar canto superior direito: Deve aparecer **"HTTP ✓"**

---

### Opção 2: Via ampy (Terminal)

1. **Reconectar ESP32 via USB**

2. **Verificar porta:**
   ```bash
   ls /dev/ttyACM* /dev/ttyUSB*
   ```

3. **Fazer upload:**
   ```bash
   cd /home/lucas-junges/Documents/clientes/w\&co/ihm_esp32
   ampy --port /dev/ttyACM0 put static/index.html static/index.html
   ```

4. **Resetar:**
   ```bash
   python3 -c "import serial; s=serial.Serial('/dev/ttyACM0', 115200); s.write(b'\x04'); s.close()"
   ```

5. **Testar:** Acessar interface e verificar "HTTP ✓"

---

## ✅ Resultado Esperado

**Antes do upload:**
```
┌─────────────────────────────────┐
│ IHM - NEOCOUDE-HD-15   WS ✓ CLP ✓ │  ← Mostra "WS"
└─────────────────────────────────┘
```

**Depois do upload:**
```
┌─────────────────────────────────┐
│ IHM - NEOCOUDE-HD-15   HTTP ✓ CLP ✓ │  ← Mostra "HTTP"
└─────────────────────────────────┘
```

---

## 🧪 Como Testar

1. Acessar interface via navegador
2. Olhar canto superior direito
3. Deve aparecer: **"HTTP"** (verde) ao invés de "WS"
4. Funcionamento normal: encoder atualiza, botões funcionam

---

## 📊 Status Atual dos Arquivos

| Arquivo | Status | Localização |
|---------|--------|-------------|
| `boot.py` | ✅ Atualizado | ESP32 (modo STA inteligente) |
| `main.py` | ✅ Atualizado | ESP32 (servidor HTTP) |
| `modbus_client_esp32.py` | ✅ OK | ESP32 |
| `modbus_map.py` | ✅ OK | ESP32 |
| `lib/umodbus/` | ✅ OK | ESP32 |
| `static/index.html` | ⏳ **Precisa upload** | Alterado localmente |

---

## 🔍 Se Não Conseguir Fazer Upload

**Alternativa rápida - Editar direto no ESP32 via Thonny:**

1. Abrir Thonny
2. `View → Files` (painel de arquivos)
3. Navegar no ESP32: `static/index.html`
4. Botão direito → `Open in Thonny`
5. Encontrar linha 430: `<span id="wsText">WS</span>`
6. Alterar para: `<span id="wsText">HTTP</span>`
7. Salvar: `CTRL+S`
8. Resetar: `CTRL+D` no console

---

**OBS:** O arquivo `index.html` atualizado já está salvo localmente em:
```
/home/lucas-junges/Documents/clientes/w&co/ihm_esp32/static/index.html
```

Basta fazer o upload para o ESP32! 🚀
