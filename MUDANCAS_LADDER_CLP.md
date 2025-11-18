# Mudanças Necessárias no Programa Ladder do CLP
## Dobradeira NEOCOUDE-HD-15 com Atos MPC4004

**Data**: 2025-11-10
**Objetivo**: Criar uma "porta dos fundos" no CLP para permitir controle 100% via Modbus RTU (RS485) pela IHM Web

---

## 📋 Sumário Executivo

O programa ladder atual da dobradeira **depende exclusivamente de entradas físicas** (botões do painel) para mudar entre os modos MANUAL e AUTOMÁTICO. Quando a IHM Web envia comandos via Modbus (ex: forçar o coil S1 em `00DC`), esses comandos **são ignorados** porque a lógica ladder verifica condições de botões físicos que não estão ativas.

**Solução**: Adicionar lógica paralela no ladder que permita que **bits internos específicos**, controláveis via Modbus, ativem as mesmas funções que os botões físicos, criando assim uma interface completa Modbus→CLP.

---

## 🔍 Análise do Problema Atual

### 1. Arquitetura Atual do Sistema

```
┌─────────────────────────┐
│  Painel Físico (Botões) │
│  - AVANÇAR (E2)         │
│  - RECUAR (E4)          │
│  - PARADA (E3)          │
│  - EMERGÊNCIA           │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐       ┌──────────────────┐
│   CLP Atos MPC4004      │◄──────│  HMI Física      │
│   Programa Ladder       │       │  (Danificada)    │
│   - ROT0: Modo Manual/  │       │  Teclas S1, S2   │
│     Auto                │       │  K0-K9, etc.     │
│   - ROT1: Contadores    │       └──────────────────┘
│   - ROT2: Classes Vel.  │
│   - ROT3: Init          │
│   - ROT4: Ângulos       │
│   - Principal: Main     │
└─────────────────────────┘
```

### 2. Mapeamento de Endereços Críticos

#### Entradas Físicas (Painel)
| Endereço Hex | Decimal | Símbolo | Função                    |
|--------------|---------|---------|---------------------------|
| `0100`       | 256     | E0      | Sensor de referência      |
| `0102`       | 258     | E2      | Botão AVANÇAR (CCW)       |
| `0103`       | 259     | E3      | Botão PARADA              |
| `0104`       | 260     | E4      | Botão RECUAR (CW)         |
| `0105`       | 261     | E5      | Entrada auxiliar          |
| `0106`       | 262     | E6      | Entrada auxiliar          |

#### Teclas HMI (Modbus Force Coil)
| Endereço Hex | Decimal | Símbolo | Função                    |
|--------------|---------|---------|---------------------------|
| `00DC`       | 220     | S1      | Mudança Manual↔Auto       |
| `00DD`       | 221     | S2      | Reset de ângulo           |
| `00A0-00A8`  | 160-168 | K1-K9   | Teclas numéricas          |
| `00A9`       | 169     | K0      | Tecla zero                |
| `00AC`       | 172     | ↑       | Seta para cima            |
| `00AD`       | 173     | ↓       | Seta para baixo           |
| `00BC`       | 188     | ESC     | Cancelar                  |
| `0025`       | 37      | ENTER   | Confirmar                 |
| `0026`       | 38      | EDIT    | Modo edição               |
| `00F1`       | 241     | LOCK    | Trava de teclado          |

#### Estados Internos do Sistema
| Endereço Hex | Decimal | Símbolo        | Função                         |
|--------------|---------|----------------|--------------------------------|
| `0190`       | 400     | BIT_MODO_MANUAL | Máquina em modo manual        |
| `0191`       | 401     | BIT_MODO_AUTO   | Máquina em modo automático    |
| `0200`       | 512     | BIT_SENTIDO_CCW | Sentido anti-horário ativo    |
| `0201`       | 513     | BIT_SENTIDO_CW  | Sentido horário ativo         |
| `0210`       | 528     | BIT_RESET_REQ   | Requisição de reset           |
| `02FF`       | 767     | BIT_SISTEMA_OK  | Sistema operacional           |
| `0300-0305`  | 768-773 | Estados Seq.    | Máquina de estados sequencial |

