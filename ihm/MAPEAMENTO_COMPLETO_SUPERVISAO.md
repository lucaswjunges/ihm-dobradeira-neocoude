# Mapeamento Completo: IHM Web com Supervisão Avançada

**Objetivo:** Transformar IHM web em sistema SCADA completo com capacidades superiores à IHM física

---

## 🎯 Filosofia da Solução

### Conceito Chave

**Toda comunicação CLP → IHM física gera um "shadow register" legível via Modbus**

```
┌─────────────────────────────────────────────────────────────┐
│  LADDER - Rotina de Sincronização (ROT05 ou nova ROT06)    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  IF (escreveu em 0FEC para IHM física) THEN                │
│     ├─ Copia para 0860 (tela atual)                        │
│     ├─ Atualiza timestamp                                  │
│     └─ Incrementa contador de comunicações                 │
│                                                             │
│  IF (escreveu dados de dobra) THEN                         │
│     └─ Copia para área de leitura Modbus                   │
│                                                             │
│  SEMPRE:                                                    │
│     ├─ Atualiza uptime                                     │
│     ├─ Espelha todas I/O                                   │
│     ├─ Calcula estatísticas                                │
│     └─ Gera flags de status                                │
└─────────────────────────────────────────────────────────────┘
```

---

## 📊 Área de Memória: Supervisão Avançada

### Bloco Base: 0x0800 - 0x08FF (2048-2303 decimal)

**256 registros dedicados para IHM web / SCADA**

