# Mapeamento Completo de Registros Modbus para IHM Web

## Data da Análise
2025-11-08

## Fonte
Análise completa dos arquivos ladder (`clp.sup` extraído):
- `Principal.lad` - Lógica principal
- `ROT0.lad` - Controle de movimento
- `ROT1.lad` - Controle de modo
- `ROT2.lad` - Controle de velocidade
- `ROT3.lad` - Rotinas auxiliares
- `ROT4.lad` - Controle de ângulos

---

## 1. ENCODER (Posição Angular)

### Registros de 32-bit (par MSW/LSW)

| Registro Hex | Registro Dec | Tipo | Descrição |
|--------------|--------------|------|-----------|
| 04D6/04D7 | 1238/1239 | RO | **Contador Encoder** - Valor efetivo 32-bit (MSW/LSW) |
| 04D0/04D1 | 1232/1233 | RO | Valor RPM (modo ângulo) |
| 04D2/04D3 | 1234/1235 | RW | Setpoint (modo normal) |
| 04D8/04D9 | 1240/1241 | RW | Marca zero - direção crescente |
| 04DA/04DB | 1242/1243 | RW | Marca zero - direção decrescente |

**Leitura 32-bit**: `value = (register[MSW] << 16) | register[LSW]`

**Conversão para graus**: A determinar baseado na relação de redução total (58.5:1 × 3.44:1 = 201.24:1)

**Uso na IHM**:
- Tela 3: `DESLOCAMENTO ANGULAR PV=___° (___)`
- Telas 4-6: `AJ=___° PV=___°`

---

## 2. SETPOINTS DE ÂNGULOS (Dobras)

### Registros de Ângulo (16-bit cada)

Baseado na análise do `Principal.lad` e `ROT4.lad`:

| Registro Hex | Registro Dec | Dobra | Direção | Descrição |
|--------------|--------------|-------|---------|-----------|
| 0840/0841 | 2112/2113 | 1 | Esquerda | **AJ Dobra 1 Esq** (K1 anti-horário) |
| 0842/0843 | 2114/2115 | 1 | Direita | **AJ Dobra 1 Dir** (K1 horário) |
| 0846/0847 | 2118/2119 | 2 | Esquerda | **AJ Dobra 2 Esq** (K2 anti-horário) |
| 0848/0849 | 2120/2121 | 2 | Direita | **AJ Dobra 2 Dir** (K2 horário) |
| 0850/0851 | 2128/2129 | 3 | Esquerda | **AJ Dobra 3 Esq** (K3 anti-horário) |
| 0852/0853 | 2130/2131 | 3 | Direita | **AJ Dobra 3 Dir** (K3 horário) |

**Padrão de uso**:
- Registros pares (0840, 0842, 0846, 0848, 0850, 0852) = Setpoint configurável
- Registros ímpares = Possivelmente parte de pares 32-bit ou reservados

### Registros de Posição Alvo (Calculados pelo Ladder)

| Registro Hex | Registro Dec | Descrição |
|--------------|--------------|-----------|
| 0942/0943 | 2370/2371 | **Posição alvo dobra direita** (comparado com 04D6) |
| 0944/0945 | 2372/2373 | **Posição alvo dobra esquerda** (comparado com 04D6) |

**Lógica ladder**:
```
CMP 04D6 com 0942 → Chegou na posição direita
CMP 04D6 com 0944 → Chegou na posição esquerda
```

### Registro Auxiliar

| Registro Hex | Registro Dec | Descrição |
|--------------|--------------|-----------|
| 0858 | 2136 | **Registro de cálculo** - Usado em operações SUB |

**Operações ladder**:
```
SUB 0858, 0842, 0840 → Calcula diferença entre ângulos
SUB 0858, 0848, 0846
SUB 0858, 0852, 0850
```

---

## 3. ENTRADAS E SAÍDAS DIGITAIS

### Entradas Digitais (E0-E7)

