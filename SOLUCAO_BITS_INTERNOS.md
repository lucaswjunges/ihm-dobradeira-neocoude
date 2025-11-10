# Solução: Controle via Bits Internos Modbus

## Data
2025-11-08

## Problema Identificado

O teste `test_s0_fast_read.py` confirmou que:
- ✓ Comunicação Modbus funcionando perfeitamente
- ✓ PLC responde write_coil() com sucesso
- ✗ **Saídas S0/S1 são SOBRESCRITAS pela ladder logic**

### Causa Raiz

A ladder logic (arquivo `ROT0.lad`) **desliga ativamente S0 e S1** quando detecta que as entradas físicas E2/E4 não estão ativas:

```
ROT0.lad Linha 1 - Branch 06:
{1;00;0102;...}{1;01;02FF;...}  # Se NOT E2 e NOT 02FF → DESLIGA S0
```

Como não há painel físico com relés, E2/E4 nunca são ativadas, então o ladder desliga S0/S1 no próximo scan (~6ms).

## Solução Implementada: BITS INTERNOS

Em vez de escrever diretamente nas saídas S0/S1 (384-385), a IHM web vai escrever em **bits internos** (estados) que o ladder pode ler e usar para ativar as saídas.

### Mapeamento de Bits Internos

Análise do ladder mostrou que os seguintes endereços estão **LIVRES**:

| Comando IHM Web | Bit Interno (Hex) | Endereço Decimal | Endereço Modbus Coil | Função |
|-----------------|-------------------|------------------|----------------------|--------|
| **AVANÇAR** (Forward) | 0x0030 | 48 | 48 | Quando ON, ladder deve ativar S0 |
| **RECUAR** (Backward) | 0x0031 | 49 | 49 | Quando ON, ladder deve ativar S1 |
| **PARADA** (Stop) | 0x0032 | 50 | 50 | Quando ON, ladder deve desligar S0 e S1 |
| **EMERGÊNCIA** | 0x0033 | 51 | 51 | Reservado para futuro |
| **COMANDO GERAL** | 0x0034 | 52 | 52 | Reservado para futuro |

### Arquitetura do Sistema

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐     ┌───────────┐
│  IHM Web    │────▶│ Modbus RTU   │────▶│ Bit Interno │────▶│  Ladder   │
│ (Tablet)    │     │ write_coil() │     │   (0x0030)  │     │  Logic    │
└─────────────┘     └──────────────┘     └─────────────┘     └─────┬─────┘
                                                                     │
                                                                     ▼
                                                              ┌─────────────┐
                                                              │ Saída S0    │
                                                              │ (coil 384)  │
                                                              └─────────────┘
```

### Fluxo de Operação

**AVANÇAR (Forward)**:
1. Usuário clica "AVANÇAR" na IHM web
2. WebSocket envia `{"action": "control_button", "control": "FORWARD"}`
3. `main_server.py` escreve TRUE no coil 48 (bit interno 0x0030)
4. **Ladder detecta bit 0x0030 ON** → Ativa S0 (384)
5. S0 ativa por tempo configurado (ex: 100ms-2s)
6. Ladder desliga bit 0x0030 e S0 automaticamente

**RECUAR (Backward)**:
- Mesmo fluxo, mas usa coil 49 (bit 0x0031) → S1 (385)

**PARADA (Stop)**:
1. IHM web escreve TRUE no coil 50 (bit 0x0032)
2. Ladder detecta → Desliga S0 e S1 **e bits 0x0030 e 0x0031**

## Modificações Necessárias

### 1. Código Python (main_server.py)

**ANTES** (escrevia diretamente em S0/S1):
```python
control_map = {
    'FORWARD': 384,   # S0 - NÃO FUNCIONA!
    'BACKWARD': 385,  # S1 - NÃO FUNCIONA!
    'STOP': 'special'
}
```

**DEPOIS** (escreve em bits internos):
```python
control_map = {
    'FORWARD': 48,    # Bit interno 0x0030
    'BACKWARD': 49,   # Bit interno 0x0031
    'STOP': 50,       # Bit interno 0x0032
    'EMERGENCY_STOP': 51,   # Bit interno 0x0033 (futuro)
    'COMMAND_ON': 52  # Bit interno 0x0034 (futuro)
}
```

**Lógica de pulso**: Continua igual (100ms ON → OFF)

### 2. Programa Ladder (WinSUP)

**CRITICAL**: O ladder **DEVE SER MODIFICADO** para ler os bits 0x0030-0x0032 e controlar S0/S1 baseado neles.

**Exemplo de lógica a adicionar** (pseudocódigo ladder):

```
# Nova Linha ROT0 - Detecção de Comando Modbus AVANÇAR
[Line NEW_01]
    Branch:
        Contato NO: 0x0030  # Bit Modbus FORWARD
        Contato NO: NOT 0x0031  # Não pode ter BACKWARD ativo
        Saída: SETR S0 (0x0180)  # Ativa S0
        Timer: 100ms  # Mantém ativo por 100ms
        Após timer: Reset 0x0030  # Desliga bit comando

