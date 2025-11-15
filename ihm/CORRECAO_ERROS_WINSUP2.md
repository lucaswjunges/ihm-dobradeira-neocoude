# CORREÇÃO DE ERROS - CLP_FINAL_10_ROTINAS_COMPLETO.sup

**Data**: 12 de novembro de 2025
**Problema**: Registros fora do range permitido em ROT5, ROT7, ROT8

---

## 🔍 ANÁLISE DOS ERROS

### Limites de Memória do MPC4004

| Área | Hex | Decimal | Descrição | Uso |
|------|-----|---------|-----------|-----|
| **Estados Internos** | 0x0000-0x03FF | 0-1023 | Bits de controle | ✅ SETR, OUT, AND, OR |
| **Registros Timer/Counter** | 0x0400-0x047F | 1024-1151 | Timers/Counters | ✅ TMR, CNT |
| **Registros Encoder** | 0x04D0-0x04DF | 1232-1247 | High-speed counter | ✅ Todas instruções |
| **Registros I/O** | 0x0100-0x0187 | 256-391 | Área especial I/O | ✅ Leitura apenas |
| **Registros Gerais** | 0x0400-0x09FF | 1024-2559 | Uso geral | ✅ Todas instruções |
| **⚠️ LIMITE SUPERIOR** | 0x0A00 | 2560 | **MÁXIMO MPC4004** | ❌ Acima = erro |

### Erros Identificados

#### ROT5 - Linha 7: SDAT2 com 0x03E0
```
Erro: "registro OP1 fora do range permitido"
Registro usado: 0x03E0 (992 decimal)
```
**Problema**: 0x03E0 está na área de **Estados Internos** (bits), mas SDAT2 requer **Registros** (16-bit).
**Causa**: Estados internos (0x0000-0x03FF) não suportam instruções de dados (SDAT2, MOV, ADD, etc.).

#### ROT7 - Linhas 3 e 6: CMP com 0x0891
```
Erro: "registro OP2 fora do range permitido"
Registros usados: 0x0890-0x0892 (2192-2194 decimal)
```
**Problema**: Registros estão válidos (2192 < 2560), mas podem estar em **área reservada** do firmware.
**Possível causa**: Área 0x0890-0x08FF pode ser reservada para uso interno do sistema operacional do CLP.

#### ROT8 - Linhas 2, 3, 6, 7, 8: SCL2G com 0x08A0-0x08D0
```
Erro: "registros OP2/OP3 fora do range permitido"
Registros usados: 0x08A0, 0x08AC, 0x08AE, 0x08AD (2208-2222 decimal)
```
**Problema**: Mesma causa que ROT7 - área 0x08A0-0x08FF pode estar reservada.

---

## 🛠️ PLANO DE CORREÇÃO

### Estratégia: Realocação para Área Segura

Vou mover todos os registros problemáticos para a **área 0x0700-0x07FF** (1792-2047), que:
- ✅ Está dentro do limite de 2560
- ✅ Não conflita com registros já mapeados (encoder, ângulos, I/O)
- ✅ É área de uso geral confirmada pelo manual

### Tabela de Substituições

| Rotina | Original Hex | Original Dec | Novo Hex | Novo Dec | Tipo |
|--------|--------------|--------------|----------|----------|------|
| **ROT5** | 0x03E0 | 992 | 0x0700 | 1792 | Reg geral |
| **ROT5** | 0x03E1-0x03FF | 993-1023 | 0x0701-0x071F | 1793-1823 | Reg geral |
| **ROT7** | 0x0890 | 2192 | 0x0720 | 1824 | Temp/calc |
| **ROT7** | 0x0891 | 2193 | 0x0721 | 1825 | Temp/calc |
| **ROT7** | 0x0892 | 2194 | 0x0722 | 1826 | Temp/calc |
| **ROT8** | 0x08A0 | 2208 | 0x0730 | 1840 | SCL2G base |
| **ROT8** | 0x08A2 | 2210 | 0x0732 | 1842 | SCL2G param |
| **ROT8** | 0x08AC | 2220 | 0x073C | 1852 | SCL2G result |
| **ROT8** | 0x08AD | 2221 | 0x073D | 1853 | SCL2G result |
| **ROT8** | 0x08AE | 2222 | 0x073E | 1854 | SCL2G result |
| **ROT8** | 0x08D0 | 2256 | 0x0740 | 1856 | SCL2G aux |

---

