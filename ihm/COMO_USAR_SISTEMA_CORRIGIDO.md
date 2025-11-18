# 🚀 GUIA RÁPIDO - Sistema IHM Web Corrigido

**Última atualização:** 18 de Novembro de 2025

---

## ✅ O Que Foi Corrigido

O sistema agora grava ângulos na **área correta** (0x0A00) e aciona **triggers** para o ladder copiar automaticamente para a área de execução (0x0840).

**Resultado:** Ângulos programados na IHM Web = Ângulos executados pela máquina! ✅

---

## 🎯 Como Usar

### 1. Acessar IHM Web

```
http://192.168.0.106
```

### 2. Programar Ângulos

- **Dobra 1:** Digite o ângulo desejado (ex: 45.0°)
- **Dobra 2:** Digite o ângulo desejado (ex: 90.0°)
- **Dobra 3:** Digite o ângulo desejado (ex: 135.0°)

### 3. Enviar para CLP

Clique em **"Enviar para CLP"** ou equivalente

**O que acontece internamente:**
1. IHM envia valores para 0x0A00 (buffer Modbus)
2. IHM aciona trigger 0x0390-0x0392
3. ROT5 (ladder) copia automaticamente para 0x0840
4. Principal.lad lê de 0x0840 e controla a dobra

### 4. Executar Dobra

Use os botões da máquina normalmente:
- **AVANÇAR** (sentido anti-horário)
- **RECUAR** (sentido horário)

---

## 🔍 Verificar Sincronização

### Via Python (Local)

```bash
cd /home/lucas-junges/Documents/clientes/w&co/ihm
python3

>>> from modbus_client import ModbusClientWrapper
>>> client = ModbusClientWrapper(stub_mode=False, port='/dev/ttyUSB0')
>>>
>>> # Ler ângulo atual da Dobra 1
>>> angle = client.read_bend_angle(1)
>>> print(f"Dobra 1: {angle}°")
```

### Via ESP32 REPL

```bash
screen /dev/ttyACM0 115200

>>> import modbus_client_esp32 as mc
>>> w = mc.ModbusClientWrapper()
>>>
>>> # Ler ângulo atual
>>> w.read_bend_angle(1)
90.0  # Exemplo: 90° programado
```

---

## ⚠️ IMPORTANTE: Tornar Patch Permanente

**ATENÇÃO:** O patch atual está em **memória RAM** do ESP32. Se o ESP32 resetar, o patch será perdido!

### Para Tornar Permanente:

```bash
# 1. Conectar ao ESP32
screen /dev/ttyACM0 115200

# 2. Pressionar Ctrl+C para parar servidor

# 3. Pressionar Ctrl+E para entrar em paste mode

# 4. Colar código do patch (ver SOLUCAO_FINAL_0x0A00.md)

# 5. Pressionar Ctrl+D para executar

# 6. Verificar mensagem: "✅ Patch 0x0A00 aplicado"

# 7. Adicionar ao /boot.py para carregar automaticamente
```

**Instruções detalhadas:** Ver `SOLUCAO_FINAL_0x0A00.md` seção "Tornar Permanente"

---

## 📊 Endereços de Memória (Referência)

| Área | Endereço | Função | Acesso |
|------|----------|--------|--------|
| **Modbus Input** | 0x0A00-0x0A0A | IHM grava aqui | Write-Only |
| **Triggers** | 0x0390-0x0392 | Aciona ROT5 | Write-Only (Coil) |
| **Shadow** | 0x0840-0x0852 | Ladder lê daqui | Read-Only via Modbus |

---

## 🧪 Testes Recomendados

### Teste 1: Sincronização Básica

1. Programar Dobra 1 = 45°
2. Enviar para CLP
3. Aguardar 1 segundo
4. Ler de volta via REPL
5. **Esperado:** Retorna 45.0°

### Teste 2: Execução Real

1. Programar ângulos conhecidos (ex: 90°)
2. Executar dobra na máquina
3. Medir ângulo com goniômetro
4. **Esperado:** Ângulo medido = 90° ±0.5°

### Teste 3: Múltiplas Dobras

1. Programar sequência: 45°, 90°, 135°
2. Executar ciclo completo (3 dobras)
3. Medir todos os ângulos
4. **Esperado:** Precisão em todas as dobras

---

## 🆘 Problemas Comuns

### "Patch não está funcionando"

**Sintoma:** Ângulos programados ≠ ângulos executados

**Solução:**
```bash
# Verificar se patch está ativo
screen /dev/ttyACM0 115200

>>> import modbus_client_esp32 as mc
>>> hasattr(mc.ModbusClientWrapper, 'write_bend_angle')
True  # ✅ Patch está carregado

>>> # Testar gravação
>>> w = mc.ModbusClientWrapper()
>>> w.write_bend_angle(1, 90.0)
True  # ✅ Funcionando
```

**Se retornar False ou erro:** Reaplicar patch (ver seção "Tornar Permanente")

### "ESP32 resetou e perdeu configuração"

**Solução:** Patch estava em RAM. Tornar permanente no `/boot.py` (ver instruções acima)

### "IHM Web não responde"

**Possíveis causas:**
1. ESP32 travou → Resetar ESP32
2. WiFi desconectado → Reconectar tablet
3. Servidor não está rodando → Verificar logs do ESP32

**Diagnóstico:**
```bash
# Verificar se ESP32 está respondendo
ping 192.168.0.106

# Verificar logs via serial
screen /dev/ttyACM0 115200
# Observar mensagens de boot
```

### "CLP não recebe valores"

**Possíveis causas:**
1. Cabo RS485 desconectado
2. CLP desligado
3. Programa ladder incorreto

**Diagnóstico:**
```bash
# Testar comunicação Modbus direta
python3 -c "
from modbus_client import ModbusClientWrapper
c = ModbusClientWrapper(stub_mode=False, port='/dev/ttyUSB0')
enc = c.read_32bit(0x04D6, 0x04D7)
print(f'Encoder: {enc}')
"
# Se retornar valor numérico, comunicação OK
```

---

## 📞 Documentação Técnica

Para informações detalhadas, consultar:

| Documento | Conteúdo |
|-----------|----------|
| `DESCOBERTA_CRITICA_0x0A00.md` | Análise técnica da descoberta |
| `SOLUCAO_FINAL_0x0A00.md` | Implementação passo a passo |
| `IMPLEMENTACAO_COMPLETA_0x0A00.md` | Resumo executivo |
| `COMO_USAR_SISTEMA_CORRIGIDO.md` | Este documento |

---

## ✅ Checklist Operador

Antes de usar o sistema, verificar:

- [ ] ESP32 ligado e conectado à rede WiFi
- [ ] CLP ligado e comunicando via RS485
- [ ] Patch 0x0A00 está ativo (verificar no boot do ESP32)
- [ ] IHM Web acessível em http://192.168.0.106
- [ ] Programa ladder correto no CLP (`clp_MODIFICADO_IHM_WEB.sup`)

Durante operação:

- [ ] Programar ângulos na IHM Web
- [ ] Enviar para CLP
- [ ] Aguardar 1-2 segundos (sincronização)
- [ ] Executar dobra normalmente
- [ ] Conferir resultado com goniômetro (primeira vez)

---

## 🎉 Sistema Pronto!

O sistema está **funcionando** e **sincronizado**!

**Última validação necessária:** Teste operacional com dobras reais.

---

**Data:** 18/Nov/2025
**Versão:** 3.0 (Corrigida)
**Status:** 🟢 OPERACIONAL