#### Saídas Físicas (Atuadores)
| Endereço Hex | Decimal | Símbolo | Função                    |
|--------------|---------|---------|---------------------------|
| `0180`       | 384     | S0      | Motor sentido horário     |
| `0181`       | 385     | S1      | Motor sentido anti-horário|
| `00C3`       | 195     | LED_K4  | LED K4 (direção esquerda) |
| `00C4`       | 196     | LED_K5  | LED K5 (direção direita)  |

### 3. Problema Identificado no Código Ladder

#### ROT0.lad - Lógica de Controle de Modo (ATUAL)

**Line 1 - Ativar Saída S0 (Sentido Horário)**
```ladder
Condições:
  - E2 (0102) AND /E2 (0102) AND /0191
    OU
  - 0305 AND /02FF AND /0191
  - E2 (0102) OR /0181 (auto reset)
  - ...outras condições com E4, E5, E6, E3, E5, 0380
Resultado: SETR 0180
```

**Line 3 - Ativar Saída S1 (Sentido Anti-Horário)**
```ladder
Condições:
  - E4 (0104) AND /E4 (0104) AND /0190
    OU
  - 0305 AND /02FF AND /0190
  - Múltiplas ramificações similares
Resultado: SETR 0181
```

**Line 5 - Detectar Mudança de Modo (KEY)**
```ladder
Condições:
  - E3 (0103) AND /02FF AND /0191 AND /0180 AND /0181 AND E5 (0105) AND 0380
Resultado: MONOA 0290
```

**🚨 PROBLEMA**: A lógica depende **diretamente** de:
- **E2 (0102)** - Botão físico AVANÇAR
- **E3 (0103)** - Botão físico PARADA
- **E4 (0104)** - Botão físico RECUAR
- **E5 (0105)** - Entrada física auxiliar

**Quando você força o coil S1 (`00DC`) via Modbus**, o ladder **não executa** a mudança de modo porque:
1. A tecla S1 (`00DC`) não está diretamente conectada à lógica de mudança de modo em ROT0
2. As condições de E2, E3, E4, E5 **não estão satisfeitas** (botões físicos não pressionados)
3. A lógica espera uma **sequência específica** de eventos físicos

#### ROT1.lad - Contador de Eventos (PROBLEMA SECUNDÁRIO)

**Line 2 - Contador baseado em S2**
```ladder
Condições:
  - 0210 OR /00DD (S2) OR /00DD (S2)
Resultado: CTCPU 0800, 0000, 0187
```

**🚨 PROBLEMA**: Mesmo quando você força S2 (`00DD`) via Modbus, a lógica pode não responder adequadamente porque espera um **pulso** (transição 0→1→0), não um nível estático.

---

## ✅ Solução Proposta: "Porta dos Fundos" Modbus

### Conceito Geral

Criar **bits internos de controle** que atuam como "sombras" dos botões físicos. A IHM Web escreverá esses bits via Modbus, e o ladder os tratará **exatamente como se fossem entradas físicas**.

### Mapeamento de Bits de Controle Modbus

| Bit Interno | Endereço Hex | Decimal | Função Equivalente         | Como Usar via Modbus          |
|-------------|--------------|---------|----------------------------|-------------------------------|
| `MB_AVANCAR`| `03E0`       | 992     | = E2 (Botão AVANÇAR)       | Force Coil 992 = TRUE         |
| `MB_RECUAR` | `03E1`       | 993     | = E4 (Botão RECUAR)        | Force Coil 993 = TRUE         |
| `MB_PARADA` | `03E2`       | 994     | = E3 (Botão PARADA)        | Force Coil 994 = TRUE         |
| `MB_S1_CMD` | `03E3`       | 995     | = S1 (Mudança modo)        | Force Coil 995 = TRUE (pulso) |
| `MB_S2_CMD` | `03E4`       | 996     | = S2 (Reset ângulo)        | Force Coil 996 = TRUE (pulso) |
| `MB_MODO_AUTO_REQ` | `03E5` | 997   | Requisição Modo AUTO       | Force Coil 997 = TRUE         |
| `MB_MODO_MANUAL_REQ` | `03E6` | 998 | Requisição Modo MANUAL     | Force Coil 998 = TRUE         |

**Nota**: Escolhi a faixa `03E0`-`03FF` (992-1023) porque está na **área de estados internos** (`0000-03FF`) do MPC4004, distante de outras alocações observadas no código.