| Endereço (Hex) | Dec  | Nome | Descrição | R/W |
|----------------|------|------|-----------|-----|
| **TELA E NAVEGAÇÃO** |||||
| 0x0860 | 2144 | SCREEN_CURRENT | Tela atual (0-10) | R |
| 0x0861 | 2145 | SCREEN_PREVIOUS | Tela anterior | R |
| 0x0862 | 2146 | SCREEN_CHANGES | Contador de mudanças de tela | R |
| 0x0863 | 2147 | SCREEN_TIMESTAMP_H | Timestamp MSW última mudança | R |
| 0x0864 | 2148 | SCREEN_TIMESTAMP_L | Timestamp LSW última mudança | R |
| **UPTIME E TEMPO** |||||
| 0x0865 | 2149 | UPTIME_HOURS_H | Horas ligado MSW (32-bit) | R |
| 0x0866 | 2150 | UPTIME_HOURS_L | Horas ligado LSW | R |
| 0x0867 | 2151 | UPTIME_MINUTES | Minutos (0-59) | R |
| 0x0868 | 2152 | UPTIME_SECONDS | Segundos (0-59) | R |
| 0x0869 | 2153 | POWER_ON_COUNT | Contador de power-ups | R |
| **PRODUÇÃO** |||||
| 0x086A | 2154 | PECAS_TOTAL_H | Total de peças MSW | R |
| 0x086B | 2155 | PECAS_TOTAL_L | Total de peças LSW | R |
| 0x086C | 2156 | PECAS_HOJE | Peças no turno atual | R |
| 0x086D | 2157 | DOBRAS_TOTAL_H | Total de dobras MSW | R |
| 0x086E | 2158 | DOBRAS_TOTAL_L | Total de dobras LSW | R |
| 0x086F | 2159 | DOBRAS_ATUAL | Dobras na peça atual (1-3) | R |
| **ENCODER E POSIÇÃO** |||||
| 0x0870 | 2160 | ENCODER_RAW_H | Encoder bruto MSW (32-bit) | R |
| 0x0871 | 2161 | ENCODER_RAW_L | Encoder bruto LSW | R |
| 0x0872 | 2162 | ENCODER_GRAUS | Encoder em graus × 10 | R |
| 0x0873 | 2163 | ENCODER_VOLTAS | Número de voltas completas | R |
| 0x0874 | 2164 | POSICAO_ZERO | Flag: máquina em posição zero | R |
| **ÂNGULOS PROGRAMADOS (READ/WRITE)** |||||
| 0x0875 | 2165 | ANGULO_1_ESQ_H | Dobra 1 esquerda MSW | R/W |
| 0x0876 | 2166 | ANGULO_1_ESQ_L | Dobra 1 esquerda LSW | R/W |
| 0x0877 | 2167 | ANGULO_1_DIR_H | Dobra 1 direita MSW | R/W |
| 0x0878 | 2168 | ANGULO_1_DIR_L | Dobra 1 direita LSW | R/W |
| 0x0879 | 2169 | ANGULO_2_ESQ_H | Dobra 2 esquerda MSW | R/W |
| 0x087A | 2170 | ANGULO_2_ESQ_L | Dobra 2 esquerda LSW | R/W |
| 0x087B | 2171 | ANGULO_2_DIR_H | Dobra 2 direita MSW | R/W |
| 0x087C | 2172 | ANGULO_2_DIR_L | Dobra 2 direita LSW | R/W |
| 0x087D | 2173 | ANGULO_3_ESQ_H | Dobra 3 esquerda MSW | R/W |
| 0x087E | 2174 | ANGULO_3_ESQ_L | Dobra 3 esquerda LSW | R/W |
| 0x087F | 2175 | ANGULO_3_DIR_H | Dobra 3 direita MSW | R/W |
| 0x0880 | 2176 | ANGULO_3_DIR_L | Dobra 3 direita LSW | R/W |
| **ESTADOS DA MÁQUINA** |||||
| 0x0881 | 2177 | STATUS_FLAGS | Flags de status (16 bits) | R |
| 0x0882 | 2178 | MODO_OPERACAO | 0=Manual, 1=Auto | R |
| 0x0883 | 2179 | VELOCIDADE_RPM | 5, 10 ou 15 rpm | R |
| 0x0884 | 2180 | SENTIDO_ATUAL | 0=Horário, 1=Anti-horário | R |
| 0x0885 | 2181 | CICLO_ATIVO | 0=Parado, 1=Em ciclo | R |
| 0x0886 | 2182 | EMERGENCIA_ATIVA | 0=Normal, 1=Emergência | R |
| **I/O DIGITAIS (ESPELHO)** |||||
| 0x0887 | 2183 | INPUT_E0_E7 | Byte com E0-E7 (1 bit cada) | R |
| 0x0888 | 2184 | OUTPUT_S0_S7 | Byte com S0-S7 (1 bit cada) | R |
| 0x0889 | 2185 | OUTPUT_CONTROL | Controle manual S0-S7 | R/W |
| 0x088A | 2186 | OUTPUT_OVERRIDE | Habilita controle manual | R/W |
| **LEDs IHM FÍSICA** |||||
| 0x088B | 2187 | LED_STATUS | LEDs 1-5 (5 bits) | R |
| **INVERSOR DE FREQUÊNCIA** |||||
| 0x088C | 2188 | VFD_FREQ_ATUAL | Frequência atual Hz × 10 | R |
| 0x088D | 2189 | VFD_RPM_ATUAL | RPM motor | R |
| 0x088E | 2190 | VFD_CORRENTE | Corrente A × 10 | R |
| 0x088F | 2191 | VFD_TENSAO | Tensão V | R |
| 0x0890 | 2192 | VFD_POTENCIA | Potência W | R |
| 0x0891 | 2193 | VFD_TEMPERATURA | Temp inversor °C | R |
| 0x0892 | 2194 | VFD_STATUS | Status word do VFD | R |
| **SENSORES (SE DISPONÍVEIS)** |||||
| 0x0893 | 2195 | TEMP_MOTOR | Temperatura motor °C | R |
| 0x0894 | 2196 | TEMP_REDUTOR | Temperatura redutor °C | R |
| 0x0895 | 2197 | PRESSAO_HIDR | Pressão hidráulica bar × 10 | R |
| **MANUTENÇÃO** |||||
| 0x0896 | 2198 | HORAS_MOTOR_H | Horas de operação MSW | R |
| 0x0897 | 2199 | HORAS_MOTOR_L | Horas de operação LSW | R |
| 0x0898 | 2200 | LUBRIFICACAO_DIAS | Dias desde última lubrif. | R/W |
| 0x0899 | 2201 | MANUTENCAO_HORAS | Horas até manutenção | R/W |
| **ALARMES E LOGS** |||||
| 0x089A | 2202 | ALARME_ATIVO | Código alarme atual (0=ok) | R |
| 0x089B | 2203 | ALARME_HISTORICO | Últimos 16 alarmes (bits) | R |
| 0x089C | 2204 | LOG_POINTER | Ponteiro log circular | R |
| 0x089D | 2205 | LOG_BUFFER_START | Início buffer logs (20 regs) | R |
| ... | ... | ... | ... | ... |
| 0x08B0 | 2224 | LOG_BUFFER_END | Fim buffer logs | R |
| **CONFIGURAÇÕES IHM WEB** |||||
| 0x08B1 | 2225 | CONFIG_FLAGS | Flags configuração | R/W |
| 0x08B2 | 2226 | AUTO_SHUTDOWN_MIN | Desligar após N min inativo | R/W |
| 0x08B3 | 2227 | BEEP_ENABLE | Habilita beep virtual | R/W |
| 0x08B4 | 2228 | BRIGHTNESS | Brilho tela virtual 0-100 | R/W |
| 0x08B5 | 2229 | LANGUAGE | 0=PT, 1=EN, 2=ES | R/W |
| **HEARTBEAT E WATCHDOG** |||||
| 0x08B6 | 2230 | HEARTBEAT | Incrementa a cada scan | R |
| 0x08B7 | 2231 | WATCHDOG_IHM | IHM web escreve aqui | R/W |
| 0x08B8 | 2232 | COMM_ERRORS | Contador erros Modbus | R |
| 0x08B9 | 2233 | SCAN_TIME_MS | Scan time médio ms | R |
| **ESTATÍSTICAS** |||||
| 0x08BA | 2234 | EFICIENCIA_HOJE | Eficiência % (0-100) | R |
| 0x08BB | 2235 | TEMPO_CICLO_AVG | Tempo médio ciclo ms | R |
| 0x08BC | 2236 | TEMPO_PARADA_MIN | Tempo parado hoje min | R |
| **COMANDOS** |||||
| 0x08BD | 2237 | CMD_RESET_CONTADOR | Escrever 1 para resetar | W |
| 0x08BE | 2238 | CMD_RESET_ALARME | Escrever 1 para ACK | W |
| 0x08BF | 2239 | CMD_ZERO_ENCODER | Escrever 1 para zerar | W |
| 0x08C0 | 2240 | CMD_EMERGENCY_STOP | Escrever 1 para parar | W |

