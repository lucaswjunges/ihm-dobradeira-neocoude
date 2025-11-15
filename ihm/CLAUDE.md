# CLAUDE.md - IHM Web Dobradeira NEOCOUDE-HD-15

Este arquivo orienta o Claude Code ao trabalhar neste projeto.

## Visão Geral do Projeto

**IHM Web** para substituir painel físico danificado (Atos 4004.95C) da dobradeira Trillor NEOCOUDE-HD-15 (2007).

### Objetivo
Desenvolver interface web moderna acessível via tablet que replica 100% das funcionalidades da IHM física original, comunicando-se com o CLP Atos MPC4004 via Modbus RTU.

---

## Arquitetura do Sistema

```
┌─────────────┐  RS485-B   ┌──────────────┐  WiFi  ┌────────────┐
│ CLP MPC4004 │◄──Modbus──►│ Servidor     │◄──────►│  Tablet    │
│  (Slave)    │  57600 bps │ Python 3     │        │ (Navegador)│
└─────────────┘            └──────────────┘        └────────────┘
      ▲                          ▲
      │                          │
      │                          ├─ modbus_client.py
      │                          ├─ state_manager.py  
      │                          └─ main_server.py (WebSocket)
      │
      └─ 95 registros mapeados (encoder, ângulos, I/O, botões)
```

---

## Estrutura de Arquivos

```
ihm/
├── CLAUDE.md              ← Este arquivo
├── README.md              ← Instruções de uso
├── requirements.txt       ← Dependências Python
│
├── modbus_map.py          ← 95 registros/coils mapeados
├── modbus_client.py       ← Cliente Modbus (stub + live)
├── state_manager.py       ← Polling asyncio (250ms)
├── main_server.py         ← Servidor WebSocket + HTTP
│
├── static/
│   └── index.html         ← Interface web completa
│
└── tests/
    ├── test_modbus.py     ← Testa comunicação Modbus
    ├── test_angles.py     ← Testa leitura de ângulos
    └── test_speed.py      ← Testa mudança de velocidade
```

---

## Mapeamento Modbus (95 Registros)

### Encoder (32-bit MSW+LSW)
- **0x04D6/0x04D7** (1238/1239): Posição angular atual
  - Formato: `value = (MSW << 16) | LSW`
  - Conversão: `graus = value / 10.0`

### Ângulos Setpoint (32-bit)
- **Dobra 1**: 0x0840/0x0842 (2112/2114) - Esquerda
- **Dobra 2**: 0x0848/0x084A (2120/2122) - Esquerda
- **Dobra 3**: 0x0850/0x0852 (2128/2130) - Esquerda
  - Escrita: `value_clp = graus * 10`

### Botões (Coils - Function 0x05)
- **K0-K9**: 0x00A9-0x00A0 (169-160)
- **S1**: 0x00DC (220) - Alterna AUTO/MANUAL
- **S2**: 0x00DD (221) - Reset/Contexto
- **ENTER**: 0x0025 (37)
- **ESC**: 0x00BC (188)
- **EDIT**: 0x0026 (38)

### I/O Digital (COILS - NÃO Registers!)
- **Entradas E0-E7**: 0x0100-0x0107 (256-263)
- **Saídas S0-S7**: 0x0180-0x0187 (384-391)
  - **⚠️ CRÍTICO:** Use Function Code 0x01 (Read Coils), NÃO 0x03 (Read Holding Registers)
  - Python: `status = client.read_coils(addr, 1)[0]` (retorna True/False)
  - **ERRO COMUM:** Tentar ler como Holding Register resulta em "Illegal data address"
  - **TESTADO ✅:** 12/Nov/2025 com mbpoll (ver RESULTADOS_TESTES_MODBUS.md)

### LEDs (Coils)
- **LED1-LED5**: 0x00C0-0x00C4 (192-196)
  - LED1: Dobra 1 ativa
  - LED2: Dobra 2 ativa
  - LED3: Dobra 3 ativa

### Estados Críticos
- **0x00BE** (190): Modbus slave habilitado (DEVE estar ON)

---

## Protocolo de Comunicação