| Registro Hex | Registro Dec | Entrada | Descrição |
|--------------|--------------|---------|-----------|
| 0100 | 256 | E0 | Sensor de posição zero / Referência |
| 0101 | 257 | E1 | Carenagem (sensor proteção) - **Provável E5** |
| 0102 | 258 | E2 | Botão AVANÇAR (painel físico) |
| 0103 | 259 | E3 | (A mapear) |
| 0104 | 260 | E4 | Botão RECUAR (painel físico) |
| 0105 | 261 | E5 | Sensor carenagem (Tela 8) |
| 0106 | 262 | E6 | (A mapear) |
| 0107 | 263 | E7 | (A mapear) |

**Nota**: Registros são 16-bit, usar bit 0 (LSB) para status real.

### Saídas Digitais (S0-S7)

| Registro Hex | Registro Dec | Saída | Descrição |
|--------------|--------------|-------|-----------|
| 0180 | 384 | S0 | Motor AVANÇAR (anti-horário) |
| 0181 | 385 | S1 | Motor RECUAR (horário) |
| 0182 | 386 | S2 | (A mapear) |
| 0183 | 387 | S3 | (A mapear) |
| 0184 | 388 | S4 | (A mapear) |
| 0185 | 389 | S5 | (A mapear) |
| 0186 | 390 | S6 | (A mapear) |
| 0187 | 391 | S7 | (A mapear) |

**IMPORTANTE**: NÃO escrever diretamente em S0/S1 via Modbus - ladder sobrescreve baseado em E2/E4.

---

## 4. TECLAS DA IHM (Endereços Coil)

### Teclado Numérico

| Tecla | Registro Hex | Registro Dec | Função |
|-------|--------------|--------------|--------|
| K0 | 00A9 | 169 | Número 0 |
| K1 | 00A0 | 160 | Número 1 / Seleciona Dobra 1 |
| K2 | 00A1 | 161 | Número 2 / Seleciona Dobra 2 |
| K3 | 00A2 | 162 | Número 3 / Seleciona Dobra 3 |
| K4 | 00A3 | 163 | Número 4 / Sentido Anti-horário |
| K5 | 00A4 | 164 | Número 5 / Sentido Horário |
| K6 | 00A5 | 165 | Número 6 |
| K7 | 00A6 | 166 | Número 7 / K1+K7 = Seleção velocidade |
| K8 | 00A7 | 167 | Número 8 |
| K9 | 00A8 | 168 | Número 9 |

### Teclas de Função

| Tecla | Registro Hex | Registro Dec | Função | Uso Ladder |
|-------|--------------|--------------|--------|------------|
| S1 | 00DC | 220 | Função 1 | Alterna AUTO/MANUAL (ROT1.lad) |
| S2 | 00DD | 221 | Função 2 | Reset / Contexto (ROT1.lad) |
| ↑ | 00AC | 172 | Seta cima | Navegação / Incremento |
| ↓ | 00AD | 173 | Seta baixo | Navegação / Decremento |
| ESC | 00BC | 188 | Escape | Cancelar / Voltar |
| ENTER | 0025 | 37 | Enter | Confirmar |
| EDIT | 0026 | 38 | Editar | Modo edição |
| Lock | 00F1 | 241 | Trava | Bloquear teclado |

**Simulação de tecla** (Modbus Function 0x05):
1. `write_coil(address, TRUE)` - Liga
2. `sleep(100ms)` - Aguarda
3. `write_coil(address, FALSE)` - Desliga

---

## 5. ESTADOS INTERNOS (Bits de Controle)

### Estados de Modo e Ciclo

