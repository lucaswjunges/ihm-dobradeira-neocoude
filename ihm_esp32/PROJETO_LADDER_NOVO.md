# PROJETO LADDER NOVO - DOBRADEIRA NEOCOUDE-HD-15

**Data:** 26 de Novembro de 2025
**Objetivo:** Reprogramar o CLP Atos MPC4004 do zero com uma lógica mais simples, inteligente e totalmente funcional.

---

## 1. VISAO GERAL DA MAQUINA

### 1.1 Hardware Existente

| Componente | Modelo | Funcao |
|------------|--------|--------|
| CLP | Atos MPC4004 | Controlador principal |
| Motor | 15 HP, 4 polos, 1755 rpm | Acionamento do prato |
| Inversor | WEG CFW-08 | Controle de velocidade |
| Encoder | Modelo 2.018.200 | Medicao angular |
| Sensor Zero | Modelo 2.018.152 | Referencia de posicao |

### 1.2 Velocidades do Prato

| Classe | RPM | Valor Saida Analogica (06E0) | Uso |
|--------|-----|------------------------------|-----|
| 1 | 5 | 527 (0x20F) | Modo Manual |
| 2 | 10 | 1055 (0x41F) | Modo Automatico |
| 3 | 15 | 1583 (0x62F) | Modo Automatico |

---

## 2. MAPEAMENTO DE I/O

### 2.1 Entradas Digitais (E0-E7)

| Entrada | Endereco Hex | Endereco Dec | Funcao | Tipo |
|---------|--------------|--------------|--------|------|
| **E0** | 0x0100 | 256 | Sensor de posicao ZERO | NA (fecha quando na posicao zero) |
| **E1** | 0x0101 | 257 | Reserva / Sensor carenagem | - |
| **E2** | 0x0102 | 258 | **PEDAL AVANCO (CCW)** | NA (fecha ao pisar) |
| **E3** | 0x0103 | 259 | **PEDAL PARADA** | NA (fecha ao pisar) |
| **E4** | 0x0104 | 260 | **PEDAL RECUO (CW)** | NA (fecha ao pisar) |
| **E5** | 0x0105 | 261 | Sensor de seguranca/carenagem | NF (abre se problema) |
| **E6** | 0x0106 | 262 | **BOTAO EMERGENCIA** | NF (abre em emergencia) |
| **E7** | 0x0107 | 263 | Reserva | - |

**Nota:** NA = Normalmente Aberto, NF = Normalmente Fechado

### 2.2 Saidas Digitais (S0-S7)

| Saida | Endereco Hex | Endereco Dec | Funcao | Logica |
|-------|--------------|--------------|--------|--------|
| **S0** | 0x0180 | 384 | Contator AVANCO (motor CCW) | Liga motor sentido anti-horario |
| **S1** | 0x0181 | 385 | Contator RECUO (motor CW) | Liga motor sentido horario |
| **S2** | 0x0182 | 386 | Habilita inversor | ON = inversor ativo |
| **S3** | 0x0183 | 387 | Reserva / Sinalizador | - |
| **S4** | 0x0184 | 388 | LED Dobra 1 | ON = dobra 1 ativa |
| **S5** | 0x0185 | 389 | LED Dobra 2 | ON = dobra 2 ativa |
| **S6** | 0x0186 | 390 | LED Dobra 3 | ON = dobra 3 ativa |
| **S7** | 0x0187 | 391 | Reserva | - |

### 2.3 Registros Especiais (Enderecos Fixos do CLP)

| Registro | Endereco Hex | Endereco Dec | Tipo | Funcao |
|----------|--------------|--------------|------|--------|
| ENCODER_MSW | 0x04D6 | 1238 | 16-bit | Posicao encoder (bits 31-16) |
| ENCODER_LSW | 0x04D7 | 1239 | 16-bit | Posicao encoder (bits 15-0) |
| VELOCIDADE_INVERSOR | 0x06E0 | 1760 | 16-bit | Saida analogica para inversor |

**Leitura do encoder:** `posicao = (ENCODER_MSW << 16) | ENCODER_LSW`
**Conversao para graus:** `graus = posicao / 10.0` (se 900 = 90.0 graus)

---

## 3. VARIAVEIS DE PROCESSO (Novos Registros)

### 3.1 Setpoints de Angulo (32-bit, unidade = 0.1 grau)

| Variavel | Endereco MSW | Endereco LSW | Valor Padrao | Descricao |
|----------|--------------|--------------|--------------|-----------|
| ANGULO_1 | 0x0840 | 0x0841 | 900 (90.0 graus) | Angulo da dobra 1 |
| ANGULO_2 | 0x0844 | 0x0845 | 900 (90.0 graus) | Angulo da dobra 2 |
| ANGULO_3 | 0x0848 | 0x0849 | 900 (90.0 graus) | Angulo da dobra 3 |

**Nota:** Usar apenas 3 angulos simplifica a logica. Valores em decimos de grau (900 = 90.0).

### 3.2 Angulo Alvo Atual (32-bit)

| Variavel | Endereco MSW | Endereco LSW | Descricao |
|----------|--------------|--------------|-----------|
| ANGULO_ALVO | 0x0942 | 0x0944 | Angulo que esta sendo perseguido no momento |

### 3.3 Registros de Trabalho (16-bit)

| Variavel | Endereco | Descricao |
|----------|----------|-----------|

| NUMERO0    | 0x0900 = 0 |
| NUMERO1    | 0x0902 = 1 |
| NUMERO2    | 0x0904 = 2 | 
| MAX_DOBRAS | 0x0906 = 3 |
| NUMERO4    | 0x0908 = 4 |
| NUMERO5    | 0x0910 = 5 |
| NUMERO6    | 0x0912 = 6 |
| NUMERO7    | 0x0914 = 7 |

| VELOCIDADE_ATUAL | 0x0916 | Classe de velocidade (1, 2 ou 3) |
| DOBRA_ATUAL      | 0x0918 | Numero da dobra atual (1, 2 ou 3) |
| CONTADOR_PECAS   | 0x0920 | Contador de pecas produzidas |
| ESTADO_ANTERIOR  | 0x0922 | 
| ESTADO_ATUAL     | 0x0924 | 


---