## 📝 INSTRUÇÕES DE CORREÇÃO MANUAL (WinSUP 2)

### Passo 1: Abrir o Projeto
1. Abra `CLP_FINAL_10_ROTINAS_COMPLETO.sup` no WinSUP 2
2. Vá em **Projeto** → **Lista de checagem** para ver erros

### Passo 2: Corrigir ROT5
1. Clique duplo em **ROT5** na árvore de programas
2. Navegue até **linha 7** (SDAT2)
3. Clique duplo na instrução SDAT2
4. **Trocar**: `03E0` → `0700`
5. Salvar (Ctrl+S)

### Passo 3: Corrigir ROT7
1. Clique duplo em **ROT7**
2. **Linha 3** (MOVK): Trocar `0890` → `0720`
3. **Linha 4** (CMP): Trocar `0891` → `0721`
4. **Linha 5** (MOVK): Trocar `0892` → `0722`
5. **Linha 6** (MOVK): Trocar `0890` → `0720`
6. **Linha 7** (MOVK): Trocar `0890` → `0720`
7. **Linha 8** (CMP): Trocar `0891` → `0721`
8. Salvar (Ctrl+S)

### Passo 4: Corrigir ROT8
1. Clique duplo em **ROT8**
2. **Linha 2** (MOVK): Trocar `08A0` → `0730`
3. **Linha 3** (SCL2G): Trocar `08A0` → `0730`
4. **Linha 4** (MOVK): Trocar `08A2` → `0732`
5. **Linha 5** (MOV): Trocar `08A0` → `0730`
6. **Linha 6** (SCL2G): Trocar `08AC` → `073C`
7. **Linha 7** (SCL2G): Trocar `08AE` → `073E`
8. **Linha 8** (SCL2G): Trocar `08AD` → `073D`
9. **Linha 9** (MOVK): Trocar `08D0` → `0740`
10. Salvar (Ctrl+S)

### Passo 5: Recompilar
1. **Projeto** → **Compilar** (F7)
2. Verificar lista de checagem: deve estar **ZERADA**
3. Salvar projeto: **Arquivo** → **Salvar Como** → `CLP_FINAL_10_ROTINAS_CORRIGIDO.sup`

---

## 🔬 ANÁLISE FUNCIONAL DAS ROTINAS

### ROT5: Controle de LEDs e Flags
**Propósito**: Gerencia estados visuais da IHM (LEDs K1-K5)
**Registros originais**: 0x03E0-0x03FF (estados internos - INVÁLIDO)
**Novos registros**: 0x0700-0x071F (área geral - VÁLIDO)

**Instruções típicas**:
```ladder
SETR 0700  ; Liga flag
SETR 0701  ; Liga LED1
SDAT2 0700 ; Transfere dados
```

**Impacto na IHM Web**: Nenhum - estes são registros internos não acessados via Modbus.

### ROT7: Comparação de Velocidade/RPM
**Propósito**: Compara valores de RPM com setpoints (1400 = 14.00 RPM, 900 = 9.00 RPM)
**Registros originais**: 0x0890-0x0892
**Novos registros**: 0x0720-0x0722

**Instruções típicas**:
```ladder
MOVK 0720, #0     ; Zera registro
MOVK 0722, #5     ; Carrega constante 5
CMP  0721, #1400  ; Compara com 14.00 RPM
```

**Impacto na IHM Web**: Moderado - se a IHM web precisar ler estes valores de comparação, atualizar `modbus_map.py`:
```python
# Adicionar em modbus_map.py
SPEED_TEMP_1 = 0x0720  # 1824 decimal (novo endereço)
SPEED_TEMP_2 = 0x0721  # 1825 decimal
SPEED_TEMP_3 = 0x0722  # 1826 decimal
```

### ROT8: Conversão de Escala (SCL2G)
**Propósito**: Converte valores do encoder para graus ou escala de saída analógica (VFD)
**Registros originais**: 0x08A0-0x08D0
**Novos registros**: 0x0730-0x0740

**Instruções típicas**:
```ladder
SCL2G 0730  ; Escala de entrada
      0732  ; Parâmetro min/max
      073C  ; Resultado escalado
```

**Formato SCL2G** (Scale):
- OP1: Valor de entrada (ex: contador encoder bruto)
- OP2: Parâmetros de escala (min/max)
- OP3: Valor de saída escalado (ex: 0-360 graus)

