# Configurações Recomendadas do CLP Atos MPC4004
## Antes do Upload do Programa Modificado

**Data**: 2025-11-10
**CLP**: Atos Expert MPC4004
**Aplicação**: Dobradeira NEOCOUDE-HD-15
**Versão do Programa**: apr03_v2_alterado.sup

---

## 📋 Índice

1. [Configurações de Hardware](#configurações-de-hardware)
2. [Parâmetros de Comunicação Modbus](#parâmetros-de-comunicação-modbus)
3. [Configurações de Memória e Retenção](#configurações-de-memória-e-retenção)
4. [Configurações de Segurança](#configurações-de-segurança)
5. [Configurações de Tempo de Scan](#configurações-de-tempo-de-scan)
6. [Configurações de Entradas/Saídas](#configurações-de-entradasaídas)
7. [Backup e Documentação](#backup-e-documentação)
8. [Verificações Pós-Upload](#verificações-pós-upload)

---

## 1. Configurações de Hardware

### 1.1 Bateria de Backup (CRÍTICO)

**Status Atual**: Verificar se presente

**Função**: Mantém memória retentiva (registradores, timers, contadores) durante power-off

**Recomendações**:

```
✅ VERIFICAR:
[ ] Bateria instalada no CLP (modelo CR2032 ou equivalente)
[ ] Tensão da bateria: ≥ 2.7V (testar com multímetro)
[ ] LED de bateria baixa: NÃO deve estar aceso
[ ] Data de fabricação da bateria: < 5 anos

⚠️  SE BATERIA FRACA OU AUSENTE:
- Substituir ANTES do upload do programa
- Timers e contadores resetarão a cada power-off
- Pode causar comportamento inesperado do timer de startup (120s)

💡 IMPACTO NO TIMER DE STARTUP:
- COM bateria: Timer T020 PODE reter valor (não desejado)
- SEM bateria: Timer T020 sempre reseta no power-on (desejado)
- Solução: Lógica do MOVK (Line 1 ROT5) reseta preset a cada boot
```

**Ação Recomendada**:
- Se bateria presente: Manter (lógica implementada suporta retenção)
- Se bateria ausente: Não instalar (sistema funciona sem)

---

### 1.2 Cabo RS485 e Terminação

**Status Atual**: Verificar instalação

**Especificações**:
```
Tipo de Cabo:    Par trançado blindado (shielded twisted pair)
Bitola mínima:   24 AWG (0.5mm²)
Comprimento:     < 1000m @ 57600 bps
                 < 500m @ 115200 bps (não recomendado)
Blindagem:       Conectar apenas em UMA extremidade (evitar loop de terra)
```

**Resistores de Terminação**:
```
✅ INSTALAR:
[ ] Resistor 120Ω no CLP (extremidade 1)
[ ] Resistor 120Ω no último dispositivo da rede (extremidade 2)

⚠️  NÃO instalar em dispositivos intermediários

🔌 POSIÇÃO DOS TERMINAIS:
- Terminal A (Data+): Pino 3 do conector RS485 do MPC4004
- Terminal B (Data-): Pino 8 do conector RS485 do MPC4004
- GND (Referência): Pino 5 (opcional, mas recomendado)
```

**Verificação**:
```bash
# Medir resistência entre A e B (com rede desconectada)
# Esperado: ~60Ω (dois resistores de 120Ω em paralelo)
multimetro: Ω mode → A-B terminals → leitura ≈ 60Ω
```

---

### 1.3 Fonte de Alimentação

**Especificações do MPC4004**:
```
Tensão de entrada:  24 VDC ± 20% (19.2V - 28.8V)
Consumo CPU:        300 mA @ 24V (7.2W)
Consumo I/O:        100 mA por 16 saídas ativas
Ripple máximo:      10% (2.4V pico-a-pico)
```

**Recomendações**:
```
✅ VERIFICAR:
[ ] Tensão de saída da fonte: 24.0V ± 0.5V (medir com multímetro)
[ ] Ripple da fonte: < 1V pico-a-pico (medir com osciloscópio)
[ ] Capacidade da fonte: ≥ 2A (para CLP + periféricos)
[ ] Disjuntor/fusível: 2A ou 3A (proteção contra curto)
[ ] Cabo de alimentação: 18 AWG mínimo (1.0mm²)

⚠️  SINTOMAS DE FONTE PROBLEMÁTICA:
- CLP reinicia aleatoriamente
- Erros de comunicação Modbus
- Timer comporta-se incorretamente
- LED de POWER pisca
```

**Ação Recomendada**: Se ripple > 10% ou tensão instável, substituir fonte

---

## 2. Parâmetros de Comunicação Modbus

### 2.1 Configuração da Porta RS485-B

**No Software Atos Expert**:

```
Caminho: Config → Communication → RS485-B

Parâmetros Recomendados:
┌────────────────────────────────────────────┐
│ Baudrate:        57600 bps                 │
│ Parity:          None                      │
│ Stop Bits:       1                         │
│ Data Bits:       8                         │
│ Slave Address:   1 (padrão, ajustar se     │
│                  necessário)               │
│ Timeout:         1000 ms                   │
│ Max Retry:       3                         │
└────────────────────────────────────────────┘
```

**Registro de Configuração**:
```
Endereço 1987H (6535 dec): Baudrate RS485-B
  - Valor 0x05 = 9600 bps
  - Valor 0x06 = 19200 bps
  - Valor 0x07 = 57600 bps ✅ RECOMENDADO
  - Valor 0x08 = 115200 bps (não recomendado para > 100m cabo)

Endereço 1988H (6536 dec): Slave Address
  - Valor 0x01 = Slave ID 1 ✅ PADRÃO
  - Valor 0x02-0xF7 = IDs alternativos (se múltiplos CLPs)

⚠️  IMPORTANTE: Anotar o Slave Address configurado!
   Servidor Python precisa usar o mesmo ID.
```

---

### 2.2 Habilitação do Modbus Slave

**Bit de Controle**: `00BE` (190 decimal)

**STATUS ATUAL NO PROGRAMA MODIFICADO**:
```
✅ ATIVAÇÃO AUTOMÁTICA com timer de 120 segundos

Sequência de Ativação (ROT5):
  1. Power-ON do CLP
  2. Line 1: Seta preset Timer 20 = 12000 (120s)
  3. Line 2: Timer 20 inicia contagem
  4. Line 3: Bit 00BE = OFF (Modbus desabilitado)
  5. ... aguarda 120 segundos ...
  6. Line 4: Timer completa → Bit 00BE = ON (Modbus habilitado)

💡 OVERRIDE MANUAL: Forçar bit 03FA (1018 dec) = TRUE
   Ativa Modbus imediatamente sem esperar 120s
```

**Verificação Pós-Upload**:
```python
# Usando software Atos Expert ou pymodbus

# MÉTODO 1: Software Atos Expert
# 1. Conectar ao CLP
# 2. Monitor → Online Variables
# 3. Adicionar variável: 00BE (ou 190 decimal)
# 4. Aguardar 120 segundos após power-on
# 5. Verificar: 00BE = TRUE

# MÉTODO 2: Python (após 120s do power-on)
from pymodbus.client import ModbusSerialClient

client = ModbusSerialClient(port='/dev/ttyUSB0', baudrate=57600,
                            slave=1, timeout=3)
client.connect()

# Verificar bit 00BE (190 decimal)
result = client.read_coils(0x00BE, 1)
if result.bits[0]:
    print("✅ Modbus Slave ATIVO")
else:
    print("⚠️  Modbus Slave INATIVO - aguardar timer ou forçar 03FA")

client.close()
```

---

### 2.3 Otimização de Comunicação

**Tempo de Resposta Modbus**:
```
Tempo de resposta = Scan Time + Processing Time + Serial Tx Time

Cálculo Exemplo:
  - Scan Time CLP:     ~12 ms (típico para este programa)
  - Processing Time:   ~2 ms (leitura/escrita Modbus)
  - Serial Tx (9600):  ~15 ms por frame (11 bytes @ 57600 bps)

  Total: ~30 ms por transação Modbus

✅ RECOMENDAÇÃO: Usar baudrate 57600 bps (valor atual)
   - 9600 bps:   ~80 ms por transação (muito lento)
   - 57600 bps:  ~30 ms por transação ✅
   - 115200 bps: ~18 ms (arriscado em cabos longos)
```

**Polling Rate do Servidor Python**:
```python
# ⚠️  NÃO fazer polling muito rápido!

# ❌ ERRADO: Polling a cada 10ms (sobrecarga do CLP)
while True:
    data = client.read_coils(...)
    time.sleep(0.01)  # MUITO RÁPIDO!

# ✅ CORRETO: Polling a cada 250ms (recomendado)
while True:
    data = client.read_coils(...)
    time.sleep(0.25)  # 4 Hz, adequado para IHM

# 💡 IDEAL: Polling baseado em eventos
# Apenas ler quando necessário (mudança de tela, ação do usuário)
```

---

## 3. Configurações de Memória e Retenção

### 3.1 Áreas de Memória do MPC4004

```
┌─────────────────────────────────────────────────────┐
│ Área de Memória      │ Endereço  │ Tipo   │ Retentivo│
├─────────────────────────────────────────────────────┤
│ Estados Internos     │ 0000-03FF │ Bit    │ ❌ Não   │
│ Timer Presets        │ 0400-047F │ Reg16  │ ✅ Sim*  │
│ Timer Effectives     │ 0480-04BF │ Reg16  │ ❌ Não   │
│ Counter Presets      │ 0400-047F │ Reg16  │ ✅ Sim*  │
│ Counter Effectives   │ 0480-04BF │ Reg16  │ ✅ Sim*  │
│ High-Speed Counter   │ 04D0-04DF │ Reg32  │ ❌ Não   │
│ Analog I/O           │ 0550-06FF │ Reg16  │ ❌ Não   │
│ User Registers       │ 0800-0FFF │ Reg16  │ ✅ Sim*  │
└─────────────────────────────────────────────────────┘

* Retentivo apenas se bateria instalada
```

**Impacto no Programa Modificado**:
```
Bits/Registradores Usados:
  - 00BE (Modbus enable):         NÃO retentivo
  - 0020 (Timer 20 bit):          NÃO retentivo
  - 0438 (Timer 20 preset):       RETENTIVO*
  - 03E0-03E6 (comandos Modbus):  NÃO retentivo
  - 03F0-03F3 (flags virtuais):   NÃO retentivo
  - 03FA (override manual):       NÃO retentivo
  - 03FF (status interface):      NÃO retentivo

✅ COMPORTAMENTO ESPERADO NO POWER-ON:
  1. Todos os bits internos (0000-03FF) resetam para 0
  2. Timer 20 preset é reescrito pelo MOVK (Line 1 ROT5)
  3. Timer 20 inicia do zero (não retém estado anterior)
  4. Bit 00BE começa em 0 e ativa após 120s
```

---

### 3.2 Configuração de Retenção (Opcional)

**Se desejar** tornar alguns bits retentivos (NÃO recomendado para este aplicação):

```
No Software Atos Expert:
  Config → Memory → Retentive Areas

  [ ] NÃO marcar área 03E0-03FF como retentiva
      (bits de comando Modbus devem resetar no power-on)

  [ ] NÃO marcar área 00BE como retentiva
      (Modbus deve ativar apenas após 120s)

✅ DEIXAR CONFIGURAÇÃO PADRÃO (não retentivo)
```

---

## 4. Configurações de Segurança

### 4.1 Prioridade de Emergência Física

**CRÍTICO**: Entrada E7 (emergência) deve ter máxima prioridade

**Verificação no Ladder**:
```
⚠️  IMPORTANTE: Adicionar verificação de emergência em TODAS as rotinas

Código Recomendado (adicionar no início de Principal.lad):

[Line NOVA - Antes de CALL ROT5]
  [Branch01]
    Condições:
      - /0107 (Emergência pressionada = FALSE)
    Ação:
      - RESET 0180 (Para motor S0)
      - RESET 0181 (Para motor S1)
      - RESET 00BE (Desativa Modbus)
      - JMP FIM (Pula para fim do programa)

💡 Isso garante que QUALQUER falha na emergência física
   para IMEDIATAMENTE todos os movimentos, independente
   de comandos Modbus.
```

**Teste de Emergência**:
```
PROCEDIMENTO:
1. Ligar COMANDO GERAL
2. Enviar comando AVANÇAR via Modbus
3. Motor deve girar
4. Pressionar EMERGÊNCIA física
5. Verificar: Motor para em < 500ms
6. Verificar: Bit 00BE = FALSE (Modbus desativado)
7. Verificar: Nenhum comando Modbus é aceito
8. Soltar EMERGÊNCIA
9. Religar COMANDO GERAL
10. Aguardar 120s
11. Verificar: Bit 00BE = TRUE (Modbus reativado)

✅ CRITÉRIO DE SUCESSO:
   - Parada do motor: < 500ms
   - Modbus desativado durante emergência
   - Sistema recupera após reset
```

---

### 4.2 Watchdog do Sistema

**Função**: Detecta travamento do programa ladder

**Configuração**:
```
No Software Atos Expert:
  Config → System → Watchdog

  Enable Watchdog:        ✅ ON
  Watchdog Time:          500 ms ✅ RECOMENDADO
  Action on Timeout:      STOP CPU & RESET OUTPUTS

⚠️  SE WATCHDOG DISPARAR:
  - CLP para de executar programa
  - Todas as saídas são desligadas (segurança)
  - LED de ERRO acende
  - Requer reset manual
```

**Alimentação do Watchdog no Ladder**:
```
Adicionar linha em Principal.lad:

[Line NOVA]
  [Branch01]
    Condições:
      - 00F7 (sempre ON)
    Ação:
      - WDTR (instrução de reset do watchdog)

💡 Executado a cada scan, mantém watchdog ativo
   Se programa travar, watchdog não é alimentado → CLP para
```

---

### 4.3 Proteção Contra Sobrecarga de Comunicação

**Limitação de Taxa de Comandos Modbus**:

```
Implementar no Servidor Python:

import time
from collections import deque

class ModbusRateLimiter:
    def __init__(self, max_commands_per_second=10):
        self.max_rate = max_commands_per_second
        self.commands = deque()

    def allow_command(self):
        now = time.time()
        # Remove comandos antigos (> 1 segundo)
        while self.commands and self.commands[0] < now - 1.0:
            self.commands.popleft()

        if len(self.commands) < self.max_rate:
            self.commands.append(now)
            return True
        else:
            print("⚠️  Rate limit atingido! Aguarde...")
            return False

# Uso:
limiter = ModbusRateLimiter(max_commands_per_second=4)

def send_modbus_command(client, address, value):
    if limiter.allow_command():
        client.write_coil(address, value)
    else:
        time.sleep(0.25)  # Aguarda antes de tentar novamente
```

---

## 5. Configurações de Tempo de Scan

### 5.1 Cálculo do Scan Time

**Fórmula**:
```
Scan Time = (Tamanho do Programa em KB) × (5 a 6 ms/KB)
```

**Programa Atual**:
```
Tamanho: ~28 KB (apr03_v2_alterado.sup)
Scan Time Esperado: 28 KB × 6 ms/KB = 168 ms

Mais realista (otimizado): ~140-160 ms
```

**Impacto**:
```
✅ ADEQUADO para aplicação de dobradeira
   - Processos mecânicos lentos (segundos)
   - Não requer resposta em tempo real (ms)

⚠️  SE Scan Time > 200 ms:
   - Considerar otimização do programa
   - Remover linhas não utilizadas
   - Simplificar lógica complexa
```

**Monitoramento**:
```python
# Ler tempo de scan do CLP (se disponível)
# Registrador específico do Atos (consultar manual)

# Método alternativo: Medir externamente
import time

start = time.time()
client.read_coils(0x03FF, 1)  # Comando simples
end = time.time()

response_time = (end - start) * 1000  # em ms
print(f"Tempo de resposta: {response_time:.1f} ms")

# Esperado: 30-50 ms @ 57600 bps
```

---

### 5.2 Otimização do Programa (Se Necessário)

**Técnicas**:
```
1. Remover linhas comentadas/não utilizadas
2. Combinar condições similares
3. Usar JMP (Jump) para pular blocos não necessários
4. Evitar loops excessivos
5. Limitar uso de funções matemáticas complexas

⚠️  NÃO OTIMIZAR SE:
   - Scan time < 200 ms
   - Sistema funciona corretamente
   - "Se não está quebrado, não conserte!"
```

---

## 6. Configurações de Entradas/Saídas

### 6.1 Filtro de Entrada Digital

**Função**: Elimina ruído e bouncing de botões/sensores

**Configuração**:
```
No Software Atos Expert:
  Config → I/O → Digital Inputs

  Input Filter Time:  10 ms ✅ RECOMENDADO (botões)
                      5 ms (sensores rápidos)
                      20 ms (relés mecânicos)

Entradas Críticas:
  - E0 (sensor referência):   5 ms
  - E2 (botão AVANÇAR):       10 ms
  - E3 (botão PARADA):        10 ms
  - E4 (botão RECUAR):        10 ms
  - E7 (EMERGÊNCIA):          0 ms ⚠️  SEM FILTRO!
```

**Emergência SEM filtro**:
```
⚠️  CRÍTICO: Entrada E7 (emergência) deve ter filtro = 0 ms

Razão:
  - Máxima velocidade de resposta
  - Sem atraso no corte de segurança
  - Normas de segurança (NR-12) exigem resposta < 100ms
```

---

### 6.2 Configuração de Saídas Digitais

**Proteção contra Curto-Circuito**:
```
✅ VERIFICAR:
[ ] Saídas S0-S7 têm proteção contra curto interna
[ ] Fusíveis ou disjuntores no painel elétrico
[ ] Diodos de roda livre em cargas indutivas (relés, contatores)

Especificação das Saídas MPC4004:
  - Tensão: 24 VDC
  - Corrente máxima: 0.5A por saída
  - Proteção: Limitação de corrente interna
  - Indicação: LED no CLP por saída

💡 Saídas S0/S1 (motores) DEVEM acionar contatores,
   NÃO diretamente o motor!
```

---

## 7. Backup e Documentação

### 7.1 Checklist de Backup PRÉ-UPLOAD

```
✅ OBRIGATÓRIO:
[ ] Backup do programa atual via Atos Expert
    - Salvar como: clp_pre_modbus_[DATA_HORA].sup
    - Local: Laptop + pendrive + nuvem

[ ] Captura de tela das configurações:
    - Parâmetros de comunicação (RS485-B)
    - Configurações de I/O
    - Configuração de watchdog
    - Endereço Modbus slave

[ ] Anotações importantes:
    - Slave Address: _______
    - Baudrate: 57600 bps
    - Última modificação: [DATA]
    - Responsável: [NOME]

[ ] Teste de backup:
    - Reabrir arquivo .sup no Atos Expert
    - Verificar integridade
    - Confirmar que pode ser restaurado
```

---

### 7.2 Documentação da Configuração

**Criar arquivo**: `CONFIGURACAO_CLP_[DATA].txt`

```
=================================================================
CONFIGURAÇÃO DO CLP - DOBRADEIRA NEOCOUDE-HD-15
=================================================================

Data: [DATA]
Responsável: [NOME]
Versão do Programa: apr03_v2_alterado.sup

-----------------------------------------------------------------
COMUNICAÇÃO MODBUS RS485-B
-----------------------------------------------------------------
Slave Address:     1
Baudrate:          57600 bps
Parity:            None
Stop Bits:         1
Data Bits:         8
Timeout:           1000 ms

-----------------------------------------------------------------
HARDWARE
-----------------------------------------------------------------
CLP:               Atos Expert MPC4004
Firmware:          [VERSÃO - ler do CLP]
Bateria:           [ ] Instalada  [ ] Não instalada
                   Tensão: _____ V (se instalada)
Cabo RS485:        Comprimento: _____ metros
                   Terminação: [x] 120Ω nas extremidades

-----------------------------------------------------------------
SEGURANÇA
-----------------------------------------------------------------
Watchdog:          [x] Habilitado - 500ms
Emergência E7:     [x] Sem filtro (0ms)
Prioridade:        [x] Física > Modbus

-----------------------------------------------------------------
TIMER DE STARTUP MODBUS
-----------------------------------------------------------------
Tempo:             120 segundos
Timer Usado:       T020 (0020)
Preset Reg:        0438 (12000 = 120s)
Override Manual:   Bit 03FA (1018 dec)

-----------------------------------------------------------------
OBSERVAÇÕES
-----------------------------------------------------------------
[Adicionar notas específicas da instalação]
```

---

## 8. Verificações Pós-Upload

### 8.1 Checklist Imediato

**Executar IMEDIATAMENTE após upload**:

```
[ ] 1. LED POWER aceso (verde)
[ ] 2. LED RUN aceso (verde) - CLP em execução
[ ] 3. LED ERROR apagado
[ ] 4. LED COMM piscando (indica comunicação RS485)

[ ] 5. Entradas físicas respondem:
        - Pressionar E2 → LED E2 acende
        - Soltar E2 → LED E2 apaga
        - Repetir para E3, E4, E7

[ ] 6. Bit 00BE DESLIGADO (primeiros 120s):
        - Ler via Atos Expert: 00BE = FALSE
        - Ou via LED no painel (se houver)

[ ] 7. Aguardar 120 segundos:
        - Cronometrar desde power-on
        - Após 120s: Bit 00BE = TRUE
        - LED Modbus acende (se houver)

[ ] 8. Teste de comunicação Modbus:
        - Conectar servidor Python
        - Ler bit 03FF (status interface)
        - Esperado: TRUE

[ ] 9. Teste de comando Modbus:
        - Forçar bit 03E0 (AVANÇAR)
        - Verificar: Flag 03F1 ativa
        - Verificar: ROT0 detecta comando

[ ] 10. Teste de emergência:
         - Pressionar E7 (emergência)
         - Verificar: Todas saídas desligam
         - Verificar: Bit 00BE = FALSE
```

---

### 8.2 Testes Funcionais

**Fase 1: Verificação de Lógica (SEM carga mecânica)**:

```
Teste 1: Timer de Startup
  1. Desligar CLP (COMANDO GERAL OFF)
  2. Ligar CLP (COMANDO GERAL ON)
  3. Anotar horário: [______]
  4. Ler bit 00BE a cada 10 segundos
  5. Verificar: 00BE fica FALSE por 120s
  6. Após 120s: 00BE = TRUE
  7. Anotar horário final: [______]
  8. Calcular tempo decorrido: _____ segundos
  ✅ SUCESSO se: 118s < tempo < 122s

Teste 2: Override Manual do Timer
  1. Desligar CLP
  2. Ligar CLP
  3. Imediatamente forçar bit 03FA = TRUE
  4. Verificar: 00BE ativa IMEDIATAMENTE (< 5s)
  5. Verificar: Timer continua contando normalmente
  ✅ SUCESSO se: Modbus ativa sem aguardar 120s

Teste 3: Comandos Modbus Híbridos
  1. Garantir 00BE = TRUE (após 120s ou override)
  2. Forçar bit 03E0 (MB_AVANCAR) = TRUE
  3. Verificar: Bit 03F1 (E2_VIRTUAL) = TRUE
  4. Simultaneamente, pressionar botão físico E2
  5. Verificar: Bit 03F1 permanece TRUE
  6. Soltar botão físico E2
  7. Verificar: Bit 03F1 permanece TRUE (Modbus ainda ativo)
  8. Forçar bit 03E0 = FALSE
  9. Verificar: Bit 03F1 = FALSE
  ✅ SUCESSO se: OR lógico funciona corretamente

Teste 4: Mudança de Modo via Modbus
  1. Verificar modo atual: Ler bits 0190/0191
  2. Se MANUAL (0190=TRUE): Forçar 03E5=TRUE (modo AUTO)
  3. Aguardar 300ms
  4. Verificar: 0191=TRUE (modo AUTO ativo)
  5. Verificar: 03E5=FALSE (auto-reset)
  6. Forçar 03E6=TRUE (modo MANUAL)
  7. Aguardar 300ms
  8. Verificar: 0190=TRUE (modo MANUAL ativo)
  ✅ SUCESSO se: Mudanças ocorrem sem pressionar S1
```

---

**Fase 2: Testes com Máquina (SEM ferro)**:

```
Teste 5: Movimento do Prato via Modbus
  1. Modo MANUAL ativo
  2. Forçar 03E0 (AVANÇAR) = TRUE por 2 segundos
  3. Verificar: Prato gira sentido anti-horário
  4. Forçar 03E0 = FALSE
  5. Verificar: Prato para
  6. Repetir com 03E1 (RECUAR)
  7. Verificar: Prato gira sentido horário
  ✅ SUCESSO se: Movimento corresponde aos comandos

Teste 6: Prioridade de Emergência
  1. Forçar 03E0 (AVANÇAR) = TRUE
  2. Prato girando
  3. Pressionar EMERGÊNCIA física (E7)
  4. Cronometrar tempo até parada completa
  5. Verificar: 00BE = FALSE (Modbus desativado)
  6. Tentar forçar 03E0 novamente
  7. Verificar: Comando ignorado
  ✅ SUCESSO se: Parada < 500ms E Modbus desativa
```

---

### 8.3 Registro de Testes

**Preencher após cada teste**:

```
=================================================================
REGISTRO DE TESTES - APR03_V2_ALTERADO.SUP
=================================================================

Data Upload: [DATA] [HORA]
Responsável: [NOME]

-----------------------------------------------------------------
TESTE 1: TIMER DE STARTUP
-----------------------------------------------------------------
Início:        [HORA]
Fim (00BE=ON): [HORA]
Tempo:         _____ segundos
Status:        [ ] APROVADO  [ ] REPROVADO
Observações:   _____________________________________________

-----------------------------------------------------------------
TESTE 2: OVERRIDE MANUAL
-----------------------------------------------------------------
03FA forçado em: [HORA]
00BE ativou em:  [HORA]
Tempo:           _____ segundos
Status:          [ ] APROVADO  [ ] REPROVADO
Observações:     _____________________________________________

-----------------------------------------------------------------
TESTE 3: COMANDOS HÍBRIDOS
-----------------------------------------------------------------
E2 físico + Modbus: [ ] OK  [ ] FALHA
E4 físico + Modbus: [ ] OK  [ ] FALHA
E3 físico + Modbus: [ ] OK  [ ] FALHA
Status:             [ ] APROVADO  [ ] REPROVADO
Observações:        _____________________________________________

-----------------------------------------------------------------
TESTE 4: MUDANÇA DE MODO
-----------------------------------------------------------------
Manual → Auto:  [ ] OK  [ ] FALHA
Auto → Manual:  [ ] OK  [ ] FALHA
Status:         [ ] APROVADO  [ ] REPROVADO
Observações:    _____________________________________________

-----------------------------------------------------------------
TESTE 5: MOVIMENTO DO PRATO
-----------------------------------------------------------------
AVANÇAR via Modbus: [ ] OK  [ ] FALHA
RECUAR via Modbus:  [ ] OK  [ ] FALHA
Status:             [ ] APROVADO  [ ] REPROVADO
Observações:        _____________________________________________

-----------------------------------------------------------------
TESTE 6: EMERGÊNCIA
-----------------------------------------------------------------
Tempo de parada:    _____ ms
Modbus desativou:   [ ] SIM  [ ] NÃO
Comandos ignorados: [ ] SIM  [ ] NÃO
Status:             [ ] APROVADO  [ ] REPROVADO
Observações:        _____________________________________________

=================================================================
APROVAÇÃO FINAL
=================================================================

Todos os testes aprovados: [ ] SIM  [ ] NÃO

Autorizado para produção: [ ] SIM  [ ] NÃO

Responsável: ___________________  Data: _________

Assinatura: _____________________
```

---

## 9. Troubleshooting Pós-Upload

### 9.1 Problemas Comuns

| Sintoma | Causa Provável | Solução |
|---------|----------------|---------|
| LED ERROR aceso | Erro de compilação ou hardware | Ler log de erros no Atos Expert |
| 00BE não ativa após 120s | Timer não configurado | Verificar MOVK na Line 1 ROT5 |
| Comandos Modbus ignorados | 00BE = FALSE | Aguardar 120s ou forçar 03FA |
| CLP reinicia aleatoriamente | Fonte de alimentação fraca | Medir tensão e ripple |
| Comunicação Modbus falha | Cabo RS485 incorreto | Verificar A/B não invertidos |
| Timer não reseta no power-on | Bateria reténdo estado | Verificar lógica MOVK (00F5) |

---

### 9.2 Logs e Diagnóstico

**Habilitar Log de Erros**:
```
No Software Atos Expert:
  Tools → Error Log

  [x] Enable Error Logging
  [x] Log Modbus Communication Errors
  [x] Log Watchdog Events
  [ ] Log Normal Operations (deixar OFF - muita informação)
```

**Exportar Log**:
```
File → Export Error Log → Salvar como: clp_errors_[DATA].txt
```

---

## 10. Checklist Final de Aprovação

```
=================================================================
CHECKLIST FINAL - ANTES DE LIBERAR PARA PRODUÇÃO
=================================================================

DOCUMENTAÇÃO:
[ ] Backup do programa original salvo
[ ] Configurações documentadas
[ ] Registro de testes preenchido
[ ] Diagrama elétrico atualizado
[ ] Manual de operação atualizado

HARDWARE:
[ ] Bateria verificada (se presente)
[ ] Cabo RS485 instalado corretamente
[ ] Terminação 120Ω nas extremidades
[ ] Fonte de alimentação estável (24V ± 0.5V)
[ ] Fusíveis/disjuntores verificados

SOFTWARE:
[ ] Programa compilado sem erros
[ ] Timer de startup (120s) testado
[ ] Modbus ativa corretamente
[ ] Comandos híbridos funcionam
[ ] Mudança de modo via Modbus OK
[ ] Emergência física tem prioridade
[ ] Override manual (03FA) funciona

SEGURANÇA:
[ ] Emergência física testada (< 500ms)
[ ] Watchdog habilitado
[ ] Todas saídas param em emergência
[ ] Modbus desativa em emergência

COMUNICAÇÃO:
[ ] Modbus responde após 120s
[ ] Baudrate 57600 bps confirmado
[ ] Slave Address anotado: _______
[ ] Polling rate adequado (≤ 4 Hz)

TESTES:
[ ] Fase 1 (lógica) aprovada
[ ] Fase 2 (sem carga) aprovada
[ ] Fase 3 (com carga) aprovada ⚠️  FAZER ANTES DA PRODUÇÃO

=================================================================
✅ APROVADO PARA PRODUÇÃO: [ ] SIM  [ ] NÃO

Responsável: _____________________  Data: __________

Assinatura: ______________________
=================================================================
```

---

## 📞 Contatos e Suporte

**Em caso de problemas**:

1. **Backup sempre disponível**: Restaurar `clp_pre_modbus_[DATA].sup`
2. **Suporte Atos**: Verificar disponibilidade (equipamento de 2007)
3. **Documentação**: Consultar manuais técnicos

**Documentos de Referência**:
- `manual_MPC4004.pdf` - Manual técnico completo
- `MUDANCAS_LADDER_CLP.md` - Especificação das mudanças
- `RELATORIO_IMPLEMENTACAO.md` - Relatório de implementação

---

**Documento Criado**: 2025-11-10
**Versão**: 2.0 (com timer de startup 120s)
**Autor**: Engenharia de Automação
**Status**: ✅ PRONTO PARA UPLOAD