## 4. VARIAVEIS DE ESTADO (Bits Internos)

### 4.1 Estados da Maquina de Estados Principal

| Bit | Endereco | Nome | Descricao |
|-----|----------|------|-----------|
| M000 | 0x0300 | ST_IDLE | Maquina parada, aguardando |
| M001 | 0x0301 | ST_AGUARDA_DIRECAO | Aguardando pedal para definir sentido |
| M002 | 0x0302 | ST_DOBRANDO | Executando dobra (motor ligado) |
| M003 | 0x0303 | ST_RETORNANDO | Retornando para posicao zero |
| M004 | 0x0304 | ST_AGUARDA_PROXIMA | Aguardando pedal para proxima dobra |
| M005 | 0x0305 | ST_COMPLETO | Sequencia de 3 dobras completa |
| M006 | 0x0306 | ST_EMERGENCIA | Emergencia ativa |
| M007 | 0x0307 | ST_MANUAL | Modo manual ativo |

### 4.2 Bits de Controle

| Bit | Endereco | Nome | Descricao |
|-----|----------|------|-----------|
| B000 | 0x0380 | DIR_AVANCO | Direcao definida = Avanco (CCW) |
| B001 | 0x0381 | DIR_RECUO | Direcao definida = Recuo (CW) |
| B002 | 0x0382 | MODO_AUTO | Modo automatico ativo |
| B003 | 0x0383 | MODO_MANUAL | Modo manual ativo |
| B004 | 0x0384 | PEDAL_SEGURA | Exige segurar pedal para movimento |
| B005 | 0x0385 | NA_POSICAO_ZERO | Encoder esta na posicao zero |
| B006 | 0x0386 | ATINGIU_ANGULO | Atingiu angulo alvo |
| B007 | 0x0387 | HABILITADO | Sistema habilitado (sem emergencia) |

### 4.3 Bits Auxiliares (Deteccao de Borda)

| Bit | Endereco | Nome | Descricao |
|-----|----------|------|-----------|
| AUX00 | 0x0390 | PEDAL_AV_ANT | Estado anterior do pedal avanco |
| AUX01 | 0x0391 | PEDAL_RC_ANT | Estado anterior do pedal recuo |
| AUX02 | 0x0392 | BORDA_AV | Borda de subida pedal avanco |
| AUX03 | 0x0393 | BORDA_RC | Borda de subida pedal recuo |
| AUX04 | 0x0394 | SENSOR_ZERO_ANT | Estado anterior sensor zero |
| AUX05 | 0x0395 | BORDA_ZERO | Borda de subida sensor zero |

---

## 5. MAQUINA DE ESTADOS

### 5.1 Diagrama de Estados

```
                            +-----------------+
                            |                 |
                   +------->|  ST_EMERGENCIA  |<------- E6=OFF (emergencia)
                   |        |     (M006)      |         a qualquer momento
                   |        +--------+--------+
                   |                 |
                   |                 | E6=ON (reset emergencia)
                   |                 v
+------------------+        +--------+--------+
|                  |        |                 |
|    POWER ON      +------->|    ST_IDLE      |<------+
|                  |        |     (M000)      |       |
+------------------+        +--------+--------+       |
                                     |                |
                            Pedal    |                |
                            pressionado              |
                                     v                |
                            +--------+--------+       |
                            |                 |       |
                            | ST_AGUARDA_DIR  |       |
                            |     (M001)      |       |
                            +--------+--------+       |
                                     |                |
                            Pedal    |                |
                            define   |                |
                            direcao  v                |
                            +--------+--------+       |
                            |                 |       |
                            |   ST_DOBRANDO   |-------+ Solta pedal
                            |     (M002)      |       | (modo SEGURA)
                            +--------+--------+       |
                                     |                |
                            Atingiu  |                |
                            angulo   v                |
                            +--------+--------+       |
                            |                 |       |
                            | ST_RETORNANDO   |       |
                            |     (M003)      |       |
                            +--------+--------+       |
                                     |                |
                            Chegou   |                |
                            no zero  v                |
                            +--------+--------+       |
                            |                 |       |
                            | ST_AGUARDA_PROX |       |
                            |     (M004)      |       |
                            +--------+--------+       |
                                     |                |
                     +---------------+---------------+|
                     |                               ||
              Dobra < 3           Dobra = 3         ||
              Pedal novo          Completo          ||
                     |                               ||
                     v                               v|
            +--------+--------+             +--------+--------+
            |                 |             |                 |
            |   ST_DOBRANDO   |             |   ST_COMPLETO   |
            |     (M002)      |             |     (M005)      |
            +--------+--------+             +--------+--------+
                                                     |
                                            Reset ou |
                                            novo ciclo
                                                     |
                                                     v
                                            +--------+--------+
                                            |                 |
                                            |    ST_IDLE      |
                                            |     (M000)      |
                                            +-----------------+
```

### 5.2 Descricao dos Estados

#### ST_IDLE (M000) - Maquina Parada
- **Condicao de Entrada:** Power-on, reset, ou apos ciclo completo
- **Acoes:**
  - Motor desligado (S0=OFF, S1=OFF)
  - LEDs de dobra apagados
  - Aguarda primeiro pedal
- **Transicoes:**
  - `E2=ON E E0=ON` (pedal avanco E na posicao zero) -> ST_AGUARDA_DIRECAO
  - `E4=ON E E0=ON` (pedal recuo E na posicao zero) -> ST_AGUARDA_DIRECAO
  - `E6=OFF` (emergencia) -> ST_EMERGENCIA
- **IMPORTANTE:** So aceita pedal se sensor de posicao zero (E0) estiver ativo!

#### ST_AGUARDA_DIRECAO (M001) - Definindo Sentido
- **Condicao de Entrada:** Primeiro pedal pressionado
- **Acoes:**
  - Se E2 ativo: DIR_AVANCO = ON
  - Se E4 ativo: DIR_RECUO = ON
  - Carrega ANGULO_1 -> ANGULO_ALVO
  - DOBRA_ATUAL = 1
- **Transicoes:**
  - Direcao definida -> ST_DOBRANDO

