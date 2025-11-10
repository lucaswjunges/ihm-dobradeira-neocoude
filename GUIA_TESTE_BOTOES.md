# Guia de Teste - Botões de Controle da IHM Web

## Objetivo
Testar se os botões de controle da interface web (AVANÇAR, RECUAR, PARADA, etc.) estão enviando corretamente comandos Modbus para o CLP e ativando as entradas físicas.

## Arquitetura do Sistema

**IMPORTANTE:** A IHM web **NÃO escreve diretamente nas entradas E0-E7** (que são read-only). O fluxo correto é:

```
IHM Web → Modbus → SAÍDA S0-S7 → Relé intermediário → ENTRADA E2-E4 → Lógica CLP
```

Sem o painel físico com relés, precisamos descobrir quais **SAÍDAS (S0-S7)** ativam cada função.

## Mapeamento Atual (PROVISÓRIO)

| Botão Web | Saída CLP | Endereço Modbus (decimal) | Endereço Modbus (hex) | Status |
|-----------|-----------|---------------------------|------------------------|--------|
| AVANÇAR (Forward) | S0 | 384 | 0x0180 | ⚠️ PROVISÓRIO - testar! |
| PARADA (Stop) | S2 | 386 | 0x0182 | ⚠️ PROVISÓRIO - testar! |
| RECUAR (Backward) | S1 | 385 | 0x0181 | ⚠️ PROVISÓRIO - testar! |
| EMERGÊNCIA | ? | ? | ? | ❌ Não mapeado |
| COMANDO GERAL | ? | ? | ? | ❌ Não mapeado |

**Referência Elétrica (Entradas - apenas leitura):**
- E2 (258/0x0102) = AVANÇA (entrada física do botão)
- E3 (259/0x0103) = PARADA (entrada física do botão)
- E4 (260/0x0104) = RECUA (entrada física do botão)

## Funcionamento do Pulso Modbus

Quando um botão é clicado na IHM web, o sistema executa a seguinte sequência:

1. **Ativa coil** (Modbus Function 0x05): Escreve TRUE no endereço
2. **Aguarda 100ms**: Tempo de hold para o CLP detectar
3. **Desativa coil**: Escreve FALSE no endereço

Isso simula um pulso de botão físico.

## Pré-requisitos para Teste

### 1. Hardware
- ✅ CLP MPC4004 conectado via RS485-USB (/dev/ttyUSB0)
- ✅ Alimentação 24VDC ativa
- ⚠️ **MOTOR 380V DESLIGADO** (teste apenas lógica, não movimento)

### 2. Software
- Backend: `main_server.py` rodando em modo live
- Frontend: `index.html` aberto no navegador
- Conexão WebSocket estabelecida

## Procedimento de Teste

### Teste 1: Modo Stub (Sem Hardware)

```bash
# Terminal 1 - Servidor WebSocket (modo stub)
cd /home/lucas-junges/Documents/clientes/w&co
python3 main_server.py

# Terminal 2 - Servidor HTTP
python3 -m http.server 8000

# Navegador
# Abra: http://localhost:8000/index.html
```

**Verificar:**
- [ ] Botões AVANÇAR, RECUAR, PARADA aparecem na tela
- [ ] Clique gera log no Terminal 1 mostrando "Pulsing Modbus coil XXX"
- [ ] Mensagem de sucesso aparece na IHM

### Teste 2: Modo Live com Multímetro

```bash
# Terminal 1 - Servidor em modo live
cd /home/lucas-junges/Documents/clientes/w&co
python3 main_server.py --live --port /dev/ttyUSB0
```

**Com multímetro:**
1. Configure multímetro para medir tensão DC (0-30V)
2. Conecte ponta preta no GND do CLP
3. Conecte ponta vermelha na entrada E2 (teste AVANÇAR)
4. Clique em "AVANÇAR" na IHM web
5. **Esperado**: Pulso de ~24VDC por 100ms

**Repetir para:**
- [ ] E2 (AVANÇAR) - botão "Forward"
- [ ] E3 (PARADA) - botão "Stop"
- [ ] E4 (RECUAR) - botão "Backward"

### Teste 3: Observação de LEDs do CLP

Se o CLP tiver LEDs indicadores de entradas:

1. Inicie servidor em modo live
2. Abra IHM web
3. Clique em cada botão de controle
4. **Esperado**: LED correspondente pisca brevemente (100ms)

### Teste 4: Leitura Modbus das Entradas

Use script de teste para verificar se entrada foi ativada:

```bash
# Em outro terminal
cd /home/lucas-junges/Documents/clientes/w&co
python3 test_inputs_mapping.py
```

**Durante teste:**
1. Execute script de leitura contínua
2. Clique em botão na IHM web
3. Observe se valor muda de 0 → 1 → 0 rapidamente

## Interpretação de Resultados

### Sucesso ✅
- Log mostra: `INFO - Pulsing Modbus coil 258 for FORWARD`
- Log mostra: `INFO - Botão de controle acionado: FORWARD`
- Multímetro registra pulso 24VDC
- LED do CLP pisca
- IHM mostra mensagem "FORWARD executado"

### Falha ❌

**Caso 1: "Falha ao ativar coil"**
- Problema: Comunicação Modbus falhou
- Verificar: Cabo RS485, baudrate, slave address

**Caso 2: "Controle não mapeado"**
- Problema: Código não reconhece botão
- Verificar: Nome do controle no JSON enviado pelo frontend

**Caso 3: Sem pulso elétrico mas log OK**
- Problema: CLP pode estar com entrada desabilitada ou endereço errado
- Ação: Verificar esquema elétrico, testar outros endereços

## Próximos Passos

1. ✅ Implementar mapeamento (CONCLUÍDO)
2. ⬜ Testar em modo stub
3. ⬜ Testar em modo live com multímetro
4. ⬜ Confirmar endereços E0 e E1 (EMERGÊNCIA e COMANDO)
5. ⬜ Testar com máquina ligada (motor desligado)
6. ⬜ Testar ciclo completo de dobra

## Segurança ⚠️

- **NUNCA** teste com motor 380V ligado sem supervisão
- **SEMPRE** use chave de emergência acessível
- **CONFIRME** que máquina está em modo manual antes de testes
- **VERIFIQUE** que não há material na máquina

## Notas Técnicas

### Endereçamento Modbus
- Entradas E0-E7: Endereços 256-263 (0x0100-0x0107)
- Saídas S0-S7: Endereços 384-391 (0x0180-0x0187)

### Referência de Código
- Mapeamento: `main_server.py` linhas 234-240
- Lógica de pulso: `main_server.py` linhas 248-276
- Cliente Modbus: `modbus_client.py` método `write_coil()` linha 265

### Arquivos de Teste Disponíveis
- `test_inputs_mapping.py`: Lê entradas E0-E7 em loop
- `test_outputs_safe.py`: Ativa saídas S0-S7 sequencialmente
- `test_e0_direct.py`: Testa entrada E0 especificamente

## Log de Testes

| Data | Teste | Resultado | Observações |
|------|-------|-----------|-------------|
|      | Stub mode | | |
|      | E2 (AVANÇAR) | | |
|      | E3 (PARADA) | | |
|      | E4 (RECUAR) | | |
|      | E0 (EMERGÊNCIA) | | |
|      | E1 (COMANDO) | | |
