# Guia de Testes da Máquina NEOCOUDE-HD-15

## ⚠️ SEGURANÇA EM PRIMEIRO LUGAR

**ANTES DE QUALQUER TESTE:**
1. ✅ Desligar o motor principal (COMANDO GERAL desligado)
2. ✅ Garantir que não há material no prato
3. ✅ Manter EMERGÊNCIA acessível
4. ✅ Usar EPIs adequados
5. ✅ Verificar aterramento
6. ✅ Desligar alimentação 380V quando mexer em bornes de potência

## 📋 Equipamentos Necessários

- ✅ Multímetro digital
- ✅ Laptop com IHM Web rodando
- ✅ Cabo USB-RS485 conectado
- ✅ Chaves de fenda para bornes
- ✅ Caderno para anotações

---

## 1️⃣ TESTE DE ENTRADAS DIGITAIS (E0-E7)

### Objetivo
Identificar quais entradas correspondem a quais sensores/botões físicos.

### Procedimento

#### 1.1. Preparação
```bash
# No terminal, rode o script de leitura contínua de entradas:
cd /home/lucas-junges/Documents/clientes/w\&co
python3 test_read_inputs.py
```

Você verá algo assim:
```
E0: OFF  E1: OFF  E2: OFF  E3: OFF
E4: OFF  E5: OFF  E6: OFF  E7: OFF
```

#### 1.2. Teste de Cada Entrada

**Configuração do Multímetro:**
- Modo: DC Voltage (V⎓)
- Range: 0-30V
- Ponta preta: GND/0V do CLP
- Ponta vermelha: Bornes de entrada E0-E7

**Tabela de Testes:**

| Borne | Ação no CLP/Máquina | Tensão Esperada | Estado no Python | Função Identificada |
|-------|---------------------|-----------------|------------------|---------------------|
| E0    | _(medir e anotar)_  | 24V = ON, 0V = OFF | ON/OFF | _________________ |
| E1    | _(medir e anotar)_  | 24V = ON, 0V = OFF | ON/OFF | _________________ |
| E2    | _(medir e anotar)_  | 24V = ON, 0V = OFF | ON/OFF | _________________ |
| E3    | _(medir e anotar)_  | 24V = ON, 0V = OFF | ON/OFF | _________________ |
| E4    | _(medir e anotar)_  | 24V = ON, 0V = OFF | ON/OFF | _________________ |
| E5    | _(medir e anotar)_  | 24V = ON, 0V = OFF | ON/OFF | _________________ |
| E6    | _(medir e anotar)_  | 24V = ON, 0V = OFF | ON/OFF | _________________ |
| E7    | _(medir e anotar)_  | 24V = ON, 0V = OFF | ON/OFF | _________________ |

**Testes Específicos a Fazer:**

1. **Sensor de Posição Zero (provável E0)**
   - Girar prato manualmente até sensor alinhar
   - Verificar qual entrada muda de OFF→ON

2. **Botão EMERGÊNCIA (provável E3)**
   - Pressionar botão de emergência vermelho
   - Verificar qual entrada vai para OFF (normalmente fechado)

3. **Botão COMANDO GERAL (provável E7)**
   - Ligar/desligar comando geral
   - Verificar entrada que muda

4. **Botões AVANÇAR/RECUAR/PARADA (prováveis E4/E5/E6)**
   - Pressionar cada botão do painel
   - Anotar qual entrada corresponde

#### 1.3. Script de Teste Automático

Crie um script para facilitar:

```python
#!/usr/bin/env python3
"""
test_inputs_mapping.py
Detecta mudanças nas entradas para mapear sensores
"""

from modbus_client import ModbusClient, ModbusConfig
import time

config = ModbusConfig(port='/dev/ttyUSB0')
client = ModbusClient(stub_mode=False, config=config)

print("=== MAPEAMENTO DE ENTRADAS DIGITAIS ===")
print("Pressione Ctrl+C para sair\n")

# Estado anterior
prev_state = [False] * 8

try:
    while True:
        # Ler entradas E0-E7 (registradores 256-263)
        inputs = []
        for i in range(8):
            result = client.read_discrete_inputs(256 + i, 1)
            if result and not result.isError():
                inputs.append(result.bits[0])
            else:
                inputs.append(False)

        # Detectar mudanças
        for i in range(8):
            if inputs[i] != prev_state[i]:
                status = "ON " if inputs[i] else "OFF"
                print(f"⚡ E{i} mudou para {status}")
                print(f"   → Hora: {time.strftime('%H:%M:%S')}")
                print(f"   → Anote a ação que você fez!\n")

        prev_state = inputs.copy()
        time.sleep(0.1)  # 100ms

except KeyboardInterrupt:
    print("\nTeste finalizado")
```

**Como usar:**
```bash
python3 test_inputs_mapping.py
# Agora pressione cada botão/mova cada sensor e anote!
```

---

## 2️⃣ TESTE DE SAÍDAS DIGITAIS (S0-S7)

### Objetivo
Identificar quais saídas controlam motor, LEDs, válvulas, etc.

### ⚠️ CUIDADO
- **NÃO force saídas de potência (motor) sem supervisão**
- **Comece com motor desligado (380V cortado)**

### Procedimento

#### 2.1. Teste Visual de LEDs

Algumas saídas podem acender LEDs no painel. Teste com segurança:

```python
#!/usr/bin/env python3
"""
test_outputs_safe.py
Ativa saídas uma por vez para identificação
"""

from modbus_client import ModbusClient, ModbusConfig
import time

config = ModbusConfig(port='/dev/ttyUSB0')
client = ModbusClient(stub_mode=False, config=config)

print("=== TESTE DE SAÍDAS (SEGURO) ===")
print("Motor 380V DEVE estar desligado!\n")

input("Confirme que 380V está DESLIGADO. Pressione Enter...")

for i in range(8):
    print(f"\n✓ Ativando S{i}...")

    # Ligar saída
    client.write_coil(384 + i, True)

    print(f"→ S{i} está LIGADA")
    print(f"→ Observe: LEDs, relés, contatores, etc")
    print(f"→ Anote o que aconteceu!")

    input("Pressione Enter para DESLIGAR e continuar...")

    # Desligar saída
    client.write_coil(384 + i, False)
    print(f"✓ S{i} desligada\n")
    time.sleep(1)

print("Teste concluído!")
```

#### 2.2. Medição com Multímetro

**Configuração:**
- Modo: DC Voltage
- Ponta preta: GND
- Ponta vermelha: Borne de saída S0-S7

**Tabela de Medições:**

| Saída | Tensão OFF | Tensão ON | Equipamento Controlado | Observação |
|-------|------------|-----------|------------------------|------------|
| S0    | 0V         | 24V?      | ___________________    | __________ |
| S1    | 0V         | 24V?      | ___________________    | __________ |
| S2    | 0V         | 24V?      | ___________________    | __________ |
| S3    | 0V         | 24V?      | ___________________    | __________ |
| S4    | 0V         | 24V?      | ___________________    | __________ |
| S5    | 0V         | 24V?      | ___________________    | __________ |
| S6    | 0V         | 24V?      | ___________________    | __________ |
| S7    | 0V         | 24V?      | ___________________    | __________ |

**Saídas Prováveis:**
- **S0/S1**: Motor sentido horário/anti-horário
- **S2**: VFD Enable (liga inversor)
- **S3/S4/S5**: Seleção de velocidade (classe 1/2/3)
- **S6/S7**: LEDs do painel (K1, K2, K3)

---

## 3️⃣ TESTE DO ENCODER

### Objetivo
Verificar se o encoder está contando corretamente.

### Procedimento

#### 3.1. Leitura Contínua