---

## 🔧 Implementação no Ladder

### ROT06.lad - Nova Rotina de Supervisão

```ladder
[ROT06 - SUPERVISAO MODBUS]
Lines: 50+

; ═══════════════════════════════════════════════════════════
; BLOCO 1: DETECÇÃO DE ESCRITA PARA IHM FÍSICA
; ═══════════════════════════════════════════════════════════

[Line00001] ; Detecta mudança de tela
  Comment: "Copia tela para registro Modbus quando muda"
  [Branch01]
    ; Detecta pulso em 00D7 (trigger load screen)
    ├─[00D7]─[POS_EDGE]───┬─[MOV 0FEC → 0860]  ; Copia tela
    └─────────────────────┼─[ADD 0862 + 1]     ; Incrementa contador
                          └─[MOV TIMER → 0863] ; Timestamp

[Line00002] ; Detecta K1 pressionado
  [Branch01]
    ├─[00A0]─[POS_EDGE]───┬─[MOVK #4 → 0860]   ; Tela 4
    └─────────────────────└─[MOVK #1 → 086F]   ; Dobra atual = 1

[Line00003] ; Detecta K2 pressionado
  [Branch01]
    ├─[00A1]─[POS_EDGE]───┬─[MOVK #5 → 0860]   ; Tela 5
    └─────────────────────└─[MOVK #2 → 086F]   ; Dobra atual = 2

[Line00004] ; Detecta K3 pressionado
  [Branch01]
    ├─[00A2]─[POS_EDGE]───┬─[MOVK #6 → 0860]   ; Tela 6
    └─────────────────────└─[MOVK #3 → 086F]   ; Dobra atual = 3

; ═══════════════════════════════════════════════════════════
; BLOCO 2: UPTIME E TIMESTAMPS
; ═══════════════════════════════════════════════════════════

[Line00005] ; Atualiza uptime a cada segundo
  [Branch01]
    ├─[TMR1SEC]───────────┬─[ADD 0868 + 1]     ; Segundos++
    │                     │
    ├─[CMP 0868 >= 60]────┼─[MOVK #0 → 0868]   ; Reset segundos
    │                     └─[ADD 0867 + 1]     ; Minutos++
    │
    ├─[CMP 0867 >= 60]────┬─[MOVK #0 → 0867]   ; Reset minutos
    │                     └─[ADD32 0865:0866]  ; Horas++ (32-bit)
    └─────────────────────────────────────────

[Line00006] ; Contador de power-ups (executa uma vez no boot)
  [Branch01]
    ├─[FIRST_SCAN]────────┬─[ADD 0869 + 1]     ; Power-ups++
    └─────────────────────────────────────────

; ═══════════════════════════════════════════════════════════
; BLOCO 3: ESPELHAMENTO DE ENCODER
; ═══════════════════════════════════════════════════════════

[Line00007] ; Copia encoder para área Modbus
  [Branch01]
    ├─[ ]─────────────────┬─[MOV 04D6 → 0870]  ; Encoder H
    │                     ├─[MOV 04D7 → 0871]  ; Encoder L
    │                     │
    │ ; Converte para graus (valor / 10)
    │                     ├─[DIV32 0870:0871 / 10 → 0872]
    │                     │
    │ ; Calcula voltas completas (valor / 3600)
    │                     └─[DIV32 0870:0871 / 3600 → 0873]
    └─────────────────────────────────────────

; ═══════════════════════════════════════════════════════════
; BLOCO 4: ESPELHAMENTO DE ÂNGULOS (BIDIRECION AL)
; ═══════════════════════════════════════════════════════════

[Line00008] ; Copia ângulos CLP → Modbus
  Comment: "Sincroniza ângulos originais para leitura Modbus"
  [Branch01]
    ├─[ ]─────────────────┬─[MOV 0840 → 0875]  ; Ângulo 1 Esq H
    │                     ├─[MOV 0842 → 0876]  ; Ângulo 1 Esq L
    │                     ├─[MOV 0846 → 0877]  ; Ângulo 1 Dir H
    │                     ├─[... continua ...]
    └─────────────────────────────────────────

[Line00009] ; Copia ângulos Modbus → CLP (se IHM web alterou)
  Comment: "Permite IHM web programar ângulos"
  [Branch01]
    ├─[CMP 0875 != 0840]──┬─[MOV 0875 → 0840]  ; Atualiza CLP
    │                     └─[SET FLAG_CHANGED]
    │
    ├─[CMP 0876 != 0842]──┬─[MOV 0876 → 0842]
    │                     └─[... continua ...]
    └─────────────────────────────────────────

; ═══════════════════════════════════════════════════════════
; BLOCO 5: CONTADOR DE PEÇAS E DOBRAS
; ═══════════════════════════════════════════════════════════

[Line00010] ; Incrementa contador ao completar peça
  [Branch01]
    ├─[0304]──[POS_EDGE]──┬─[ADD32 086A:086B + 1]  ; Peças total
    │                     ├─[ADD 086C + 1]         ; Peças hoje
    │                     └─[ADD32 086D:086E + 3]  ; Dobras total (+3)
    └─────────────────────────────────────────

[Line00011] ; Reset contador diário à meia-noite
  [Branch01]
    ├─[HORA == 0]─[MIN == 0]──┬─[MOVK #0 → 086C]
    └─────────────────────────────────────────────

; ═══════════════════════════════════════════════════════════
; BLOCO 6: ESTADOS DA MÁQUINA
; ═══════════════════════════════════════════════════════════

[Line00012] ; Monta word de status
  Comment: "Bit 0=Manual, 1=Auto, 2=Emergência, 3=Ciclo, etc"
  [Branch01]
    ├─[ ]─────────────────┬─[MOVK #0 → 0881]      ; Limpa
    │                     │
    ├─[0210]──────────────┼─[SET_BIT 0881, 0]     ; Bit 0: Manual
    ├─[0190/0191]─────────┼─[SET_BIT 0881, 1]     ; Bit 1: Auto
    ├─[EMERG_INPUT]───────┼─[SET_BIT 0881, 2]     ; Bit 2: Emergência
    ├─[0300-0304]─────────┼─[SET_BIT 0881, 3]     ; Bit 3: Ciclo
    ├─[POSICAO_ZERO]──────┼─[SET_BIT 0881, 4]     ; Bit 4: Posição zero
    └─────────────────────────────────────────────

[Line00013] ; Modo operação
  [Branch01]
    ├─[0210]──────────────┬─[MOVK #0 → 0882]      ; Manual
    └─[0190/0191]─────────┴─[MOVK #1 → 0882]      ; Auto

[Line00014] ; Velocidade RPM
  [Branch01]
    ├─[CLASS_1]───────────┬─[MOVK #5 → 0883]
    ├─[CLASS_2]───────────┼─[MOVK #10 → 0883]
    └─[CLASS_3]───────────┴─[MOVK #15 → 0883]

[Line00015] ; Sentido rotação
  [Branch01]
    ├─[0190]──────────────┬─[MOVK #1 → 0884]      ; Anti-horário
    └─[0191]──────────────┴─[MOVK #0 → 0884]      ; Horário

[Line00016] ; Ciclo ativo
  [Branch01]
    ├─[0300-0304]─────────┬─[MOVK #1 → 0885]
    └─[ELSE]──────────────┴─[MOVK #0 → 0885]

[Line00017] ; Emergência
  [Branch01]
    ├─[INPUT_EMERG]───────┬─[MOVK #1 → 0886]
    └─[ELSE]──────────────┴─[MOVK #0 → 0886]

; ═══════════════════════════════════════════════════════════
; BLOCO 7: I/O DIGITAIS COMPACTADAS
; ═══════════════════════════════════════════════════════════

[Line00018] ; Empacota E0-E7 em 1 byte
  [Branch01]
    ├─[ ]─────────────────┬─[MOVK #0 → 0887]
    ├─[0100]──────────────┼─[SET_BIT 0887, 0]
    ├─[0101]──────────────┼─[SET_BIT 0887, 1]
    ├─[0102]──────────────┼─[SET_BIT 0887, 2]
    ├─[0103]──────────────┼─[SET_BIT 0887, 3]
    ├─[0104]──────────────┼─[SET_BIT 0887, 4]
    ├─[0105]──────────────┼─[SET_BIT 0887, 5]
    ├─[0106]──────────────┼─[SET_BIT 0887, 6]
    └─[0107]──────────────┴─[SET_BIT 0887, 7]

[Line00019] ; Empacota S0-S7 em 1 byte
  [Branch01]
    ├─[ ]─────────────────┬─[MOVK #0 → 0888]
    ├─[0180]──────────────┼─[SET_BIT 0888, 0]
    ├─[... S1-S7 ...]
    └─────────────────────┴─────────────────────

; ═══════════════════════════════════════════════════════════
; BLOCO 8: CONTROLE MANUAL DE SAÍDAS (OVERRIDE)
; ═══════════════════════════════════════════════════════════

[Line00020] ; Permite IHM web controlar S0-S7 manualmente
  Comment: "Se 088A (OVERRIDE) = 1, usa 0889 para S0-S7"
  [Branch01]
    ├─[088A == 1]─────────┬─[BIT_TEST 0889, 0]─[OUT 0180]
    │                     ├─[BIT_TEST 0889, 1]─[OUT 0181]
    │                     ├─[... S2-S7 ...]
    └─────────────────────┴─────────────────────────────────

; ═══════════════════════════════════════════════════════════
; BLOCO 9: LEDs IHM FÍSICA
; ═══════════════════════════════════════════════════════════

[Line00021] ; Empacota LEDs 1-5
  [Branch01]
    ├─[ ]─────────────────┬─[MOVK #0 → 088B]
    ├─[00C0]──────────────┼─[SET_BIT 088B, 0]  ; LED1
    ├─[00C1]──────────────┼─[SET_BIT 088B, 1]  ; LED2
    ├─[00C2]──────────────┼─[SET_BIT 088B, 2]  ; LED3
    ├─[00C3]──────────────┼─[SET_BIT 088B, 3]  ; LED4
    └─[00C4]──────────────┴─[SET_BIT 088B, 4]  ; LED5

; ═══════════════════════════════════════════════════════════
; BLOCO 10: HEARTBEAT E WATCHDOG
; ═══════════════════════════════════════════════════════════

[Line00022] ; Incrementa heartbeat a cada scan
  [Branch01]
    ├─[ ]─────────────────┬─[ADD 08B6 + 1]

[Line00023] ; Monitora watchdog IHM web
  Comment: "Se IHM não escreve em 08B7 por 5s, assume desconectada"
  [Branch01]
    ├─[TMR_5SEC]──────────┬─[CMP 08B7_OLD == 08B7]
    │                     └─[SET ALARME_IHM_OFFLINE]
    └─[MOV 08B7 → 08B7_OLD]

; ═══════════════════════════════════════════════════════════
; BLOCO 11: SCAN TIME
; ═══════════════════════════════════════════════════════════

[Line00024] ; Calcula scan time médio
  [Branch01]
    ├─[SCAN_TIME_TIMER]───┬─[MOV TIMER → TEMP]
    │                     ├─[SUB TEMP - LAST → DELTA]
    │                     ├─[AVG DELTA → 08B9]  ; Média móvel
    │                     └─[MOV TEMP → LAST]
    └─────────────────────────────────────────────────────

; ═══════════════════════════════════════════════════════════
; BLOCO 12: COMANDOS DA IHM WEB
; ═══════════════════════════════════════════════════════════

[Line00025] ; Processa comando reset contador
  [Branch01]
    ├─[08BD == 1]─────────┬─[MOVK #0 → 086A]   ; Reset peças H
    │                     ├─[MOVK #0 → 086B]   ; Reset peças L
    │                     ├─[MOVK #0 → 086C]   ; Reset hoje
    │                     └─[MOVK #0 → 08BD]   ; Limpa comando
    └─────────────────────────────────────────────────────

[Line00026] ; Processa comando reset alarme
  [Branch01]
    ├─[08BE == 1]─────────┬─[MOVK #0 → 089A]   ; Limpa alarme
    │                     └─[MOVK #0 → 08BE]   ; Limpa comando
    └─────────────────────────────────────────────────────

[Line00027] ; Processa comando zero encoder
  [Branch01]
    ├─[08BF == 1]─────────┬─[MOVK #0 → 04D6]   ; Zera encoder H
    │                     ├─[MOVK #0 → 04D7]   ; Zera encoder L
    │                     └─[MOVK #0 → 08BF]   ; Limpa comando
    └─────────────────────────────────────────────────────

[Line00028] ; Processa comando emergency stop
  [Branch01]
    ├─[08C0 == 1]─────────┬─[SET EMERGENCY_BIT]
    │                     └─[MOVK #0 → 08C0]   ; Limpa comando
    └─────────────────────────────────────────────────────
```

