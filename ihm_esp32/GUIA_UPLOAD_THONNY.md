# 📤 GUIA DE UPLOAD - IHM Web para ESP32

**Data:** 18 de Novembro de 2025
**Ferramenta:** Thonny IDE

---

## 🎯 Objetivo

Fazer upload de todos os arquivos da IHM Web para o ESP32 usando Thonny IDE.

---

## 📋 Pré-requisitos

### 1. Hardware Conectado
- ✅ ESP32 conectado via USB ao Ubuntu
- ✅ Verificar porta: `ls /dev/ttyUSB*` (deve aparecer `/dev/ttyUSB0` ou `/dev/ttyUSB1`)

### 2. Thonny IDE Instalado
```bash
# Se não tiver instalado:
sudo apt update
sudo apt install thonny

# Ou via pip:
pip3 install thonny
```

### 3. Permissões de Porta Serial
```bash
# Adicionar usuário ao grupo dialout (necessário 1x):
sudo usermod -a -G dialout $USER

# Logout e login novamente para aplicar
# OU executar temporariamente:
sudo chmod 666 /dev/ttyUSB0
```

---

## 📁 Estrutura de Arquivos a Upload

```
ihm_esp32/
├── boot.py                      ← EDITAR ANTES DO UPLOAD (WiFi)
├── main.py                      ← Servidor principal
├── modbus_map.py                ← Endereços Modbus
├── modbus_client_esp32.py       ← Cliente Modbus
├── static/
│   └── index.html               ← Interface web
└── lib/
    └── umodbus/                 ← Biblioteca Modbus
        ├── __init__.py
        ├── serial.py
        └── functions.py
```

---

## ⚙️ PASSO 1: Configurar WiFi

**IMPORTANTE:** Editar `boot.py` **ANTES** do upload!

```bash
# Abrir boot.py no editor
nano /home/lucas-junges/Documents/clientes/w&co/ihm_esp32/boot.py
```

**Alterar linhas 8-9:**
```python
WIFI_SSID = "IHM_NEOCOUDE"       # ← Trocar pelo nome desejado
WIFI_PASSWORD = "dobradeira123"  # ← Trocar pela senha (min 8 chars)
```

**Salvar:** `Ctrl+O` → `Enter` → `Ctrl+X`

---

## 🚀 PASSO 2: Abrir Thonny e Conectar ESP32

### 2.1 Iniciar Thonny
```bash
thonny
```

### 2.2 Selecionar Interpretador MicroPython
1. Menu: **Executar** → **Selecionar interpretador...**
2. Selecionar: **MicroPython (ESP32)**
3. Porta: `/dev/ttyUSB0` (ou `/dev/ttyUSB1`)
4. Clicar: **OK**

### 2.3 Verificar Conexão
No **Shell** (parte inferior do Thonny), você deve ver:
```
MicroPython v1.21.0 on 2023-10-05; ESP32 module with ESP32
Type "help()" for more information.
>>>
```

**Se não aparecer:**
- Apertar botão **EN** no ESP32 (reset)
- Ou: Menu **Executar** → **Interromper/Reiniciar backend**

---

## 📂 PASSO 3: Abrir Sistema de Arquivos do ESP32

### 3.1 Abrir Gerenciador de Arquivos
Menu: **Ver** → **Arquivos** (ou `Ctrl+Shift+F`)

Você verá 2 painéis:
```
┌─────────────────────────────────────────┐
│ Este computador                         │  ← Seu Ubuntu
│ /home/lucas-junges/...                  │
├─────────────────────────────────────────┤
│ MicroPython device                      │  ← ESP32
│ (vazio ou com boot.py, main.py antigos)│
└─────────────────────────────────────────┘
```

### 3.2 Limpar Arquivos Antigos (se necessário)
No painel **MicroPython device**:
1. Clicar com botão direito em arquivo antigo
2. Selecionar **Deletar**
3. Confirmar

**Importante:** Deixar vazio para começar fresh!

---

## 📤 PASSO 4: Upload dos Arquivos Principais

### 4.1 Navegar no Painel "Este computador"
```
/home/lucas-junges/Documents/clientes/w&co/ihm_esp32/
```