```python
#!/usr/bin/env python3
"""
test_encoder_live.py
Monitora encoder em tempo real
"""

from modbus_client import ModbusClient, ModbusConfig
import time

config = ModbusConfig(port='/dev/ttyUSB0')
client = ModbusClient(stub_mode=False, config=config)

print("=== TESTE DO ENCODER ===")
print("Gire o prato manualmente e observe a contagem\n")

try:
    while True:
        # Ler registradores 04D6/04D7 (1238/1239 decimal)
        result_msw = client.read_holding_registers(1238, 1)
        result_lsw = client.read_holding_registers(1239, 1)

        if result_msw and result_lsw:
            msw = result_msw.registers[0]
            lsw = result_lsw.registers[0]

            # Combinar em 32-bit
            encoder_raw = (msw << 16) | lsw

            # Converter para ângulo (depende da configuração)
            # Provisoriamente, mostrar valor bruto e calculado
            angle_estimated = (encoder_raw / 65536.0) * 360.0

            print(f"\rEncoder RAW: {encoder_raw:10d}  |  Ângulo estimado: {angle_estimated:6.1f}°", end='')

        time.sleep(0.1)

except KeyboardInterrupt:
    print("\n\nTeste finalizado")
```

**Teste Manual:**
1. Rodar o script
2. Marcar posição inicial do prato (ex: marca de tinta)
3. Girar prato lentamente 90° (usar transferidor ou esquadro)
4. Anotar valor do encoder
5. Repetir para 180°, 270°, 360°

**Fórmula de Calibração:**
```
Pulsos por revolução = Valor_360° - Valor_0°
Graus por pulso = 360 / Pulsos_por_revolução
```

#### 3.2. Teste de Direção

Verificar se encoder conta Up ou Down em cada direção:

1. Zerar contador (S2 na IHM física?)
2. Girar sentido horário → contador deve AUMENTAR ou DIMINUIR?
3. Girar sentido anti-horário → contador faz o oposto?

---

## 4️⃣ MAPEAMENTO DE REGISTRADORES INTERNOS

### Objetivo
Encontrar os registradores de ângulos, modo, velocidade, etc.

### Procedimento

#### 4.1. Busca por Padrão

**Registradores de Ângulo (D1E, D2E, D3E, D1D, D2D, D3D):**

Provável faixa: `0500h-053Fh` (1280-1343 dec) - Área de setpoints

```python
#!/usr/bin/env python3
"""
test_find_angles.py
Busca registradores de ângulos programados
"""

from modbus_client import ModbusClient, ModbusConfig

config = ModbusConfig(port='/dev/ttyUSB0')
client = ModbusClient(stub_mode=False, config=config)

print("=== BUSCA DE REGISTRADORES DE ÂNGULOS ===\n")

# Ler área de setpoints
print("Lendo registradores 1280-1343 (área de setpoints)...\n")

for addr in range(1280, 1344):
    result = client.read_holding_registers(addr, 1)
    if result and not result.isError():
        value = result.registers[0]
        if value > 0 and value < 360:  # Provável ângulo
            print(f"Reg {addr:4d} (0x{addr:04X}): {value:5d} → Possível ângulo: {value}°")

print("\n=== DICA ===")
print("Valores entre 0-360 são candidatos a ângulos programados")
print("Anote quais registradores têm valores que fazem sentido")
```

#### 4.2. Teste de Escrita

**⚠️ IMPORTANTE:** Anote valores originais antes de escrever!

```python
#!/usr/bin/env python3
"""
test_write_angle.py
Testa escrita de ângulo (CUIDADO!)
"""

from modbus_client import ModbusClient, ModbusConfig

config = ModbusConfig(port='/dev/ttyUSB0')
client = ModbusClient(stub_mode=False, config=config)

# Exemplo: Testar registrador 1280
TEST_REG = 1280

print(f"=== TESTE DE ESCRITA NO REGISTRADOR {TEST_REG} ===\n")

# Ler valor original
result = client.read_holding_registers(TEST_REG, 1)
if result:
    original = result.registers[0]
    print(f"Valor original: {original}")

    # Escrever valor de teste (ex: 45°)
    input("\nPressione Enter para escrever 45 neste registrador...")
    client.write_register(TEST_REG, 45)

    # Ler de volta
    result2 = client.read_holding_registers(TEST_REG, 1)
    if result2:
        new_value = result2.registers[0]
        print(f"Valor após escrita: {new_value}")

        if new_value == 45:
            print("✓ Escrita bem-sucedida!")

        # Restaurar valor original
        input("\nPressione Enter para RESTAURAR valor original...")
        client.write_register(TEST_REG, original)
        print(f"✓ Valor restaurado para {original}")
```

