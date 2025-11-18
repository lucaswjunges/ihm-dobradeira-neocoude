# CORREÇÃO FINAL - SISTEMA DE ÂNGULOS

**Data:** 18 de Novembro de 2025
**Status:** ✅ Implementado e pronto para teste com CLP

---

## 🎯 Problema Identificado

O código estava usando a **área 0x0500** que **NÃO EXISTE** no ladder logic do CLP. Análise completa do arquivo `clp_MODIFICADO_IHM_WEB_COM_ROT5.sup` revelou a arquitetura correta.

---

## 📋 Solução Implementada

### 1. **Área de Escrita: 0x0A00 (MODBUS INPUT)**

A IHM Web deve **ESCREVER** ângulos nesta área, que é monitorada pelo ROT5.lad:

| Dobra | MSW (bits 31-16) | LSW (bits 15-0) | Trigger (COIL) |
|-------|------------------|-----------------|----------------|
| 1     | 0x0A00 (2560)    | 0x0A02 (2562)   | 0x0390 (912)   |
| 2     | 0x0A04 (2564)    | 0x0A06 (2566)   | 0x0391 (913)   |
| 3     | 0x0A08 (2568)    | 0x0A0A (2570)   | 0x0392 (914)   |

**Formato:** 32-bit (MSW/LSW)
**Conversão:** `value_clp = graus * 10`

---

### 2. **Protocolo de Escrita**

```python
# Exemplo: Gravar 90.5° na Dobra 1
degrees = 90.5
value_32bit = int(degrees * 10)  # = 905
msw = (value_32bit >> 16) & 0xFFFF  # = 0
lsw = value_32bit & 0xFFFF          # = 905

# 1. Escrever MSW
write_register(0x0A00, msw)  # Function 0x06

# 2. Escrever LSW
write_register(0x0A02, lsw)  # Function 0x06

# 3. Ativar trigger via COIL (não registro!)
write_coil(0x0390, True)     # Function 0x05
sleep(100ms)                 # Aguardar 2 scans CLP

# 4. Desativar trigger
write_coil(0x0390, False)    # Function 0x05
```

**IMPORTANTE:** Triggers **DEVEM** ser acionados via `write_coil()` (Function 0x05), **NÃO** via `write_register()`.

---

### 3. **Área de Leitura: 0x0B00 (SCADA MIRROR)**

A IHM Web deve **LER** ângulos desta área, que é automaticamente sincronizada pelo ROT5.lad:

| Dobra | LSW (bits 15-0) | MSW (bits 31-16) | Espaçamento |
|-------|-----------------|------------------|-------------|
| 1     | 0x0B00 (2816)   | 0x0B02 (2818)    | GAP = 2     |
| 2     | 0x0B04 (2820)   | 0x0B06 (2822)    | GAP = 2     |
| 3     | 0x0B08 (2824)   | 0x0B0A (2826)    | GAP = 2     |

**Atenção ao GAP:** Entre LSW e MSW há um intervalo de 2 registros (não consecutivos).

---

### 4. **Protocolo de Leitura**

```python
# Exemplo: Ler Dobra 1 (área SCADA)
addr_lsw = 0x0B00
addr_msw = 0x0B02  # LSW + 2 (pulando 1 registro)

lsw = read_register(addr_lsw)
msw = read_register(addr_msw)

value_32bit = (msw << 16) | lsw
degrees = value_32bit / 10.0
```

---

## 🔄 Fluxo Completo de Dados

```
┌──────────────────────────────────────────────────────────────┐
│  IHM WEB (ESP32)                                             │
│  Usuário digita: 90.5°                                       │
└─────────────────┬────────────────────────────────────────────┘
                  │
                  │ write_bend_angle(1, 90.5)
                  │
                  ▼ ESCRITA (Modbus Function 0x06 + 0x05)
┌──────────────────────────────────────────────────────────────┐
│  ÁREA MODBUS INPUT (0x0A00)                                  │
│  MSW: 0x0A00 = 0      ┐                                      │
│  LSW: 0x0A02 = 905    ├─ 32-bit value = 905                 │
│  Trigger: 0x0390 = ON ┘                                      │
└─────────────────┬────────────────────────────────────────────┘
                  │
                  │ ROT5.lad Lines 7-8 (auto-copy quando trigger ativo)
                  │ MOV 0x0A00 → 0x0842
                  │ MOV 0x0A02 → 0x0840
                  │
                  ▼
┌──────────────────────────────────────────────────────────────┐
│  ÁREA SHADOW (0x0840) - Registros Oficiais                  │
│  LSW: 0x0840 = 905    ┐                                      │
│  MSW: 0x0842 = 0      ├─ PRINCIPAL.lad lê daqui!            │
└─────────────────┬────────────────────────────────────────────┘
                  │
                  │ ROT5.lad Line 13 (sempre ativo, sem trigger)
                  │ MOV 0x0840 → 0x0B00
                  │
                  ▼
┌──────────────────────────────────────────────────────────────┐
│  ÁREA SCADA (0x0B00) - Espelho Read-Only                     │
│  LSW: 0x0B00 = 905    ┐                                      │
│  MSW: 0x0B02 = 0      ├─ IHM lê daqui!                      │
└─────────────────┬────────────────────────────────────────────┘
                  │
                  │ read_bend_angle(1)
                  │
                  ▼ LEITURA (Modbus Function 0x03)
┌──────────────────────────────────────────────────────────────┐
│  IHM WEB (ESP32)                                             │
│  Mostra: 90.5° (validado!)                                   │
└──────────────────────────────────────────────────────────────┘
```

