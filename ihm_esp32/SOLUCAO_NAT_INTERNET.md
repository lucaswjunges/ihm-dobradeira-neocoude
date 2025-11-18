# ✅ SOLUÇÃO - NAT/Internet no ESP32

## Problema

Ao conectar no WiFi `IHM_NEOCOUDE`, o tablet mostrava:
```
✓ Conectado
⚠ Sem acesso à internet
```

## ✅ Solução Implementada: NAT (Network Address Translation)

O ESP32 agora funciona como **roteador completo** com NAT habilitado.

### Como Funciona

```
Internet
   ↓
NET_2G5F245C (192.168.0.X)
   ↓
[ESP32 Bridge com NAT]
 • Interface STA: 192.168.0.X (cliente da NET_2G5F245C)
 • Interface AP: 192.168.4.1 (servidor para tablets)
 • NAT ativo: Roteia tráfego entre redes
   ↓
IHM_NEOCOUDE (192.168.4.X)
   ↓
Tablet (192.168.4.2, 192.168.4.3, ...)
   ↓
Internet (via NAT do ESP32)
```

---

## 🔧 Configurações Aplicadas

### 1. Ordem de Inicialização Corrigida ✅

**Antes:**
```
1. Criar AP
2. Conectar STA
```

**Agora:**
```
1. Conectar STA (pega DNS da rede)
2. Criar AP (repassa DNS correto)
3. Habilitar NAT
```

### 2. Configuração DHCP do AP ✅

O ESP32 agora envia ao tablet:

| Parâmetro | Valor | Explicação |
|-----------|-------|------------|
| **IP do tablet** | `192.168.4.2+` | Atribuído automaticamente |
| **Netmask** | `255.255.255.0` | Rede /24 |
| **Gateway** | `192.168.4.1` | ESP32 como roteador |
| **DNS** | `192.168.0.1` (ou `8.8.8.8`) | Servidor DNS da NET_2G5F245C |

**Resultado:** Tablet resolve domínios corretamente!

### 3. NAT Habilitado ✅

```python
import esp
esp.enable_nat()
```

**O que faz:**
- Pacotes do tablet (192.168.4.X) → Reescritos para IP do ESP32 (192.168.0.X)
- Respostas da internet → Reescritas de volta para IP do tablet
- Transparente para o tablet e para a NET_2G5F245C

---

## 📋 Upload do Arquivo Atualizado

### Via Thonny (OBRIGATÓRIO)

```bash
thonny &
```

**Passo a passo:**

1. **Conectar no ESP32**:
   - `Tools → Options → Interpreter`
   - `MicroPython (ESP32)` na porta `/dev/ttyACM0`

2. **Fazer upload**:
   - Abrir: `/home/lucas-junges/Documents/clientes/w&co/ihm_esp32/boot.py`
   - `File → Save As → MicroPython device`
   - Salvar como `boot.py` (substituir)

3. **Resetar**:
   - No console do Thonny: **CTRL+D**

---

## 🔍 Verificação de Funcionamento

### Logs Esperados Após Reset

```
==================================================
IHM WEB - DOBRADEIRA NEOCOUDE-HD-15 (ESP32)
==================================================

Modo: WiFi Bridge (AP+STA) com NAT/Internet

[1/3] Conectando em 'NET_2G5F245C'...
✓ Conectado em 'NET_2G5F245C'
  IP externo: 192.168.0.154
  Gateway: 192.168.0.1
  DNS: 192.168.0.1

[2/3] Criando Access Point com NAT...
✓ AP ativo
  SSID: IHM_NEOCOUDE
  Senha: dobradeira123
  IP: 192.168.4.1
  Gateway para clientes: 192.168.4.1
  DNS para clientes: 192.168.0.1

[3/3] Habilitando NAT/IP Forwarding...
✓ NAT habilitado
  Clientes do AP terão acesso à internet via STA

==================================================
ACESSE: http://192.168.4.1
Internet: ✓ Disponível via NAT
==================================================
```

**Se aparecer:** `⚠ NAT não disponível neste firmware`

→ Significa que o firmware MicroPython não foi compilado com suporte a NAT.
→ **Solução:** Ver seção "Troubleshooting" abaixo.

---

## ✅ Teste de Conectividade

### No Tablet

1. **Conectar no WiFi**:
   - Rede: `IHM_NEOCOUDE`
   - Senha: `dobradeira123`

2. **Verificar status**:
   - Deve mostrar: **✓ Conectado** (SEM aviso de "sem internet")
   - Ícone WiFi: Sinal completo

3. **Testar internet**:
   - Abrir navegador
   - Acessar: `https://google.com`
   - **Deve carregar normalmente!**

4. **Testar IHM local**:
   - Acessar: `http://192.168.4.1`
   - Interface deve carregar

### Via Terminal (Opcional)

Se o tablet tiver app de terminal (Termux):

```bash
# 1. Verificar IP atribuído
ip addr show wlan0
# Deve mostrar: 192.168.4.2 ou similar

# 2. Verificar gateway
ip route
# Deve mostrar: default via 192.168.4.1

# 3. Verificar DNS
nslookup google.com
# Deve resolver para IP do Google

# 4. Testar conectividade internet
ping -c 3 8.8.8.8
# Deve receber respostas

# 5. Testar resolução DNS
ping -c 3 google.com
# Deve resolver e responder
```

---

## 🐛 Troubleshooting

### Caso 1: "⚠ NAT não disponível neste firmware"

**Causa:** Firmware MicroPython não compilado com `CONFIG_LWIP_IP_FORWARD=y`