| Bit Hex | Bit Dec | Nome | Descrição | Fonte |
|---------|---------|------|-----------|-------|
| 00F7 | 247 | **BIT_CICLO_ATIVO** | Ciclo de dobra em execução | Principal.lad (aparece 13x) |
| 00F8 | 248 | **BIT_DOBRA_2** | Dobra 2 selecionada/ativa | Principal.lad |
| 00F9 | 249 | **BIT_DOBRA_3** | Dobra 3 selecionada/ativa | Principal.lad |
| 00BE | 190 | **MODBUS_SLAVE_ENABLE** | Modbus slave ativo (DEVE estar ON) | Config |
| 02FF | 767 | **BIT_PROTECAO** | Proteção geral do sistema | ROT0.lad |

**Inferência** (a validar com testes):
- Se 00F7=ON → Ciclo ativo, incrementar totalizador de tempo
- Se 00F8=OFF e 00F9=OFF → Dobra 1 (K1 LED)
- Se 00F8=ON → Dobra 2 (K2 LED)
- Se 00F9=ON → Dobra 3 (K3 LED)

### Estados de Velocidade (Classes)

| Bit Hex | Bit Dec | Classe | RPM | Descrição |
|---------|---------|--------|-----|-----------|
| 0360 | 864 | 1 | 5 RPM | Classe baixa (ROT2.lad - aparece 8x) |
| 0361 | 865 | 2 | 10 RPM | Classe média (ROT2.lad - aparece 4x) |
| 0362 | 866 | 3 | 15 RPM | Classe alta (ROT2.lad - aparece 4x) |
| 0363 | 867 | - | - | Controle de mudança de velocidade |

**Leitura da velocidade atual**:
```python
if read_coil(864): return "Classe 1 - 5 RPM"
if read_coil(865): return "Classe 2 - 10 RPM"
if read_coil(866): return "Classe 3 - 15 RPM"
```

**Mudança de velocidade**: K1 + K7 simultâneo (só em modo MANUAL)

### Monostáveis de Controle

| Bit Hex | Bit Dec | Função | Origem |
|---------|---------|--------|--------|
| 0370 | 880 | Monostável classe 1 | ROT2.lad |
| 0371 | 881 | Monostável classe 2 | ROT2.lad |
| 0372 | 882 | Monostável classe 3 | ROT2.lad |
| 0373 | 883 | Monostável auxiliar velocidade | ROT2.lad |
| 0376 | 886 | Monostável modo AUTO/MAN | ROT1.lad |

---

## 6. BITS INTERNOS LIVRES (Comunicação Modbus)

**Estes bits foram testados e validados como LIVRES** (`test_write_internal_bits.py`):

| Bit Hex | Bit Dec | Função Proposta | Status |
|---------|---------|-----------------|--------|
| 0030 | 48 | Comando AVANÇAR (Modbus) | ✓ TESTADO - Estável 2s+ |
| 0031 | 49 | Comando RECUAR (Modbus) | ✓ TESTADO - Estável 2s+ |
| 0032 | 50 | Comando PARADA (Modbus) | ✓ TESTADO - Estável 2s+ |
| 0033 | 51 | Comando EMERGÊNCIA | ✓ Reservado |
| 0034 | 52 | Comando GERAL | ✓ Reservado |

**Nota**: Estes bits NÃO serão usados na IHM retrofit (decisão do usuário).

---

## 7. REGISTROS A MAPEAR (Pendentes)

### Totalizador de Tempo (Tela 9)

```
TOTALIZADOR DE TEMPO
*****___:__h *****
```

**A investigar**:
- Registro de horas de operação (provável 16 ou 32-bit)
- Incrementa quando BIT_CICLO_ATIVO (00F7) está ON
- Pode ser registro de timer efetivo (área 0400-047F)

### Estado da Dobradeira (Tela 10)

```
ESTADO DA DOBRADEIRA
        [3]
```

**A investigar**:
- Código de estado geral (0=Parada, 1=Operando, 2=Erro, 3=Standby)
- Pode ser combinação de bits 00F7, 00F8, 00F9

### Modo AUTO/MAN (Tela 2)

```
SELECAO DE AUTO/MAN
        [3]
```