---

## 🔄 Modificação do Principal.lad

```ladder
; Adicionar no final do PRINCIPAL (após ROT5):

[Line00025] ; Chama rotina de supervisão
  [Branch01]
    ├─[00F7]──────────────┬─[CALL ROT06]  ; Sempre executa
    └─────────────────────────────────────────────
```

---

## 📊 Dados do Inversor (Se Disponível via Modbus)

Se o inversor WEG está conectado via Modbus ao CLP:

```ladder
[Line00029] ; Lê dados do VFD via Modbus
  [Branch01]
    ; Assumindo VFD como slave 2 no Modbus
    ├─[MODBUS_READ slave=2, reg=1 → 088C]  ; Frequência
    ├─[MODBUS_READ slave=2, reg=2 → 088D]  ; RPM
    ├─[MODBUS_READ slave=2, reg=3 → 088E]  ; Corrente
    ├─[MODBUS_READ slave=2, reg=4 → 088F]  ; Tensão
    └─[MODBUS_READ slave=2, reg=6 → 0891]  ; Temperatura
```

**Nota:** Se VFD não está em Modbus, calcular aproximações:
- RPM: baseado na classe de velocidade (5/10/15)
- Corrente: ler via entrada analógica se disponível

---

## 🔍 Log Circular de Eventos