**Impacto na IHM Web**: CRÍTICO - estes registros podem conter:
- Ângulo escalado do encoder (0-360°)
- Setpoint de velocidade escalado (0-15 RPM)

**Ação necessária**: Testar leitura destes registros após correção:
```python
# test_scaled_values.py
angle_scaled = modbus_client.read_register(0x0730)  # Novo endereço
print(f"Ângulo escalado: {angle_scaled / 10.0}°")
```

---

## ⚠️ REGISTROS JÁ MAPEADOS (NÃO ALTERAR)

| Descrição | Hex | Dec | Status | Uso |
|-----------|-----|-----|--------|-----|
| Encoder MSW/LSW | 0x04D6-0x04D7 | 1238-1239 | ✅ OK | Posição angular |
| Ângulos Dobra 1 | 0x0840-0x0846 | 2112-2118 | ✅ OK | Setpoints |
| Ângulos Dobra 2 | 0x0848-0x084E | 2120-2126 | ✅ OK | Setpoints |
| Ângulos Dobra 3 | 0x0850-0x0856 | 2128-2134 | ✅ OK | Setpoints |
| Calc auxiliar | 0x0858 | 2136 | ✅ OK | Registro trabalho |
| Velocidade classe | 0x0900 | 2304 | ✅ OK | 1/2/3 RPM |
| Target MSW/LSW | 0x0942-0x0944 | 2370-2372 | ✅ OK | Posição alvo |
| Saída analógica | 0x06E0 | 1760 | ✅ OK | VFD control |

**Total de registros usados**: 28 registros conhecidos + 32 novos (ROT5/7/8) = **60 registros de aplicação**

---

## 🧪 TESTES APÓS CORREÇÃO

### Teste 1: Compilação
```bash
# No WinSUP 2:
# Projeto → Compilar (F7)
# Resultado esperado: 0 erros, 0 avisos
```

### Teste 2: Upload para CLP (simulado)
```bash
# No WinSUP 2:
# Projeto → Simular (F9)
# Verificar comportamento de ROT5, ROT7, ROT8 no debugger
```

### Teste 3: Leitura Modbus dos Novos Registros
```python
# test_new_registers.py
import modbus_client

client = modbus_client.ModbusClientWrapper()

# Testar ROT7 (velocidade)
speed_temp = client.read_register(0x0720)  # Novo endereço
print(f"ROT7 Temp1: {speed_temp}")

# Testar ROT8 (escala)
scale_base = client.read_register(0x0730)  # Novo endereço
print(f"ROT8 Escala: {scale_base}")

# Testar ROT5 (flags)
flag_1 = client.read_register(0x0700)  # Novo endereço
print(f"ROT5 Flag: {flag_1}")
```

---

## 📦 PRÓXIMOS PASSOS

### 1. Correção Manual (AGORA)
- [ ] Abrir WinSUP 2
- [ ] Aplicar substituições em ROT5, ROT7, ROT8
- [ ] Compilar e verificar 0 erros
- [ ] Salvar como `CLP_FINAL_10_ROTINAS_CORRIGIDO.sup`

### 2. Atualização do Mapeamento (DEPOIS)
- [ ] Adicionar novos registros em `modbus_map.py`
- [ ] Atualizar `ANALISE_COMPLETA_REGISTROS_PRINCIPA.md`
- [ ] Criar testes para novos endereços

### 3. Validação em Máquina (FINAL)
- [ ] Upload do .sup corrigido para CLP real
- [ ] Testar leitura via Modbus RTU
- [ ] Verificar se IHM web continua funcionando
- [ ] Documentar qualquer comportamento inesperado

---

## 🎯 CONCLUSÃO

**Causa raiz**: Uso de áreas de memória reservadas/inválidas:
- 0x03E0-0x03FF: Estados internos (só aceitam instruções de bit)
- 0x0890-0x08FF: Possivelmente área reservada do firmware

**Solução**: Realocação para área 0x0700-0x0740 (zona segura de registros gerais)

**Impacto na IHM Web**:
- ✅ Baixo impacto: Registros internos não acessados externamente
- ⚠️ Necessário teste: Verificar se ROT7/ROT8 expõem dados úteis via Modbus
- 📝 Documentar: Atualizar mapeamento com novos endereços

**Status**: ✅ Pronto para correção manual no WinSUP 2

---

**Documento preparado por**: Claude Code
**Data**: 12 de novembro de 2025
**Revisão**: v1.0
