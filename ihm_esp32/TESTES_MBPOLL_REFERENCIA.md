# Referência Rápida - Testes Modbus com mbpoll

**Status:** ✅ TESTADO E VALIDADO (2025-11-18)
**Arquivo CLP:** `clp_MODIFICADO_IHM_WEB_COM_ROT5.sup`

---

## ⚙️ Configuração Modbus Validada

```
Porta:      /dev/ttyUSB0
Baudrate:   57600
Parity:     None
Stop bits:  2  ⚠️ CRÍTICO - usar -s 2
Slave ID:   1
```

**Comando base mbpoll:**
```bash
mbpoll -a 1 -b 57600 -P none -s 2 /dev/ttyUSB0 [opções]
```

---

## Endereços Testados

### Área 0x0A00 (IHM Web - Experimental)
```
0x0A00 (2560) - Ângulo 1 Esquerda
0x0A01 (2561) - Ângulo 2 Esquerda
0x0A02 (2562) - Ângulo 3 Esquerda
0x0A03 (2563) - Ângulo 1 Direita
0x0A04 (2564) - Ângulo 2 Direita
0x0A05 (2565) - Ângulo 3 Direita
```

### Área 0x0500 (Ângulos Oficiais do Ladder)
```
0x0500 (1280) - Ângulo Inicial 1
0x0501 (1281) - Ângulo Final 1
0x0502 (1282) - Ângulo Inicial 2
0x0503 (1283) - Ângulo Final 2
0x0504 (1284) - Ângulo Inicial 3
0x0505 (1285) - Ângulo Final 3
```

### Área 0x0392 (Trigger Alternativo)
```
0x0392 (914) - Bit de trigger/controle
```

## Comandos mbpoll Rápidos

### Leitura
```bash
# Ler 1 registrador
mbpoll -a 1 -r 2560 -c 1 -t 4:int -b 57600 -P none /dev/ttyUSB0

# Ler área completa (6 ângulos)
mbpoll -a 1 -r 2560 -c 6 -t 4:int -b 57600 -P none /dev/ttyUSB0

# Ler encoder (32-bit)
mbpoll -a 1 -r 1238 -c 2 -t 4:int -b 57600 -P none /dev/ttyUSB0
```

### Escrita de Registrador
```bash
# Escrever ângulo 90.0° (valor 900) em 0x0A00
mbpoll -a 1 -r 2560 -t 4:int -b 57600 -P none /dev/ttyUSB0 900

# Escrever ângulo 120.0° (valor 1200) em 0x0A01
mbpoll -a 1 -r 2561 -t 4:int -b 57600 -P none /dev/ttyUSB0 1200
```

### Escrita de Coil (Bit)
```bash
# Ativar bit 0x0392
mbpoll -a 1 -r 914 -t 0 -b 57600 -P none /dev/ttyUSB0 1

# Desativar bit 0x0392
mbpoll -a 1 -r 914 -t 0 -b 57600 -P none /dev/ttyUSB0 0
```

## Conversão de Valores

### Ângulos
```
45.0°  = 450
60.0°  = 600
90.0°  = 900
120.0° = 1200
135.0° = 1350
180.0° = 1800
```

**Fórmula:** `valor_modbus = graus × 10`

## Tipos de Teste

### 1. Teste de Escrita Básico
1. Escrever valor no registrador
2. Ler registrador para validar
3. Comparar valor lido com valor escrito

### 2. Teste de Persistência
1. Escrever valor
2. Aguardar 5 segundos
3. Ler novamente
4. Verificar se valor foi mantido

### 3. Teste de Trigger
1. Escrever ângulos na área
2. Ativar bit de trigger
3. Monitorar se CLP reagiu
4. Desativar trigger

### 4. Teste de Área Completa
1. Escrever 6 ângulos sequencialmente
2. Ler área completa (6 registradores)
3. Validar todos os valores

## ✅ Checklist de Validação (Resultados dos Testes)

- [x] **Comunicação básica funciona** - Leitura encoder OK
- [x] **Leitura de 0x0A00** - ✅ Retorna valores (lixo de memória)
- [x] **Escrita em 0x0A00** - ❌ FALHA "Invalid data" (área READ-ONLY)
- [x] **Escrita em 0x0500** - ✅ ACEITA! (área WRITE-ABLE)
- [x] **Leitura de 0x0500** - ✅ Retorna valores (modificados pelo CLP)
- [ ] Trigger 0x0392 aceita escrita - A testar
- [ ] CLP reage ao trigger - A testar
- [ ] Valores persistem após escrita - A validar
- [x] **Área completa pode ser lida de uma vez** - ✅ Funciona