---

## 🛠️ Mudanças Específicas no Ladder

### 1️⃣ NOVO: Rotina MODBUS_INTERFACE (Criar como ROT5.lad)

**Objetivo**: Processar comandos Modbus e convertê-los em sinais internos compatíveis com a lógica existente.

```ladder
;==============================================================================
; ROT5.lad - INTERFACE MODBUS PARA IHM WEB
; Autor: Sistema IHM Web - Claude Code
; Data: 2025-11-10
; Descrição: "Porta dos fundos" para controle total via Modbus RTU
;==============================================================================

;------------------------------------------------------------------------------
; Line 1: Detecção de Pulso para MB_S1_CMD (Mudança de Modo Manual↔Auto)
;------------------------------------------------------------------------------
; Gera um pulso interno quando 03E3 (MB_S1_CMD) é ativado via Modbus
; Equivalente a pressionar S1 (00DC) na HMI física

[Line00001]
  [Branch01]
    Condições:
      - 03E3 (MB_S1_CMD) = TRUE
      - /03F0 (Flag auxiliar de borda) = FALSE
    Ação: SETR 03F0 (Set flag de borda)

  [Branch02]
    Condições:
      - /03E3 = FALSE (botão solto)
      - 03F0 = TRUE
    Ação:
      - SETR 00DC (Simula pressionamento de S1 HMI)
      - RESET 03F0 (Reset flag de borda)

;------------------------------------------------------------------------------
; Line 2: Mudança Forçada para Modo AUTOMÁTICO
;------------------------------------------------------------------------------
; Permite que a IHM Web force diretamente o modo AUTO,
; bypassando todas as condições de botões físicos

[Line00002]
  [Branch01]
    Condições:
      - 03E5 (MB_MODO_AUTO_REQ) = TRUE
      - 0190 (BIT_MODO_MANUAL) = TRUE  ; Só se estiver em manual
      - 02FF (BIT_SISTEMA_OK) = TRUE   ; Sistema operacional
      - 0300 (Estado inicial) = TRUE   ; Na 1ª dobra (K1)
    Ação:
      - RESET 0190 (Desativa modo MANUAL)
      - SETR 0191 (Ativa modo AUTO)
      - RESET 03E5 (Auto-reset do comando)
      - MONOA 0500 (Log de mudança - criar registro)

;------------------------------------------------------------------------------
; Line 3: Mudança Forçada para Modo MANUAL
;------------------------------------------------------------------------------
; Permite retorno para modo MANUAL a qualquer momento (segurança)

[Line00003]
  [Branch01]
    Condições:
      - 03E6 (MB_MODO_MANUAL_REQ) = TRUE
      - 0191 (BIT_MODO_AUTO) = TRUE    ; Só se estiver em auto
      - 02FF (BIT_SISTEMA_OK) = TRUE   ; Sistema operacional
    Ação:
      - RESET 0191 (Desativa modo AUTO)
      - SETR 0190 (Ativa modo MANUAL)
      - RESET 03E6 (Auto-reset do comando)
      - MONOA 0501 (Log de mudança - criar registro)

;------------------------------------------------------------------------------
; Line 4: Emulação de Botão AVANÇAR (E2) via Modbus
;------------------------------------------------------------------------------
; Cria um "OR" virtual: E2 físico OU MB_AVANCAR Modbus

[Line00004]
  [Branch01]
    Condições:
      - 03E0 (MB_AVANCAR) = TRUE
    Ação:
      - SETR 03F1 (Flag interna "E2 virtual")

  [Branch02]
    Condições:
      - 0102 (E2 físico) = TRUE
    Ação:
      - SETR 03F1 (Flag interna "E2 virtual")

  [Branch03]
    Condições:
      - /03E0 AND /0102 (nenhum ativo)
    Ação:
      - RESET 03F1 (Limpa flag)

;------------------------------------------------------------------------------
; Line 5: Emulação de Botão RECUAR (E4) via Modbus
;------------------------------------------------------------------------------
[Line00005]
  [Branch01]
    Condições:
      - 03E1 (MB_RECUAR) = TRUE
    Ação:
      - SETR 03F2 (Flag interna "E4 virtual")

  [Branch02]
    Condições:
      - 0104 (E4 físico) = TRUE
    Ação:
      - SETR 03F2 (Flag interna "E4 virtual")

  [Branch03]
    Condições:
      - /03E1 AND /0104
    Ação:
      - RESET 03F2

;------------------------------------------------------------------------------
; Line 6: Emulação de Botão PARADA (E3) via Modbus
;------------------------------------------------------------------------------
[Line00006]
  [Branch01]
    Condições:
      - 03E2 (MB_PARADA) = TRUE
    Ação:
      - SETR 03F3 (Flag interna "E3 virtual")

  [Branch02]
    Condições:
      - 0103 (E3 físico) = TRUE
    Ação:
      - SETR 03F3 (Flag interna "E3 virtual")

  [Branch03]
    Condições:
      - /03E2 AND /0103
    Ação:
      - RESET 03F3

;------------------------------------------------------------------------------
; Line 7: Auto-reset dos Comandos Modbus (Limpeza de Pulsos)
;------------------------------------------------------------------------------
; Garante que os bits de comando não fiquem travados

[Line00007]
  [Branch01]
    Condições:
      - 03E0 OR 03E1 OR 03E2 OR 03E3 OR 03E4 (qualquer comando ativo)
      - Timer T010 > 500ms (tempo de pulso máximo)
    Ação:
      - RESET 03E0 (MB_AVANCAR)
      - RESET 03E1 (MB_RECUAR)
      - RESET 03E2 (MB_PARADA)
      - RESET 03E3 (MB_S1_CMD)
      - RESET 03E4 (MB_S2_CMD)
      - RESET T010

;------------------------------------------------------------------------------
; Line 8: Diagnóstico - Estado da Interface Modbus
;------------------------------------------------------------------------------
; Bit de status para a IHM Web monitorar se a interface está ativa

[Line00008]
  [Branch01]
    Condições:
      - 00BE (Modbus slave habilitado) = TRUE
      - 02FF (Sistema OK) = TRUE
    Ação:
      - SETR 03FF (BIT_MODBUS_INTERFACE_OK)

  [Branch02]
    Condições:
      - /00BE OR /02FF
    Ação:
      - RESET 03FF
```