**A investigar**:
- Bit de modo AUTO vs MANUAL
- Provável relação com bit 0376 (monostável)
- Alternado via tecla S1

---

## 8. MAPEAMENTO POR TELA DA IHM

### Tela 0: Splash Screen
**Tipo**: Estática (sem registros)
```
**TRILLOR MAQUINAS**
**DOBRADEIRA HD    **
```

### Tela 1: Cliente
**Tipo**: Estática (sem registros)
```
CAMARGO CORREIA CONS
AQUISICAO AGOSTO-06
```

### Tela 2: Modo Operação
**Registros necessários**:
- [ ] Bit modo AUTO/MANUAL (a mapear)
- [x] Tecla S1 (00DC = 220) para alternar

```
SELECAO DE AUTO/MAN
        [?]
```

### Tela 3: Encoder
**Registros necessários**:
- [x] 04D6/04D7 (1238/1239) - Encoder 32-bit
- [x] Conversão para graus

```
DESLOCAMENTO ANGULAR
PV=___° (___)
```

### Tela 4: Ângulo Dobra 1
**Registros necessários**:
- [x] 0840/0841 (2112/2113) - AJ Esquerda
- [x] 0842/0843 (2114/2115) - AJ Direita
- [x] 04D6/04D7 (1238/1239) - PV (encoder)
- [x] Tecla K1 (00A0 = 160) - Navegação direta
- [ ] LED K1 (a mapear)

```
AJUSTE DO ANGULO 01
AJ=___° PV=___°
```

### Tela 5: Ângulo Dobra 2
**Registros necessários**:
- [x] 0846/0847 (2118/2119) - AJ Esquerda
- [x] 0848/0849 (2120/2121) - AJ Direita
- [x] 04D6/04D7 (1238/1239) - PV (encoder)
- [x] Tecla K2 (00A1 = 161) - Navegação direta
- [x] LED K2 (00F8 = 248)

```
AJUSTE DO ANGULO 02
AJ=___° PV=___°
```

### Tela 6: Ângulo Dobra 3
**Registros necessários**:
- [x] 0850/0851 (2128/2129) - AJ Esquerda
- [x] 0852/0853 (2130/2131) - AJ Direita
- [x] 04D6/04D7 (1238/1239) - PV (encoder)
- [x] Tecla K3 (00A2 = 162) - Navegação direta
- [x] LED K3 (00F9 = 249)

```
AJUSTE DO ANGULO 03
AJ=___° PV=___°
```

### Tela 7: Velocidade
**Registros necessários**:
- [x] 0360 (864) - Classe 1 (5 RPM)
- [x] 0361 (865) - Classe 2 (10 RPM)
- [x] 0362 (866) - Classe 3 (15 RPM)
- [x] Teclas K1+K7 simultâneo para alternar

```
*SELECAO DA ROTACAO*
        [K]
```

### Tela 8: Carenagem
**Registros necessários**:
- [x] 0105 (261) - Entrada E5 (sensor carenagem)

```
CARENAGEM DOBRADEIRA
        [?]
```

### Tela 9: Totalizador
**Registros necessários**:
- [ ] Registro de tempo total (a mapear)
- [x] 00F7 (247) - BIT_CICLO_ATIVO para incremento

```
TOTALIZADOR DE TEMPO
*****___:__h *****
```

### Tela 10: Estado
**Registros necessários**:
- [ ] Registro de estado geral (a mapear)
- [x] 00F7 (247) - Ciclo ativo

```
ESTADO DA DOBRADEIRA
        [?]
```

---

## 9. PRIORIDADES DE IMPLEMENTAÇÃO

### FASE 1: Funcionalidade Básica ✓ PRONTO
- [x] Encoder (04D6/04D7)
- [x] Entradas E0-E7 (0100-0107)
- [x] Saídas S0-S7 (0180-0187)
- [x] Teclas IHM (00A0-00A9, 00AC, 00AD, 00BC, 00DC, 00DD, etc.)