### Modbus RTU
```python
PORT = '/dev/ttyUSB0'  # ou /dev/ttyUSB1
BAUDRATE = 57600
PARITY = 'N' (None)
STOPBITS = 2
BYTESIZE = 8
SLAVE_ID = 1
```

### Function Codes Suportados
- **0x01**: Read Coils (I/O digital E0-E7/S0-S7, LEDs, estados)
- **0x03**: Read Holding Registers (encoder, ângulos, inversor)
- **0x05**: Write Single Coil (simular botões, escrever I/O)
- **0x06**: Write Single Register (escrever ângulos)

### Simulação de Botão (Pulso)
```python
# 1. ON
client.write_coil(address, True)
# 2. Aguarda 100ms
time.sleep(0.1)
# 3. OFF
client.write_coil(address, False)
```

### Mudança de Velocidade (K1+K7 simultâneo)
```python
client.write_coil(0x00A0, True)   # K1 ON
client.write_coil(0x00A6, True)   # K7 ON
time.sleep(0.1)
client.write_coil(0x00A0, False)  # K1 OFF
client.write_coil(0x00A6, False)  # K7 OFF
```

---

## Desenvolvimento Web-First

### Modo Stub (SEM CLP)
```bash
python3 main_server.py --stub
```
- Simula todos os registros
- Permite desenvolver/testar interface sem hardware
- Encoder oscila, ângulos pré-carregados

### Modo Live (COM CLP)
```bash
python3 main_server.py --port /dev/ttyUSB0
```
- Comunicação real via RS485-B
- Requer CLP ligado e cabo conectado

---

## Componentes Python

### 1. `modbus_map.py`
- **Propósito**: Constantes com endereços Modbus
- **Helpers**: `read_32bit()`, `split_32bit()`
- **Dicionários**: `KEYBOARD_NUMERIC`, `BEND_ANGLES`, `DIGITAL_INPUTS`

### 2. `modbus_client.py`
- **Classe**: `ModbusClientWrapper`
- **Modos**: `stub_mode=True/False`
- **Métodos principais**:
  - `read_coil(address)` → bool
  - `read_register(address)` → int (16-bit)
  - `read_32bit(msw_addr, lsw_addr)` → int
  - `write_coil(address, value)` → bool
  - `write_32bit(msw_addr, lsw_addr, value)` → bool
  - `press_key(address, hold_ms=100)` → bool
  - `change_speed_class()` → bool

### 3. `state_manager.py`
- **Classe**: `MachineStateManager`
- **Polling**: 250ms (4 Hz)
- **Estado**: Dicionário `machine_state` com:
  - `encoder_angle`, `encoder_raw`
  - `bend_1_left`, `bend_2_left`, `bend_3_left`
  - `inputs`, `outputs`, `leds`, `buttons`
  - `modbus_connected`, `last_update`
- **Métodos**:
  - `get_state()` → estado completo
  - `get_changes()` → apenas deltas (otimização)

### 4. `main_server.py`
- **Servidores**:
  - WebSocket: `ws://localhost:8765`
  - HTTP: `http://localhost:8080`
- **Mensagens WebSocket**:
  - **→ Cliente**: `full_state`, `state_update`
  - **← Cliente**: `press_key`, `change_speed`, `write_angle`

---

## Interface Web (`index.html`)

### Estrutura Visual
```
┌─────────────────────────────────────┐
│ [LED1] [LED2] [LED3] [LED4] [LED5] │
│                                     │
│         ÂNGULO ATUAL                │
│           45.7°                     │
│         CONECTADO                   │
├─────────────────────────────────────┤
│ ÂNGULOS PROGRAMADOS                 │
│ [Dobra 1: 90.0°] [2: 120°] [3: 56°]│
├─────────────────────────────────────┤
│  [1] [2] [3] [S1]                   │
│  [4] [5] [6] [S2]                   │
│  [7] [8] [9] [ESC]                  │
│  [0]  [ENTER]  [EDIT]               │
└─────────────────────────────────────┘
```

### Tecnologias
- **HTML5 + CSS3 + JavaScript Vanilla**
- **WebSocket** (comunicação real-time)
- **Sem frameworks** (portabilidade ESP32)