---

### 2️⃣ MODIFICAÇÃO: Principal.lad

**Adicionar chamada para ROT5 no início da rotina principal**

```ladder
[Line00001] (EXISTENTE - manter)
  ...
  Out: MONOA T:-006 Size:001 E:0260

[Line00002] (NOVO - ADICIONAR ANTES DE "CALL ROT0")
  [Features]
    Branchs:01
    Type:0
    Label:0
    Comment:INTERFACE MODBUS - IHM WEB
    Out:CALL T:-001 Size:001 E:ROT5
    Height:01
  [Branch01]
    X1position:00
    X2position:13
    Yposition:00
    Height:01
    {0;00;00F7;-1;-1;-1;-1;00}  ; Sempre executar
    ###

[Line00003] (ERA Line00002 - AJUSTAR NUMERAÇÃO)
  ...
  Out:CALL T:-001 Size:001 E:ROT0
```

---

### 3️⃣ MODIFICAÇÃO: ROT0.lad

**Substituir referências diretas às entradas físicas pelas flags virtuais**

#### 🔧 Line 1 - Ativar Saída S0 (MODIFICAR)

**ANTES:**
```ladder
{0;00;0102;-1;02;-1;-1;00}  ; E2 físico
```

**DEPOIS:**
```ladder
{0;00;03F1;-1;02;-1;-1;00}  ; E2 virtual (físico OR Modbus)
```

**Repetir para todas as ocorrências de 0102 (E2) em ROT0.lad**

#### 🔧 Line 3 - Ativar Saída S1 (MODIFICAR)

**ANTES:**
```ladder
{0;00;0104;-1;02;-1;-1;00}  ; E4 físico
```

**DEPOIS:**
```ladder
{0;00;03F2;-1;02;-1;-1;00}  ; E4 virtual (físico OR Modbus)
```

#### 🔧 Line 5 - Detectar Mudança de Modo (MODIFICAR)

**ANTES:**
```ladder
{0;00;0103;-1;-1;-1;-1;00}  ; E3 físico (PARADA)
{0;01;0105;-1;-1;-1;-1;00}  ; E5 físico
```