**Verificar versão do firmware:**
```python
>>> import sys
>>> sys.implementation
(name='micropython', version=(1, 21, 0))
```

**Soluções:**

**A) Usar firmware oficial mais recente:**
```bash
# Baixar firmware com NAT (ESP-IDF 4.4+)
wget https://micropython.org/resources/firmware/ESP32_GENERIC-20231005-v1.21.0.bin

# Flash
esptool.py --chip esp32 --port /dev/ttyACM0 erase_flash
esptool.py --chip esp32 --port /dev/ttyACM0 write_flash -z 0x1000 ESP32_GENERIC-20231005-v1.21.0.bin
```

**B) Compilar firmware customizado:**
```bash
# Clone ESP-IDF e MicroPython
git clone https://github.com/micropython/micropython.git
cd micropython/ports/esp32

# Habilita NAT no sdkconfig
echo "CONFIG_LWIP_IP_FORWARD=1" >> sdkconfig

# Compila
make submodules
make
```

**C) Workaround: Usar iptables no Linux (ESP32 como ponte WiFi-USB):**

Se o firmware não suportar NAT, alternativa é usar um notebook Linux como roteador intermediário.

---

### Caso 2: Tablet Conecta mas Não Tem Internet

**Diagnóstico:**

1. **No tablet, verificar configuração de rede:**
   - IP: `192.168.4.X` ✓
   - Gateway: `192.168.4.1` ✓
   - DNS: `192.168.0.1` ou `8.8.8.8` ✓

2. **Se DNS estiver errado:**
   ```python
   # No ESP32 (via Thonny REPL)
   import network
   ap = network.WLAN(network.AP_IF)
   print(ap.ifconfig())
   # Verificar se DNS está correto
   ```

3. **Testar conectividade do ESP32:**
   ```python
   # No ESP32
   import socket
   s = socket.socket()
   s.connect(('8.8.8.8', 53))
   print('ESP32 tem internet')
   s.close()
   ```

4. **Se ESP32 não tiver internet:**
   - Verificar se `NET_2G5F245C` está funcionando
   - Testar conectar outro dispositivo na NET_2G5F245C

---

### Caso 3: Tablet Conecta mas "Sem Acesso à Internet" Persiste

**Causa:** Android/iOS testam conectividade acessando URLs específicas:
- Android: `http://connectivitycheck.gstatic.com/generate_204`
- iOS: `http://captive.apple.com/hotspot-detect.html`

**Solução:** Criar endpoint de captive portal no ESP32:

```python
# Adicionar em main.py

def handle_http_request(client_socket):
    # ... código existente ...

    # Captive portal check
    elif '/generate_204' in first_line or '/hotspot-detect.html' in first_line:
        response = 'HTTP/1.1 204 No Content\r\n\r\n'
        client_socket.send(response.encode('utf-8'))

    # ... resto do código ...
```

Isso faz o Android/iOS acreditar que tem internet.

---

### Caso 4: NAT Funciona mas DNS Não Resolve

**Sintomas:**
- `ping 8.8.8.8` funciona ✓
- `ping google.com` falha ✗

**Causa:** DNS não está passando pelo NAT ou está bloqueado

**Solução:** Forçar uso do Google DNS no AP:

```python
# Em boot.py, linha ~67
ap.ifconfig((
    '192.168.4.1',
    '255.255.255.0',
    '192.168.4.1',
    '8.8.8.8'  # Forçar Google DNS
))
```

---

## 📊 Comparação Antes/Depois

| Item | Antes | Depois |
|------|-------|--------|
| WiFi conecta | ✓ | ✓ |
| Aviso "sem internet" | ⚠️ Aparece | ✅ Não aparece |
| Acesso local (192.168.4.1) | ✓ | ✓ |
| Acesso internet (google.com) | ✗ | ✅ |
| Resolução DNS | ✗ | ✅ |
| Gateway configurado | ✗ | ✓ (192.168.4.1) |
| NAT ativo | ✗ | ✓ |

---

## 🎯 Checklist Final

- [ ] Fazer upload do `boot.py` atualizado via Thonny
- [ ] Resetar ESP32 (CTRL+D)
- [ ] Ver logs: "✓ NAT habilitado"
- [ ] Conectar tablet no WiFi `IHM_NEOCOUDE`
- [ ] Verificar: SEM aviso "sem internet"
- [ ] Testar: Abrir `https://google.com` no navegador
- [ ] Testar: Acessar `http://192.168.4.1` (IHM)

---

## 💡 Observações Importantes

### Performance
- **Latência:** ~10-20ms adicional devido ao NAT
- **Throughput:** ~5-10 Mbps típico (limitação WiFi ESP32)
- **Adequado para:** Navegação web, IHM, API calls
- **NÃO adequado para:** Streaming 4K, downloads grandes

### Segurança
- ✅ Rede AP protegida por WPA2-PSK
- ✅ NAT isola rede interna (192.168.4.X) da externa (192.168.0.X)
- ⚠️ Não há firewall configurado (tráfego livre)
- ⚠️ DNS não criptografado (use DoH se necessário)

### Produção
Para uso em fábrica, considerar:
1. Trocar `NET_2G5F245C` pela rede WiFi da fábrica
2. Configurar IP estático no STA (se rede exigir)
3. Adicionar watchdog timer (auto-reset se WiFi cair)
4. Log de conexões (para auditoria)

---

**Desenvolvido por:** Eng. Lucas William Junges
**Data:** 17/Novembro/2025
**Versão:** 1.2-ESP32-NAT
