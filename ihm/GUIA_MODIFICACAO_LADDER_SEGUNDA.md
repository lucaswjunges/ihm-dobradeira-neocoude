# 🔧 GUIA COMPLETO - MODIFICAÇÃO LADDER SEGUNDA-FEIRA

**Data preparação:** 15/Nov/2025 02:30
**Execução:** Segunda-feira na fábrica
**Objetivo:** Habilitar controle de ângulos e motor via IHM web

---

## ⚠️ PRÉ-REQUISITOS

### Hardware/Software Necessário:
- ✅ Laptop Windows com WinSUP instalado
- ✅ Cabo RS485 (mesmo usado para testes)
- ✅ Pen drive para backup
- ✅ Acesso físico ao CLP
- ✅ Autorização para modificar ladder

### Conhecimento Necessário:
- Programação ladder básica
- Instruções: MOV, MOVK, SETR, RSTR
- Estrutura de memória CLP Atos

---

## 📋 ROTEIRO COMPLETO (2-3 HORAS)

### FASE 1: BACKUP E CONEXÃO (15-30min)

#### 1.1 Backup Completo do Ladder

```
1. Conectar WinSUP ao CLP
   - Cabo RS485 → Porta B do CLP
   - Configurar: 57600 bps, slave ID 1

2. WinSUP → Online → Download from PLC
   - Salvar como: clp_backup_ANTES_MODIFICACAO_DDMMAA.sup
   - Copiar para PEN DRIVE (segurança!)

3. Verificar integridade:
   - Reabrir arquivo .sup baixado
   - Conferir se todos os programas aparecem
   - Se OK → prosseguir
```

**⚠️ SE ALGO DER ERRADO:** Você pode fazer Upload deste backup para restaurar!

---

### FASE 2: ANÁLISE DO LADDER (30-60min)

#### 2.1 Identificar Área de Ângulos Input

**Objetivo:** Descobrir DE ONDE o ladder LÊ os ângulos setpoint que a IHM física configurava.

**Método 1: Busca por Instruções MOV**

```
WinSUP → Edit → Find/Replace
Buscar: "MOV"

Procurar por instruções como:
MOV E:0500 → 0840  (copia de NVRAM para área de trabalho)
MOV E:0A00 → 0840  (copia de área input para trabalho)
MOVK 0 → 0840      (zera registros)
```

**Método 2: Busca por Endereços Conhecidos**

```
Buscar sequencialmente:
1. "0840" (dobra 1 LSW)
2. "0842" (dobra 1 MSW)
3. "0500" (NVRAM área ângulos)
4. "0940" (área supervisão)
```

**Método 3: Análise de Cross-Reference**

```
WinSUP → View → Cross Reference
Selecionar: 0840, 0842, 0846, 0848, 0850, 0852

Ver TODOS os lugares que usam esses registros:
- Instruções que LÊEM (fonte de dados)
- Instruções que ESCREVEM (destino)
```

#### 2.2 Mapear Estrutura Atual

Preencher tabela (pode estar no ladder ou descobrir agora):

| Componente | Endereço | Tipo | Usado por |
|------------|----------|------|-----------|
| Input Ângulo 1 | 0x???? | R/W | IHM física escreve |
| Cálculo Ângulo 1 | 0x0840/0x0842 | R/O | Ladder calcula |
| Target Ângulo 1 | 0x???? | R/W | Usado pelo controle |

---

### FASE 3: ESTRATÉGIAS DE MODIFICAÇÃO

#### ESTRATÉGIA A: Criar Nova Área Input Modbus (RECOMENDADA)

**Ideia:** Criar registros EXCLUSIVOS para Modbus escrever.

```ladder
; === NOVO CÓDIGO A ADICIONAR ===

; Área de Input Modbus (0x0A00-0x0A10)
; IHM web escreve aqui, ladder copia para área de trabalho

Line_NEW_01:
    ; Se Modbus escreveu algo diferente de zero em 0x0A00/0x0A02
    ; Copiar para área de trabalho

    In:LDP  E:0A00  ; Detect pulse quando 0A00 muda
    Out:MOV E:0A02 E:0840  ; Copia LSW Dobra 1
    Out:MOV E:0A00 E:0842  ; Copia MSW Dobra 1

Line_NEW_02:
    In:LDP  E:0A04  ; Detect pulse quando 0A04 muda
    Out:MOV E:0A06 E:0846  ; Copia LSW Dobra 2
    Out:MOV E:0A04 E:0848  ; Copia MSW Dobra 2

Line_NEW_03:
    In:LDP  E:0A08  ; Detect pulse quando 0A08 muda
    Out:MOV E:0A0C E:0850  ; Copia LSW Dobra 3
    Out:MOV E:0A08 E:0852  ; Copia MSW Dobra 3
```

