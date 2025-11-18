# RESUMO DA MODIFICAÇÃO - ATIVAÇÃO DE ROT5

## 📋 O Problema Identificado

Durante os testes via Ubuntu/mbpoll, descobrimos que:

1. ✅ **Escrita Modbus funcionava** - Valores eram gravados em 0x0A00 com sucesso
2. ❌ **Shadow area não atualizava** - Área 0x0840 permanecia inalterada
3. 🔍 **ROT5 existia mas não executava** - A rotina estava definida em ROT5.lad mas não era chamada

### Análise do Ladder Original

**Arquivo:** `clp_MODIFICADO_IHM_WEB.sup`

**Principal.lad original:**
```
[Line00002] CALL ROT0
[Line00003] CALL ROT1
[Line00004] CALL ROT2
[Line00005] CALL ROT3
[Line00006] CALL ROT4
[Line00007] OUT 0x00C5  # <-- Faltava CALL ROT5 aqui!
```

**ROT5.lad (não chamado):**
- Linha 7: MOV 0x0A00 → 0x0842 [MSW] quando bit 0x0390
- Linha 8: MOV 0x0A02 → 0x0840 [LSW] quando bit 0x0390
- Linha 9: MOV 0x0A04 → 0x0848 [MSW] quando bit 0x0391
- Linha 10: MOV 0x0A06 → 0x0846 [LSW] quando bit 0x0391
- Linha 11: MOV 0x0A08 → 0x0852 [MSW] quando bit 0x0392
- Linha 12: MOV 0x0A0A → 0x0850 [LSW] quando bit 0x0392

**Conclusão:** ROT5 contém toda a lógica de cópia Modbus→Shadow, mas nunca é executado!

---

## ✅ A Solução Aplicada

### Modificação Realizada

**Arquivo novo:** `clp_MODIFICADO_IHM_WEB_COM_ROT5.sup`

**Mudança em Principal.lad:**
```
[Line00002] CALL ROT0
[Line00003] CALL ROT1
[Line00004] CALL ROT2
[Line00005] CALL ROT3
[Line00006] CALL ROT4
[Line00007] CALL ROT5  # ✅ ADICIONADO!
[Line00008] OUT 0x00C5  # (ex-Line00007)
```

### Detalhes Técnicos da Linha Adicionada

```
[Line00007]
  [Features]
    Branchs:01
    Type:0
    Label:0
    Comment:0
    Out:CALL    T:-001 Size:001 E:ROT5
    Height:01
  [Branch01]
    X1position:00
    X2position:13
    Yposition:00
    Height:01
    B1:00
    B2:00
    BInputnumber:00
    {0;00;00F7;-1;-1;-1;-1;00}  # Condição: bit 0x00F7
    ###
```

**Condição de execução:** Bit 0x00F7 (sempre ativo no ladder atual)

---

## 📊 Resultado Esperado

### ANTES (sem CALL ROT5):
```
IHM → Modbus FC 0x10 → Escreve em 0x0A00 ✅
                    → Ativa trigger 0x0390 ✅
                    → Shadow 0x0840 NÃO muda ❌
```

### DEPOIS (com CALL ROT5):
```
IHM → Modbus FC 0x10 → Escreve em 0x0A00 ✅
                    → Ativa trigger 0x0390 ✅
                    → ROT5 executa a cada scan ✅
                    → Detecta trigger 0x0390 ON ✅
                    → Copia 0x0A00 → 0x0840 ✅
```

---

## 🧪 Como Testar

### 1. Upload do Ladder Modificado

**Via WinSUP2 (Windows):**
1. Abrir WinSUP2
2. File → Open Project
3. Selecionar: `clp_MODIFICADO_IHM_WEB_COM_ROT5.sup`
4. PLC → Download
5. Aguardar conclusão

**Verificação:**
- No modo monitor do WinSUP2, linha "CALL ROT5" deve aparecer e piscar (verde) durante execução

### 2. Teste Básico (Ubuntu/mbpoll)

**Script automático:**
```bash
cd /home/lucas-junges/Documents/clientes/w&co/ihm_esp32
./teste_rot5_completo.sh
```

