# Configuração Modbus RTU Validada - CLP ATOS MPC4004

**Data de validação**: 18/11/2025
**Hardware**: Raspberry Pi 3B+ + USB-RS485 (CH340)
**Status**: ✅ **COMUNICAÇÃO ESTABELECIDA**

---

## ✅ Parâmetros Funcionais Confirmados

### Comunicação Serial

| Parâmetro | Valor | Status |
|-----------|-------|--------|
| **Porta** | `/dev/ttyUSB0` | ✅ Detectado |
| **Baudrate** | `57600` | ✅ Validado |
| **Parity** | `None` (N) | ✅ Validado |
| **Stop Bits** | `1` ou `2` | ✅ Ambos funcionam |
| **Data Bits** | `8` | ✅ Padrão |
| **Slave ID** | `1` | ✅ Confirmado |
| **Timeout** | `1 segundo` | ✅ Adequado |

### Hardware USB-RS485

| Item | Detalhes |
|------|----------|
| **Chipset** | QinHeng Electronics CH340 |
| **Vendor ID** | `1a86` |
| **Product ID** | `7523` |
| **Device** | `/dev/ttyUSB0` |
| **Permissões** | `crw-rw----` (grupo dialout) |

---

## 📊 Registros Testados

### Encoder (32-bit)

| Registro (Hex) | Registro (Dec) | Tipo | Descrição | Valor Lido |
|----------------|----------------|------|-----------|------------|
| `04D6` | `1238` | 16-bit MSW | Encoder - Word Alta | `0` (0x0000) |
| `04D7` | `1239` | 16-bit LSW | Encoder - Word Baixa | `30581` (0x7775) |
| **Combinado** | **1238-1239** | **32-bit** | **Encoder completo** | **30581 pulsos** |

**Fórmula 32-bit**: `valor = (MSW << 16) | LSW`

**Exemplo**:
```
MSW = 0x0000 = 0
LSW = 0x7775 = 30581
Valor 32-bit = (0 << 16) | 30581 = 30581
```

### Status de Leitura

| Registro(s) | Status | Observação |
|-------------|--------|------------|
| `1238-1239` (Encoder) | ✅ **OK** | Leitura estável e consistente |
| `256-263` (Entradas E0-E7) | ⚠️ Não testado | Registros existem no mapa |
| `384-391` (Saídas S0-S7) | ⚠️ Não testado | Registros existem no mapa |

---

## 🔧 Código Python Validado

### pymodbus (Recomendado)

```python
from pymodbus.client import ModbusSerialClient

# Criar cliente
client = ModbusSerialClient(
    port='/dev/ttyUSB0',
    baudrate=57600,
    parity='N',
    stopbits=1,
    bytesize=8,
    timeout=1
)

# Conectar
if client.connect():
    # Ler encoder (32-bit)
    result = client.read_holding_registers(
        address=1238,
        count=2,
        slave=1
    )

    if not result.isError():
        msw = result.registers[0]
        lsw = result.registers[1]
        encoder_value = (msw << 16) | lsw
        print(f"Encoder: {encoder_value} pulsos")

    client.close()
```

### mbpoll (Linha de Comando)

```bash
# Ler encoder (registros 1238-1239)
mbpoll -a 1 -b 57600 -P none -s 1 -t 3 -r 1238 -c 2 /dev/ttyUSB0

# Saída esperada:
# [1238]: 0
# [1239]: 30581
```

---

## 🐛 Problemas Encontrados e Soluções

### Problema 1: mbpoll com `-s 2` dava timeout

**Causa**: mbpoll com 2 stop bits apresentou timeouts iniciais

**Solução**: Usar `-s 1` (1 stop bit) que funciona perfeitamente

**Observação**: pymodbus funciona com `stopbits=1` ou `stopbits=2`

### Problema 2: pymodbus com paridade `E` ou `O` falhou

**Causa**: CLP configurado sem paridade

**Solução**: Usar `parity='N'` (None)

### Problema 3: Scan de slave IDs com mbpoll não encontrou

**Causa**: mbpoll com configurações erradas (2 stop bits) não detectava

**Solução**: Usar pymodbus com 1 stop bit funcionou imediatamente

---

## ✅ Scripts Criados

| Script | Descrição | Status |
|--------|-----------|--------|
| `test_modbus_diagnostic.py` | Diagnóstico completo (scan configurações) | ✅ Funcional |
| `test_modbus_clp.py` | Cliente com display visual (I/Os + encoder) | ✅ Criado |
| `test_read_simple.py` | Leitura simples para testes rápidos | ✅ Validado |
| `test_scan_modbus.sh` | Scan de slave IDs (bash) | ✅ Criado |

---

## 📋 Checklist de Validação

- [x] USB-RS485 detectado (`/dev/ttyUSB0`)
- [x] Usuário no grupo `dialout` (permissões)
- [x] mbpoll instalado e testado
- [x] pymodbus instalado (via apt)
- [x] Baudrate 57600 confirmado
- [x] Slave ID 1 confirmado
- [x] Leitura de encoder funcionando
- [x] Valor 32-bit calculado corretamente
- [ ] Leitura de entradas digitais (E0-E7)
- [ ] Leitura de saídas digitais (S0-S7)
- [ ] Escrita de coils (Force Single Coil 0x05)
- [ ] Escrita de registros (Preset Single Register 0x06)

---

## 📝 Próximos Passos

1. **Validar leitura de I/Os digitais**
   - Testar registros 256-263 (entradas)
   - Testar registros 384-391 (saídas)

2. **Testar escrita de coils**
   - Simular pressão de teclas (0x05)
   - Validar endereços K0-K9, S1, S2, etc.

3. **Integrar ao servidor web**
   - Adaptar `modbus_client.py` do Ubuntu
   - Usar configuração validada
   - Testar polling 250ms

4. **Validar área de ângulos**
   - Ler registros 0x0A00-0x0A05 (área validada no ladder)
   - Testar escrita de ângulos

---

## 🔍 Informações de Debug

### Logs do Kernel (dmesg)

```
usb 1-1.2: New USB device found, idVendor=1a86, idProduct=7523
usb 1-1.2: Product: USB Serial
ch341-uart converter now attached to ttyUSB0
```

### Permissões

```bash
$ ls -l /dev/ttyUSB0
crw-rw---- 1 root dialout 188, 0 Nov 18 21:17 /dev/ttyUSB0

$ groups
lucas-junges adm dialout cdrom sudo ...
```

### Teste de Comunicação

```
[1] Encoder:      30581 (0x00007775)  MSW=    0  LSW=30581
[2] Encoder:      30581 (0x00007775)  MSW=    0  LSW=30581
[3] Encoder:      30581 (0x00007775)  MSW=    0  LSW=30581
```

**Resultado**: ✅ Leitura consistente e estável

---

## 📚 Referências

- Manual CLP Atos MPC4004 (página 133-134 - Modbus)
- Código ladder validado (`clp_MODIFICADO_extract/ROT5.lad`)
- Documentação pymodbus: https://pymodbus.readthedocs.io/
- Modbus RTU Specification: http://www.modbus.org/

---

**Validado por**: Lucas William Junges
**Device**: Raspberry Pi 3B+ (ARM64, Debian Bookworm)
**Python**: 3.11 + pymodbus 3.0.0
**Status**: ✅ Pronto para integração com servidor web