**Atualizar `modbus_map.py` depois:**
```python
BEND_ANGLES = {
    'BEND_1_LEFT_MSW': 0x0A00,  # Nova área input
    'BEND_1_LEFT_LSW': 0x0A02,
    # ...
}
```

---

#### ESTRATÉGIA B: Remover Sobrescrita dos Registros Oficiais

**Ideia:** Encontrar e REMOVER instruções que sobrescrevem 0x0840-0x0852.

**Passos:**

1. Buscar todas as instruções que ESCREVEM em 0x0840:
   ```
   MOV ??? → 0840
   MOVK ??? → 0840
   ```

2. Analisar CADA uma:
   - Se for cálculo necessário → mover para OUTRO registro
   - Se for inicialização → remover
   - Se for cópia → verificar origem

3. Exemplo de modificação:
   ```ladder
   ; ANTES (sobrescreve)
   Out:SUB E:0858 E:0842 E:0840  ; Calcula e grava em 0840

   ; DEPOIS (calcula em área separada)
   Out:SUB E:0860 E:0842 E:0840  ; Calcula em 0860 (novo)
   ```

---

#### ESTRATÉGIA C: Usar Área NVRAM (Se Existir)

**Verificar se ladder JÁ usa 0x0500-0x053F:**

```
Buscar: "0500", "0502", "0504" (NVRAM ângulos)

Se encontrar instruções tipo:
MOV E:0500 → 0840  ; Copia NVRAM para área trabalho

ENTÃO:
1. IHM web escreve em 0x0500/0x0502
2. Ladder já copia automaticamente!
3. Nenhuma modificação necessária!
```

**Atualizar apenas `modbus_map.py`:**
```python
BEND_ANGLES = {
    'BEND_1_LEFT_MSW': 0x0500,  # NVRAM
    'BEND_1_LEFT_LSW': 0x0502,
}
```

---

### FASE 4: CONTROLE DE MOTOR (S0/S1)

#### 4.1 Identificar Bloqueio SETR

**Buscar em ROT0.lad:**
```
Out:SETR T:0043 Size:003 E:0180  ; S0
Out:SETR T:0043 Size:003 E:0181  ; S1
```

#### 4.2 Adicionar Branch Modbus

**Modificar linha S0 (exemplo):**

```ladder
; === ANTES ===
Out:SETR T:0043 Size:003 E:0180
Branch01: E2 AND (NOT S1)
Branch02: 0305 AND 02FF AND (NOT S1)
; ... (outras branches)
Branch08: (NOT E6) AND (NOT E6)

; === DEPOIS ===
Out:SETR T:0043 Size:003 E:0180
Branch01: E2 AND (NOT S1)
Branch02: 0305 AND 02FF AND (NOT S1)
; ... (branches originais)
Branch08: (NOT E6) AND (NOT E6)
Branch09: 0500 AND (NOT S1)  ; ← NOVO: Bit comando Modbus
```

**Criar bit de comando:**
```
0x0500 (1280 decimal) = MODBUS_CMD_AVANCAR
0x0501 (1281 decimal) = MODBUS_CMD_RECUAR
```

**Atualizar `modbus_map.py`:**
```python
MOTOR_CONTROL = {
    'CMD_FORWARD': 0x0500,  # IHM web escreve True para avançar
    'CMD_REVERSE': 0x0501,  # IHM web escreve True para recuar
}
```

---

### FASE 5: UPLOAD E TESTES (30-45min)

#### 5.1 Validar Modificações

```
WinSUP → Program → Compile
- Verificar 0 erros de sintaxe
- Se houver erros → corrigir antes de upload
```

#### 5.2 Upload Seguro

```
1. WinSUP → Online → Stop PLC
   ⚠️ Máquina vai parar!

2. WinSUP → Online → Upload to PLC
   - Aguardar conclusão (1-2min)

3. WinSUP → Online → Run PLC
   - Máquina volta a funcionar
```

#### 5.3 Teste Imediato

**Teste 1: Ângulos**
```python
# No notebook Ubuntu
python3 -c "
from modbus_client import ModbusClientWrapper
import modbus_map as mm

client = ModbusClientWrapper(port='/dev/ttyUSB0')

# Escrever ângulo teste: 45°
client.write_32bit(
    mm.BEND_ANGLES['BEND_1_LEFT_MSW'],
    mm.BEND_ANGLES['BEND_1_LEFT_LSW'],
    450  # 45.0°
)

# Aguardar 5 segundos
import time
time.sleep(5)

# Ler de volta
value = client.read_32bit(
    mm.BEND_ANGLES['BEND_1_LEFT_MSW'],
    mm.BEND_ANGLES['BEND_1_LEFT_LSW']
)

if value == 450:
    print('✅✅✅ SUCESSO! Ângulo persistiu!')
else:
    print(f'❌ FALHA: Leu {value}, esperava 450')

client.close()
"
```