```ladder
[Line00030] ; Grava evento no buffer circular
  Comment: "Quando evento ocorre, grava timestamp + código"
  [Branch01]
    ; Evento: mudança de tela
    ├─[SCREEN_CHANGED]────┬─[LOG_PTR → ADDR]
    │                     ├─[MOV 0860 → LOG[ADDR]]
    │                     ├─[MOV TIMESTAMP → LOG[ADDR+1]]
    │                     ├─[INC LOG_PTR]
    │                     └─[IF LOG_PTR > 20 THEN LOG_PTR = 0]
    └─────────────────────────────────────────────────────────────
```

---

## 📡 Protocolo de Comunicação IHM Web

### Polling Otimizado (250ms)

```python
# state_manager.py

POLL_GROUPS = {
    'fast': {  # A cada 250ms
        'registers': [
            0x0860,  # Tela atual
            0x0870, 0x0871,  # Encoder
            0x0881,  # Status flags
            0x0885,  # Ciclo ativo
            0x0886,  # Emergência
            0x0887, 0x0888,  # I/O
            0x088B,  # LEDs
        ],
        'interval_ms': 250,
    },
    'medium': {  # A cada 1s
        'registers': [
            0x0865, 0x0866, 0x0867, 0x0868,  # Uptime
            0x086A, 0x086B, 0x086C,  # Peças
            0x088C, 0x088D, 0x088E,  # VFD
        ],
        'interval_ms': 1000,
    },
    'slow': {  # A cada 5s
        'registers': [
            0x0869,  # Power-ups
            0x0896, 0x0897,  # Horas motor
            0x08B9,  # Scan time
        ],
        'interval_ms': 5000,
    },
}
```