**DEPOIS:**
```ladder
{0;00;03F3;-1;-1;-1;-1;00}  ; E3 virtual (PARADA)
{0;01;0105;-1;-1;-1;-1;00}  ; E5 - manter físico (segurança)
```

**OU adicionar ramo alternativo para Modbus direto:**

```ladder
[Branch NEW]
  Condições:
    - 03E3 (MB_S1_CMD) = TRUE (pulso de mudança via Modbus)
    - 02FF (Sistema OK) = TRUE
    - 0300 (Estado inicial K1) = TRUE
  Ação: MONOA 0290
```

---

### 4️⃣ MODIFICAÇÃO: ROT1.lad

**Adicionar detecção de S2 via Modbus**

#### 🔧 Line 2 - Contador baseado em S2 (ADICIONAR RAMO)

**ANTES:**
```ladder
[Branch01]
  {0;00;0210;-1;02;01;02;00}
[Branch02]
  {0;00;00DD;-1;03;-1;-1;00}  ; S2 HMI físico
  {0;01;00DD;-1;-1;01;03;00}
```

**DEPOIS (adicionar Branch03):**
```ladder
[Branch03]
  X1position:00
  X2position:01
  Yposition:02
  Height:01
  B1:02
  B2:02
  BInputnumber:-01
  {0;00;03E4;-1;-1;-1;-1;00}  ; MB_S2_CMD (Modbus)
  {0;01;0250;-1;-1;-1;-1;00}  ; Condição auxiliar
```

---

### 5️⃣ NOVO: Criar Registros de Log (Opcional mas Recomendado)

**Para diagnóstico e auditoria, criar registros que registrem quando comandos Modbus foram usados**

```ladder
;==============================================================================
; Novo: MODBUS_LOG.lad (Opcional - ROT6)
;==============================================================================

[Line00001]
  ; Contador de comandos Modbus recebidos
  [Branch01]
    Condições:
      - 03E0 OR 03E1 OR 03E2 OR 03E3 OR 03E4 OR 03E5 OR 03E6
    Ação: CNT 0030 (Contador total de comandos Modbus)

[Line00002]
  ; Timestamp do último comando (usar registro de hora do PLC se disponível)
  [Branch01]
    Condições:
      - 03E0 OR 03E1 OR 03E2 OR 03E3 OR 03E4 OR 03E5 OR 03E6
    Ação: MOV 04D6, 0A00 (Salva valor do encoder no momento do comando)
```

---

## 📊 Tabela Resumo: Comandos Modbus → CLP

| Comando IHM Web | Função Modbus | Endereço | Efeito no CLP |
|-----------------|---------------|----------|---------------|
| **Mudar para AUTO** | Force Coil ON | 997 (03E5) | Ativa 0191, desativa 0190, sem verificar E2/E3/E4 |
| **Mudar para MANUAL** | Force Coil ON | 998 (03E6) | Ativa 0190, desativa 0191 |
| **Pressionar S1** | Force Coil pulso | 995 (03E3) | Simula tecla S1 da HMI física |
| **Pressionar S2** | Force Coil pulso | 996 (03E4) | Simula tecla S2 (reset ângulo) |
| **Avançar (Start)** | Force Coil ON | 992 (03E0) | Equivale a pressionar botão AVANÇAR |
| **Recuar (Start)** | Force Coil ON | 993 (03E1) | Equivale a pressionar botão RECUAR |
| **Parada** | Force Coil ON | 994 (03E2) | Equivale a pressionar botão PARADA |

### Exemplo de Sequência: Mudança Manual → Auto via Web

```python
# Servidor Python IHM Web envia:

# 1. Verificar se está em K1 (1ª dobra) - ler coil 0x0300
status_k1 = modbus_client.read_coils(0x0300, 1)[0]

if status_k1:
    # 2. Forçar mudança para AUTO
    modbus_client.write_coil(997, True)  # MB_MODO_AUTO_REQ = ON

    # 3. Aguardar 200ms para o ladder processar
    time.sleep(0.2)

    # 4. Verificar se mudou (ler bit 0191)
    modo_auto = modbus_client.read_coils(0x0191, 1)[0]

    if modo_auto:
        print("✅ Modo AUTO ativado com sucesso via Modbus")
    else:
        print("❌ Falha ao ativar modo AUTO")
```

