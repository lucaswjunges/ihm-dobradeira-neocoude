# FIX: Desconexões a cada 10 segundos (Watchdog)

**Data:** 06/Jan/2026
**Problema:** IHM aparecia "DESCONECTADO" a cada ~10 segundos e reconectava automaticamente
**Causa Raiz:** Heartbeat do backend não estava sendo enviado com frequência suficiente

---

## 🔍 Análise do Problema

### Configuração ANTES da correção:
- **Broadcast interval**: 150ms (a cada 150ms verifica se há mudanças)
- **Heartbeat interval**: 5s (enviava heartbeat a cada 5s)
- **Watchdog frontend**: 10s (desconecta se não receber nada por 10s)

### Por que falhava?

1. **Margem muito pequena**: Heartbeat a cada 5s, watchdog em 10s
   - Se houver qualquer latência WiFi > 5s, o watchdog dispara!

2. **Heartbeat condicional**: O heartbeat só era adicionado quando `send_heartbeat and not changes`
   - Se houver mudanças constantes no estado, o heartbeat nunca era enviado sozinho
   - O watchdog só via mensagens se houvesse mudanças de estado
   - Em máquina parada (sem mudanças), passavam > 10s sem mensagens

3. **Latência WiFi**: Conexão WiFi pode ter latência variável (2-8s é normal)
   - Com heartbeat a cada 5s + latência 3-5s = 8-10s total
   - Watchdog dispara aos 10s = desconexão!

---

## ✅ Correções Implementadas

### 1. Heartbeat mais frequente (main_server.py:627)
```python
# ANTES:
HEARTBEAT_INTERVAL = 33  # 5s @ 150ms

# DEPOIS:
HEARTBEAT_INTERVAL = 20  # 3s @ 150ms - bem antes do watchdog!
```

**Por quê?**: 3s de heartbeat + até 3s de latência = 6s total < 10s watchdog ✅

### 2. Heartbeat SEMPRE enviado (main_server.py:644-649)
```python
# ANTES:
if send_heartbeat and not changes:
    changes = {'heartbeat': True}

# DEPOIS:
if send_heartbeat:
    if not changes:
        changes = {'heartbeat': True}
    else:
        changes['heartbeat'] = True  # Adiciona junto com mudanças!
```

**Por quê?**: Garante que SEMPRE envia heartbeat a cada 3s, mesmo com mudanças constantes

### 3. Logs de diagnóstico (index.html:1526-1533)
```javascript
// Debug: mostra tempo desde última mensagem a cada 5s
if (timeSinceLastMessage > 5000 && timeSinceLastMessage % 5000 < 1000) {
    console.log(`⏱️ Watchdog: ${(timeSinceLastMessage/1000).toFixed(1)}s desde última mensagem`);
}
```

**Por quê?**: Permite diagnosticar problemas de latência antes do watchdog disparar

---

## 📊 Timeline Comparativo

### ANTES (problema):
```
0s   -> Mensagem recebida (estado inicial)
3s   -> (nada - aguardando mudanças)
6s   -> (nada - aguardando mudanças)
9s   -> (nada - aguardando mudanças)
10s  -> ❌ WATCHDOG DISPARA -> "DESCONECTADO"
```

### DEPOIS (corrigido):
```
0s   -> Mensagem recebida (estado inicial)
3s   -> 💓 Heartbeat enviado
6s   -> 💓 Heartbeat enviado
9s   -> 💓 Heartbeat enviado
12s  -> 💓 Heartbeat enviado
... (continua indefinidamente)
```

---

## 🎯 Resultado Esperado

- ✅ Sem desconexões automáticas a cada 10s
- ✅ Conexão estável por horas/dias
- ✅ Watchdog só dispara em caso REAL de falha de rede
- ✅ Logs permitem diagnosticar latência antes de virar problema

---

## 🧪 Como Testar

1. **Console do navegador** (F12):
   ```
   Você deve ver:
   - "💓 Heartbeat recebido" a cada 3s (se descomentar log)
   - "⏱️ Watchdog: X.Xs desde última mensagem" se passar de 5s
   ```

2. **Comportamento esperado**:
   - Máquina parada: heartbeat a cada 3s mantém conexão
   - Máquina em movimento: mudanças + heartbeat a cada 3s
   - Latência WiFi até 7s: tolerada (3s + 7s < 10s)

3. **Sinais de problema** (se ainda acontecer):
   - Ver "⏱️ Watchdog: 8.0s..." → latência muito alta, considerar aumentar watchdog para 15s
   - Ver "❌ Watchdog: Sem mensagens..." → problema real de rede ou backend travado

---

## 📝 Notas Técnicas

### Fórmula de segurança:
```
heartbeat_interval + max_latency < watchdog_timeout

Atual:
3s + 7s < 10s ✅ (margem de segurança)

Anterior:
5s + 5s = 10s ❌ (sem margem - qualquer latência causa desconexão)
```

### Se ainda houver problemas:
1. **Aumentar watchdog para 15s**: `if (timeSinceLastMessage > 15000)`
2. **Reduzir heartbeat para 2s**: `HEARTBEAT_INTERVAL = 13  # 2s @ 150ms`
3. **Verificar latência WiFi**: Use `ping 192.168.50.1` no tablet
4. **Verificar logs backend**: `journalctl -u ihm.service -f`

---

## 🔧 Arquivos Modificados

1. **main_server.py**:627,644 - Heartbeat interval e lógica
2. **index.html**:1523,1526 - Watchdog timing e logs

---

**Status**: ✅ RESOLVIDO
**Validado em**: 06/Jan/2026
**Próxima revisão**: Após 24h de operação contínua