---

## 🎨 IHM Web: Dashboards Avançados

### Tela 1: Operação (Clássica)
- Replicação literal da IHM física
- Teclado virtual K0-K9, S1, S2
- Encoder visual (ponteiro + números)

### Tela 2: Supervisão (NOVA)
```
┌─────────────────────────────────────────────────────┐
│  SUPERVISÃO EM TEMPO REAL                           │
├─────────────────────────────────────────────────────┤
│  Uptime: 1234h 56min      Peças hoje: 89            │
│  RPM: 10      Corrente: 15.2A      Pot: 12.5kW      │
│                                                      │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐ │
│  │  ENCODER    │  │  CICLO      │  │  I/O        │ │
│  │   125.5°    │  │  ATIVO      │  │  E:10110101 │ │
│  │  [========] │  │  55% compl. │  │  S:01100011 │ │
│  └─────────────┘  └─────────────┘  └─────────────┘ │
│                                                      │
│  Gráfico de produção (24h):                         │
│  [████████████████▓▓▓▓▓▓▓▓░░░░░░░░░░░░░░]           │
└─────────────────────────────────────────────────────┘
```

### Tela 3: Manutenção (NOVA)
```
┌─────────────────────────────────────────────────────┐
│  MANUTENÇÃO PREDITIVA                               │
├─────────────────────────────────────────────────────┤
│  Horas motor: 12,456h                               │
│  Próxima manutenção: 544h (23 dias)                 │
│  Lubrificação: há 12 dias  [ALERTAR EM 3 DIAS]     │
│                                                      │
│  Temperatura motor: 68°C  [OK]                      │
│  Temperatura VFD:   45°C  [OK]                      │
│                                                      │
│  [Resetar Contador Manutenção]                      │
│  [Registrar Lubrificação]                           │
└─────────────────────────────────────────────────────┘
```

