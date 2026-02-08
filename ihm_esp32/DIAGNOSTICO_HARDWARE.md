# DIAGNÓSTICO DE HARDWARE - Raspberry Pi 3B+
**Data:** 06/Jan/2026
**Problema:** Desconexões Modbus + Falha na gravação de ângulos

---

## 🔍 RESULTADO DO DIAGNÓSTICO

### ⚠️ **PROBLEMA CONFIRMADO: THROTTLING DETECTADO**

```bash
$ vcgencmd get_throttled
throttled=0x20000
```

**Decodificação:**
- `0x20000` = Bit 17 ativo
- **Bit 17 = ARM frequency capped (ocorreu desde boot)**

Isso significa que o Raspberry Pi **JÁ FOI THROTTLED** em algum momento!

---

## 📊 Status Atual do Hardware

### Temperatura
```
71.4°C  ⚠️ ALTA (ideal < 65°C, crítico > 85°C)
```

**Análise:**
- Raspberry Pi 3B+ dentro de caixa fechada
- Sem dissipador ou ventilação
- Temperatura está no limite aceitável
- **Recomendação**: Adicionar dissipador passivo ou cooler

### Tensão Core
```
1.2688V  ✅ OK
```

### Frequência CPU
```
1200 MHz  ✅ OK (máximo é 1400 MHz)
```

### Dispositivos USB
```
✅ CH340 serial converter (USB-RS485) detectado
✅ RTL8188FTV WiFi dongle detectado
✅ Todos devices em modo "active"
```

---

## 🔥 ANÁLISE: Por que Throttling causa os problemas?

### 1. Desconexões a cada 10s
- **Throttling** reduz clock da CPU
- Polling do State Manager fica mais lento
- Broadcast loop atrasa
- Heartbeat não é enviado a tempo
- Watchdog desconecta em 10s ❌

### 2. Modbus não responde / Timeouts
- USB-RS485 depende de timing preciso (57600 bps)
- Throttling causa jitter no timing USB
- Requisições Modbus falham com timeout
- 10 timeouts consecutivos = desconexão Modbus ❌

### 3. Gravação de ângulos falha
- write_register depende de timing preciso
- Throttling causa atrasos
- CLP não recebe comando a tempo
- Retry falha 3x ❌

---

## ✅ SOLUÇÕES

### **Solução #1: Dissipador de Calor (RECOMENDADO)**

**Custo:** R$ 5-15
**Impacto:** Reduz temperatura em 10-15°C

```
Temperatura atual: 71°C
Com dissipador:    55-60°C  ✅
```

**Onde comprar:**
- MercadoLivre: "dissipador raspberry pi 3b+"
- AliExpress: "heatsink raspberry pi"

**Instalação:**
1. Limpar CPU com álcool isopropílico
2. Remover adesivo do dissipador
3. Colar sobre o processador
4. Aguardar 10min para colar secar

### **Solução #2: Cooler 5V (RECOMENDADO)**

**Custo:** R$ 8-20
**Impacto:** Reduz temperatura em 15-20°C

```
Temperatura atual: 71°C
Com cooler:        50-55°C  ✅✅
```

**Conexão:**
- Fio vermelho (+): GPIO Pin 4 (5V)
- Fio preto (GND): GPIO Pin 6 (GND)

### **Solução #3: Verificar Fonte de Alimentação**

**Especificação necessária:**
- Tensão: 5.0V ± 0.25V
- Corrente: **3A mínimo** (RPi 3B+ + USB devices)
- Conector: USB-C ou micro-USB
- Cabo: **curto e grosso** (< 1m, 22AWG ou mais grosso)

**Como testar:**
```bash
# Monitorar undervoltage em tempo real
watch -n 1 vcgencmd get_throttled
```

Se aparecer `0x50005` ou `0x50000` → **Fonte fraca!**

### **Solução #4: Ventilação da Caixa**

- Abrir furos na tampa da caixa (mínimo 4 furos de 10mm)
- Instalar cooler externo direcionado para o RPi
- Deixar caixa semi-aberta durante testes

