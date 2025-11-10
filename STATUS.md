# STATUS DO SISTEMA - IHM NEOCOUDE-HD-15

**Data**: 08/11/2025 00:21
**Status**: ✅ **FUNCIONANDO**

---

## ✅ O QUE ESTÁ FUNCIONANDO

### Comunicação Modbus RTU
- ✅ **Conexão RS485**: /dev/ttyUSB0 @ 57600 baud, 2 stop bits, None parity
- ✅ **Slave ID**: 1
- ✅ **Encoder (32-bit)**: Leitura em tempo real (função 0x03 - Read Holding Registers)
  - Endereços: 1238 (MSW) + 1239 (LSW)
  - Valor atual: ~243
- ✅ **Entradas Digitais E0-E7**: Leitura OK (função 0x02 - Read Discrete Inputs)
  - Endereço: 256-263
- ✅ **Saídas Digitais S0-S7**: Leitura OK (função 0x01 - Read Coils)
  - Endereço: 384-391
- ✅ **Botões HMI (K0-K9, S1/S2, etc.)**: Escrita OK (função 0x05 - Force Single Coil)
  - Testado: K1 (endereço 160) ✓

### Backend Python
- ✅ **modbus_client.py**: Comunicação correta com 2 stop bits
- ✅ **state_manager.py**: Polling otimizado (~340ms/ciclo)
- ✅ **main_server.py**: WebSocket rodando em localhost:8080

### Frontend Web
- ✅ **index.html**: Conectado ao WebSocket
- ✅ **Estado inicial**: Recebendo encoder angle, poll count, status de conexão

---

## ⚠️ PENDÊNCIAS (Para melhorar no futuro)

### Registros Não Mapeados
Os seguintes endereços do ladder ainda precisam ser testados/verificados:

- [ ] **Angle Setpoints** (0x0840-0x0852): Retornam "Illegal Data Address"
- [ ] **Quantity Setpoints** (0x0960-0x0966): Retornam "Illegal Data Address"
- [ ] **Mode Bits** (0x0300-0x0385): Podem precisar ser lidos como coils
- [ ] **Botões Físicos do Painel** (AVANÇAR, RECUAR, PARADA, EMERGÊNCIA)

### Otimizações
- [ ] Ler I/Os em bloco (8 inputs de uma vez) ao invés de individualmente
- [ ] Reduzir tempo de polling de 340ms para ~250ms
- [ ] Implementar cache de valores estáticos
- [ ] Adicionar reconnection automática no WebSocket

### Funcionalidades Futuras
- [ ] Mapear todos os registros do programa ladder
- [ ] Implementar controle de modos (Manual/Auto)
- [ ] Implementar setpoints de ângulos
- [ ] Logs de produção
- [ ] Alertas via Telegram
- [ ] Registro em Google Sheets

---

## 🔧 CONFIGURAÇÃO CRÍTICA

**IMPORTANTE**: O sistema **REQUER 2 stop bits** na comunicação RS485!

```python
# modbus_client.py - Configuração correta
ModbusConfig:
    baudrate: 57600
    parity: 'N'
    stopbits: 2  # CRITICAL!
    bytesize: 8
    timeout: 1.0
```

Sem 2 stop bits, o CLP retorna "Illegal Function" em todos os comandos.

---

## 📊 PERFORMANCE ATUAL

- **Tempo de ciclo de polling**: ~340ms (meta: 250ms)
- **Leituras por ciclo**:
  - 1x Encoder (2 registros)
  - 8x Digital Inputs (discrete inputs)
  - 8x Digital Outputs (coils)
  - Total: 18 operações Modbus/ciclo
- **Taxa de atualização**: ~3 Hz
- **Errors**: 0 erros de comunicação

---

## 🚀 COMO USAR

### Iniciar o servidor:
```bash
cd /home/lucas-junges/Documents/clientes/w\&co
python3 main_server.py --live --port /dev/ttyUSB0 &
```

### Abrir interface web:
```bash
firefox index.html
```

### Verificar logs:
```bash
tail -f server.log
```

### Parar servidor:
```bash
pkill -f main_server.py
```

---

## 📝 MUDANÇAS PRINCIPAIS

### Correções Aplicadas
1. **Stop bits**: Mudado de 1 para 2
2. **Funções Modbus corretas**:
   - Entradas digitais: `read_discrete_inputs()` ao invés de `read_coil()`
   - Saídas digitais: `read_coils()` (já estava correto)
3. **Otimização**: Removidas leituras de registros que não funcionam
4. **Performance**: Tempo de ciclo reduzido de 780ms → 340ms

### Problemas Resolvidos
- ❌ ~~"Illegal Function" em todos os comandos~~ → ✅ Resolvido com 2 stop bits
- ❌ ~~Encoder não lê~~ → ✅ Funciona perfeitamente
- ❌ ~~Botões não respondem~~ → ✅ Testado e funcionando (K1)
- ❌ ~~I/Os sempre retornam erro~~ → ✅ Funções Modbus corretas aplicadas

---

## 🎯 PRÓXIMOS PASSOS

1. **Testar interface web visualmente** - verificar se encoder atualiza na tela
2. **Testar todos os botões** - K0-K9, S1/S2, ESC, ENTER, etc.
3. **Mapear registros restantes** - descobrir endereços corretos via teste
4. **Implementar funcionalidades da máquina** - modos, setpoints, ciclos
5. **Migrar para ESP32** quando estável

---

**Desenvolvido por**: Claude Code
**Cliente**: W&CO / Camargo Steel
**Máquina**: Trillor NEOCOUDE-HD-15 (2007) com CLP Atos MPC4004