#### ST_DOBRANDO (M002) - Executando Dobra
- **Condicao de Entrada:** Direcao definida e pedal correto pressionado
- **Acoes:**
  - Se DIR_AVANCO: S0=ON (motor CCW)
  - Se DIR_RECUO: S1=ON (motor CW)
  - Monitora encoder vs ANGULO_ALVO
  - Se PEDAL_SEGURA=ON e pedal solto: para motor
- **Transicoes:**
  - `ENCODER >= ANGULO_ALVO` -> ST_RETORNANDO
  - Pedal solto (modo SEGURA) -> ST_IDLE
  - `E6=OFF` (emergencia) -> ST_EMERGENCIA

#### ST_RETORNANDO (M003) - Voltando para Zero
- **Condicao de Entrada:** Angulo atingido
- **Acoes:**
  - Motor gira sentido oposto ao da dobra
  - Se dobrou em avanco: S1=ON (recua)
  - Se dobrou em recuo: S0=ON (avanca)
  - Monitora sensor E0 (posicao zero)
- **Transicoes:**
  - `E0=ON` (sensor zero) -> ST_AGUARDA_PROXIMA
  - `E6=OFF` -> ST_EMERGENCIA

#### ST_AGUARDA_PROXIMA (M004) - Aguardando Proxima Dobra
- **Condicao de Entrada:** Chegou na posicao zero
- **Acoes:**
  - Motor desligado
  - Incrementa DOBRA_ATUAL
  - Carrega proximo angulo
  - LED da proxima dobra acende
- **Transicoes:**
  - `DOBRA_ATUAL > 3` -> ST_COMPLETO
  - Pedal correto pressionado -> ST_DOBRANDO

#### ST_COMPLETO (M005) - Ciclo Finalizado
- **Condicao de Entrada:** 3 dobras executadas
- **Acoes:**
  - Incrementa CONTADOR_PECAS
  - Todos LEDs piscam (opcional)
  - Motor desligado
- **Transicoes:**
  - Timeout ou pedal parada -> ST_IDLE

#### ST_EMERGENCIA (M006) - Parada de Emergencia
- **Condicao de Entrada:** E6=OFF (contato NF aberto)
- **Acoes:**
  - Motor IMEDIATAMENTE desligado (S0=OFF, S1=OFF)
  - Inversor desabilitado (S2=OFF)
  - Sistema travado
- **Transicoes:**
  - `E6=ON` (emergencia resolvida) -> ST_IDLE

#### ST_MANUAL (M007) - Modo Manual
- **Condicao de Entrada:** Chave de modo em manual
- **Acoes:**
  - Motor gira enquanto pedal pressionado
  - Sem controle de angulo
  - Apenas velocidade classe 1 (5 RPM)
- **Transicoes:**
  - Pedal solto -> para motor
  - Chave em auto -> ST_IDLE

---

## 6. TABELA DE VALORES POR ESTADO (PARA IMPLEMENTACAO COM CALL)

Esta secao mostra **exatamente** quais saidas e variaveis devem estar ativas em cada estado.
Use esta tabela para implementar cada rotina ROTx no ladder.

### 6.1 Estrutura do Programa Principal

```
PRINCIPAL.LAD:
================================================================================
| E6=OFF |----( SETR M006 )----| CALL ROT_EMERGENCIA |   ; Emergencia sempre!
|---------+--------------------+-----------------------|
          |
| M000 |-------| CALL ROT0_IDLE |                       ; Se estado IDLE
|------+-------+----------------|
          |
| M001 |-------| CALL ROT1_AGUARDA_DIR |                ; Se aguardando direcao
|------+-------+------------------------|
          |
| M002 |-------| CALL ROT2_DOBRANDO |                   ; Se dobrando
|------+-------+--------------------|
          |
| M003 |-------| CALL ROT3_RETORNANDO |                 ; Se retornando
|------+-------+----------------------|
          |
| M004 |-------| CALL ROT4_AGUARDA_PROX |               ; Se aguardando proxima
|------+-------+------------------------|
          |
| M005 |-------| CALL ROT5_COMPLETO |                   ; Se ciclo completo
|------+-------+--------------------|
          |
| M006 |-------| CALL ROT6_EMERGENCIA |                 ; Se emergencia
|------+-------+----------------------|
          |
| M007 |-------| CALL ROT7_MANUAL |                     ; Se modo manual
|------+-------+-------------------|
================================================================================
```

### 6.2 Tabela Completa de Saidas por Estado

| Saida/Variavel | M000 IDLE | M001 AG_DIR | M002 DOBRA | M003 RETORNA | M004 AG_PROX | M005 COMPL | M006 EMERG | M007 MANUAL |
|----------------|:---------:|:-----------:|:----------:|:------------:|:------------:|:----------:|:----------:|:-----------:|
| **S0 (Motor CCW)** | OFF | OFF | ON* | ON** | OFF | OFF | **OFF!** | ON*** |
| **S1 (Motor CW)** | OFF | OFF | ON* | ON** | OFF | OFF | **OFF!** | ON*** |
| **S2 (Inversor)** | OFF | OFF | ON | ON | OFF | OFF | **OFF!** | ON |
| **S4 (LED Dobra1)** | OFF | ON**** | ON**** | ON**** | ON**** | PISCA | OFF | OFF |
| **S5 (LED Dobra2)** | OFF | ON**** | ON**** | ON**** | ON**** | PISCA | OFF | OFF |
| **S6 (LED Dobra3)** | OFF | ON**** | ON**** | ON**** | ON**** | PISCA | OFF | OFF |

**Legenda:**
- `*` S0 se DIR_AVANCO, S1 se DIR_RECUO (e pedal correto se PEDAL_SEGURA)
- `**` Sentido OPOSTO: S1 se dobrou em avanco, S0 se dobrou em recuo
- `***` Depende do pedal: S0 se E2, S1 se E4
- `****` Conforme DOBRA_ATUAL: S4 se dobra=1, S5 se dobra=2, S6 se dobra=3

### 6.3 Tabela de Bits de Controle por Estado