---

## 🔒 Considerações de Segurança

### 1. Botão de Emergência Física

**NUNCA** substituir a entrada física de emergência. Ela DEVE permanecer **hard-wired** e com prioridade absoluta.

```ladder
; Garantir que emergência física sempre tem prioridade
[Qualquer rotina]
  [Branch FINAL]
    Condições:
      - /0107 (Entrada E7 - Emergência física) = FALSE
    Ação:
      - RESET TODAS as saídas (0180, 0181, etc.)
      - RESET 02FF (Sistema OK)
      - SETR 0400 (Flag de emergência ativa)
```

### 2. Timeout de Comandos Modbus

Implementar watchdog para detectar perda de comunicação:

```ladder
;==============================================================================
; Watchdog Modbus (adicionar em ROT5)
;==============================================================================
[Line NEW]
  [Branch01]
    Condições:
      - 03FF (Interface Modbus OK) = TRUE
      - Timer T020 > 5000ms (5 segundos sem heartbeat)
    Ação:
      - RESET 03FF (Interface Modbus FALHA)
      - RESET todas flags MB_* (03E0-03E6)
      - SETR 0410 (Flag de timeout Modbus)
```

**No servidor Python:**
```python
# Enviar heartbeat a cada 2 segundos
while True:
    modbus_client.write_coil(0x03FF, True)  # Refresh do bit de status
    time.sleep(2)
```

### 3. Ordem de Prioridade de Controle

```
1. 🔴 EMERGÊNCIA FÍSICA (E7) - Prioridade MÁXIMA, hard-wired
2. 🟡 BOTÕES FÍSICOS DO PAINEL - Prioridade ALTA
3. 🟢 COMANDOS MODBUS (IHM Web) - Prioridade NORMAL
4. 🔵 SEQUÊNCIAS AUTOMÁTICAS - Prioridade BAIXA
```

Garantir no ladder:
```ladder
; Se botão físico E2 for pressionado, ele tem prioridade sobre Modbus
[Line Exemplo]
  [Branch01]
    Condições:
      - 0102 (E2 físico) = TRUE
    Ação: RESET 03E0 (Cancela comando Modbus AVANÇAR)
```

---

## 🧪 Plano de Testes

### Fase 1: Testes em Bancada (sem carga mecânica)

1. **Teste de Interface Modbus**
   ```python
   # Verificar leitura de registros
   assert modbus_client.read_coils(0x03FF, 1)[0] == True  # Interface OK
   ```

2. **Teste de Mudança de Modo**
   ```python
   # Manual → Auto
   modbus_client.write_coil(997, True)
   time.sleep(0.3)
   assert modbus_client.read_coils(0x0191, 1)[0] == True

   # Auto → Manual
   modbus_client.write_coil(998, True)
   time.sleep(0.3)
   assert modbus_client.read_coils(0x0190, 1)[0] == True
   ```

3. **Teste de Pulsos (S1/S2)**
   ```python
   # Simular pressionamento de S1
   modbus_client.write_coil(995, True)
   time.sleep(0.1)  # Pulso de 100ms
   modbus_client.write_coil(995, False)

   # Verificar efeito (deve ter mudado de modo)
   ```

4. **Teste de Prioridade**
   ```
   - Pressionar botão físico AVANÇAR no painel
   - Simultaneamente enviar comando Modbus AVANÇAR
   - Verificar que AMBOS acionam a saída S0
   ```

### Fase 2: Testes com Máquina Ligada (sem ferro)

1. **Verificar movimento do prato**
   - Comando Modbus AVANÇAR → Prato gira sentido anti-horário
   - Comando Modbus RECUAR → Prato gira sentido horário

2. **Verificar mudança de classe de velocidade**
   - Em modo MANUAL, forçar bits de seleção de classe
   - Verificar resposta do inversor de frequência

3. **Teste de sequência completa**
   ```
   1. Modo MANUAL via Modbus
   2. Avançar até ângulo X via Modbus
   3. Modo AUTO via Modbus
   4. Executar dobra K1, K2, K3 automaticamente
   5. Verificar retorno à posição zero
   ```

### Fase 3: Testes em Produção (com ferro)

