# Testes de Gravação com mbpoll

**Data**: 16/Novembro/2025
**CLP**: Atos MPC4004 - Slave ID 1
**Conexão**: RS485-B @ 57600 bps, 8N2

---

## Scripts Disponíveis

### 1. **test_write_complete_mbpoll.sh** (RECOMENDADO)
Menu interativo completo com todas as opções de teste.

**Uso**:
```bash
cd /home/lucas-junges/Documents/clientes/w&co/ihm
./test_write_complete_mbpoll.sh
```

**Funcionalidades**:
- ✅ Gravar e ler ângulos de dobra (90°, 120°, 135°)
- ✅ Mudar classe de velocidade (K1+K7 simultâneo)
- ✅ Testar qualquer botão individual (pulso 100ms)
- ✅ Ler encoder atual
- ✅ Ler todas as entradas digitais (E0-E7)
- ✅ Ler todas as saídas digitais (S0-S7)
- ✅ Gravar ângulo customizado em qualquer dobra
- ✅ Teste automatizado completo (executa tudo sequencialmente)

---

### 2. **test_write_angles_mbpoll.sh**
Teste focado em gravação de ângulos de dobra.

**Uso**:
```bash
./test_write_angles_mbpoll.sh
```

**O que faz**:
1. Grava 3 ângulos padrão (90°, 120°, 135°)
2. Lê de volta para confirmar gravação
3. Testa ângulos fracionários (45°, 67°, 89°)
4. Exibe conversão graus ↔ valor_clp

**Registros testados**:
- Dobra 1 Esquerda: 2112/2114 (MSW/LSW)
- Dobra 2 Esquerda: 2120/2122 (MSW/LSW)
- Dobra 3 Esquerda: 2128/2130 (MSW/LSW)

---

### 3. **test_write_speed_mbpoll.sh**
Teste de mudança de classe de velocidade.

**Uso**:
```bash
./test_write_speed_mbpoll.sh
```

**O que faz**:
1. Pressiona K1+K7 simultaneamente (pulso 100ms)
2. Aguarda confirmação do usuário para próxima mudança
3. Repete 3 vezes (para testar ciclo completo: 5→10→15→5 rpm)

**⚠️ ATENÇÃO**:
- Só funciona em **MODO MANUAL**
- Máquina deve estar **PARADA**
- Verificar mudança no **display físico** (pode não ter registro Modbus para velocidade atual)

---

## Formato dos Dados

### Ângulos de Dobra (32-bit MSW+LSW)

**Conversão**:
```
Graus → CLP: value_clp = graus × 10
CLP → Graus: graus = value_clp ÷ 10
```

**Exemplo**: 90.0° = 900 (valor CLP)
- MSW (registro par): 0 (bits 31-16)
- LSW (registro ímpar): 900 (bits 15-0)

**Escrita**:
```bash
# Escrever 90° na Dobra 1 (2112/2114)
mbpoll -a 1 -b 57600 -P none -s 2 -r 2112 -t 4 /dev/ttyUSB0 0      # MSW
mbpoll -a 1 -b 57600 -P none -s 2 -r 2114 -t 4 /dev/ttyUSB0 900    # LSW
```

**Leitura**:
```bash
# Ler Dobra 1 (2 registros consecutivos)
mbpoll -a 1 -b 57600 -P none -s 2 -r 2112 -t 4 -c 2 /dev/ttyUSB0
# Saída: [0] [900] → 90.0°
```

---

### Botões (Coils - Pulso)

**Protocolo**:
1. Escreve 1 (ON)
2. Aguarda 100ms
3. Escreve 0 (OFF)

**Exemplo**: Pressionar K1 (endereço 160)
```bash
mbpoll -a 1 -b 57600 -P none -s 2 -r 160 -t 0 /dev/ttyUSB0 1
sleep 0.1
mbpoll -a 1 -b 57600 -P none -s 2 -r 160 -t 0 /dev/ttyUSB0 0
```

**Endereços dos botões**:
| Botão | Endereço | Uso |
|-------|----------|-----|
| K0    | 169      | Teclado numérico |
| K1    | 160      | Teclado numérico + mudança velocidade |
| K2    | 161      | Teclado numérico |
| K3    | 162      | Teclado numérico |
| K4    | 163      | Teclado numérico |
| K5    | 164      | Teclado numérico |
| K6    | 165      | Teclado numérico |
| K7    | 166      | Teclado numérico + mudança velocidade |
| K8    | 167      | Teclado numérico |
| K9    | 168      | Teclado numérico |
| S1    | 220      | Alterna MANUAL/AUTO |
| S2    | 221      | Reset/Contexto |
| ENTER | 37       | Confirma |
| ESC   | 188      | Cancela |
| EDIT  | 38       | Modo edição |