| Bit | M000 IDLE | M001 AG_DIR | M002 DOBRA | M003 RETORNA | M004 AG_PROX | M005 COMPL | M006 EMERG | M007 MANUAL |
|-----|:---------:|:-----------:|:----------:|:------------:|:------------:|:----------:|:----------:|:-----------:|
| **B000 (DIR_AV)** | OFF | SET* | HOLD | HOLD | HOLD | OFF | OFF | - |
| **B001 (DIR_RC)** | OFF | SET* | HOLD | HOLD | HOLD | OFF | OFF | - |
| **B006 (ATINGIU)** | OFF | OFF | SET** | OFF | OFF | OFF | OFF | OFF |
| **B007 (HABILIT)** | ON | ON | ON | ON | ON | ON | **OFF** | ON |

**Legenda:**
- `SET*` Setado conforme pedal pressionado (E2->B000, E4->B001)
- `SET**` Setado quando ENCODER >= ANGULO_ALVO
- `HOLD` Mantem valor anterior

### 6.4 Tabela de Registros por Estado

| Registro | M000 IDLE | M001 AG_DIR | M002 DOBRA | M003 RETORNA | M004 AG_PROX | M005 COMPL | M006 EMERG | M007 MANUAL |
|----------|:---------:|:-----------:|:----------:|:------------:|:------------:|:----------:|:----------:|:-----------:|
| **DOBRA_ATUAL (0901)** | 1 | 1 | HOLD | HOLD | +1 | HOLD | HOLD | - |
| **ANGULO_ALVO (0942)** | - | LOAD* | HOLD | - | LOAD* | - | - | - |
| **CONTADOR (0902)** | HOLD | HOLD | HOLD | HOLD | HOLD | +1 | HOLD | HOLD |
| **VEL_INVER (06E0)** | 527 | 527 | VEL** | VEL** | 527 | 527 | 0 | 527 |

**Legenda:**
- `LOAD*` Carrega ANGULOx conforme DOBRA_ATUAL
- `VEL**` Conforme VELOCIDADE_ATUAL (527/1055/1583)

### 6.5 Detalhamento de Cada Rotina (ROTx)

---

#### ROT0_IDLE (Quando M000=ON)

```
ACOES NA ENTRADA:
-----------------
S0 = OFF          ; Motor avanco desligado
S1 = OFF          ; Motor recuo desligado
S2 = OFF          ; Inversor desabilitado
S4 = OFF          ; LED dobra 1 apagado
S5 = OFF          ; LED dobra 2 apagado
S6 = OFF          ; LED dobra 3 apagado
B000 = OFF        ; Reset direcao avanco
B001 = OFF        ; Reset direcao recuo
B006 = OFF        ; Reset flag atingiu angulo
DOBRA_ATUAL = 1   ; Reinicia contador de dobra
VEL_INVERSOR = 527 ; Velocidade minima (standby)

TRANSICOES:
-----------
; *** IMPORTANTE: SO ACEITA PEDAL SE ESTIVER NA POSICAO ZERO! ***

SE E2=ON E E0=ON ENTAO:   ; Pedal avanco E sensor zero ativo
   M000 = OFF
   M001 = ON
   B000 = ON              ; Define direcao avanco

SE E4=ON E E0=ON ENTAO:   ; Pedal recuo E sensor zero ativo
   M000 = OFF
   M001 = ON
   B001 = ON              ; Define direcao recuo

; Se pedal pressionado mas NAO esta no zero -> ignora (nao faz nada)
; Isso evita iniciar ciclo com maquina fora de posicao

SE E6=OFF ENTAO:
   M000 = OFF
   M006 = ON      ; Vai para emergencia
```

---

#### ROT1_AGUARDA_DIR (Quando M001=ON)

```
ACOES NA ENTRADA:
-----------------
S0 = OFF          ; Motor ainda desligado
S1 = OFF          ; Motor ainda desligado
S2 = OFF          ; Inversor ainda desabilitado
S4 = (DOBRA=1)    ; LED conforme dobra atual
S5 = (DOBRA=2)
S6 = (DOBRA=3)

; Carrega angulo alvo conforme dobra atual:
SE DOBRA_ATUAL=1 ENTAO ANGULO_ALVO = ANGULO_1
SE DOBRA_ATUAL=2 ENTAO ANGULO_ALVO = ANGULO_2
SE DOBRA_ATUAL=3 ENTAO ANGULO_ALVO = ANGULO_3

TRANSICOES:
-----------
SE B000=ON E E2=ON ENTAO:  ; Direcao avanco e pedal avanco
   M001 = OFF
   M002 = ON               ; Vai para dobrando

SE B001=ON E E4=ON ENTAO:  ; Direcao recuo e pedal recuo
   M001 = OFF
   M002 = ON               ; Vai para dobrando

SE E6=OFF ENTAO:
   M001 = OFF
   M006 = ON               ; Vai para emergencia
```

---

#### ROT2_DOBRANDO (Quando M002=ON)

```
ACOES CONTINUAS:
----------------
; Controle do motor conforme direcao e modo SEGURA:

SE B000=ON ENTAO:                    ; Direcao avanco
   SE B004=OFF ENTAO:                ; Modo normal (pisadinha)
      S0 = ON
      S1 = OFF
   SENAO SE B004=ON E E2=ON ENTAO:   ; Modo SEGURA com pedal
      S0 = ON
      S1 = OFF
   SENAO:                            ; Modo SEGURA sem pedal
      S0 = OFF
      S1 = OFF
      M002 = OFF
      M000 = ON                      ; Volta para IDLE

SE B001=ON ENTAO:                    ; Direcao recuo
   SE B004=OFF ENTAO:                ; Modo normal (pisadinha)
      S0 = OFF
      S1 = ON
   SENAO SE B004=ON E E4=ON ENTAO:   ; Modo SEGURA com pedal
      S0 = OFF
      S1 = ON
   SENAO:                            ; Modo SEGURA sem pedal
      S0 = OFF
      S1 = OFF
      M002 = OFF
      M000 = ON                      ; Volta para IDLE

S2 = ON                              ; Inversor habilitado
VEL_INVERSOR = (conforme VEL_ATUAL)  ; 527, 1055 ou 1583

; Comparacao de angulo:
SE ENCODER >= ANGULO_ALVO ENTAO:
   B006 = ON                         ; Seta flag atingiu

TRANSICOES:
-----------
SE B006=ON ENTAO:
   S0 = OFF
   S1 = OFF
   M002 = OFF
   M003 = ON                         ; Vai para retornando
   B006 = OFF                        ; Reset flag

SE E6=OFF ENTAO:
   S0 = OFF
   S1 = OFF
   M002 = OFF
   M006 = ON                         ; Vai para emergencia
```