1. **Dobra de teste com CA-25 Ø 10mm**
   - 90° esquerda via Modbus
   - 90° direita via Modbus

2. **Teste de emergência**
   - Pressionar emergência física durante operação via Modbus
   - Verificar parada imediata

3. **Teste de reconexão**
   - Desconectar comunicação Modbus durante operação
   - Verificar que máquina para de forma segura (watchdog)

---

## 📝 Checklist de Implementação

### Pré-requisitos
- [ ] Backup completo do programa ladder atual (`clp.sup`)
- [ ] Documentação da versão atual do firmware Atos (versão: ______)
- [ ] Software Atos Expert de programação instalado
- [ ] Cabo de programação RS232/USB-RS485 funcionando
- [ ] Acesso físico ao painel do CLP

### Etapas de Modificação

#### 1. Preparação
- [ ] Desligar a máquina (COMANDO GERAL OFF)
- [ ] Descarregar toda energia residual (aguardar 5 minutos)
- [ ] Conectar laptop ao CLP via RS485
- [ ] Fazer upload do programa atual (backup adicional)

#### 2. Criar ROT5.lad (Nova Rotina)
- [ ] Criar novo arquivo `ROT5.lad` no projeto
- [ ] Implementar Lines 1-8 conforme especificado acima
- [ ] Compilar e verificar erros de sintaxe
- [ ] Salvar projeto

#### 3. Modificar Principal.lad
- [ ] Abrir `Principal.lad`
- [ ] Adicionar `CALL ROT5` antes de `CALL ROT0` (Line 2 nova)
- [ ] Ajustar numeração das linhas subsequentes
- [ ] Compilar

#### 4. Modificar ROT0.lad
- [ ] Substituir `0102` (E2) por `03F1` em todas ocorrências
- [ ] Substituir `0104` (E4) por `03F2` em todas ocorrências
- [ ] Substituir `0103` (E3) por `03F3` onde aplicável
- [ ] Adicionar ramo alternativo para mudança de modo Modbus (Line 5)
- [ ] Compilar

#### 5. Modificar ROT1.lad
- [ ] Adicionar Branch03 para detectar S2 via Modbus (`03E4`)
- [ ] Compilar

#### 6. Upload e Teste
- [ ] Download do programa modificado para o CLP
- [ ] Verificar bit `00BE` (Modbus slave) = ON
- [ ] Ligar COMANDO GERAL
- [ ] Executar Fase 1 de testes (bancada)
- [ ] Executar Fase 2 de testes (sem carga)
- [ ] Executar Fase 3 de testes (produção)

#### 7. Documentação
- [ ] Atualizar diagrama elétrico com novos bits
- [ ] Atualizar manual de operação da IHM Web
- [ ] Criar log de mudanças (changelog) do projeto
- [ ] Salvar versão final do `.sup` com data: `clp_v2_modbus_2025-11-10.sup`

---

## 🐛 Troubleshooting

### Problema: Comando Modbus não funciona

**Sintomas**: Bit `03E5` é forçado mas modo não muda

**Diagnóstico**:
1. Verificar se `00BE` está ON (Modbus slave habilitado)
2. Ler bit `03FF` - deve estar TRUE (interface OK)
3. Verificar se `0300` está ON (máquina em K1)
4. Verificar se `02FF` está ON (sistema operacional)

**Soluções**:
```python
# Forçar habilitação Modbus
modbus_client.write_coil(0x00BE, True)

# Verificar diagnóstico
status = {
    'modbus_slave': modbus_client.read_coils(0x00BE, 1)[0],
    'interface_ok': modbus_client.read_coils(0x03FF, 1)[0],
    'sistema_ok': modbus_client.read_coils(0x02FF, 1)[0],
    'estado_k1': modbus_client.read_coils(0x0300, 1)[0],
}
print(status)
```

### Problema: Botões físicos param de funcionar

**Sintomas**: Painel físico não responde após modificações

**Causa Provável**: Flags virtuais (`03F1`, `03F2`, `03F3`) travadas em TRUE

**Solução**:
```python
# Reset manual das flags virtuais
for addr in range(0x03F1, 0x03F4):
    modbus_client.write_coil(addr, False)
```

