# DIAGNÓSTICO DE ERRO NO WINSUP 2

**Data**: 2025-11-10
**Problema**: Arquivos modificados não abrem no WinSup 2

---

## 🔍 TESTE PASSO A PASSO

Vamos descobrir qual é o limite do WinSup 2 testando arquivos incrementalmente:

### TESTE 1: Arquivo Original (Baseline)

**Arquivo**: `clp.sup` (original sem modificações)
**O que tem**: Programa original de fábrica

**Instruções**:
```
1. Abrir WinSup 2
2. Arquivo → Abrir Projeto
3. Selecionar: clp.sup
4. Resultado esperado: ✅ Deve abrir
```

**Se não abrir**: Problema é com o WinSup 2 ou arquivo corrompido.

---

### TESTE 2: Apenas FRONTREMOTO=1

**Arquivo**: `TESTE_BASE_SEM_MODIFICACAO.sup`
**O que tem**: Apenas FRONTREMOTO=1 habilitado (sem ROT5)

**Instruções**:
```
1. Abrir WinSup 2
2. Arquivo → Abrir Projeto
3. Selecionar: TESTE_BASE_SEM_MODIFICACAO.sup
4. Verificar se abre
```

**Se abrir ✅**: Arquivo base está OK, problema é adicionar ROT5
**Se não abrir ❌**: WinSup 2 não aceita mudança na data/recompressão

---

### TESTE 3: Verificar Qual Arquivo Específico Causa Erro

Se TESTE 2 não abrir, o problema pode ser:

#### 3a) Verificar ROT4.lad
```
1. Extrair TESTE_BASE_SEM_MODIFICACAO.sup
2. Abrir ROT4.lad em editor de texto
3. Verificar:
   - Primeira linha: Lines:00021
   - Última linha termina com ###
   - Sem caracteres estranhos
```

#### 3b) Verificar Project.spr
```
1. Abrir Project.spr
2. Deve conter:
   LastEdit=0
   PrincipalType=0
   ScreenType=1
```

---

## 🎯 SOLUÇÃO ALTERNATIVA (SEM MODIFICAR LADDER)

Se **nenhum** arquivo modificado abrir, use esta abordagem:

### Opção A: Usar Arquivo Original + Comandos Diretos

**Arquivo**: `clp.sup` (original)

**Vantagem**: Sem risco, sem modificação do ladder

**Funcionalidades disponíveis**:

1. ✅ **Controle de RPM**: Escrever registro 0900
2. ✅ **Ler Encoder**: Registros 04D6/04D7
3. ✅ **Ler Modo**: Bits 0190 (MANUAL) / 0191 (AUTO)
4. ✅ **Ler Entradas**: Registros 0100-0107
5. ✅ **Ler Saídas**: Registros 0180-0187

**O que NÃO terá**:
- ❌ Espelhamento LCD (registros shadow)
- ❌ Emulação de teclas via Modbus
- ❌ Flags virtuais em paralelo

**Código Python para usar**:

```python
from pymodbus.client import ModbusSerialClient
import time

client = ModbusSerialClient(
    port='/dev/ttyUSB0',
    baudrate=57600,
    stopbits=2,
    parity='N'
)

client.connect()

# 1. Ler encoder diretamente (sem shadow register)
result = client.read_holding_registers(0x04D6, 2, slave=1)
encoder = (result.registers[0] << 16) | result.registers[1]
print(f"Encoder: {encoder}°")

# 2. Ler modo diretamente (sem shadow register)
modo_manual = client.read_coils(0x0190, 1, slave=1).bits[0]
modo_auto = client.read_coils(0x0191, 1, slave=1).bits[0]
modo = "AUTO" if modo_auto else "MANUAL"
print(f"Modo: {modo}")

# 3. Mudar RPM (funciona sem ROT5!)
print("Mudando para 10 RPM...")
client.write_register(0x0900, 2, slave=1)
time.sleep(0.3)
velocidade = client.read_holding_registers(0x0900, 1, slave=1).registers[0]
print(f"Velocidade: Classe {velocidade}")

# 4. Ler entradas digitais
entradas = []
for i in range(8):
    bit = client.read_coils(0x0100 + i, 1, slave=1).bits[0]
    entradas.append(bit)
print(f"Entradas E0-E7: {entradas}")

# 5. Ler saídas digitais
saidas = []
for i in range(8):
    bit = client.read_coils(0x0180 + i, 1, slave=1).bits[0]
    saidas.append(bit)
print(f"Saídas S0-S7: {saidas}")

client.close()
```

---

### Opção B: Usar Apenas Modbus Master (Sem Modificar CLP)

**Conceito**: O IHM Web lê/escreve diretamente nos registros originais do CLP, sem precisar de ROT5.

**Arquitetura**:
```
IHM Web (Tablet)
    ↓ Modbus RTU
CLP (Programa Original)
    ↓ I/O
Máquina (Sensores/Atuadores)
```

**Funcionalidades Possíveis**:

| Funcionalidade | Como Fazer | Precisa ROT5? |
|----------------|------------|---------------|
| Ler Encoder | Registros 04D6/04D7 | ❌ Não |
| Ler Modo | Bits 0190/0191 | ❌ Não |
| Mudar RPM | Registro 0900 | ❌ Não |
| Ler Entradas E0-E7 | Bits 0100-0107 | ❌ Não |
| Ler Saídas S0-S7 | Bits 0180-0187 | ❌ Não |
| Ler Ângulos | Regs 0842/0840, 0848/0846, 0852/0850 | ❌ Não |
| Simular Teclas | Bits 00A0-00A9, etc. | ⚠️ Arriscado sem flags virtuais |
| Simular Botões | Bits 0102-0104 (E2/E3/E4) | ⚠️ Pode conflitar com físico |