# Nova Linha ROT0 - Detecção de Comando Modbus RECUAR
[Line NEW_02]
    Branch:
        Contato NO: 0x0031  # Bit Modbus BACKWARD
        Contato NO: NOT 0x0030  # Não pode ter FORWARD ativo
        Saída: SETR S1 (0x0181)  # Ativa S1
        Timer: 100ms
        Após timer: Reset 0x0031

# Nova Linha ROT0 - Detecção de Comando Modbus PARADA
[Line NEW_03]
    Branch:
        Contato NO: 0x0032  # Bit Modbus STOP
        Saída: RESET S0 (0x0180)  # Desliga S0
        Saída: RESET S1 (0x0181)  # Desliga S1
        Saída: RESET 0x0030  # Limpa bit FORWARD
        Saída: RESET 0x0031  # Limpa bit BACKWARD
        Saída: RESET 0x0032  # Auto-limpa
```

**IMPORTANTE**: As linhas **antigas** que desligam S0/S1 quando NOT E2/E4 devem ser **MODIFICADAS** para:
- Se bit 0x0030 ou 0x0031 está ON → **NÃO DESLIGAR** S0/S1
- Apenas desligar se nenhum comando Modbus está ativo

## Testes de Validação

### Teste 1: Escrever nos Bits Internos

```bash
python3 test_write_internal_bits.py
```

Espera-se:
- ✓ write_coil(48, True) retorna sucesso
- ✓ read_coils(48, 1) retorna TRUE
- ✓ Bit permanece ON (não é sobrescrito pelo ladder)

### Teste 2: IHM Web → Bits Internos

```bash
# Terminal 1: Iniciar servidor
python3 main_server.py --live --port /dev/ttyUSB0

# Terminal 2: Servidor HTTP
python3 -m http.server 8000

# Navegador: http://localhost:8000/test_websocket.html
# Clicar em AVANÇAR
```

Espera-se:
- ✓ Bit 48 (0x0030) é ativado por 100ms
- ✓ Bit retorna a FALSE após pulso
- ⚠️ S0 ainda não ativa (aguardando modificação do ladder)

### Teste 3: Após Modificar Ladder

Com ladder modificado:
- ✓ Clicar AVANÇAR → Bit 48 ON → S0 ativa → Medimos 24VDC em S0
- ✓ Clicar RECUAR → Bit 49 ON → S1 ativa → Medimos 24VDC em S1
- ✓ Clicar PARADA → S0 e S1 desligam imediatamente

## Próximos Passos

1. **URGENTE**: Atualizar `main_server.py` para usar bits internos (48-50) ✅
2. **Testar**: Verificar que bits 48-50 podem ser escritos e permanecem estáveis
3. **Modificar Ladder**: Adicionar lógica para ler bits 0x0030-0x0032
4. **Gravar no CLP**: Upload do ladder modificado via WinSUP
5. **Teste Final**: Validar controle completo via IHM web

## Vantagens desta Solução

✓ **Não invasiva**: Usa bits livres, não afeta lógica existente
✓ **Segura**: Ladder mantém controle final das saídas físicas
✓ **Escalável**: Bits 51-52 já reservados para futuros comandos
✓ **Compatível**: Funciona com ou sem painel físico
✓ **Testável**: Pode testar Modbus sem modificar hardware

## Referências

- `ladder_extract/ROT0.lad`: Linhas 1-10 (controle de S0/S1)
- `test_s0_fast_read.py`: Diagnóstico que identificou o problema
- `test_state_00BE.py`: Confirmação que Modbus slave está habilitado
- Manual MPC4004: Página 53-104 (Memory mapping: 0000-03FF = Internal States)