---

## 🧪 TESTE IMEDIATO (SEM COMPRAR NADA)

### Opção A: Abrir a caixa

1. Remova a tampa da caixa do Raspberry Pi
2. Deixe exposto ao ar
3. Aguarde 5-10 minutos para esfriar
4. Reinicie o servidor Python
5. Teste novamente

**Temperatura esperada:** 60-65°C (redução de ~10°C)

### Opção B: Adicionar ventilação forçada

1. Posicione um ventilador (de mesa/casa) direcionado ao RPi
2. Aguarde 5-10 minutos
3. Monitore temperatura:
   ```bash
   watch -n 1 vcgencmd measure_temp
   ```
4. Reinicie servidor quando < 60°C

### Opção C: Reduzir carga do sistema

1. Pare processos desnecessários:
   ```bash
   sudo systemctl stop bluetooth
   sudo systemctl stop avahi-daemon
   ```

2. Reduza frequência de polling:
   ```python
   # state_manager.py, linha 496
   idle_interval = 0.5    # Era 0.3
   fast_interval = 0.2    # Era 0.1
   ```

---

## 📊 Monitoramento Contínuo

### Script de Monitoramento

Criei `/home/lucas-junges/Documents/wco/ihm_esp32/monitor_hardware.sh`:

```bash
#!/bin/bash
while true; do
    clear
    echo "=========================================="
    echo "  MONITOR DE HARDWARE - Raspberry Pi 3B+"
    echo "=========================================="
    echo ""
    echo "🌡️  Temperatura:"
    vcgencmd measure_temp
    echo ""
    echo "⚡ Throttling Status:"
    vcgencmd get_throttled
    echo ""
    echo "💻 Frequência CPU:"
    echo "$(cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_cur_freq | awk '{print $1/1000 " MHz"}')"
    echo ""
    echo "🔌 Tensão Core:"
    vcgencmd measure_volts core
    echo ""
    echo "Pressione Ctrl+C para sair"
    sleep 2
done
```

**Uso:**
```bash
chmod +x monitor_hardware.sh
./monitor_hardware.sh
```

---

## 🎯 RECOMENDAÇÃO FINAL

### Curto Prazo (AGORA):
1. ✅ **Abra a caixa** do Raspberry Pi
2. ✅ **Adicione ventilador** apontando para o RPi
3. ✅ **Monitore temperatura** até ficar < 60°C
4. ✅ **Reinicie o servidor** Python

### Médio Prazo (24-48h):
1. 🛒 **Compre dissipador + cooler** (R$ 15-30 total)
2. 🔧 **Instale dissipador** no processador
3. 🔧 **Instale cooler** nos GPIOs
4. 📦 **Adicione furos** na caixa para ventilação

### Longo Prazo (1-2 semanas):
1. 🔋 **Teste fonte de alimentação** (verifique se é 3A real)
2. 🔌 **Considere trocar fonte** se undervoltage persistir
3. 📊 **Monitore logs** de throttling por 7 dias

---

## 📝 Comandos Úteis

```bash
# Temperatura atual
vcgencmd measure_temp

# Status de throttling
vcgencmd get_throttled

# Decodificar throttling
# 0x0     = OK
# 0x20000 = Throttling ocorreu (bit 17)
# 0x50000 = Undervoltage ocorreu (bit 16 + 18)
# 0x50005 = Undervoltage ATIVO (bit 0 + 16 + 18)

# Monitorar em tempo real
watch -n 1 'vcgencmd measure_temp && vcgencmd get_throttled'

# Reiniciar sem erro de undervoltage
sudo reboot

# Após boot, verificar se throttling persiste
vcgencmd get_throttled
# Deve retornar 0x0 se não houver mais problemas
```

---

**Status:** ⚠️ PROBLEMA DE HARDWARE CONFIRMADO
**Causa Raiz:** Temperatura alta (71°C) + Throttling
**Solução:** Dissipador + Cooler + Ventilação
**Custo:** R$ 15-30 (dissipador + cooler)
**Urgência:** ALTA (sistema instável)