**Teste manual:**
```bash
# 1. Escrever ângulo 90° em 0x0A00/0x0A02
mbpoll -m rtu -a 1 -b 57600 -P none -s 2 -t 4 -r 0x0A00 -1 /dev/ttyUSB1 -- 0
mbpoll -m rtu -a 1 -b 57600 -P none -s 2 -t 4 -r 0x0A02 -1 /dev/ttyUSB1 -- 90

# 2. Ativar trigger 0x0390
mbpoll -m rtu -a 1 -b 57600 -P none -s 2 -t 0 -r 0x0390 -1 /dev/ttyUSB1 -- 1
sleep 0.1
mbpoll -m rtu -a 1 -b 57600 -P none -s 2 -t 0 -r 0x0390 -1 /dev/ttyUSB1 -- 0

# 3. Ler shadow area 0x0840/0x0842
mbpoll -m rtu -a 1 -b 57600 -P none -s 2 -t 4 -r 0x0840 -c 2 -1 /dev/ttyUSB1

# Resultado esperado:
# [2112]: 90 (LSW em 0x0840)
# [2113]: 0  (MSW em 0x0842)
```

### 3. Verificações de Sucesso

✅ **Bit 0x00F7 está ON?**
```bash
mbpoll -m rtu -a 1 -b 57600 -P none -s 2 -t 0 -r 0x00F7 -1 /dev/ttyUSB1
# Deve retornar: [247]: ON
```

✅ **Shadow area atualiza?**
- Após escrever em 0x0A00 e ativar trigger, ler 0x0840
- Valor deve corresponder ao escrito em 0x0A00

✅ **ROT5 aparece no monitor WinSUP2?**
- Modo monitor deve mostrar "CALL ROT5" piscando

---

## 🔧 Próximos Passos

### 1. Confirmar Funcionamento do Ladder
- Upload do `clp_MODIFICADO_IHM_WEB_COM_ROT5.sup`
- Executar `teste_rot5_completo.sh`
- Verificar todas as 3 shadow areas atualizam corretamente

### 2. Atualizar Código ESP32

**Arquivos a modificar:**

#### `modbus_map.py` - Adicionar constantes
```python
# Área Modbus Input (IHM → CLP)
'MODBUS_INPUT_BASE': 0x0A00,  # 6 registros (3 ângulos x 2 reg cada)

# Triggers de cópia
'TRIGGER_ANGULO_ESQ_1': 0x0390,  # bit decimal 912
'TRIGGER_ANGULO_DIR_1': 0x0391,  # bit decimal 913
'TRIGGER_ANGULO_ESQ_2': 0x0392,  # bit decimal 914

# Shadow area (onde Principal.lad lê)
'SHADOW_ANGULO_ESQ_1_LSW': 0x0840,  # decimal 2112
'SHADOW_ANGULO_ESQ_1_MSW': 0x0842,  # decimal 2114
'SHADOW_ANGULO_DIR_1_LSW': 0x0846,  # decimal 2118
'SHADOW_ANGULO_DIR_1_MSW': 0x0848,  # decimal 2120
'SHADOW_ANGULO_ESQ_2_LSW': 0x0850,  # decimal 2128
'SHADOW_ANGULO_ESQ_2_MSW': 0x0852,  # decimal 2130
```

#### `modbus_client_esp32.py` - Implementar escrita com trigger
```python
def write_angle_with_trigger(self, angle_index, angle_value):
    """
    Escreve ângulo na área Modbus e ativa trigger para ROT5 copiar

    angle_index: 0=Esq1, 1=Dir1, 2=Esq2
    angle_value: 0-359 graus
    """
    # Mapa de endereços
    angle_addrs = [
        (0x0A00, 0x0A02, 0x0390),  # Ângulo Esquerda 1
        (0x0A04, 0x0A06, 0x0391),  # Ângulo Direita 1
        (0x0A08, 0x0A0A, 0x0392),  # Ângulo Esquerda 2
    ]

    if angle_index not in [0, 1, 2]:
        return False

    msw_addr, lsw_addr, trigger_addr = angle_addrs[angle_index]

    # 1. Escrever MSW (sempre 0 para ângulos até 359°)
    if not self.write_multiple_registers(msw_addr, [0]):
        return False

    # 2. Escrever LSW (valor do ângulo)
    if not self.write_multiple_registers(lsw_addr, [angle_value]):
        return False

    # 3. Ativar trigger (ON)
    if not self.write_single_coil(trigger_addr, True):
        return False

    # 4. Aguardar 100ms
    time.sleep(0.1)

    # 5. Desativar trigger (OFF)
    if not self.write_single_coil(trigger_addr, False):
        return False

    return True
```