---

## 5️⃣ TESTE DE CICLO COMPLETO (COM CAUTELA)

### ⚠️ EXECUTAR SOMENTE COM SUPERVISÃO E SEM MATERIAL NO PRATO

#### 5.1. Modo Manual - Teste Básico

**Pré-requisitos:**
- ✅ Comando geral ligado
- ✅ Sem emergência
- ✅ Motor 380V pode ser ligado
- ✅ Prato vazio
- ✅ Área livre

**Procedimento:**

1. **Verificar Modo Manual**
```python
# Via IHM Web, verificar que está em MANUAL
```

2. **Selecionar Dobra 1 (K1)**
```python
# Pressionar K1 na IHM web
# LED K1 deve acender (verificar no painel físico)
```

3. **Selecionar Direção Esquerda (K4)**
```python
# Pressionar K4 na IHM web
# LED K4 deve acender
```

4. **Programar Ângulo Pequeno (ex: 10°)**
```python
# Pressionar EDIT
# Navegar para D1E
# Digitar 010.0
# Confirmar
```

5. **Testar Movimento (ATENÇÃO!)**
```python
# Manter AVANÇAR pressionado (botão físico)
# Observar:
#   - Motor liga?
#   - Prato gira?
#   - Encoder conta?
#   - Para no ângulo correto?
#   - Retorna para zero?
```

#### 5.2. Checklist de Observação

Durante o teste, anotar:

| Item | OK? | Observação |
|------|-----|------------|
| Motor liga quando pressiona AVANÇAR | ☐ | __________ |
| Prato gira na direção esperada | ☐ | __________ |
| Encoder conta durante movimento | ☐ | __________ |
| Para no ângulo programado | ☐ | __________ |
| Retorna automaticamente para zero | ☐ | __________ |
| Display mostra ângulo correto | ☐ | __________ |
| S2 zera display quando pressionado | ☐ | __________ |

---

## 6️⃣ ANÁLISE DO LADDER (clp.sup)

### Objetivo
Extrair informações do programa ladder que está rodando no CLP.

### Procedimento

#### 6.1. Abrir Arquivo no WinSUP (se conseguir rodar)

Se conseguir abrir `clp.sup`:
1. Procurar por variáveis com nomes:
   - `ANG_*` (ângulos)
   - `VEL_*` (velocidade)
   - `MODO_*` (modo)
   - `DOBRA_*` (dobra atual)

2. Anotar endereços de memória associados

#### 6.2. Análise Hexadecimal

```bash
# Ver primeiros bytes do arquivo
hexdump -C clp.sup | head -100

# Buscar strings ASCII
strings clp.sup | grep -i "ang\|vel\|dobra\|modo"
```

---

## 7️⃣ TABELA DE RESULTADOS

### Preencher Conforme Testes

#### Entradas Digitais Mapeadas

| Entrada | Endereço Modbus | Função Identificada | Tipo | Notas |
|---------|-----------------|---------------------|------|-------|
| E0 | 256 (0x0100) | _________________ | NO/NC | _____ |
| E1 | 257 (0x0101) | _________________ | NO/NC | _____ |
| E2 | 258 (0x0102) | _________________ | NO/NC | _____ |
| E3 | 259 (0x0103) | _________________ | NO/NC | _____ |
| E4 | 260 (0x0104) | _________________ | NO/NC | _____ |
| E5 | 261 (0x0105) | _________________ | NO/NC | _____ |
| E6 | 262 (0x0106) | _________________ | NO/NC | _____ |
| E7 | 263 (0x0107) | _________________ | NO/NC | _____ |

#### Saídas Digitais Mapeadas