## Resultados Esperados

### Sucesso
```
[2560]: 900
```
Valor escrito foi retornado corretamente.

### Falha de Escrita
```
Protocol error
```
Área não aceita escrita ou endereço protegido.

### Timeout
```
mbpoll: read: Connection timed out
```
Verificar conexão física RS485.

## Observações

1. **Delay entre comandos:** Aguardar pelo menos 500ms entre operações
2. **Valores negativos:** Se aparecerem valores negativos, verificar tipo int vs uint
3. **Áreas protegidas:** Algumas áreas do CLP podem ser read-only
4. **Trigger timing:** Trigger pode precisar ser mantido por tempo mínimo

## 📊 Áreas Conhecidas do CLP (Validadas)

| Endereço | Tipo | Descrição | R/W | Status |
|----------|------|-----------|-----|--------|
| 0x04D6-0x04D7 (1238-1239) | 32-bit | Encoder (contador alta velocidade) | R | ✅ Testado |
| **0x0500-0x053F (1280-1343)** | 16-bit | **Ângulos iniciais/finais (16 ângulos)** | **RW** | ✅ **USAR ESTA!** |
| 0x0A00-0x0AFF (2560-2815) | 16-bit | Área experimental IHM Web | R | ❌ READ-ONLY |
| 0x0392 (914) | bit | Trigger alternativo | ? | ⏳ A testar |

**Legenda:** R=Read, W=Write

---

## 🎯 DESCOBERTAS IMPORTANTES

### ✅ Área 0x0500 - FUNCIONAL PARA ESCRITA

**Comportamento observado:**
1. ✅ Aceita escrita via Modbus Function 0x06 (Write Single Register)
2. ⚠️ CLP processa/modifica valores após escrita (lógica ladder ativa)
3. ✅ Valores podem ser lidos de volta

**Exemplo prático:**
```bash
# Escrever 90.0° (900) em 0x0500
mbpoll -a 1 -r 1280 -t 4 -b 57600 -P none -s 2 /dev/ttyUSB0 900
# Resultado: "Written 1 references." ✅

# Ler de volta
mbpoll -a 1 -r 1280 -c 1 -t 4 -b 57600 -P none -s 2 -1 /dev/ttyUSB0
# Resultado: [1280]: 900 (ou valor processado pelo CLP)
```

### ❌ Área 0x0A00 - READ-ONLY

**Comportamento observado:**
1. ❌ Rejeita escrita com erro "Invalid data"
2. ✅ Leitura funciona (retorna valores de memória)
3. 💡 Pode ser área de status/leitura apenas

**Valores lidos (aparentemente lixo de memória):**
```
[0x0A00]: 816
[0x0A01]: 14128
[0x0A02]: 14127
[0x0A03]: 12344
[0x0A04]: 12080
[0x0A05]: 14128
```

---

## 🔧 Comandos Validados em Testes Reais

### ✅ FUNCIONAM

**Leitura de área completa:**
```bash
mbpoll -a 1 -r 1280 -c 10 -t 4 -b 57600 -P none -s 2 -1 /dev/ttyUSB0
```

**Escrita em 0x0500:**
```bash
mbpoll -a 1 -r 1280 -t 4 -b 57600 -P none -s 2 /dev/ttyUSB0 900
mbpoll -a 1 -r 1281 -t 4 -b 57600 -P none -s 2 /dev/ttyUSB0 1200
```

### ❌ NÃO FUNCIONAM

**Escrita em 0x0A00 (retorna "Invalid data"):**
```bash
mbpoll -a 1 -r 2560 -t 4 -b 57600 -P none -s 2 /dev/ttyUSB0 900
# Erro: Write output (holding) register failed: Invalid data
```

---

## 💡 Recomendações Finais

1. **USAR ÁREA 0x0500 para gravar ângulos** ✅
2. Ignorar área 0x0A00 (read-only)
3. Validar se valores gravados em 0x0500 persistem após reset do CLP
4. Testar escrita de múltiplos registradores de uma vez (função 0x10)
5. Analisar ladder para entender processamento dos valores