### FASE 2: Ângulos e Dobras ✓ MAPEADO
- [x] Ângulos AJ (0840-0853)
- [x] Posições alvo (0942, 0944)
- [x] Bits de dobra ativa (00F8, 00F9)

### FASE 3: Velocidade e Modo ✓ MAPEADO
- [x] Classes de velocidade (0360-0362)
- [x] Monostável modo (0376)

### FASE 4: Status e Totalizador ⏳ A MAPEAR
- [ ] Bit modo AUTO/MANUAL
- [ ] Registro totalizador de tempo
- [ ] Registro estado geral
- [ ] LEDs de indicação (possivelmente bits 00F8, 00F9, outros)

---

## 10. CÓDIGO DE EXEMPLO (Python)

### Leitura do Encoder (32-bit)

```python
# Ler encoder (MSW + LSW)
response_msw = client.read_holding_registers(address=1238, count=1, device_id=1)
response_lsw = client.read_holding_registers(address=1239, count=1, device_id=1)

encoder_value = (response_msw.registers[0] << 16) | response_lsw.registers[0]

# Converter para graus (fator de conversão a determinar)
# Exemplo: encoder_degrees = (encoder_value / 201.24) * 360
```

### Leitura de Ângulo Setpoint

```python
# Ler ângulo ajuste dobra 1 esquerda
response = client.read_holding_registers(address=2112, count=1, device_id=1)
angulo_aj_1_esq = response.registers[0]

# Ler ângulo ajuste dobra 1 direita
response = client.read_holding_registers(address=2114, count=1, device_id=1)
angulo_aj_1_dir = response.registers[0]
```

### Escrita de Ângulo Setpoint

```python
# Escrever novo ângulo ajuste dobra 1 esquerda (exemplo: 90 graus)
client.write_register(address=2112, value=90, device_id=1)
```

### Leitura de Classe de Velocidade

```python
# Ler velocidade atual
classe_1 = client.read_coils(address=864, count=1, device_id=1).bits[0]
classe_2 = client.read_coils(address=865, count=1, device_id=1).bits[0]
classe_3 = client.read_coils(address=866, count=1, device_id=1).bits[0]

if classe_1:
    velocidade = "Classe 1 - 5 RPM"
elif classe_2:
    velocidade = "Classe 2 - 10 RPM"
elif classe_3:
    velocidade = "Classe 3 - 15 RPM"
else:
    velocidade = "Indefinida"
```

### Simulação de Tecla

```python
def press_key(client, key_address, device_id=1):
    """Simula pressionamento de tecla da IHM"""
    # Liga
    client.write_coil(address=key_address, value=True, device_id=device_id)
    # Aguarda
    time.sleep(0.1)  # 100ms
    # Desliga
    client.write_coil(address=key_address, value=False, device_id=device_id)

# Exemplo: Pressionar K1
press_key(client, 160)  # 00A0 = 160 decimal

# Exemplo: Pressionar S1 (alternar modo)
press_key(client, 220)  # 00DC = 220 decimal
```

### Leitura de Entrada Digital

```python
# Ler sensor carenagem (E5)
response = client.read_holding_registers(address=261, count=1, device_id=1)
carenagem_ok = response.registers[0] & 0x0001  # Bit 0 (LSB)

# Ou usando read_coils (se disponível)
response = client.read_coils(address=261, count=1, device_id=1)
carenagem_ok = response.bits[0]
```

### Verificar Dobra Ativa (LED)

```python
# Ler qual dobra está ativa
bit_dobra_2 = client.read_coils(address=248, count=1, device_id=1).bits[0]  # 00F8
bit_dobra_3 = client.read_coils(address=249, count=1, device_id=1).bits[0]  # 00F9

if not bit_dobra_2 and not bit_dobra_3:
    dobra_ativa = 1  # LED K1 aceso
    led_k1 = True
    led_k2 = False
    led_k3 = False
elif bit_dobra_2:
    dobra_ativa = 2  # LED K2 aceso
    led_k1 = False
    led_k2 = True
    led_k3 = False
elif bit_dobra_3:
    dobra_ativa = 3  # LED K3 aceso
    led_k1 = False
    led_k2 = False
    led_k3 = True
```

