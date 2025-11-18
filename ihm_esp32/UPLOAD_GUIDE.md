# Guia de Upload - ESP32 IHM Web

## ✅ Arquivos Criados

Todos os arquivos necessários foram criados com sucesso:

```
ihm_esp32/
├── boot.py                      ✅ Configuração WiFi
├── main.py                      ✅ Servidor HTTP + WebSocket
├── modbus_map.py                ✅ Mapeamento Modbus
├── modbus_client_esp32.py       ✅ Cliente Modbus RTU
├── state_manager_esp32.py       ✅ Gerenciador de estado
├── static/
│   └── index.html               ✅ Interface web
└── lib/
    └── umodbus/
        ├── __init__.py          ✅ Biblioteca Modbus
        └── serial.py            ✅ Serial RTU
```

---

## 📡 Configuração WiFi

### Credenciais Configuradas em `boot.py`:

```python
WIFI_SSID = 'IHM_NEOCOUDE'
WIFI_PASSWORD = 'dobradeira123'
```

### Modo: Access Point (AP)
O ESP32 cria sua própria rede WiFi:

- **SSID:** `IHM_NEOCOUDE`
- **Senha:** `dobradeira123` (mínimo 8 caracteres)
- **IP Fixo:** `192.168.4.1`

### Como Conectar:

1. No tablet/celular, vá em **Configurações → WiFi**
2. Procure a rede **IHM_NEOCOUDE**
3. Digite a senha: **dobradeira123**
4. Aguarde conexão
5. Abra o navegador e acesse: **http://192.168.4.1**

---

## 🔧 Upload dos Arquivos (Via Thonny IDE)

### Método 1: Upload Automático via Thonny (RECOMENDADO)

1. **Instalar Thonny** (se não tiver):
   ```bash
   sudo apt install thonny
   ```

2. **Abrir Thonny**:
   ```bash
   thonny &
   ```

3. **Configurar Porta**:
   - Menu: `Tools → Options → Interpreter`
   - Selecionar: `MicroPython (ESP32)`
   - Porta: `/dev/ttyACM0`
   - Clicar `OK`

4. **Fazer Upload**:

   **Arquivos raiz:**
   - Abrir `boot.py` no Thonny
   - Menu: `File → Save As → MicroPython device`
   - Salvar como `boot.py` (raiz)
   - Repetir para: `main.py`, `modbus_map.py`, `modbus_client_esp32.py`, `state_manager_esp32.py`

   **Pasta static:**
   - No painel "Files" (View → Files)
   - Criar pasta `static/` no ESP32
   - Arrastar `index.html` para dentro de `static/`

   **Pasta lib:**
   - Criar pasta `lib/` no ESP32
   - Criar pasta `lib/umodbus/` no ESP32
   - Arrastar `__init__.py` e `serial.py` para `lib/umodbus/`

5. **Resetar ESP32**:
   - Menu: `Run → Send EOF / Soft reboot` (ou CTRL+D no Shell)

---

### Método 2: Upload Manual via ampy (Alternativo)

Se preferir linha de comando:

```bash
cd /home/lucas-junges/Documents/clientes/w\&co/ihm_esp32

# Arquivos raiz
ampy --port /dev/ttyACM0 --baud 115200 put boot.py
ampy --port /dev/ttyACM0 --baud 115200 put main.py
ampy --port /dev/ttyACM0 --baud 115200 put modbus_map.py
ampy --port /dev/ttyACM0 --baud 115200 put modbus_client_esp32.py
ampy --port /dev/ttyACM0 --baud 115200 put state_manager_esp32.py

# Diretórios
ampy --port /dev/ttyACM0 --baud 115200 put static/
ampy --port /dev/ttyACM0 --baud 115200 put lib/

# Resetar
python3 -c "import serial; s=serial.Serial('/dev/ttyACM0', 115200); s.write(b'\x04')"
```

---

## 🧪 Teste de Funcionamento

### 1. Verificar Boot no Console Serial

```bash
screen /dev/ttyACM0 115200
```