---

#### ROT3_RETORNANDO (Quando M003=ON)

```
ACOES CONTINUAS:
----------------
; Motor gira no sentido OPOSTO ao da dobra:

SE B000=ON ENTAO:        ; Se dobrou em avanco
   S0 = OFF
   S1 = ON               ; Retorna com recuo

SE B001=ON ENTAO:        ; Se dobrou em recuo
   S0 = ON               ; Retorna com avanco
   S1 = OFF

S2 = ON                  ; Inversor habilitado
VEL_INVERSOR = 527       ; Velocidade baixa para retorno (seguranca)

TRANSICOES:
-----------
SE E0=ON ENTAO:          ; Sensor de posicao zero ativo
   S0 = OFF
   S1 = OFF
   ENCODER = 0           ; Zera encoder (opcional)
   M003 = OFF
   M004 = ON             ; Vai para aguarda proxima

SE E6=OFF ENTAO:
   S0 = OFF
   S1 = OFF
   M003 = OFF
   M006 = ON             ; Vai para emergencia
```

---

#### ROT4_AGUARDA_PROX (Quando M004=ON)

```
ACOES NA ENTRADA (executar apenas 1 vez):
-----------------------------------------
S0 = OFF
S1 = OFF
S2 = OFF
DOBRA_ATUAL = DOBRA_ATUAL + 1    ; Incrementa dobra

; Atualiza LEDs:
S4 = (DOBRA_ATUAL = 1)
S5 = (DOBRA_ATUAL = 2)
S6 = (DOBRA_ATUAL = 3)

; Carrega proximo angulo:
SE DOBRA_ATUAL=2 ENTAO ANGULO_ALVO = ANGULO_2
SE DOBRA_ATUAL=3 ENTAO ANGULO_ALVO = ANGULO_3

TRANSICOES:
-----------
SE DOBRA_ATUAL > 3 ENTAO:
   M004 = OFF
   M005 = ON             ; Vai para completo

SE B000=ON E E2=ON ENTAO:    ; Pedal avanco para continuar
   M004 = OFF
   M002 = ON             ; Volta para dobrando

SE B001=ON E E4=ON ENTAO:    ; Pedal recuo para continuar
   M004 = OFF
   M002 = ON             ; Volta para dobrando

SE E6=OFF ENTAO:
   M004 = OFF
   M006 = ON             ; Vai para emergencia
```

---

#### ROT5_COMPLETO (Quando M005=ON)

```
ACOES NA ENTRADA (executar apenas 1 vez):
-----------------------------------------
S0 = OFF
S1 = OFF
S2 = OFF
CONTADOR_PECAS = CONTADOR_PECAS + 1    ; Incrementa producao

; LEDs piscam (opcional):
; Usar timer para alternar S4, S5, S6

TRANSICOES:
-----------
; Timer de 2 segundos:
SE TIMER_COMPLETO >= 2000ms ENTAO:
   M005 = OFF
   M000 = ON             ; Volta para IDLE
   DOBRA_ATUAL = 1       ; Reinicia dobra

SE E3=ON ENTAO:          ; Pedal parada para reiniciar rapido
   M005 = OFF
   M000 = ON
   DOBRA_ATUAL = 1

SE E6=OFF ENTAO:
   M005 = OFF
   M006 = ON
```

---

#### ROT6_EMERGENCIA (Quando M006=ON)

```
ACOES IMEDIATAS (PRIORIDADE MAXIMA):
------------------------------------
S0 = OFF      ; DESLIGA MOTOR AVANCO IMEDIATAMENTE!
S1 = OFF      ; DESLIGA MOTOR RECUO IMEDIATAMENTE!
S2 = OFF      ; DESLIGA INVERSOR!
S4 = OFF      ; Apaga LED 1
S5 = OFF      ; Apaga LED 2
S6 = OFF      ; Apaga LED 3
B007 = OFF    ; Sistema NAO habilitado

; Opcional: LED de emergencia piscando
; S3 = PISCA (toggle a cada 500ms)

TRANSICOES:
-----------
SE E6=ON ENTAO:          ; Emergencia resolvida (botao destravado)
   M006 = OFF
   M000 = ON             ; Volta para IDLE
   DOBRA_ATUAL = 1       ; Reinicia sequencia
   B000 = OFF            ; Reset direcao
   B001 = OFF
   B007 = ON             ; Sistema habilitado novamente
```

---

#### ROT7_MANUAL (Quando M007=ON)

```
ACOES CONTINUAS:
----------------
VEL_INVERSOR = 527       ; Sempre velocidade minima em manual

; Motor gira SOMENTE enquanto pedal pressionado:
SE E2=ON ENTAO:
   S0 = ON
   S1 = OFF
   S2 = ON
SENAO SE E4=ON ENTAO:
   S0 = OFF
   S1 = ON
   S2 = ON
SENAO:
   S0 = OFF
   S1 = OFF
   S2 = OFF

; Nao ha controle de angulo em modo manual
; LEDs apagados
S4 = OFF
S5 = OFF
S6 = OFF

TRANSICOES:
-----------
SE CHAVE_AUTO=ON ENTAO:  ; Chave seletora muda para auto
   M007 = OFF
   M000 = ON             ; Vai para IDLE

SE E6=OFF ENTAO:
   S0 = OFF
   S1 = OFF
   M007 = OFF
   M006 = ON             ; Vai para emergencia
```

---

### 6.6 Resumo das Transicoes de Estado