---

## 📝 Arquivos Modificados

### 1. `modbus_map.py`

**Linha 103-118:** Corrigido `BEND_ANGLES_MODBUS_INPUT`
- ❌ Removido área 0x0500 (não existe no ladder)
- ✅ Adicionado área 0x0A00 (validada no ROT5.lad)
- ✅ Triggers como COILS (0x0390/0x0391/0x0392)

**Linha 138-152:** Mantido `BEND_ANGLES_SCADA` (já estava correto)

---

### 2. `modbus_client_esp32.py`

**write_bend_angle() - Linha 131-201:**
- ✅ Usa área 0x0A00/0x0A02 para escrita
- ✅ Triggers acionados via `write_coil()` (Function 0x05)
- ✅ Documentação completa do fluxo ROT5

**read_bend_angle() - Linha 203-242 (NOVO):**
- ✅ Lê da área SCADA (0x0B00)
- ✅ Usa `read_register_32bit_scada()` com gap handling
- ✅ Conversão automática para graus

---

### 3. `test_angles_complete.py` (NOVO)

Script de teste com 4 cenários:

1. **test_write_angles():** Escreve 3 ângulos diferentes
2. **test_read_angles():** Lê 3 ângulos da área SCADA
3. **test_write_read_cycle():** Ciclo completo com validação (tolerância 0.2°)
4. **test_direct_register_access():** Debug mostrando todas as áreas (0x0A00, 0x0840, 0x0B00)

---

## 🧪 Como Testar

### Pré-requisitos

1. CLP ligado
2. RS485 conectado (GPIO17/16 no ESP32 ou /dev/ttyUSB0 no Ubuntu)
3. Estado `0x00BE` (190) = ON no ladder (habilita Modbus slave)

### Executar Teste

```bash
cd /home/lucas-junges/Documents/clientes/w&co/ihm_esp32
python3 test_angles_complete.py
```

### Saída Esperada

```
🔌 Conectando ao CLP...
✅ CLP conectado!

TESTE 1: ESCRITA DE ÂNGULOS (área 0x0A00 + triggers)
📝 Gravando Dobra 1: 90.5°
   ✅ Sucesso! Dobra 1 = 90.5°
...

TESTE 2: LEITURA DE ÂNGULOS (área SCADA 0x0B00)
📖 Lendo Dobra 1...
   ✅ Dobra 1 = 90.5°
...

TESTE 3: CICLO COMPLETO (escrita + leitura + validação)
🔄 Testando Dobra 1: 135.0°
   1️⃣ Gravando 135.0°...
   2️⃣ Lendo de volta...
   3️⃣ Validando...
      Esperado: 135.0°
      Lido:     135.0°
      Diferença: 0.0°
   ✅ PASSOU! (diff=0.0° < 0.2°)
...
```

---

## ⚠️ Troubleshooting

### Erro: "Timeout ao escrever registro 0x0A00"

**Causa:** Área pode estar protegida
**Solução:** Verificar se ROT5.lad está carregado no CLP

### Erro: "Leitura retorna 0.0° sempre"

**Causa:** Trigger não foi acionado corretamente
**Solução:** Garantir que `write_coil()` está sendo usado (não `write_register()`)

### Erro: "Diferença entre escrito e lido > 0.2°"

**Causa:** Timing issue - ROT5 ainda não copiou
**Solução:** Aumentar `sleep(0.5)` para `sleep(1.0)` após escrita

### Erro: "Connection refused"

**Causa:** CLP não está em modo Modbus slave
**Solução:** Forçar estado `0x00BE` (190) = ON no ladder

---

## ✅ Checklist de Validação

- [ ] Teste 1 PASSOU (escrita sem erros)
- [ ] Teste 2 PASSOU (leitura sem erros)
- [ ] Teste 3 PASSOU (validação dentro da tolerância)
- [ ] Teste 4 mostra valores coerentes em todas as áreas (0x0A00, 0x0840, 0x0B00)
- [ ] Valores persistem após reiniciar ESP32 (CLP mantém valores)

---

## 📚 Referências Técnicas

### Ladder Logic Analisado

- **ROT5.lad Lines 7-12:** Cópia automática 0x0A00 → 0x0840 (com triggers)
- **ROT5.lad Line 13:** Cópia automática 0x0840 → 0x0B00 (sem trigger)
- **Principal.lad Lines 8-10:** Cálculos usando 0x0840/0x0842/etc

### Funções Modbus Usadas

- **Function 0x03:** Read Holding Registers (leitura)
- **Function 0x05:** Force Single Coil (triggers)
- **Function 0x06:** Write Single Register (escrita MSW/LSW)

### Áreas de Memória

| Área | Endereço | Uso | Acesso |
|------|----------|-----|--------|
| MODBUS INPUT | 0x0A00-0x0A0A | IHM escreve aqui | R/W |
| SHADOW | 0x0840-0x0852 | Ladder lê daqui | R/W (protegido) |
| SCADA MIRROR | 0x0B00-0x0B0A | IHM lê daqui | Read-Only |

---

**Desenvolvido por:** Eng. Lucas William Junges
**Validado com:** clp_MODIFICADO_IHM_WEB_COM_ROT5.sup
**Próximo passo:** Testar com CLP real conectado
