# BITS DE SISTEMA - IHM EXPERT SERIES

## Mapeamento Descoberto (manual_plc.txt linhas 3300-3399)

A tabela no manual está em ordem DECRESCENTE (00E0 → 0078).

### Bits Relevantes para IHM

| Hex | Dec | Descrição | Tipo |
|-----|-----|-----------|------|
| **00DD** | 221 | **ON = Tecla S2 FECHADA / OFF = Tecla S2 ABERTA** | Entrada |
| **00DC** | 220 | **ON = Tecla S1 FECHADA / OFF = Tecla S1 ABERTA** | Entrada |
| **00DB** | 219 | **APAGA DISPLAY** | Controle |
| **00DA** | 218 | Mudança de valor via RS232 (1 varredura) | Sistema |
| **00D9** | 217 | (reservado) | - |
| **00D8** | 216 | **TENTATIVA DE EDIÇÃO COM TECLADO BLOQUEADO** | Sistema |
| **00D7** | 215 | **Transição OFF→ON: CARREGA TELA ALVO NO DISPLAY** | Controle |
| **00D6** | 214 | (reservado) | - |
| **00D5** | 213 | (reservado) | - |
| **00D4** | 212 | (reservado) | - |
| **00D3** | 211 | (reservado) | - |
| **00D2** | 210 | **BLOQUEIO DE CONTAGEM (contador rápido)** | Controle |
| **00D1** | 209 | (reservado) | - |
| **00D0** | 208 | (reservado) | - |

### Contagem Reversa para Encontrar Bit de Edição

A linha 3358 diz: **"FICA ATIVO DURANTE A EDIÇÃO DE VALORES (modo RUN)"**

Contando de 00E0 (linha 3307) para baixo:
- 00E0 (3307)
- 00DF (3308)
- 00DE (3309)
- 00DD (3310) = S2
- 00DC (3311) = S1
- 00DB (3312) = APAGA DISPLAY
- 00DA (3313) = Mudança valor
- 00D9 (3314)
- 00D8 (3315)
- 00D7 (3316)
- 00D6 (3317)
- 00D5 (3318)
- 00D4 (3319)
- 00D3 (3320)
- 00D2 (3321) = BLOQUEIO CONTAGEM
- 00D1 (3322)
- 00D0 (3323)

Preciso verificar linha 3355 até 3393 para confirmar a contagem correta.

## Bits de Teclas (já conhecidos)

| Hex | Dec | Descrição |
|-----|-----|-----------|
| 00A0 | 160 | K1 |
| 00A1 | 161 | K2 |
| 00A2 | 162 | K3 |
| 00A3 | 163 | K4 |
| 00A4 | 164 | K5 |
| 00A5 | 165 | K6 |
| 00A6 | 166 | K7 |
| 00A7 | 167 | K8 |
| 00A8 | 168 | K9 |
| 00A9 | 169 | K0 |
| 00AC | 172 | Seta CIMA (↑) |
| 00AD | 173 | Seta BAIXO (↓) |
| 00BC | 188 | ESC |
| 0025 | 37 | ENTER |
| 0026 | 38 | EDIT |
| 00F1 | 241 | LOCK |

## Registro de Tela

| Hex | Dec | Descrição | Tipo |
|-----|-----|-----------|------|
| **0FEC** | 4076 | **Número da tela alvo** | Write (ladder→IHM) |

Quando o bit **00D7** faz transição OFF→ON, a IHM carrega a tela cujo número está em 0FEC.

## CONCLUSÃO PROVISÓRIA

**A IHM EXPERT NÃO ESCREVE DIRETAMENTE OS VALORES DE ÂNGULOS!**

A IHM apenas:
1. Mostra valores lidos de registros
2. Permite edição via teclado numérico
3. Quando confirma (ENTER), **escreve o valor editado de volta no registro**

O ladder define QUAIS registros são editáveis em cada tela!

Preciso encontrar QUAL registro a IHM usa para transferir valores editados.