### Tela 4: Controle Manual I/O (NOVA)
```
┌─────────────────────────────────────────────────────┐
│  CONTROLE MANUAL DE SAÍDAS                          │
├─────────────────────────────────────────────────────┤
│  ⚠️  ATENÇÃO: Modo avançado - usar com cuidado     │
│                                                      │
│  [✓] Habilitar Controle Manual                      │
│                                                      │
│  Saídas:                                            │
│  S0: [ ON ] Motor principal                         │
│  S1: [OFF ] Bomba hidráulica                        │
│  S2: [ ON ] Iluminação                              │
│  S3: [OFF ] Reserva                                 │
│  S4: [OFF ] Ventilador                              │
│  S5: [OFF ] Reserva                                 │
│  S6: [OFF ] Reserva                                 │
│  S7: [OFF ] Sinaleiro                               │
└─────────────────────────────────────────────────────┘
```

---

## 🚀 Próximos Passos

1. **Criar ROT06.lad** com toda lógica acima
2. **Modificar Principal.lad** para chamar ROT06
3. **Compilar e gravar** no CLP
4. **Testar** com `test_screen_sync.py` expandido
5. **Implementar dashboards** na IHM web

---

**Resultado:** IHM web com **poderes de SCADA profissional**, mantendo emulação literal da IHM física quando necessário! 🎯