**Limitações**:
- ⚠️ Simular teclas/botões pode conflitar com uso físico
- ⚠️ Sem flags virtuais, botão físico + Modbus podem causar comportamento inesperado
- ⚠️ Sem espelhamento LCD, precisa ler registros originais (menos eficiente)

---

## 📝 QUAL MENSAGEM DE ERRO APARECE?

Para melhor diagnóstico, por favor responda:

1. **Qual mensagem exata de erro?**
   - "Erro ao abrir o projeto"
   - "Arquivo corrompido"
   - "Projeto inválido"
   - Outro:

2. **Qual arquivo está testando?**
   - clp.sup (original)
   - TESTE_BASE_SEM_MODIFICACAO.sup
   - clp_FINAL_COM_ROT5_V2.sup
   - Outro:

3. **O que acontece ao tentar abrir?**
   - WinSup 2 trava/fecha
   - Mostra erro e continua aberto
   - Abre mas mostra projeto vazio
   - Outro:

4. **Versão do WinSup 2**:
   - WinSup 2.xx
   - Não sei

---

## 🎯 RECOMENDAÇÃO IMEDIATA

**TESTE AGORA** (nesta ordem):

1. ✅ Teste arquivo original: `clp.sup`
   - Se não abrir → problema é com WinSup 2

2. ✅ Teste arquivo base: `TESTE_BASE_SEM_MODIFICACAO.sup`
   - Se não abrir → problema é recompressão
   - Se abrir → problema é adicionar ROT5

3. ⚠️ Se nada abrir:
   - Use arquivo que já estava no CLP
   - Use abordagem "Opção A" acima (sem modificar ladder)

4. ✅ Se TESTE 2 abrir:
   - Carregue esse no CLP
   - Use Modbus direto nos registros originais
   - Depois tentamos adicionar ROT5 linha por linha

---

## 💡 SOLUÇÃO PRÁTICA (EMERGENCIAL)

**Se nada funcionar**, use esta configuração:

1. **CLP**: Programa original (clp.sup)
2. **IHM Web**: Acessa registros diretos via Modbus
3. **Funcionalidades**: Leitura completa + Mudança de RPM

**Código pronto**:

```python
# ihm_server_DIRETO.py
from pymodbus.client import ModbusSerialClient
import asyncio
import websockets
import json

client = ModbusSerialClient(
    port='/dev/ttyUSB0',
    baudrate=57600,
    stopbits=2,
    parity='N'
)

async def ler_estado_completo():
    """Lê estado diretamente do CLP (sem shadow registers)"""
    estado = {}

    # Encoder (04D6/04D7)
    result = client.read_holding_registers(0x04D6, 2, slave=1)
    if not result.isError():
        estado['encoder'] = (result.registers[0] << 16) | result.registers[1]

    # Modo (0190/0191)
    modo_manual = client.read_coils(0x0190, 1, slave=1).bits[0]
    modo_auto = client.read_coils(0x0191, 1, slave=1).bits[0]
    estado['modo'] = 'AUTO' if modo_auto else 'MANUAL'

    # Velocidade (0900)
    result = client.read_holding_registers(0x0900, 1, slave=1)
    if not result.isError():
        estado['velocidade'] = result.registers[0]

    # Ângulo 1 (0842/0840)
    result = client.read_holding_registers(0x0842, 2, slave=1)
    if not result.isError():
        estado['angulo_1'] = (result.registers[0] << 16) | result.registers[1]

    # Entradas E0-E7
    entradas = []
    for i in range(8):
        bit = client.read_coils(0x0100 + i, 1, slave=1).bits[0]
        entradas.append(bit)
    estado['entradas'] = entradas

    # Saídas S0-S7
    saidas = []
    for i in range(8):
        bit = client.read_coils(0x0180 + i, 1, slave=1).bits[0]
        saidas.append(bit)
    estado['saidas'] = saidas

    return estado

async def mudar_rpm(classe):
    """Muda velocidade da máquina"""
    if classe not in [1, 2, 3]:
        return {'error': 'Classe inválida'}

    # Verificar modo MANUAL
    modo_manual = client.read_coils(0x0190, 1, slave=1).bits[0]
    if not modo_manual:
        return {'error': 'Requer modo MANUAL'}

    # Escrever novo valor
    result = client.write_register(0x0900, classe, slave=1)
    if result.isError():
        return {'error': 'Falha ao escrever'}

    return {'success': True, 'classe': classe, 'rpm': {1:5, 2:10, 3:15}[classe]}

async def handle_client(websocket, path):
    while True:
        # Enviar estado a cada 250ms
        estado = await ler_estado_completo()
        await websocket.send(json.dumps(estado))
        await asyncio.sleep(0.25)

# Iniciar servidor
client.connect()
start_server = websockets.serve(handle_client, 'localhost', 8080)
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
```

---

**Me avise**:
1. Qual teste funcionou (1, 2, ou nenhum)
2. Qual mensagem de erro exata aparece
3. Se quer usar solução alternativa (sem modificar ladder)

---

**Data**: 2025-11-10
**Status**: Aguardando diagnóstico