### Estados de Erro
- **DESLIGADO**: WebSocket desconectado
- **FALHA CLP**: Modbus desconectado
- Overlay vermelho piscante

---

## Regras de Negócio (do Manual NEOCOUDE)

### Mudança de Velocidade
- ✅ Permitido: Modo MANUAL, máquina parada
- ❌ Bloqueado: Modo AUTO, ciclo ativo
- Classes: 5 rpm → 10 rpm → 15 rpm (cíclico)

### Sequência de Dobras
- Ordem fixa: K1 (dobra 1) → K2 (dobra 2) → K3 (dobra 3)
- **NÃO pode voltar** para dobra anterior
- Reset: Desliga/liga sistema

### Modo Operação
- **MANUAL**: Usuário controla com AVANÇAR/RECUAR (botões físicos)
- **AUTO**: Sistema executa automaticamente até ângulo programado
- Troca: Tecla S1 (só quando parado e na dobra 1)

---

## Tarefas Comuns com Claude Code

### Adicionar Novo Botão
1. Verificar endereço em `modbus_map.py`
2. Adicionar em `KEYBOARD_NUMERIC` ou `KEYBOARD_FUNCTION`
3. Criar `<button>` em `index.html` com `data-key="XX"`
4. Event listener já captura automaticamente

### Adicionar Nova Leitura
1. Mapear endereço em `modbus_map.py`
2. Adicionar em `state_manager.py::poll_once()`
3. Adicionar campo em `machine_state`
4. Atualizar `index.html` para exibir

### Debugar Comunicação Modbus
```bash
# Ver todos os registros
python3 tests/test_modbus.py

# Testar ângulos específicos
python3 tests/test_angles.py

# Log detalhado
python3 main_server.py --stub  # Modo seguro sem CLP
```

---

## Troubleshooting

### WebSocket não conecta
```bash
# Verificar se servidor está rodando
lsof -i :8765
lsof -i :8080

# Verificar firewall
sudo ufw allow 8765
sudo ufw allow 8080
```

### Modbus timeout
```bash
# Verificar porta serial
ls -l /dev/ttyUSB*

# Testar comunicação básica
python3 -c "from modbus_client import *; c = ModbusClientWrapper(); print(c.read_32bit(0x04D6, 0x04D7))"

# Verificar estado 00BE
python3 -c "from modbus_client import *; c = ModbusClientWrapper(); print('Estado 00BE:', c.read_coil(0x00BE))"
```

### Ângulos não atualizam
- Verificar fator de conversão (÷10 ou ×10)
- Confirmar MSW/LSW não invertidos
- Testar com valores conhecidos (900 = 90.0°)

---

## Limitações Conhecidas

1. **Apenas 3 dobras**: Sistema original suporta 3 ângulos (esquerda/direita)
2. **Sem histórico**: Não armazena logs de produção (implementar futuramente)
3. **WiFi local**: Tablet deve estar na mesma rede (hotspot)
4. **Segurança**: Sem autenticação (adicionar futuramente)

---

## Próximas Melhorias

1. **Logs de Produção**: SQLite + gráficos
2. **Diagnóstico Avançado**: Monitorar entradas/saídas em tempo real
3. **Telegram Alerts**: Notificações de emergência
4. **Receitas**: Salvar/carregar perfis de dobra
5. **PWA**: Instalar como app nativo no tablet

---

## Referências Técnicas

- **Manual CLP**: `/home/lucas-junges/Documents/clientes/w&co/manual_MPC4004.txt`
- **Manual Máquina**: `NEOCOUDE-HD 15 - Camargo 2007 (1).pdf`
- **Análise Ladder**: `ANALISE_COMPLETA_REGISTROS_PRINCIPA.md`
- **Resumo Registros**: `RESUMO_ANALISE_PRINCIPA.txt`

---

## Contato

**Desenvolvedor**: Claude Code (Anthropic)  
**Cliente**: W&Co  
**Máquina**: Trillor NEOCOUDE-HD-15 (2007)  
**Data**: Novembro 2025
