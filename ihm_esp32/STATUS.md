# STATUS DO PROJETO - IHM Web

Data: 18/Nov/2025

## ✅ O QUE FOI FEITO

### 1. Correções no State Manager (COMPLETO)
- ✅ Removidas todas as escritas problemáticas em registros 0x0940-0x094E
- ✅ Removida leitura problemática do registro 0x094C (velocidade)
- ✅ Sistema agora opera 100% em modo leitura + inferência local
- ✅ Zero timeouts e travamentos no polling Modbus
- ✅ Encoder lendo corretamente: 30581 raw = 3058.1°

**Arquivos modificados:**
- `state_manager.py` - Método `write_supervision_area()` → `update_supervision_state()`
- `modbus_client.py` - Corrigido stub mode (comentado BEND_ANGLES)

### 2. Scripts Utilitários Criados (COMPLETO)
- ✅ `check_server.sh` - Verifica status do servidor
- ✅ `run_server.sh` - Gerencia servidor (start/stop/restart/status)
- ✅ `CHANGELOG.md` - Documentação completa das mudanças
- ✅ `QUICK_START.md` - Guia rápido de uso

## ⚠️ PROBLEMAS IDENTIFICADOS

### 1. Servidor HTTP Travando (CRÍTICO)
**Sintoma:** Porta 8080 abre mas não responde às requisições HTTP
**Causa:** Event loop do asyncio bloqueado pelo `state_manager.start_polling()`
**Detalhes:**
- Porta está aberta: ✅
- Processo rodando: ✅
- Responde a requisições HTTP: ❌ (timeout)

**Diagnóstico:**
O método `start_polling()` do state_manager roda um `while self.running:` que consome todo o tempo do event loop, impedindo que os coroutines do aiohttp (HTTP handler) sejam executados.

**Solução proposta:**
1. Rodar Modbus em thread separada usando `ThreadPoolExecutor`
2. Ou usar `await asyncio.sleep(0)` dentro do loop de polling para yield control
3. Ou redesenhar com `asyncio.create_task()` e garantir que tasks concorram corretamente

### 2. WebSocket vs HTTP Polling (PENDENTE)
**Requisição do usuário:** "Trocar HTTP polling por WebSockets"
**Status:** WebSocket JÁ ESTÁ IMPLEMENTADO no código!
- Backend: `main_server.py` já tem servidor WebSocket na porta 8765
- Frontend: `static/index.html` já usa WebSocket (linha 510: `ws://${wsHost}:8765`)

**Problema:** O servidor HTTP não está respondendo, então a interface não carrega para testar o WebSocket.

### 3. WiFi AP + STA Simultaneamente (NÃO INICIADO)
**Requisição do usuário:** RPi3 deve ser Access Point E conectar em WiFi ao mesmo tempo

**Passos necessários:**
1. Configurar `hostapd` (AP)
2. Configurar `dnsmasq` (DHCP)
3. Configurar `dhcpcd` (STA)
4. Habilitar IP forwarding e NAT para roteamento de internet
5. Testar servidor em ambos IPs (WiFi STA e AP)

**Arquivos já criados (mas não testados):**
- `config/hostapd.conf`
- `config/dnsmasq.conf`
- `config/dhcpcd.conf`
- `scripts/setup_wifi.sh`

### 4. Página não Carrega no Ubuntu (RELACIONADO AO ITEM 1)
**Causa:** Servidor HTTP não está respondendo (veja item 1)
**Solução:** Resolver o problema do event loop bloqueado

## 📋 PRÓXIMOS PASSOS (PRIORITÁRIOS)

### Passo 1: Resolver Event Loop Bloqueado
Escolher uma das opções:

**Opção A: Thread Pool (RECOMENDADO)**
```python
import concurrent.futures

# No main():
loop = asyncio.get_event_loop()
executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)

# Rodar polling Modbus em thread separada
def run_modbus_polling():
    while state_manager.running:
        state_manager.poll_once_sync()  # Versão síncrona
        time.sleep(0.25)

loop.run_in_executor(executor, run_modbus_polling)
```

**Opção B: Yield Control**
```python
# Em state_manager.py, dentro de start_polling():
async def start_polling(self):
    while self.running:
        start_time = time.time()
        await self.poll_once()
        elapsed = time.time() - start_time
        sleep_time = max(0, self.poll_interval - elapsed)
        await asyncio.sleep(sleep_time)
        await asyncio.sleep(0)  # ADICIONAR: Yield control para outros coroutines
```

**Opção C: Task Concurrency**
```python
# Garantir que todas as tasks rodem concorrentemente
async def main():
    modbus_task = asyncio.create_task(state_manager.start_polling())
    broadcast_task = asyncio.create_task(broadcast_loop())
    http_task = asyncio.create_task(start_http_server())
    ws_task = asyncio.create_task(start_ws_server())

    await asyncio.gather(modbus_task, broadcast_task, http_task, ws_task)
```

### Passo 2: Configurar WiFi AP + STA
```bash
cd /home/lucas-junges/Documents/wco/ihm_esp32
sudo bash scripts/setup_wifi.sh
```

### Passo 3: Testar Servidor em Ambos IPs
- IP da rede WiFi (STA): 192.168.0.213
- IP do Access Point (AP): 192.168.4.1

### Passo 4: Validar WebSocket
Testar que a interface web usa WebSocket e não HTTP polling.

## 🔍 COMANDOS DE DIAGNÓSTICO

### Verificar se servidor está rodando:
```bash
./check_server.sh
```

### Ver logs em tempo real:
```bash
tail -f ihm.log
```

### Testar HTTP sem interface:
```bash
curl -I http://localhost:8080/test
```

### Verificar portas abertas:
```bash
ss -tlnp | grep -E ":8080|:8765"
```

### Ver processos Python:
```bash
ps aux | grep python
```

## 📊 CONFIGURAÇÃO ATUAL

- **IP**: 192.168.0.213
- **Porta HTTP**: 8080
- **Porta WebSocket**: 8765
- **Modbus**: /dev/ttyUSB0 @ 57600 bps, slave 1
- **Encoder**: Lendo corretamente (3058.1°)

## 🎯 OBJETIVO FINAL

1. ✅ Servidor HTTP/WebSocket funcionando sem travamentos
2. ✅ WebSocket ativo (ao invés de HTTP polling)
3. ✅ RPi3 como AP + STA simultâneo
4. ✅ Roteamento de internet pelo AP
5. ✅ Interface acessível de qualquer dispositivo (Ubuntu, tablet, etc.)
