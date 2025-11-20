# STATUS ATUAL - IHM Web - 20/Nov/2025

## ✅ O QUE ESTÁ FUNCIONANDO

### 1. Comunicação Modbus (100% Validado)
- ✅ Escrita de ângulos: **OK** (endereços 0x0A00, 0x0A04, 0x0A08)
- ✅ Leitura de ângulos: **OK** (endereços 0x0842, 0x0848, 0x0852)
- ✅ Formato 16-bit: **OK** (1 registro por ângulo)
- ✅ Leitura de encoder: **OK** (30581 raw = 3058.1°)
- ✅ Conversão: **OK** (valor_clp = graus * 10)

**Teste direto via Python funciona 100%:**
```python
from modbus_client import ModbusClientWrapper
client = ModbusClientWrapper(stub_mode=False, port='/dev/ttyUSB0')
client.write_bend_angle(1, 90.0)  # ✅ Funciona
angle = client.read_bend_angle(1)  # ✅ Retorna 90.0
client.close()
```

### 2. Servidor HTTP (OK)
- ✅ Porta 8080: **RESPONDENDO**
- ✅ Interface web: **CARREGA** (http://localhost:8080)
- ✅ Arquivos estáticos: **OK**
- ✅ Servidor rodando: **PID 12317**
- ✅ Modo LIVE: **OK** (/dev/ttyUSB0)
- ✅ Auto-start (systemd): **CONFIGURADO**

### 3. Configuração Systemd
- ✅ Serviço criado: `/etc/systemd/system/ihm-web.service`
- ✅ Modo LIVE configurado: `--port /dev/ttyUSB0`
- ✅ Auto-start habilitado: `systemctl enable ihm-web`
- ✅ Logs disponíveis: `sudo journalctl -u ihm-web -f`

---

## ❌ O QUE NÃO ESTÁ FUNCIONANDO

### 1. WebSocket (PROBLEMA)
- ❌ Porta 8765: **ABERTA** mas **NÃO ACEITA CONEXÕES**
- ❌ Conexões via Python: **TIMEOUT**
- ❌ Interface web: **FICA CARREGANDO** (aguardando WebSocket)

**Sintoma:**
- A porta está em LISTEN (confirmado por `lsof`)
- Mas tentativas de conexão ficam penduradas/timeout
- O handler `handle_websocket()` nunca é chamado

**Causa Provável:**
- Problema no loop assíncrono do WebSocket server
- Possível conflito entre `aiohttp` (HTTP) e `websockets` (WebSocket) rodando no mesmo event loop
- O `async with websockets.serve()` pode não estar entrando no contexto corretamente

---

## 🔍 DIAGNÓSTICO

### Comandos de Verificação

```bash
# Ver status do servidor
sudo systemctl status ihm-web

# Ver logs em tempo real
sudo journalctl -u ihm-web -f

# Verificar portas abertas
sudo lsof -i :8080 -i :8765

# Verificar processo rodando
ps aux | grep main_server

# Testar HTTP (deve funcionar)
curl http://localhost:8080

# Testar WebSocket (dá timeout)
python3 -c "import asyncio; import websockets; asyncio.run(websockets.connect('ws://localhost:8765'))"
```

### Logs Atuais

```
Nov 20 12:14:25 raspberrypi3 systemd[1]: Started ihm-web.service
lucas-junges  12317  /usr/bin/python3 main_server.py --port /dev/ttyUSB0
tcp  0  0.0.0.0:8080  0.0.0.0:*  LISTEN  12317/python3
tcp  0  0.0.0.0:8765  0.0.0.0:*  LISTEN  12317/python3
```

---

## 🛠️ SOLUÇÕES TENTADAS

1. ✅ Corrigido formato Modbus (32-bit → 16-bit)
2. ✅ Corrigido pymodbus addressing (adicionado `slave=` parameter)
3. ✅ Corrigido systemd service (stub → live mode)
4. ✅ Desabilitado serviços conflitantes
5. ✅ Adicionado logs de debug ao servidor
6. ❌ WebSocket ainda não funciona (problema persiste)

---

## 🚀 PRÓXIMOS PASSOS SUGERIDOS

### Opção 1: Testar Direto no Navegador (RECOMENDADO)

**O problema pode ser específico dos testes via linha de comando.** O navegador pode conseguir conectar normalmente.

**Teste:**
1. No celular, acessar: http://192.168.50.1:8080
2. Abrir DevTools do navegador (F12)
3. Verificar aba Console se há erros
4. Verificar aba Network > WS se WebSocket conectou
5. Tentar gravar um ângulo

**Se funcionar no navegador:** Problema resolvido! Usar normalmente.
**Se não funcionar:** Continuar para Opção 2.

### Opção 2: Refatorar Servidor (Separar HTTP e WebSocket)

Criar dois processos separados:
- Processo 1: HTTP server (porta 8080)
- Processo 2: WebSocket server (porta 8765)

Isso evita conflitos entre `aiohttp` e `websockets`.

### Opção 3: Usar Outro Framework

Substituir `aiohttp` + `websockets` por um framework integrado:
- **FastAPI** + **WebSockets nativo**
- **Tornado** (HTTP + WebSocket integrado)
- **Sanic** (async HTTP + WebSocket)

### Opção 4: Debug Profundo

Adicionar logging extensivo ao código:
- Log em cada etapa do `run()`
- Log no início de `handle_websocket()`
- Capturar exceções silenciosas
- Verificar se event loop está travado

---

## 📊 RESUMO EXECUTIVO

### O Que Funciona 100%
- Modbus RTU (CLP ↔ Raspberry Pi)
- Gravação/leitura de ângulos no CLP
- Servidor HTTP
- Interface web carrega

### O Que Precisa Corrigir
- **WebSocket não aceita conexões**
  - Porta aberta mas não responde
  - Interface fica "carregando" eternamente

### Impacto
- **Interface web inutilizável** (depende de WebSocket)
- **Gravação via web NÃO funciona**
- **Leitura via Python direto FUNCIONA** (workaround temporário)

### Recomendação
**Testar no navegador do celular primeiro.** Se não funcionar, refatorar o servidor para separar HTTP e WebSocket em processos distintos.

---

## 📝 NOTAS TÉCNICAS

### Endereços Modbus Validados

| Tipo | Dobra | Escrita | Leitura |
|------|-------|---------|---------|
| Ângulo | 1 | 0x0A00 | 0x0842 |
| Ângulo | 2 | 0x0A04 | 0x0848 |
| Ângulo | 3 | 0x0A08 | 0x0852 |
| RPM | - | 0x0A02 | 0x06E0 |

### Configuração Modbus
- Porta: `/dev/ttyUSB0`
- Baudrate: 57600
- Slave ID: 1
- Formato: 16-bit (1 registro)
- Conversão: CLP = graus × 10

### Arquivos Chave
- `/etc/systemd/system/ihm-web.service` - Serviço systemd
- `/home/lucas-junges/Documents/wco/ihm_esp32/main_server.py` - Servidor principal
- `/home/lucas-junges/Documents/wco/ihm_esp32/modbus_client.py` - Cliente Modbus (OK)
- `/home/lucas-junges/Documents/wco/ihm_esp32/static/index.html` - Interface web

---

**Última atualização:** 20/Nov/2025 12:20
**Status:** Modbus 100% ✅ | HTTP OK ✅ | WebSocket FALHA ❌