#### `state_manager_esp32.py` - Adicionar leitura de shadow area
```python
async def _poll_loop(self):
    """Polling loop - lê estado do CLP a cada 500ms"""
    while True:
        try:
            # ... leitura existente de encoder, I/O, etc.

            # Ler shadow areas (ângulos que o CLP está usando)
            shadow_esq1 = self.modbus_client.read_holding_registers(0x0840, 2)
            shadow_dir1 = self.modbus_client.read_holding_registers(0x0846, 2)
            shadow_esq2 = self.modbus_client.read_holding_registers(0x0850, 2)

            if shadow_esq1:
                self.machine_state['angulo_esq_1'] = (shadow_esq1[1] << 16) | shadow_esq1[0]
            if shadow_dir1:
                self.machine_state['angulo_dir_1'] = (shadow_dir1[1] << 16) | shadow_dir1[0]
            if shadow_esq2:
                self.machine_state['angulo_esq_2'] = (shadow_esq2[1] << 16) | shadow_esq2[0]

            await asyncio.sleep(0.5)
        except Exception as e:
            print(f"[ERROR] Polling: {e}")
            await asyncio.sleep(1.0)
```

### 3. Migração de FC 0x06 para FC 0x10

**Importante:** Durante os testes, descobrimos que:
- ❌ FC 0x06 (Write Single Register) falha no ESP32
- ✅ FC 0x10 (Write Multiple Registers) funciona perfeitamente

**Solução:** Implementar `write_multiple_registers()` no uModbus para ESP32:

```python
# lib/umodbus/serial.py
def write_multiple_registers(self, slave_addr, start_addr, values):
    """
    Function Code 0x10: Write Multiple Registers

    values: lista de valores 16-bit
    """
    qty = len(values)
    byte_count = qty * 2

    # Montar frame
    frame_header = struct.pack('>BBHHB',
                               slave_addr,
                               0x10,           # FC 0x10
                               start_addr,
                               qty,
                               byte_count)

    # Adicionar valores
    frame_data = b''
    for val in values:
        frame_data += struct.pack('>H', val & 0xFFFF)

    frame = frame_header + frame_data

    # Enviar e receber resposta
    self._send_frame(frame)
    response = self._receive_frame()

    if not response:
        return False

    # Verificar resposta
    if len(response) >= 6:
        resp_func = response[1]
        if resp_func == 0x10:
            return True

    return False
```

---

## 📝 Arquivos Gerados

1. **clp_MODIFICADO_IHM_WEB_COM_ROT5.sup** (27 KB)
   - Ladder modificado com CALL ROT5
   - Pronto para upload no CLP

2. **TESTE_LADDER_COM_ROT5.md**
   - Documentação completa do teste
   - Inclui troubleshooting

3. **teste_rot5_completo.sh**
   - Script bash para teste automático
   - Testa todos os 3 ângulos

4. **RESUMO_MODIFICACAO_ROT5.md** (este arquivo)
   - Resumo executivo da modificação

---

## 🎯 Conclusão

A modificação foi **mínima mas crítica**:
- ✅ Adicionada apenas 1 linha no Principal.lad: `CALL ROT5`
- ✅ Nenhuma mudança em ROT5.lad (já estava correto)
- ✅ Nenhuma mudança em outras rotinas
- ✅ Arquivo SUP comprimido e pronto para uso

**Próximo passo:** Upload no CLP e teste com o script fornecido.

---

**Desenvolvido por:** Eng. Lucas William Junges
**Data:** 2025-11-18
**Status:** ✅ Pronto para teste no CLP
**Arquivo:** `/home/lucas-junges/Documents/clientes/w&co/ihm_esp32/clp_MODIFICADO_IHM_WEB_COM_ROT5.sup`