```
DIAGRAMA DE TRANSICOES:
=======================

                    E6=OFF (qualquer momento)
                           |
                           v
+-------+  E2/E4   +-------+  pedal ok  +-------+  ENC>=ALV  +-------+
| IDLE  |--------->| AG_DIR|---------->| DOBRA |---------->| RETOR |
| M000  |          | M001  |           | M002  |           | M003  |
+-------+          +-------+           +-------+           +-------+
    ^                                      |                   |
    |                                      | solta pedal       | E0=ON
    |                                      | (modo SEGURA)     |
    |                                      v                   v
    |                                  +-------+ DOBRA<=3  +-------+
    +----------------------------------| AG_PRX|<----------| RETOR |
    |                                  | M004  |           | M003  |
    |                                  +-------+           +-------+
    |                                      |
    |                                      | DOBRA>3
    |         timeout 2s                   v
    +----------------------------------+-------+
                                       | COMPL |
                                       | M005  |
                                       +-------+

                    +-------+
                    | EMERG |  <-- E6=OFF de qualquer estado
                    | M006  |
                    +-------+
                        |
                        | E6=ON
                        v
                    +-------+
                    | IDLE  |
                    | M000  |
                    +-------+
```

---

## 7. REGRAS DE SEGURANCA

### 7.1 Condicoes para Iniciar Ciclo Automatico

O modo automatico **SO PODE SER INICIADO** se **TODAS** as condicoes abaixo forem verdadeiras:

| Condicao | Entrada | Estado Requerido | Motivo |
|----------|---------|------------------|--------|
| Posicao Zero | E0 | **ON** | Maquina deve estar na referencia |
| Emergencia | E6 | **ON** (NF fechado) | Sem emergencia ativa |
| Seguranca | E5 | **ON** (NF fechado) | Protecoes OK |

```
LOGICA DE PERMISSAO:
====================
PERMITE_INICIO = E0 AND E6 AND E5

SE pedal_pressionado E NAO PERMITE_INICIO ENTAO:
   -> Ignora pedal (nao faz nada)
   -> Opcional: piscar LED de erro
```

### 7.2 Por que exigir posicao zero?

1. **Seguranca:** Garante que o operador sabe exatamente onde a maquina esta
2. **Precisao:** O encoder e zerado na posicao de referencia
3. **Previsibilidade:** A dobra sempre comeca do mesmo ponto
4. **Protecao:** Evita iniciar com peca ja parcialmente dobrada

### 7.3 O que fazer se NAO estiver no zero?

Se o operador pressionar o pedal mas E0=OFF:
1. **Nao inicia** o ciclo automatico
2. Deve usar **modo MANUAL** para posicionar a maquina
3. Ao chegar no zero (E0=ON), pode iniciar ciclo automatico

---

## 8. OPCOES DE OPERACAO

### 8.1 Modo PEDAL_SEGURA (B004)

Quando `PEDAL_SEGURA = ON`:
- O motor **so gira enquanto o pedal estiver pressionado**
- Soltando o pedal, o motor para imediatamente
- Mais seguro para operadores inexperientes

Quando `PEDAL_SEGURA = OFF`:
- Uma **pisadinha** inicia o movimento
- O motor continua ate atingir o angulo
- Mais comodo para operadores experientes

### 8.2 Modo MANUAL (B003)

Quando `MODO_MANUAL = ON`:
- Nao ha controle de angulo
- Motor gira enquanto pedal pressionado
- Velocidade fixa em 5 RPM (classe 1)
- Util para ajustes e manutencao

---

## 9. LOGICA LADDER SIMPLIFICADA

### 9.1 Rotina Principal (PRINCIPAL.LAD)