### 4.2 Upload boot.py
1. **Painel Ubuntu:** Clicar em `boot.py`
2. **Botão direito** → **Upload para /**
3. Aguardar mensagem: "Uploaded boot.py"

### 4.3 Upload main.py
1. **Painel Ubuntu:** Clicar em `main.py`
2. **Botão direito** → **Upload para /**
3. Aguardar mensagem: "Uploaded main.py"

### 4.4 Upload modbus_map.py
1. **Painel Ubuntu:** Clicar em `modbus_map.py`
2. **Botão direito** → **Upload para /**
3. Aguardar mensagem: "Uploaded modbus_map.py"

### 4.5 Upload modbus_client_esp32.py
1. **Painel Ubuntu:** Clicar em `modbus_client_esp32.py`
2. **Botão direito** → **Upload para /**
3. Aguardar mensagem: "Uploaded modbus_client_esp32.py"

**Painel ESP32 agora deve mostrar:**
```
MicroPython device
├── boot.py
├── main.py
├── modbus_map.py
└── modbus_client_esp32.py
```

---

## 📁 PASSO 5: Upload da Pasta `static/`

### 5.1 Criar Diretório `static` no ESP32
No **painel MicroPython device**:
1. **Botão direito** no espaço vazio
2. Selecionar **Novo diretório**
3. Digitar: `static`
4. Pressionar **Enter**

### 5.2 Upload index.html
1. **Painel Ubuntu:** Navegar até `ihm_esp32/static/`
2. Clicar em `index.html`
3. **Botão direito** → **Upload para /static**
4. Aguardar mensagem: "Uploaded index.html"

**Painel ESP32 agora:**
```
MicroPython device
├── boot.py
├── main.py
├── modbus_map.py
├── modbus_client_esp32.py
└── static/
    └── index.html
```

---

## 📚 PASSO 6: Upload da Pasta `lib/umodbus/`

### 6.1 Criar Diretório `lib` no ESP32
No **painel MicroPython device**:
1. **Botão direito** no espaço vazio
2. Selecionar **Novo diretório**
3. Digitar: `lib`
4. Pressionar **Enter**

### 6.2 Criar Diretório `umodbus` dentro de `lib`
1. **Painel ESP32:** Entrar na pasta `lib` (duplo clique)
2. **Botão direito** no espaço vazio
3. Selecionar **Novo diretório**
4. Digitar: `umodbus`
5. Pressionar **Enter**

### 6.3 Upload dos Arquivos umodbus
1. **Painel Ubuntu:** Navegar até `ihm_esp32/lib/umodbus/`
2. Selecionar `__init__.py`
3. **Botão direito** → **Upload para /lib/umodbus**
4. Repetir para `serial.py`
5. Repetir para `functions.py`

**Estrutura final no ESP32:**
```
MicroPython device
├── boot.py
├── main.py
├── modbus_map.py
├── modbus_client_esp32.py
├── static/
│   └── index.html
└── lib/
    └── umodbus/
        ├── __init__.py
        ├── serial.py
        └── functions.py
```

---

## ✅ PASSO 7: Verificar Upload Completo

### 7.1 Listar Arquivos via Shell
No **Shell do Thonny**, executar:
```python
>>> import os
>>> os.listdir('/')
['boot.py', 'main.py', 'modbus_map.py', 'modbus_client_esp32.py', 'static', 'lib']

>>> os.listdir('/static')
['index.html']

>>> os.listdir('/lib')
['umodbus']

>>> os.listdir('/lib/umodbus')
['__init__.py', 'serial.py', 'functions.py']
```

**Se algum arquivo faltar:** Voltar ao passo correspondente e refazer upload.

---

## 🔄 PASSO 8: Resetar ESP32 e Testar

### 8.1 Reset via Shell
No **Shell do Thonny**, executar:
```python
>>> import machine
>>> machine.reset()
```

**OU apertar botão EN no ESP32.**

### 8.2 Verificar Boot no Console
Aguardar 6 segundos. O console deve mostrar:
```
IHM WEB - SERVIDOR ESP32
========================================
Modo: LIVE (CLP real)
✓ Modbus conectado
✓ Sistema inicializado
✓ Thread Modbus iniciada
✓ Servidor HTTP iniciado em :80
✓ Pronto para receber conexões
========================================
```

**Se houver erro:**
- Verificar mensagem de erro
- Verificar todos os arquivos foram uploaded
- Verificar `boot.py` tem WiFi configurado

---

## 📡 PASSO 9: Conectar ao WiFi e Testar

### 9.1 Descobrir IP do ESP32
No **Shell do Thonny**, executar:
```python
>>> import network
>>> wlan = network.WLAN(network.AP_IF)
>>> wlan.ifconfig()
('192.168.4.1', '255.255.255.0', '192.168.4.1', '8.8.8.8')
```

**IP do ESP32:** `192.168.4.1` (padrão para modo AP)

### 9.2 Conectar Tablet ao WiFi
No tablet:
1. Abrir **Configurações WiFi**
2. Procurar rede: `IHM_NEOCOUDE` (ou nome que você configurou)
3. Conectar com senha: `dobradeira123` (ou senha configurada)
4. Aguardar conexão

### 9.3 Testar no Navegador do Tablet
1. Abrir navegador (Chrome, Firefox, etc)
2. Acessar: `http://192.168.4.1/`
3. Interface IHM deve carregar

**Se não carregar:**
- Verificar tablet está conectado ao WiFi correto
- Verificar ESP32 não deu erro no console
- Tentar: `http://192.168.4.1/index.html`

---

## 🧪 PASSO 10: Testes Funcionais

### Teste 1: Estado da Máquina
No navegador do tablet (ou Ubuntu):
```
http://192.168.4.1/api/state
```

**Resposta esperada:**
```json
{
  "encoder_angle": 0.0,
  "bend_1_angle": 0.0,
  "bend_2_angle": 0.0,
  "bend_3_angle": 0.0,
  "speed_class": 5,
  "connected": true
}
```

### Teste 2: Gravar Ângulo via API
```
http://192.168.4.1/api/write_bend?bend=1&angle=45.0
```

**Resposta esperada:**
```json
{
  "success": true,
  "bend": 1,
  "angle": 45.0,
  "message": "OK"
}
```

**Verificar console ESP32:**
```
Gravando Dobra 1: 45.0° -> 0x0A00/0x0A02 (MSW=0, LSW=450)
  Acionando trigger 0x0390...
✓ OK: Dobra 1 = 45.0°
```

### Teste 3: Interface Web Completa
1. Abrir `http://192.168.4.1/` no tablet
2. Verificar encoder atualiza
3. Clicar em card "DOBRA 1"
4. Digitar `90.5`
5. Clicar "SALVAR"
6. Verificar card mostra "90.5°"

---

## 🐛 Troubleshooting

### Problema: "Permission denied: /dev/ttyUSB0"
**Solução:**
```bash
sudo chmod 666 /dev/ttyUSB0
# OU adicionar permanentemente:
sudo usermod -a -G dialout $USER
# Logout e login novamente
```

### Problema: "Could not enter REPL"
**Solução:**
1. Desconectar e reconectar USB
2. Apertar botão **EN** no ESP32
3. Thonny: Menu **Executar** → **Reiniciar backend**

### Problema: "MemoryError" durante upload
**Solução:**
1. Deletar arquivos desnecessários do ESP32
2. Upload arquivos um por um (não em lote)
3. Resetar ESP32 entre uploads grandes

### Problema: "ImportError: no module named 'umodbus'"
**Solução:**
Verificar estrutura de pastas:
```python
>>> os.listdir('/lib/umodbus')
['__init__.py', 'serial.py', 'functions.py']
```
Se faltar arquivo, refazer upload da pasta `lib/umodbus/`

### Problema: ESP32 reseta sozinho
**Causa:** Código tem erro de sintaxe ou import falhando
**Solução:**
1. Ver última mensagem de erro antes do reset
2. Corrigir arquivo com erro
3. Fazer upload novamente

### Problema: WiFi não aparece
**Solução:**
1. Verificar `boot.py` tem `WIFI_SSID` e `WIFI_PASSWORD` corretos
2. Verificar senha tem mínimo 8 caracteres
3. Resetar ESP32 e aguardar 10 segundos

---

## 📊 Monitoramento via Console Serial

### Manter Console Aberto
Para ver logs em tempo real:
1. Thonny aberto com Shell visível
2. Não executar comandos (deixar em branco)
3. Logs aparecem automaticamente:

```
✓ Serviu index.html
→ Cliente conectado: 192.168.4.2
✓ Comando executado: set_angle
Gravando Dobra 1: 90.5° -> 0x0A00/0x0A02 (MSW=0, LSW=905)
  Acionando trigger 0x0390...
✓ OK: Dobra 1 = 90.5°
[GC] RAM livre: 45832 bytes
```

---

## ✅ Checklist Final

Após completar todos os passos, verificar:

- [ ] Todos arquivos uploaded (boot.py, main.py, modbus_map.py, modbus_client_esp32.py)
- [ ] Pasta `static/index.html` criada
- [ ] Pasta `lib/umodbus/` criada com 3 arquivos
- [ ] ESP32 reseta sem erros
- [ ] Console mostra "Servidor HTTP iniciado em :80"
- [ ] WiFi `IHM_NEOCOUDE` aparece nas redes disponíveis
- [ ] Tablet conecta ao WiFi
- [ ] Navegador acessa `http://192.168.4.1/`
- [ ] API `/api/state` retorna JSON válido
- [ ] Teste de gravação via `/api/write_bend` funciona
- [ ] Interface web carrega e é responsiva
- [ ] Encoder atualiza em tempo real
- [ ] Cards de ângulo são clicáveis

**Se todos marcados:** Sistema está **100% operacional**! 🎉

---

## 📚 Próximos Passos

Após upload bem-sucedido:
1. ✅ Testar todos os 3 ângulos (Dobra 1, 2, 3)
2. ✅ Verificar leitura da área SCADA (0x0B00)
3. ✅ Testar controles de motor (AVANÇAR/PARAR/RECUAR)
4. ✅ Validar mudança de velocidade
5. ✅ Deixar rodando 24h para teste de estabilidade

---

**Versão:** 1.0
**Autor:** Eng. Lucas William Junges
**Data:** 18/Nov/2025