**Saída esperada:**
```
==================================================
IHM WEB - DOBRADEIRA NEOCOUDE-HD-15 (ESP32)
==================================================

Modo: Access Point (rede própria)
✓ WiFi AP ativo
  SSID: IHM_NEOCOUDE
  Senha: dobradeira123
  IP: 192.168.4.1

Acesse: http://192.168.4.1

RAM livre: 95832 bytes

========================================
IHM WEB - ESP32
========================================
✓ Modo STUB ativado
✓ Polling iniciado (500ms)
✓ Servidor HTTP iniciado em :80
```

### 2. Conectar no WiFi

No tablet:
- Buscar rede `IHM_NEOCOUDE`
- Senha: `dobradeira123`
- Aguardar conexão

### 3. Acessar Interface

Navegador: **http://192.168.4.1**

**Deve aparecer:**
- Interface da IHM carregada
- Status "WebSocket ✓" (canto superior)
- Status "CLP ✓" (se modo STUB ativo)
- Valor do encoder atualizando (~45.7°)
- Botões funcionais (K0-K9, S1, S2, etc.)

---

## ⚙️ Alterar para Modo LIVE (Com CLP Real)

Quando conectar o MAX485 e o CLP:

1. **Editar `main.py` no ESP32**:
   ```python
   # Linha ~188
   STUB_MODE = False  # Trocar True → False
   ```

2. **Configurar Slave ID** (se necessário):
   ```python
   # Linha ~194
   modbus = ModbusClientWrapper(stub_mode=False, slave_id=1)  # Trocar 1 pelo ID correto
   ```

3. **Salvar e Resetar**

---

## 🐛 Troubleshooting

### WiFi não aparece

**Causa:** ESP32 não bootou corretamente

**Solução:**
```bash
# Ver logs
screen /dev/ttyACM0 115200

# Resetar manualmente
python3 -c "import serial; s=serial.Serial('/dev/ttyACM0', 115200); s.write(b'\x04')"
```

### Interface não carrega (404)

**Causa:** Arquivo `index.html` não foi enviado

**Solução:**
```bash
# Verificar se existe
ampy --port /dev/ttyACM0 ls static/

# Re-enviar
ampy --port /dev/ttyACM0 put static/
```

### WebSocket não conecta

**Causa:** Implementação minimalista pode ter limitações

**Solução:** Use modo STUB primeiro para testar a interface. O WebSocket básico deve funcionar para operações simples.

### Modbus timeout (modo LIVE)

**Causa:** Cabos MAX485 ou configuração incorreta

**Solução:**
1. Verificar conexões GPIO17/16/4
2. Verificar RS485-A/B no CLP
3. Confirmar baudrate 57600
4. Confirmar slave_id correto

---

## 📊 Status Atual

| Item | Status |
|------|--------|
| Arquivos criados | ✅ 100% |
| WiFi AP configurado | ✅ Pronto |
| Credenciais definidas | ✅ SSID: IHM_NEOCOUDE / Senha: dobradeira123 |
| IP configurado | ✅ 192.168.4.1 |
| Upload pendente | ⏳ Fazer via Thonny |
| Teste WiFi | ⏳ Aguardando upload |
| Teste com CLP | ⏳ Aguardando MAX485 |

---

## 🎯 Próximos Passos

1. ✅ **Fazer upload via Thonny** (seguir instruções acima)
2. ✅ **Resetar ESP32** (CTRL+D no Thonny)
3. ✅ **Conectar no WiFi** `IHM_NEOCOUDE` com senha `dobradeira123`
4. ✅ **Acessar** http://192.168.4.1
5. ⏳ **Testar interface** em modo STUB
6. ⏳ **Conectar MAX485** quando pronto
7. ⏳ **Alterar para modo LIVE** (`STUB_MODE = False`)
8. ⏳ **Testar comunicação com CLP**

---

**Desenvolvido por:** Eng. Lucas William Junges
**Data:** 17/Novembro/2025
**Versão:** 1.0-ESP32