| Saída | Endereço Modbus | Função Identificada | Tipo | Notas |
|-------|-----------------|---------------------|------|-------|
| S0 | 384 (0x0180) | _________________ | Relé/LED | _____ |
| S1 | 385 (0x0181) | _________________ | Relé/LED | _____ |
| S2 | 386 (0x0182) | _________________ | Relé/LED | _____ |
| S3 | 387 (0x0183) | _________________ | Relé/LED | _____ |
| S4 | 388 (0x0184) | _________________ | Relé/LED | _____ |
| S5 | 389 (0x0185) | _________________ | Relé/LED | _____ |
| S6 | 390 (0x0186) | _________________ | Relé/LED | _____ |
| S7 | 391 (0x0187) | _________________ | Relé/LED | _____ |

#### Registradores Mapeados

| Variável | Endereço Modbus | Tipo | Range | Função |
|----------|-----------------|------|-------|--------|
| Encoder MSW | 1238 (0x04D6) | 16-bit | 0-65535 | Parte alta contador |
| Encoder LSW | 1239 (0x04D7) | 16-bit | 0-65535 | Parte baixa contador |
| D1E (Dobra 1 Esq) | _______ | 16-bit | 0-360 | Ângulo esquerda 1 |
| D2E (Dobra 2 Esq) | _______ | 16-bit | 0-360 | Ângulo esquerda 2 |
| D3E (Dobra 3 Esq) | _______ | 16-bit | 0-360 | Ângulo esquerda 3 |
| D1D (Dobra 1 Dir) | _______ | 16-bit | 0-360 | Ângulo direita 1 |
| D2D (Dobra 2 Dir) | _______ | 16-bit | 0-360 | Ângulo direita 2 |
| D3D (Dobra 3 Dir) | _______ | 16-bit | 0-360 | Ângulo direita 3 |
| Modo (Manual/Auto) | _______ | BIT | 0/1 | 0=Manual, 1=Auto |
| Dobra Atual | _______ | 16-bit | 1-3 | Dobra ativa |
| Velocidade Classe | _______ | 16-bit | 1-3 | 1=5rpm, 2=10rpm, 3=15rpm |
| Direção ESQ | _______ | BIT | 0/1 | 1=Esquerda ativa |
| Direção DIR | _______ | BIT | 0/1 | 1=Direita ativa |
| Ciclo Ativo | _______ | BIT | 0/1 | 1=Dobrando |

---

## 8️⃣ SCRIPTS ÚTEIS PARA CRIAR

Vou criar alguns scripts prontos para você usar:

### test_all_inputs.py
```bash
python3 test_inputs_mapping.py
```

### test_all_outputs.py
```bash
python3 test_outputs_safe.py
```

### test_encoder_calibration.py
```bash
python3 test_encoder_live.py
```

### scan_registers.py
```bash
python3 test_find_angles.py
```

---

## 📝 RELATÓRIO FINAL

Após concluir todos os testes, compilar um arquivo:

**`MAPEAMENTO_COMPLETO.md`**

Contendo:
1. Todas as entradas mapeadas
2. Todas as saídas mapeadas
3. Todos os registradores encontrados
4. Fórmula de conversão do encoder
5. Comportamento da máquina em cada modo
6. Observações e particularidades

---

## 🔧 PRÓXIMOS PASSOS APÓS MAPEAMENTO

1. Atualizar `modbus_map.py` com endereços reais
2. Implementar funções de escrita em `main_server.py`
3. Testar IHM web controlando máquina real
4. Ajustar calibração do encoder
5. Validar ciclo completo automático

---

## ⚡ COMANDOS RÁPIDOS

```bash
# Monitorar entradas em tempo real
python3 test_inputs_mapping.py

# Testar saídas com segurança
python3 test_outputs_safe.py

# Ver encoder ao vivo
python3 test_encoder_live.py

# Buscar registradores de ângulos
python3 test_find_angles.py

# Monitorar comunicação Modbus
tail -f ihm_server.log | grep -i "modbus\|read\|write"
```

---

**Criado por:** Claude Code
**Data:** 2025-11-08
**Projeto:** IHM Virtual NEOCOUDE-HD-15