```
================================================================================
LINHA 1: DETECCAO DE EMERGENCIA (PRIORIDADE MAXIMA)
================================================================================
    +----[/]----+----( )----+
    |    E6     |   M006    |  Se E6=OFF (emergencia) -> Seta ST_EMERGENCIA
    +-----------+-----------+

    +----[ ]----+----(R)----+
    |   M006    |    S0     |  Se em emergencia -> Reset S0 (motor avanco)
    +-----------+-----------+

    +----[ ]----+----(R)----+
    |   M006    |    S1     |  Se em emergencia -> Reset S1 (motor recuo)
    +-----------+-----------+

    +----[ ]----+----(R)----+
    |   M006    |    S2     |  Se em emergencia -> Reset S2 (inversor)
    +-----------+-----------+

================================================================================
LINHA 2: RESET DE EMERGENCIA -> RETORNA A IDLE
================================================================================
    +----[ ]----+----[/]----+----(R)----+
    |   M006    |    E6     |   M006    |  Se estava em emergencia E E6=ON
    +-----------+-----------+-----------+  -> Reset emergencia

    +----[ ]----+----[ ]----+----( )----+
    |   M006    |    E6     |   M000    |  -> Seta IDLE
    +-----------+-----------+-----------+

================================================================================
LINHA 3: ESTADO IDLE - AGUARDA PRIMEIRO PEDAL
================================================================================
    +----[ ]----+----[ ]----+----( )----+
    |   M000    |    E2     |   M001    |  Se IDLE e pedal avanco
    |           |           |  B000=1   |  -> ST_AGUARDA_DIR, direcao avanco
    +-----------+-----------+-----------+

    +----[ ]----+----[ ]----+----( )----+
    |   M000    |    E4     |   M001    |  Se IDLE e pedal recuo
    |           |           |  B001=1   |  -> ST_AGUARDA_DIR, direcao recuo
    +-----------+-----------+-----------+

================================================================================
LINHA 4: CARREGA ANGULO ALVO CONFORME DOBRA ATUAL
================================================================================
    +----[ ]----+----[=]----+----[MOV]--+
    |   M001    | DOBRA=1   | ANG1->ALV |  Se dobra 1: carrega angulo 1
    +-----------+-----------+-----------+

    +----[ ]----+----[=]----+----[MOV]--+
    |   M001    | DOBRA=2   | ANG2->ALV |  Se dobra 2: carrega angulo 2
    +-----------+-----------+-----------+

    +----[ ]----+----[=]----+----[MOV]--+
    |   M001    | DOBRA=3   | ANG3->ALV |  Se dobra 3: carrega angulo 3
    +-----------+-----------+-----------+

================================================================================
LINHA 5: INICIA DOBRA - VERIFICA CONDICOES
================================================================================
    +----[ ]----+----[ ]----+----[ ]----+----( )----+
    |   M001    |   B000    |    E2     |   M002    |  Se direcao avanco e pedal
    +-----------+-----------+-----------+-----------+  avanco -> ST_DOBRANDO

    +----[ ]----+----[ ]----+----[ ]----+----( )----+
    |   M001    |   B001    |    E4     |   M002    |  Se direcao recuo e pedal
    +-----------+-----------+-----------+-----------+  recuo -> ST_DOBRANDO

================================================================================
LINHA 6: CONTROLE DO MOTOR DURANTE DOBRA
================================================================================
    +----[ ]----+----[ ]----+----[/]----+----( )----+
    |   M002    |   B000    |   B004    |    S0     |  Se dobrando em avanco
    +-----------+-----------+-----------+-----------+  sem modo SEGURA -> S0 ON

    +----[ ]----+----[ ]----+----[ ]----+----[ ]----+----( )----+
    |   M002    |   B000    |   B004    |    E2     |    S0     |  Se dobrando avanco
    +-----------+-----------+-----------+-----------+-----------+  com SEGURA e pedal -> S0

    (Mesma logica para recuo com S1)

================================================================================
LINHA 7: COMPARACAO ENCODER VS ANGULO ALVO
================================================================================
    +----[ ]----+----[>=]---+----( )----+
    |   M002    | ENC>=ALV  |   B006    |  Se encoder >= alvo -> ATINGIU_ANGULO
    +-----------+-----------+-----------+

    +----[ ]----+----[ ]----+----(R)----+----( )----+
    |   M002    |   B006    |    S0     |   M003    |  Se atingiu -> para motor
    |           |           |    S1     |           |  -> ST_RETORNANDO
    +-----------+-----------+-----------+-----------+

================================================================================
LINHA 8: RETORNO PARA POSICAO ZERO
================================================================================
    +----[ ]----+----[ ]----+----( )----+
    |   M003    |   B000    |    S1     |  Se retornando de avanco -> motor recuo
    +-----------+-----------+-----------+

    +----[ ]----+----[ ]----+----( )----+
    |   M003    |   B001    |    S0     |  Se retornando de recuo -> motor avanco
    +-----------+-----------+-----------+

================================================================================
LINHA 9: DETECTA CHEGADA NA POSICAO ZERO
================================================================================
    +----[ ]----+----[ ]----+----(R)----+----( )----+
    |   M003    |    E0     |   S0,S1   |   M004    |  Se sensor zero ativo
    +-----------+-----------+-----------+-----------+  -> para motor, ST_AGUARDA_PROX

================================================================================
LINHA 10: INCREMENTA DOBRA E VERIFICA FIM
================================================================================
    +----[ ]----+----[ADD]--+
    |   M004    | DOBRA+1   |  Incrementa numero da dobra
    +-----------+-----------+

    +----[ ]----+----[>]----+----( )----+
    |   M004    | DOBRA>3   |   M005    |  Se dobra > 3 -> ST_COMPLETO
    +-----------+-----------+-----------+

    +----[ ]----+----[<=]---+----( )----+
    |   M004    | DOBRA<=3  |   M001    |  Se dobra <= 3 -> volta para aguardar pedal
    +-----------+-----------+-----------+

================================================================================
LINHA 11: CICLO COMPLETO
================================================================================
    +----[ ]----+----[ADD]--+
    |   M005    | PECAS+1   |  Incrementa contador de pecas
    +-----------+-----------+

    +----[ ]----+----[TMR]--+----( )----+
    |   M005    |  T001=2s  |   M000    |  Apos 2 segundos -> volta para IDLE
    +-----------+-----------+-----------+

================================================================================
LINHA 12: LEDS DE INDICACAO
================================================================================
    +----[=]----+----( )----+
    | DOBRA=1   |    S4     |  LED dobra 1
    +-----------+-----------+

    +----[=]----+----( )----+
    | DOBRA=2   |    S5     |  LED dobra 2
    +-----------+-----------+

    +----[=]----+----( )----+
    | DOBRA=3   |    S6     |  LED dobra 3
    +-----------+-----------+

================================================================================
LINHA 13: VELOCIDADE DO INVERSOR
================================================================================
    +----[=]----+----[MOV]--+
    | VEL=1     | 527->06E0 |  Classe 1: 5 RPM
    +-----------+-----------+

    +----[=]----+----[MOV]--+
    | VEL=2     | 1055->06E0|  Classe 2: 10 RPM
    +-----------+-----------+

    +----[=]----+----[MOV]--+
    | VEL=3     | 1583->06E0|  Classe 3: 15 RPM
    +-----------+-----------+

================================================================================
LINHA 14: HABILITACAO DO INVERSOR
================================================================================
    +----[/]----+----[ ]----+----( )----+
    |   M006    |   ANY_S   |    S2     |  Se nao em emergencia e algum motor
    +-----------+-----------+-----------+  ligado -> habilita inversor

```

---

## 10. TABELA DE INSTRUCOES ATOS

### 10.1 Instrucoes Usadas

| Instrucao | Codigo | Descricao | Exemplo |
|-----------|--------|-----------|---------|
| OUT | -008 | Saida simples | OUT S0 |
| SETR | 0043 | Set/Reset bit | SETR M000 |
| MOVK | 0029 | Move constante | MOVK 0x06E0, 527 |
| MOV | 0028 | Move registro | MOV 0x0840, 0x0942 |
| CMP | 0010 | Compara registros | CMP 0x04D6, 0x0942 |
| ADD | - | Adicao | ADD DOBRA, 1 |
| TMR | 0056 | Temporizador | TMR 0005 (500ms) |
| CNT | 0013 | Contador | CNT 0015 |

### 10.2 Formato de Condicoes no Ladder Atos

```
{tipo;posicao;endereco;-1;branch;-1;-1;00}

tipo: 0 = contato NA, 1 = contato NF
posicao: posicao horizontal na linha
endereco: endereco hex do bit/registro
branch: numero do branch para conexao OR
```

---

## 11. SEQUENCIA DE INICIALIZACAO

### 11.1 Power-On

1. **Reset de todos os estados:**
   - M000-M007 = OFF
   - B000-B007 = OFF
   - S0-S7 = OFF

2. **Inicializacao de registros:**
   - DOBRA_ATUAL = 1
   - VELOCIDADE_ATUAL = 1 (5 RPM)
   - ANGULO_1 = 900 (90 graus)
   - ANGULO_2 = 900 (90 graus)
   - ANGULO_3 = 900 (90 graus)