---

### Encoder (32-bit MSW+LSW)

**Registros**: 1238/1239 (0x04D6/0x04D7)

**Leitura**:
```bash
mbpoll -a 1 -b 57600 -P none -s 2 -r 1238 -t 4 -c 2 /dev/ttyUSB0
# Saída exemplo: [5] [2450] → (5 << 16) + 2450 = 329650 → 32965.0°
```

**Conversão para graus**:
```python
value_clp = (msw << 16) | lsw
graus = value_clp / 10.0
```

---

## Checklist de Testes

### Teste de Ângulos
- [ ] Gravar 90° na Dobra 1
- [ ] Gravar 120° na Dobra 2
- [ ] Gravar 135° na Dobra 3
- [ ] Ler de volta e confirmar valores
- [ ] Verificar no display físico da IHM
- [ ] Testar ângulo com decimal (45.5°, 67.3°)

### Teste de Velocidade
- [ ] Confirmar máquina em MODO MANUAL
- [ ] Confirmar máquina PARADA
- [ ] Pressionar K1+K7
- [ ] Verificar mudança no display (5→10→15→5 rpm)
- [ ] Repetir ciclo completo 3 vezes

### Teste de Botões
- [ ] Pressionar K1 (verificar resposta no CLP)
- [ ] Pressionar S1 (mudar modo - verificar no display)
- [ ] Pressionar ENTER (verificar no display)
- [ ] Pressionar ESC (verificar no display)

### Teste de I/O
- [ ] Ler E0-E7 (entradas digitais)
- [ ] Ler S0-S7 (saídas digitais)
- [ ] Verificar correlação com estado físico da máquina

---

## Troubleshooting

### "Connection failed" ou timeout
```bash
# Verificar porta serial
ls -l /dev/ttyUSB*

# Testar conexão básica
mbpoll -a 1 -b 57600 -P none -s 2 -r 190 -t 0 -c 1 /dev/ttyUSB0
# Deve retornar [1] se estado 0x00BE estiver ON
```

### Valores gravados não aparecem
- Confirmar conversão (graus × 10 = valor_clp)
- Verificar se MSW/LSW não estão invertidos
- Conferir endereço correto (decimal, não hex)

### Mudança de velocidade não funciona
- Verificar se está em MODO MANUAL (display deve mostrar)
- Confirmar máquina PARADA (sem ciclo ativo)
- Tentar pressionar K1+K7 fisicamente para confirmar lógica

### Botões não respondem
- Verificar pulso de 100ms (não muito rápido)
- Confirmar endereço correto (coil, não register)
- Verificar se estado 0x00F1 (Lock) não está ativo

---

## Comandos Úteis

### Ler estado Modbus habilitado
```bash
mbpoll -a 1 -b 57600 -P none -s 2 -r 190 -t 0 -c 1 /dev/ttyUSB0
# Deve retornar [1] (ON)
```

### Ler todos os LEDs
```bash
mbpoll -a 1 -b 57600 -P none -s 2 -r 192 -t 0 -c 5 /dev/ttyUSB0
# [LED1] [LED2] [LED3] [LED4] [LED5]
```

### Dump completo de registros de ângulos
```bash
mbpoll -a 1 -b 57600 -P none -s 2 -r 2112 -t 4 -c 16 /dev/ttyUSB0
# Lê 16 registros a partir de 2112 (cobre todas as 3 dobras esquerdas + direitas)
```

---

## Próximos Passos

1. ✅ Executar teste automatizado (`./test_write_complete_mbpoll.sh` → opção 8)
2. ✅ Verificar valores no display físico da IHM
3. ✅ Comparar com valores gravados via software WinSUP (se disponível)
4. ✅ Documentar qualquer discrepância em novo arquivo de análise
5. ✅ Atualizar `modbus_map.py` com registros confirmados

---

## Referências

- **Manual CLP**: `manual_MPC4004.txt` (página 133-134: Modbus)
- **Análise Ladder**: `ANALISE_COMPLETA_REGISTROS_PRINCIPA.md`
- **Mapa Modbus**: `modbus_map.py` (95 registros)
- **CLAUDE.md**: Especificação completa do projeto

---

**Última atualização**: 16/Nov/2025 às 11:45
**Status**: ✅ Scripts prontos para teste com CLP online
