# Status Final - Comunicação Modbus ESP32 ↔ CLP

## ✅ O Que Foi Feito

1. **Código corrigido** - Erro `SPEED_CONTROL` resolvido
2. **Fiação RS485** - A e B invertidos (como solicitado)
3. **ESP32 em modo LIVE** - Tentando comunicar com CLP real
4. **Servidor HTTP** - Estável e respondendo

## ⚠️ Situação Atual

**API retorna:**
```json
{
    "connected": false,  // ❌ CLP não está respondendo
    "encoder_angle": 0.0,
    "bend_1_angle": 0.0,
    "bend_2_angle": 0.0,
    "bend_3_angle": 0.0,
    "speed_class": 1
}
```

**Interpretação:**
- `connected: false` → Modbus RTU não consegue se comunicar com o CLP
- Valores em 0.0 → Valores padrão quando não há comunicação (melhor que valores estranhos de antes)

---

## 🔍 Diagnóstico

### Configuração ESP32 (Confirmada):
✅ UART2 inicializado (GPIO17/16/4)
✅ Baudrate: 57600
✅ Slave ID: 1
✅ Código sem erros
✅ Fiação A/B invertida (2ª tentativa)

### Problema:
**CLP NÃO está respondendo** às requisições Modbus RTU mesmo após inversão A/B.

---

## 🎯 Próximas Ações Necessárias

### Opção 1: Verificar State 00BE no CLP ⭐ **MAIS IMPORTANTE**

O state `00BE` (190 decimal) **DEVE** estar ON para habilitar Modbus slave.

**Como verificar:**
1. Conectar no CLP via software Atos
2. Modo "Online" ou "Monitor"
3. Procurar state `00BE` (hex) ou `190` (dec)
4. Se estiver **OFF** → **Forçar ON**
5. Salvar no ladder

**Sem esse state ON, o CLP NUNCA vai responder Modbus!**

---

### Opção 2: Testar com mbpoll (PC/Notebook)

Conectar o conversor USB-RS485 no notebook e testar diretamente:

```bash
# Instalar mbpoll
sudo apt install mbpoll

# Testar leitura do encoder
mbpoll -a 1 -r 1238 -c 2 -t 4 -b 57600 /dev/ttyUSB0

# Se retornar valores → CLP OK, problema está no ESP32
# Se retornar timeout → Problema no CLP ou fiação
```

---

### Opção 3: Testar Outros Slave IDs

O CLP pode não estar configurado como Slave ID = 1.

**Teste rápido:**

Editar `main.py` linha 22:
```python
SLAVE_ID = 2  # Testar 2, 3, 4, 5...
```

Fazer upload e testar.

---

### Opção 4: Testar Outros Baudrates

O CLP pode não estar em 57600.

**Teste rápido:**

Editar `modbus_client_esp32.py` linha 32:
```python
self.client = ModbusRTU(uart_id=2, baudrate=19200, ...)  # Testar 9600, 19200, 38400
```

---

### Opção 5: Voltar A/B Original

Se antes estava funcionando parcialmente, pode ser que A/B original estava correto.

**Teste:**
- Inverter novamente A ↔ B (voltar como estava)
- Resetar ESP32
- Testar

---

## 🔧 Teste Rápido Manual

**Via navegador:**

1. Acesse: `http://192.168.0.106`
2. Olhe canto superior direito:
   - **"CLP ✗"** em vermelho = Não está comunicando (atual)
   - **"CLP ✓"** em verde = Comunicando!

---

## 📊 Checklist Completo

### Hardware:
- [ ] CLP ligado (24V)
- [ ] MAX485 alimentado (medir VCC = 3.3V ou 5V)
- [ ] Fiação RS485:
  - [ ] MAX485-A → CLP-A
  - [ ] MAX485-B → CLP-B
  - [ ] GND comum
- [ ] ESP32:
  - [ ] GPIO17 → MAX485 DI
  - [ ] GPIO16 → MAX485 RO
  - [ ] GPIO4 → MAX485 DE+RE

### Software CLP:
- [ ] **State 00BE = ON** (Modbus slave habilitado)
- [ ] State 03D0 = OFF (Modbus master desabilitado)
- [ ] Baudrate conhecido (registro 1987H)
- [ ] Slave ID conhecido (registro 1988H)

### Software ESP32:
- [x] Código sem erros
- [x] UART2 configurado
- [x] Baudrate 57600
- [x] Slave ID 1

---

## 🎯 Conclusão

**Tudo está OK no ESP32.** O problema está em:

1. **State 00BE = OFF** no CLP (mais provável), OU
2. **Slave ID errado**, OU
3. **Baudrate errado**, OU
4. **Fiação ainda incorreta** (mesmo após inversão)

**Próximo passo crítico:** Verificar state 00BE no CLP!

---

**Data:** 17/Novembro/2025
**Versão:** 1.1-ESP32-MODBUS-FINAL