OU via ladder, adicionar reset periódico:
```ladder
[ROT5 - Line adicional]
  [Branch01]
    Condições:
      - Timer T011 > 10000ms (10 segundos)
    Ação:
      - RESET 03F1, 03F2, 03F3 (Limpeza preventiva)
      - RESET T011
```

### Problema: Máquina não para com botão físico

**Sintomas**: Emergência física não funciona

**PERIGO**: Situação crítica de segurança

**Ação Imediata**:
1. DESLIGAR DISJUNTOR GERAL
2. NÃO reativar até corrigir

**Correção**:
Verificar que entrada E7 (emergência) tem prioridade absoluta em TODAS as rotinas:

```ladder
; Adicionar em TODAS as rotinas (Principal, ROT0-5)
[Line PRIMEIRA de cada rotina]
  [Branch01]
    Condições:
      - /0107 (Emergência) = FALSE
    Ação:
      - RESET 0180 (Parar motor)
      - RESET 0181 (Parar motor)
      - JMP FIM (Pular para fim da rotina)
```

---

## 📚 Referências Técnicas

### Documentos Consultados
1. **Manual MPC4004** (`manual_MPC4004.pdf`)
   - Seção 7.3: Mapa de memória (páginas 53-104)
   - Seção 9.1: Comunicação Modbus RTU (páginas 133-134)
   - Seção 8.2: Estados internos e registros (página 85-86)

2. **Manual NEOCOUDE-HD-15** (`NEOCOUDE-HD 15 - Camargo 2007 (1).pdf`)
   - Seção "Operação" (páginas 7-8)
   - Diagrama elétrico (páginas 34-42)
   - Painel de comando (página 33)

3. **CLAUDE.md** (Especificação do projeto)
   - Mapeamento de teclas HMI (Physical HMI Button Mapping)
   - Endereços Modbus conhecidos

### Códigos de Instrução Atos Relevantes

| Mnemônico | Código | Função                        |
|-----------|--------|-------------------------------|
| `SETR`    | 0043   | Set Reset (latch)             |
| `RESET`   | 0042   | Reset (unlatch)               |
| `MONOA`   | -006   | Monoestável (one-shot)        |
| `TMR`     | 0056   | Timer                         |
| `CNT`     | 0013   | Counter                       |
| `CALL`    | -001   | Call subroutine               |
| `MOV`     | 0028   | Move                          |
| `MOVK`    | 0029   | Move constant                 |
| `CMP`     | 0010   | Compare                       |

---

## ✅ Validação Final

**Critérios de Sucesso**:

1. ✅ Mudança Manual↔Auto funciona **100% via Modbus** sem botões físicos
2. ✅ Botões físicos continuam funcionando **normalmente** (não foram quebrados)
3. ✅ Emergência física tem **prioridade absoluta** sobre Modbus
4. ✅ Timeout de comunicação **para a máquina** em caso de falha
5. ✅ IHM Web consegue **ler e escrever** todos os parâmetros críticos
6. ✅ Sistema **não apresenta falhas** em 100 ciclos de teste
7. ✅ **Nenhum sensor/encoder** foi comprometido pelas mudanças

**Assinatura de Aprovação**:

```
[ ] Testado em bancada    Data: ___/___/___  Responsável: _____________
[ ] Testado sem carga     Data: ___/___/___  Responsável: _____________
[ ] Testado com carga     Data: ___/___/___  Responsável: _____________
[ ] Aprovado para produção Data: ___/___/___  Responsável: _____________
```

---

## 📞 Suporte

**Em caso de dúvidas ou problemas durante implementação:**

1. **Consultar documentação Atos Expert**: Manual do usuário do software de programação
2. **Suporte Atos**: Verificar disponibilidade de suporte técnico do fabricante (contato desatualizado, equipamento de 2007)
3. **Backup sempre disponível**: Manter laptop com programa original sempre carregado próximo à máquina

**Contatos de Emergência**:
- **Eletricista responsável**: ________________________
- **Programador PLC**: ________________________
- **Engenheiro de automação**: ________________________

---

**Documento Criado**: 2025-11-10
**Versão**: 1.0
**Status**: Aguardando Implementação
**Autor**: Sistema IHM Web - Claude Code
**Baseado em**: Análise do programa ladder `clp.sup` e manuais técnicos