3. **Verificacao de seguranca:**
   - Se E6 = OFF -> ST_EMERGENCIA
   - Se E6 = ON -> ST_IDLE

4. **Zerar encoder:**
   - ENCODER_MSW = 0
   - ENCODER_LSW = 0

---

## 12. COMUNICACAO MODBUS

### 12.1 Registros Acessiveis via Modbus

| Registro | Endereco | R/W | Descricao |
|----------|----------|-----|-----------|
| ANGULO_1 | 0x0840 | R/W | Setpoint angulo dobra 1 |
| ANGULO_2 | 0x0844 | R/W | Setpoint angulo dobra 2 |
| ANGULO_3 | 0x0848 | R/W | Setpoint angulo dobra 3 |
| ENCODER | 0x04D6 | R | Posicao atual encoder |
| DOBRA_ATUAL | 0x0901 | R | Numero da dobra atual |
| VELOCIDADE | 0x0900 | R/W | Classe de velocidade |
| CONTADOR_PECAS | 0x0902 | R | Pecas produzidas |

### 12.2 Bits Acessiveis via Modbus

| Coil | Endereco | R/W | Descricao |
|------|----------|-----|-----------|
| S0-S7 | 0x0180-0x0187 | R | Status saidas digitais |
| E0-E7 | 0x0100-0x0107 | R | Status entradas digitais |
| M000-M007 | 0x0300-0x0307 | R | Estados da maquina |
| B000-B007 | 0x0380-0x0387 | R/W | Bits de controle |

### 12.3 Configuracao Modbus

```
Porta: RS485-B
Baudrate: 57600
Paridade: None
Stop bits: 1
Slave ID: 1 (configuravel em 0x1988)
Estado 0x00BE: DEVE estar ON para Modbus funcionar
```

---

## 13. TESTE E VALIDACAO

### 13.1 Checklist de Testes

- [ ] **Emergencia:** E6 aberto para motor imediatamente
- [ ] **Sensor zero:** E0 detecta posicao corretamente
- [ ] **Bloqueio fora do zero:** Pedal NAO funciona se E0=OFF
- [ ] **Pedal avanco:** E2 inicia movimento CCW (com E0=ON)
- [ ] **Pedal recuo:** E4 inicia movimento CW (com E0=ON)
- [ ] **Encoder:** Leitura correta da posicao angular
- [ ] **Angulo alvo:** Motor para no angulo programado
- [ ] **Retorno:** Motor retorna para posicao zero
- [ ] **Sequencia:** Dobras 1->2->3 executam corretamente
- [ ] **LEDs:** Indicam dobra atual corretamente
- [ ] **Velocidade:** Inversor responde aos 3 valores
- [ ] **Modbus:** Leitura/escrita de registros funciona
- [ ] **Modo SEGURA:** Motor para ao soltar pedal

### 13.2 Procedimento de Teste

1. **Ligar com E6 desconectado** -> deve ir para ST_EMERGENCIA
2. **Conectar E6** -> deve ir para ST_IDLE
3. **Mover maquina para FORA do zero (E0=OFF)**
4. **Pisar E2** -> NAO deve fazer nada (bloqueado!)
5. **Usar modo MANUAL para voltar ao zero (E0=ON)**
6. **Pisar E2** -> agora deve avancar ate angulo
7. **Verificar retorno** -> deve voltar para zero automaticamente
8. **Pisar E2 novamente** -> executa dobra 2
9. **Repetir** -> dobra 3
10. **Verificar contador** -> deve incrementar

---

## 14. DIFERENCAS DO LADDER ORIGINAL

| Aspecto | Ladder Original | Ladder Novo |
|---------|-----------------|-------------|
| Linhas de codigo | ~150+ | ~50 |
| Sub-rotinas | ROT0-ROT9 | Apenas Principal |
| Estados | ~20 bits dispersos | 8 estados claros |
| Angulos | 6 (esq/dir) | 3 (simplificado) |
| Complexidade | Alta | Baixa |
| Manutencao | Dificil | Facil |
| Modo SEGURA | Nao tinha | Implementado |
| Emergencia | Complexa | Simples e direta |

---

## 15. PROXIMOS PASSOS

1. **Criar arquivo .LAD** com a logica descrita
2. **Compilar no WinSUP** (software Atos)
3. **Gerar arquivo .SUP** para upload
4. **Fazer backup** do ladder atual antes de sobrescrever
5. **Upload para CLP** via RS232
6. **Testes** conforme checklist
7. **Ajustes** conforme necessario

---

## APENDICE A: RESUMO RAPIDO DE ENDERECOS

```
ENTRADAS:
E0 (0x0100) = Sensor Zero
E2 (0x0102) = Pedal Avanco
E3 (0x0103) = Pedal Parada
E4 (0x0104) = Pedal Recuo
E5 (0x0105) = Seguranca
E6 (0x0106) = Emergencia (NF)

SAIDAS:
S0 (0x0180) = Motor Avanco (CCW)
S1 (0x0181) = Motor Recuo (CW)
S2 (0x0182) = Habilita Inversor
S4 (0x0184) = LED Dobra 1
S5 (0x0185) = LED Dobra 2
S6 (0x0186) = LED Dobra 3

ENCODER:
0x04D6/0x04D7 = Posicao (32-bit)

ANGULOS:
0x0840 = Angulo 1
0x0844 = Angulo 2
0x0848 = Angulo 3
0x0942 = Angulo Alvo

ESTADOS:
0x0300 = ST_IDLE
0x0301 = ST_AGUARDA_DIR
0x0302 = ST_DOBRANDO
0x0303 = ST_RETORNANDO
0x0304 = ST_AGUARDA_PROX
0x0305 = ST_COMPLETO
0x0306 = ST_EMERGENCIA
0x0307 = ST_MANUAL

CONTROLE:
0x0380 = Direcao Avanco
0x0381 = Direcao Recuo
0x0384 = Modo Segura Pedal
0x0900 = Velocidade (1,2,3)
0x0901 = Dobra Atual
0x0902 = Contador Pecas

INVERSOR (0x06E0):
527 = 5 RPM
1055 = 10 RPM
1583 = 15 RPM
```

---

**Documento gerado pelo Eng. Lucas William Junges**
**Data: 26/Nov/2025**