**Teste 2: Motor (se modificou S0/S1)**
```python
python3 test_alternative_angle_addresses.py
```

Se motor girar → ✅ SUCESSO TOTAL!

---

### FASE 6: BACKUP FINAL

```
WinSUP → Online → Download from PLC
Salvar como: clp_MODIFICADO_FUNCIONANDO_DDMMAA.sup
Copiar para PEN DRIVE
```

---

## 🚨 PLANO DE ROLLBACK

**SE ALGO DER ERRADO:**

```
1. WinSUP → Online → Stop PLC

2. WinSUP → File → Open
   - Abrir: clp_backup_ANTES_MODIFICACAO_DDMMAA.sup

3. WinSUP → Online → Upload to PLC
   - Restaura versão anterior

4. WinSUP → Online → Run PLC
   - Máquina volta ao normal

Tempo de rollback: 2-3 minutos
```

---

## 📋 CHECKLIST PRÉ-EXECUÇÃO

Imprimir e marcar:

- [ ] Backup ladder baixado e salvo em PEN DRIVE
- [ ] WinSUP conectado e comunicando com CLP
- [ ] Laptop com bateria carregada (ou fonte ligada)
- [ ] Equipe ciente que máquina vai parar temporariamente
- [ ] Operador disponível para testes após modificação
- [ ] Notebook Ubuntu com código Python pronto
- [ ] Cabo RS485 testado e funcionando

---

## 📄 DOCUMENTOS DE APOIO

### Durante Análise:
1. Fazer PRINT SCREEN de cada linha relevante do ladder
2. Anotar no papel:
   - Endereços encontrados
   - Instruções que escrevem em 0x0840-0x0852
   - Lógica de cópia (se houver)

### Após Modificação:
1. Documentar o que foi mudado
2. Salvar screenshots do antes/depois
3. Atualizar este guia com descobertas

---

## ⏱️ CRONOGRAMA ESTIMADO

| Fase | Tempo | Observações |
|------|-------|-------------|
| Backup | 15min | Crítico - não pular! |
| Análise Ladder | 30-60min | Pode ser rápido se encontrar NVRAM |
| Modificação | 30min | Depende da estratégia |
| Upload + Testes | 30min | Inclui validação |
| Documentação | 15min | Backup final |
| **TOTAL** | **2-3h** | Com imprevistos |

---

## 🎯 CRITÉRIOS DE SUCESSO

### Ângulos:
- ✅ IHM web escreve 90° → CLP mantém 90° após 10 segundos
- ✅ Ladder usa valor escrito (não sobrescreve)
- ✅ Motor executa dobra no ângulo correto

### Motor (se modificado):
- ✅ Botão AVANÇAR na IHM web → Motor gira anti-horário
- ✅ Botão RECUAR na IHM web → Motor gira horário
- ✅ Botões físicos continuam funcionando

---

## 📞 CONTATOS EMERGÊNCIA

**Se precisar de ajuda:**
- Suporte Atos: [número do manual]
- Integrador original: [se disponível]
- WhatsApp grupo: [se tiver]

**Documentação técnica:**
- Manual CLP: `/manual_MPC4004.txt`
- Este guia: `GUIA_MODIFICACAO_LADDER_SEGUNDA.md`
- Diagnósticos: `DIAGNOSTICO_FINAL_MOTOR.md`, `RELATORIO_AUDITORIA_IHM_FINAL.md`

---

## ✅ PÓS-MODIFICAÇÃO

### Atualizar Código Python:

```bash
# Se usou Estratégia A (nova área 0x0A00)
# Editar modbus_map.py linhas 96-117

# Se usou Estratégia C (NVRAM 0x0500)
# Editar modbus_map.py linhas 96-117

# Testar servidor
python3 main_server.py --port /dev/ttyUSB0
```

### Testar IHM Web Completa:

```
1. Abrir Chrome → localhost:8080
2. Configurar ângulo: 90°
3. Aguardar 5s
4. Verificar no CLP se persistiu
5. Testar botão AVANÇAR
6. Verificar motor gira
7. ✅ SUCESSO TOTAL!
```

---

**Preparado por:** Engenheiro Automação Sênior
**Data:** 15/Nov/2025 02:30
**Versão:** 1.0 - Guia Completo Modificação Ladder

**BOA SORTE SEGUNDA-FEIRA! 🚀**
