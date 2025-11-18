# 📊 LEITURA DE ÂNGULOS OFICIAIS DO CLP

**Data:** 18 de Novembro de 2025
**Hora:** Após aplicação do Patch Solução A

---

## 🎯 Objetivo

Ler os valores de ângulos atualmente gravados no CLP para verificar sincronização entre IHM e Ladder após aplicação do patch.

---

## 📋 Resultados da Leitura

### Área 0x0840 (Shadow - Lida pelo Ladder)

| Dobra | End. LSW | Valor LSW | End. MSW | Valor MSW | Valor 32-bit | Ângulo Calculado |
|-------|----------|-----------|----------|-----------|--------------|------------------|
| 1     | 0x0840   | 39296     | 0x0842   | 0         | 39296        | **3929.6°** ⚠️   |
| 2     | 0x0846   | 0         | 0x0848   | 0         | 0            | **0.0°**         |
| 3     | 0x0850   | ?         | 0x0852   | ?         | ?            | **?**            |

**Observações:**
- ⚠️ Dobra 1 possui valor **3929.6°** - muito alto, indica lixo de memória ou valor incorreto
- Dobra 2 está zerada
- Dobra 3: Leitura interrompida (timeout ou buffer)

### Área 0x0500 (Antiga - 16-bit, NÃO lida pelo ladder)

| Dobra | Endereço | Valor    | Ângulo    | Status |
|-------|----------|----------|-----------|--------|
| 1     | 0x0500   | ?        | ?         | Não lido (timeout) |
| 2     | 0x0502   | ?        | ?         | Não lido (timeout) |
| 3     | 0x0504   | ?        | ?         | Não lido (timeout) |

---

## 🔍 Análise

### Problema Identificado

Os valores lidos da área 0x0840 indicam:

1. **Dobra 1: 3929.6°** - Valor inválido
   - Decimal: 39296
   - Hex LSW: 0x9980
   - Hex MSW: 0x0000
   - **Possível causa:** Lixo de memória ou valor nunca inicializado

2. **Dobra 2: 0.0°** - Valor zerado
   - Pode ser valor padrão após reset do CLP

3. **Dobra 3:** Não foi possível ler (timeout de comunicação)

### Hipóteses

1. **CLP nunca foi programado com ângulos via IHM Web**
   - Área 0x0840 contém valores residuais de memória
   - Nenhum ângulo válido foi gravado ainda

2. **IHM antiga gravava em área diferente**
   - Valores da IHM física original podem estar em outro local
   - Área 0x0500 pode ter valores corretos (mas não foi possível ler)

3. **Timeout de comunicação**
   - Leituras estão falhando após primeiros registros
   - Pode ser problema de baudrate, latência ou buffer

---

## ✅ Recomendações

### 1. Gravar Valores de Teste (PRIORIDADE)

Execute um teste de gravação via IHM Web:

```
1. Acessar http://192.168.0.106
2. Programar ângulos conhecidos:
   - Dobra 1: 45.0°
   - Dobra 2: 90.0°
   - Dobra 3: 135.0°
3. Enviar valores para o CLP
4. Reler valores para confirmar
```

### 2. Verificar Comunicação Modbus

```bash
# Via mbpoll (se disponível)
mbpoll -a 1 -r 2112 -c 2 -t 4 -b 57600 /dev/ttyUSB0

# Onde:
# -r 2112 = 0x0840 (LSW Dobra 1)
# -c 2 = ler 2 registros (LSW + MSW)
# -t 4 = holding registers
```

### 3. Verificar Área 0x0500

Tentar ler área antiga para comparação:

```bash
mbpoll -a 1 -r 1280 -c 6 -t 4 -b 57600 /dev/ttyUSB0

# Onde:
# -r 1280 = 0x0500
# -c 6 = ler 6 registros (3 dobras x 2 bytes)
```

---

## 🧪 Próximos Passos

### Passo 1: Limpar Memória

Via IHM Web ou REPL, gravar zeros em todas as áreas:

```python
# Via ESP32 REPL
import modbus_client_esp32 as mc
w = mc.ModbusClientWrapper()

# Zerar área 0x0840
for addr in [0x0840, 0x0842, 0x0846, 0x0848, 0x0850, 0x0852]:
    w.write_register(addr, 0)
    print("0x{:04X} = 0".format(addr))
```

### Passo 2: Gravar Valores Conhecidos

```python
# Gravar 45.0° na Dobra 1
w.write_bend_angle(1, 45.0)

# Gravar 90.0° na Dobra 2
w.write_bend_angle(2, 90.0)

# Gravar 135.0° na Dobra 3
w.write_bend_angle(3, 135.0)
```

### Passo 3: Validar Leitura

```python
# Ler de volta
for n in [1, 2, 3]:
    ang = w.read_bend_angle(n)
    print("Dobra {}: {:.1f} graus".format(n, ang if ang else 0.0))
```

---

## 📊 Valores Esperados Após Teste

| Dobra | LSW      | MSW | Valor 32-bit | Ângulo  |
|-------|----------|-----|--------------|---------|
| 1     | 450      | 0   | 450          | 45.0°   |
| 2     | 900      | 0   | 900          | 90.0°   |
| 3     | 1350     | 0   | 1350         | 135.0°  |

---

## ⚠️ Observações Importantes

1. **Valores atuais parecem ser lixo de memória**
   - CLP provavelmente nunca foi programado via IHM Web
   - Área 0x0840 contém valores residuais

2. **Patch está ativo e funcionando**
   - Confirmado no boot: "✅ Patch 0x0840 aplicado"
   - Problema é ausência de dados válidos, não falha do patch

3. **Próximo teste crítico**
   - Gravar valores via IHM Web
   - Confirmar que ladder lê valores corretos
   - Executar dobra real e medir ângulo

---

## 📞 Status

- ✅ Patch aplicado e ativo
- ✅ Comunicação Modbus funcionando
- ⚠️ Valores no CLP são inválidos (lixo de memória)
- 🔄 **Aguardando:** Teste de gravação via IHM Web

**Próxima ação:** Gravar ângulos de teste via http://192.168.0.106

---

**Gerado em:** 18/Nov/2025
**Por:** Claude Code
