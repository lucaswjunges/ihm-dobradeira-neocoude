# Diagnóstico de Conexão CLP - mbpoll

## Problema
Timeout ao tentar comunicar com CLP via mbpoll.

## Checklist de Diagnóstico

### 1. Hardware
- [?] Cabo RS485 conectado corretamente (A-A, B-B)
- [?] Conversor USB-RS485 alimentado
- [?] LED de RX/TX no conversor piscando
- [?] CLP ligado e operacional

### 2. Porta Serial
- [x] Porta existe: `/dev/ttyUSB0`
- [x] Porta não está em uso por outro processo
- [ ] Permissão de acesso à porta

### 3. Configuração Modbus
- [?] Baudrate: 57600 (verificar no CLP)
- [?] Slave ID: 1 (verificar registro 0x1988 = 6536 decimal)
- [?] Bit 0x00BE (190 decimal) habilitado no CLP

### 4. mbpoll
- [x] mbpoll instalado: `/usr/bin/mbpoll`
- [ ] Sintaxe correta do comando

## Comandos de Teste

### Teste 1: Verificar permissão
```bash
ls -l /dev/ttyUSB0
# Saída esperada: crw-rw---- 1 root dialout
```

### Teste 2: Adicionar usuário ao grupo dialout
```bash
sudo usermod -a -G dialout $USER
# Depois: logout/login ou newgrp dialout
```

### Teste 3: Teste básico sem especificar tipo
```bash
timeout 5 mbpoll -a 1 -b 57600 -P none /dev/ttyUSB0
```

### Teste 4: Teste com broadcast (slave ID 0)
```bash
timeout 5 mbpoll -a 0 -r 1238 -c 2 -t 4 -b 57600 -P none /dev/ttyUSB0
```

### Teste 5: Teste com diferentes baudrates
```bash
# 9600
timeout 5 mbpoll -a 1 -r 1238 -c 2 -t 4 -b 9600 -P none /dev/ttyUSB0

# 19200
timeout 5 mbpoll -a 1 -r 1238 -c 2 -t 4 -b 19200 -P none /dev/ttyUSB0

# 57600
timeout 5 mbpoll -a 1 -r 1238 -c 2 -t 4 -b 57600 -P none /dev/ttyUSB0

# 115200
timeout 5 mbpoll -a 1 -r 1238 -c 2 -t 4 -b 115200 -P none /dev/ttyUSB0
```

### Teste 6: Teste com paridade
```bash
# Even parity
timeout 5 mbpoll -a 1 -r 1238 -c 2 -t 4 -b 57600 -P even /dev/ttyUSB0

# Odd parity
timeout 5 mbpoll -a 1 -r 1238 -c 2 -t 4 -b 57600 -P odd /dev/ttyUSB0
```

### Teste 7: Modo verbose
```bash
timeout 5 mbpoll -a 1 -r 1238 -c 2 -t 4 -b 57600 -P none -v /dev/ttyUSB0
```

## Configurações Alternativas do CLP

### Verificar no manual/ladder:
- **Registro 0x1987 (6535 dec):** Baudrate do canal RS485-B
  - Valores possíveis: 1200, 2400, 4800, 9600, 19200, 38400, 57600, 115200

- **Registro 0x1988 (6536 dec):** Slave ID Modbus
  - Valor padrão: 1
  - Tentar: 1, 2, 247

- **Bit 0x00BE (190 dec):** Habilitar Modbus slave
  - Deve estar ON (1)
  - Se OFF, CLP não responde a comandos Modbus

## Solução com Python (pymodbus)

Se mbpoll continuar falhando, testar com script Python:

```python
from pymodbus.client import ModbusSerialClient

client = ModbusSerialClient(
    port='/dev/ttyUSB0',
    baudrate=57600,
    parity='N',
    stopbits=1,
    bytesize=8,
    timeout=3
)

if client.connect():
    print("✓ Conectado!")

    # Ler encoder
    result = client.read_holding_registers(address=1238, count=2, slave=1)

    if not result.isError():
        print(f"Encoder: {result.registers}")
    else:
        print(f"Erro: {result}")

    client.close()
else:
    print("✗ Falha na conexão")
```

## Próximos Passos

1. Executar testes 1-7 sequencialmente
2. Se nenhum funcionar, verificar hardware (trocar cabo, conversor)
3. Se hardware OK, analisar ladder do CLP para confirmar configurações
4. Considerar usar Modbus TCP (se CLP tiver porta Ethernet)
