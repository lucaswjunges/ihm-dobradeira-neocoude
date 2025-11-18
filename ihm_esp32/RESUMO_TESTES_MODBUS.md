# Resumo dos Testes Modbus - CLP Atos

**Data:** 2025-11-18
**Arquivo CLP:** `clp_MODIFICADO_IHM_WEB_COM_ROT5.sup`
**Objetivo:** Validar escrita de ângulos em diferentes áreas de memória

---

## Status Atual

❌ **Comunicação não estabelecida**

### Problema Identificado

1. **Porta serial:** `/dev/ttyUSB0` - OK (porta existe e abre corretamente)
2. **Permissões:** OK (usuário no grupo `dialout`)
3. **Pymodbus:** ⚠️ Erro na API `read_holding_registers()` - incompatibilidade de versão ou sintaxe

### Erro Observado

```
✗ Exceção: ModbusClientMixin.read_holding_registers() got an unexpected keyword argument
```

Isso indica que a versão do `pymodbus` instalada tem API diferente.

---

## Arquivos Criados

1. **`test_battery_mbpoll.sh`** - Script bash completo para testes com mbpoll
2. **`test_conexao_clp.py`** - Script Python de diagnóstico (com bug de API)
3. **`TESTES_MBPOLL_REFERENCIA.md`** - Referência rápida de comandos mbpoll
4. **`DIAGNOSTICO_CONEXAO_CLP.md`** - Checklist de diagnóstico
5. **`RESUMO_TESTES_MODBUS.md`** - Este arquivo

---

## Próximas Ações Recomendadas

### Opção 1: Usar mbpoll (Manual)

Como a automação está com problemas, execute testes manualmente:

```bash
# Teste 1: Comunicação básica (ler encoder)
mbpoll -a 1 -r 1238 -c 2 -t 4 -b 57600 -P none -s 2 /dev/ttyUSB0

# Teste 2: Escrever ângulo 90° em 0x0A00
mbpoll -a 1 -r 2560 -t 4 -b 57600 -P none -s 2 /dev/ttyUSB0 900

# Teste 3: Ler ângulo escrito
mbpoll -a 1 -r 2560 -c 1 -t 4 -b 57600 -P none -s 2 /dev/ttyUSB0

# Teste 4: Escrever em 0x0500 (ângulo oficial)
mbpoll -a 1 -r 1280 -t 4 -b 57600 -P none -s 2 /dev/ttyUSB0 900

# Teste 5: Ler área completa 0x0A00 (6 ângulos)
mbpoll -a 1 -r 2560 -c 6 -t 4 -b 57600 -P none -s 2 /dev/ttyUSB0
```

**Importante:**
- Usar `-s 2` (2 stop bits)
- Usar `-P none` (sem paridade)
- Baudrate: `57600`

### Opção 2: Corrigir Script Python

Verificar versão do pymodbus e ajustar sintaxe:

```bash
pip3 show pymodbus
```

Se versão >= 3.0, a sintaxe mudou. Atualizar para:

```python
# Versão antiga (< 3.0)
result = client.read_holding_registers(address=1238, count=2, slave=1)

# Versão nova (>= 3.0)
result = client.read_holding_registers(address=1238, count=2, unit=1)  # slave → unit
```

### Opção 3: Verificar Hardware

**Checklist físico:**
- [ ] CLP está ligado (LED verde aceso)
- [ ] Cabo RS485 conectado (A-A, B-B, GND-GND)
- [ ] Conversor USB-RS485 alimentado (LED aceso)
- [ ] Cabo USB bem conectado (verificar com `dmesg | tail`)

**Teste de loopback:**
```bash
# Curto-circuitar A e B no conversor (sem CLP)
# Se mbpoll receber eco, conversor está OK
```

### Opção 4: Usar IHM Python Existente

Se a IHM Python da pasta `/ihm` estiver funcionando, usar ela para testar escrita:

```bash
cd ../ihm
python3 test_write_official_angles.py
```

---

## Áreas de Memória a Testar

### Prioridade ALTA

| Endereço Hex | Endereço Dec | Descrição | Esperado |
|--------------|--------------|-----------|----------|
| `0x0A00` | 2560 | Ângulo 1 Esquerda (IHM Web) | Escrita OK |
| `0x0A01` | 2561 | Ângulo 2 Esquerda (IHM Web) | Escrita OK |
| `0x0A02` | 2562 | Ângulo 3 Esquerda (IHM Web) | Escrita OK |
| `0x0A03` | 2563 | Ângulo 1 Direita (IHM Web) | Escrita OK |
| `0x0A04` | 2564 | Ângulo 2 Direita (IHM Web) | Escrita OK |
| `0x0A05` | 2565 | Ângulo 3 Direita (IHM Web) | Escrita OK |

### Prioridade MÉDIA

| Endereço Hex | Endereço Dec | Descrição | Esperado |
|--------------|--------------|-----------|----------|
| `0x0500` | 1280 | Ângulo Inicial 1 (oficial) | ? |
| `0x0501` | 1281 | Ângulo Final 1 (oficial) | ? |
| `0x0502` | 1282 | Ângulo Inicial 2 (oficial) | ? |
| `0x0503` | 1283 | Ângulo Final 2 (oficial) | ? |

### Prioridade BAIXA

| Endereço Hex | Endereço Dec | Descrição | Tipo |
|--------------|--------------|-----------|------|
| `0x0392` | 914 | Trigger alternativo | Coil |
| `0x0A10` | 2576 | Trigger IHM | Coil |

---

## Valores de Teste Sugeridos

| Ângulo | Valor Modbus | Uso |
|--------|--------------|-----|
| 45.0°  | 450 | Teste básico |
| 60.0°  | 600 | Teste médio |
| 90.0°  | 900 | Teste padrão (ângulo reto) |
| 120.0° | 1200 | Teste comum na indústria |
| 135.0° | 1350 | Teste médio-alto |
| 180.0° | 1800 | Teste máximo (ângulo raso) |

**Fórmula:** `valor_modbus = graus × 10`

---

## Template de Relatório de Teste

```
Data: _____________________
Testador: __________________

Teste: Escrita em 0x0A00
Comando: mbpoll -a 1 -r 2560 -t 4 -b 57600 -P none -s 2 /dev/ttyUSB0 900
Resultado: [ ] Sucesso  [ ] Timeout  [ ] Erro Modbus
Valor lido: ____________
Observações: __________________________________________

Teste: Leitura de 0x0A00
Comando: mbpoll -a 1 -r 2560 -c 1 -t 4 -b 57600 -P none -s 2 /dev/ttyUSB0
Resultado: [ ] Sucesso  [ ] Timeout  [ ] Erro Modbus
Valor lido: ____________
Valores conferem: [ ] Sim  [ ] Não

[Repetir para cada área testada]
```

---

## Referências

- **Manual mbpoll:** https://github.com/epsilonrt/mbpoll
- **Protocolo Modbus RTU:** https://modbus.org/docs/Modbus_over_serial_line_V1_02.pdf
- **PyModbus Docs:** https://pymodbus.readthedocs.io/

---

## Notas

- **CRÍTICO:** Sempre usar 2 stop bits (`-s 2`) conforme especificação do usuário
- **CRÍTICO:** Paridade NONE (`-P none`)
- Se timeout persistir, verificar bit 0x00BE (190 decimal) no ladder do CLP
- Considerar slave ID diferente (tentar 2, 3, 247 se ID 1 falhar)
- Delay mínimo de 100ms entre comandos Modbus

---

**Status:** 🔴 Aguardando teste manual ou correção de script Python
**Bloqueio:** Incompatibilidade de API do pymodbus
