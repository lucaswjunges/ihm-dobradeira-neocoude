# Mapeamento de Controles Descoberto

## Data da Descoberta
2025-11-08

## Fonte
Análise de ladder logic (arquivos `ladder_extract/ROT0.lad`)

## Arquitetura

```
IHM Web → WebSocket → main_server.py → Modbus → SAÍDA (S0-S7) → Relé → ENTRADA (E0-E7) → Lógica CLP
```

## Mapeamento Confirmado

| Botão IHM Web | Saída CLP | Endereço Modbus | Entrada Física | Lógica |
|---------------|-----------|-----------------|----------------|---------|
| **AVANÇAR** (Forward) | S0 | 384 (0x0180) | E2 (0x0102) | Pulso 100ms ON→OFF |
| **RECUAR** (Backward) | S1 | 385 (0x0181) | E4 (0x0104) | Pulso 100ms ON→OFF |
| **PARADA** (Stop) | - | - | E3 (0x0103) | Desliga S0 E S1 |

### Detalhes Técnicos

**AVANÇAR:**
- Ativa saída S0 (coil 384) por 100ms
- Relé fecha circuito para entrada E2
- CLP detecta E2 ativa e inicia movimento anti-horário
- Ladder: `Out:SETR T:0043 Size:003 E:0180` + `{0;00;0102;-1;02;-1;-1;00}`

**RECUAR:**
- Ativa saída S1 (coil 385) por 100ms
- Relé fecha circuito para entrada E4
- CLP detecta E4 ativa e inicia movimento horário
- Ladder: `Out:SETR T:0043 Size:003 E:0181` + `{0;00;0104;-1;02;-1;-1;00}`

**PARADA:**
- NÃO tem saída dedicada
- Desliga AMBAS as saídas S0 e S1 (força FALSE)
- Interrompe qualquer movimento em andamento
- Ladder: `{1;03;0180...}` e `{1;04;0181...}` (contatos NC que desligam)

## Mapeamento Pendente

| Botão IHM Web | Status | Notas |
|---------------|--------|-------|
| EMERGÊNCIA | ❌ Não mapeado | Provável E0 (256), mas precisa confirmação |
| COMANDO GERAL | ❌ Não mapeado | Provável E1 (257) ou E7 (263), precisa confirmação |

## Como Testar

### Teste com Multímetro

**AVANÇAR:**
1. Conectar multímetro: GND + terminal S0
2. Clicar em "AVANÇAR" na IHM web
3. **Esperado:** Pulso de ~24VDC por 100ms

**RECUAR:**
1. Conectar multímetro: GND + terminal S1
2. Clicar em "RECUAR" na IHM web
3. **Esperado:** Pulso de ~24VDC por 100ms

**PARADA:**
1. Primeiro ativar AVANÇAR ou RECUAR (saída fica ligada)
2. Clicar em "PARADA" na IHM web
3. **Esperado:** Saída desliga imediatamente

### Teste com Script Python

```bash
# Testar saídas individualmente
python3 test_control_outputs.py

# Ou testar diretamente
python3 -c "from modbus_client import *; c = ModbusClient(False, ModbusConfig()); c.write_coil(384, True); import time; time.sleep(2); c.write_coil(384, False)"
```

## Implementação no Código

### main_server.py (linhas 232-318)

```python
control_map = {
    'EMERGENCY_STOP': None,
    'COMMAND_ON': None,
    'FORWARD': 384,           # S0 - CONFIRMADO
    'BACKWARD': 385,          # S1 - CONFIRMADO
    'STOP': 'special'         # Desliga S0 e S1
}
```

**Lógica STOP (especial):**
```python
if modbus_address == 'special' and control == 'STOP':
    success_s0 = write_coil(384, False)
    success_s1 = write_coil(385, False)
```

**Lógica FORWARD/BACKWARD (pulso):**
```python
write_coil(address, True)
await sleep(0.1)  # 100ms
write_coil(address, False)
```

## Referências

- `ladder_extract/ROT0.lad`: Linhas com `Out:SETR` e endereços 0180/0181
- `NEOCOUDE-HD 15 - Camargo 2007 (1).pdf`: Página 42 - Esquema elétrico do quadro de controle
- `main_server.py`: Linhas 232-318 - Implementação dos controles

## Notas Importantes

1. **Sem painel físico:** Os relés intermediários estão ausentes, então ao ativar S0/S1 via Modbus, as entradas E2/E4 NÃO serão ativadas automaticamente

2. **Para testes completos:** Seria necessário jumpers ou relés externos para fechar o circuito de 24VDC entre saídas e entradas

3. **Multímetro é suficiente:** Para validar que a IHM web está funcionando, basta medir 24VDC nas saídas S0 e S1

4. **Próximo passo:** Depois de validar as saídas, implementar relés de estado sólido ou optoacopladores para fechar o circuito E2/E4