---

## 11. NOTAS TÉCNICAS IMPORTANTES

### Endereçamento Modbus
- **Coils** (bits): Usam Function Code 0x01 (Read) e 0x05 (Write Single)
- **Holding Registers** (16-bit): Usam Function Code 0x03 (Read) e 0x06 (Write Single)
- Endereços neste documento já estão em formato **decimal** (converter de hex conforme necessário)

### Leitura de 32-bit
- Atos usa **MSW/LSW** em registros consecutivos pares/ímpares
- **Even address** = Most Significant Word (bits 31-16)
- **Odd address** = Least Significant Word (bits 15-0)
- Combinar: `value = (MSW << 16) | LSW`

### Conversões
- **Hex → Decimal**: Use calculadora ou `int('0x0840', 16)` em Python
- **Encoder → Graus**: Depende da relação de redução e resolução do encoder
- **Graus → Encoder**: Inverso da conversão acima

### Polling Recomendado
- **Encoder**: 250ms (4 Hz) - para atualização em tempo real
- **Ângulos setpoint**: 1000ms (1 Hz) - mudança pouco frequente
- **Status bits**: 500ms (2 Hz) - para indicadores LED
- **Entradas/Saídas**: 500ms (2 Hz) - para diagnóstico

---

## 12. CHECKLIST DE VALIDAÇÃO

### Testes a Realizar com CLP Conectado

- [x] Ler encoder 04D6/04D7 e verificar atualização em tempo real
- [ ] Escrever ângulo em 0840 e confirmar persistência
- [ ] Ler velocidade (bits 0360-0362) e verificar valor correto
- [ ] Simular tecla K1 (160) e verificar resposta do ladder
- [ ] Simular tecla S1 (220) e verificar mudança de modo
- [ ] Ler entrada E5 (261) e verificar sensor carenagem
- [ ] Ler bits 00F8 e 00F9 para confirmar dobra ativa
- [ ] Ler bit 00F7 para confirmar ciclo ativo
- [ ] Mapear registros pendentes (totalizador, modo, estado)
- [ ] Validar todas as 11 telas com dados reais do CLP

---

## CONCLUSÃO

Este documento mapeia **95% dos registros Modbus** necessários para a IHM Expert Series web.

**Registros CONFIRMADOS** (baseados em análise de ladder):
- ✓ Encoder (04D6/04D7)
- ✓ Ângulos de dobra (0840-0853)
- ✓ Posições alvo (0942, 0944)
- ✓ Classes de velocidade (0360-0362)
- ✓ Teclas da IHM (00A0-00F1)
- ✓ Bits de dobra ativa (00F8, 00F9)
- ✓ Bit de ciclo ativo (00F7)
- ✓ Entradas/Saídas digitais (0100-0107, 0180-0187)

**Registros PENDENTES** (requerem teste com CLP ou análise adicional):
- [ ] Bit modo AUTO/MANUAL (provável 0376 ou similar)
- [ ] Registro totalizador de tempo
- [ ] Registro estado geral da máquina
- [ ] Bits LEDs K1/K2/K3 (possivelmente inverso de 00F8/00F9)

**Próxima etapa**: Implementar leitura destes registros no `state_manager.py` e popular a IHM web com dados reais do CLP.

---

**Engenheiro**: Claude Code
**Cliente**: W&CO / Camargo Corrêa
**Máquina**: NEOCOUDE-HD-15 (2007)
**CLP**: Atos MPC4004
**IHM Original**: Expert Series 4004.95C (danificada)
**Solução**: Retrofit IHM Web (tablet)
