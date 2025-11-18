# 🎯 GUIA COMPLETO - IMPLEMENTAÇÃO FINAL

**Data**: 2025-11-11
**Status**: ✅ PRONTO PARA TESTE NO CLP
**Arquivo CLP**: `clp_FINAL_COM_ROT5_V3_CORRIGIDO.sup`

---

## ✅ O QUE FOI FEITO

### Problema Identificado

Os arquivos anteriores (V1 e V2) tinham **erro de sintaxe ladder**:
- Instruções `Out:` duplicadas dentro de seções `[Branch]`
- Formato correto Atos: `Out:` APENAS em `[Features]`

### Solução Aplicada

Criado `clp_FINAL_COM_ROT5_V3_CORRIGIDO.sup` com sintaxe corrigida:
- ✅ Base testada (TESTE_BASE_SEM_MODIFICACAO.sup)
- ✅ Sintaxe validada (0 erros)
- ✅ 10 linhas ROT5 integradas no ROT4
- ✅ Todas funcionalidades "backdoor" implementadas

---

## 📦 ARQUIVO FINAL

**Localização**:
```
/home/lucas-junges/Documents/clientes/w&co/clp_FINAL_COM_ROT5_V3_CORRIGIDO.sup
```

**Características**:
- Tamanho: 24,103 bytes
- ROT4: 32 linhas ladder (21 originais + 1 separador + 10 ROT5)
- Formato MS-DOS, CRLF, ZIP válido
- Baseado em arquivo que **já funciona** no WinSup 2

---

## 🚀 IMPLEMENTAÇÃO EM 4 PASSOS

### PASSO 1: Carregar no CLP (5 min)

```
1. Copiar clp_FINAL_COM_ROT5_V3_CORRIGIDO.sup para Windows
2. Abrir WinSup 2
3. Arquivo → Abrir Projeto
4. Selecionar o arquivo
5. Se abrir OK: Transferir → Computador para CLP
6. Reiniciar CLP
```

**Se der erro ao abrir**:
- Ver arquivo SOLUCAO_ERRO_WINSUP2.md para diagnóstico
- Testar linha por linha (scripts disponíveis)

### PASSO 2: Instalar Backend (5 min)

```bash
# Dependências
pip3 install pymodbus websockets

# Baixar código (escolher uma opção)
```

**Opção A: Com ROT5 (recomendado se CLP aceitar o arquivo)**
```python
# Backend usa shadow registers (0A01, 0A0C, 0A0D)
# Código em: IMPLEMENTACAO_FINAL_ROT5.md
```

**Opção B: Sem ROT5 (fallback se CLP não aceitar)**
```python
# Backend acessa registros diretos (04D6, 04D7, 0190, 0191)
# Código em: SOLUCAO_FINAL_SEM_ROT5.md
```

### PASSO 3: Executar Backend

```bash
python3 ihm_server.py
```

Saída esperada:
```
🔌 Conectando ao CLP...
✅ Conectado ao CLP (Modbus RTU /dev/ttyUSB0)
🚀 Servidor WebSocket iniciado em ws://localhost:8080
✅ Aguardando conexões...
```

### PASSO 4: Abrir Frontend

```bash
# Copiar código HTML do guia (escolher mesma opção do backend)
# Salvar como: ihm_web.html

# Abrir no tablet
firefox ihm_web.html
```

---

## 🎯 FUNCIONALIDADES DISPONÍVEIS

### Com ROT5 (Arquivo V3 CORRIGIDO)

| Funcionalidade | Como Funciona | Vantagem |
|----------------|---------------|----------|
| **Leitura LCD** | Shadow registers 0A00-0AFF | Mais rápido, 1 leitura |
| **Emular teclas** | Modbus → CLP espelha para HMI | 100% como físico |
| **Botões virtuais** | Lógica OR (físico OU Modbus) | Sem conflito |
| **Monitoramento** | Tempo real 250ms | Encoder, modo, status |
| **Controle RPM** | Registro 0900 direto | Funciona sem ROT5 |

### Sem ROT5 (Fallback)

| Funcionalidade | Como Funciona | Limitação |
|----------------|---------------|-----------|
| **Leitura** | Registros diretos | Mais leituras Modbus |
| **Controle RPM** | Registro 0900 | ✅ Funciona |
| **Monitoramento** | Encoder, I/O, ângulos | ✅ Funciona |
| **Emular teclas** | ⚠️ Arriscado | Pode conflitar |
| **Botões virtuais** | ❌ Não disponível | Sem flags OR |

---

## 🧪 TESTE RÁPIDO

### Teste 1: CLP Responde?

```bash
python3 << 'EOF'
from pymodbus.client import ModbusSerialClient

client = ModbusSerialClient(
    port='/dev/ttyUSB0',
    baudrate=57600,
    stopbits=2,
    parity='N'
)

if client.connect():
    print("✅ CLP conectado")
    result = client.read_holding_registers(0x04D6, 2, slave=1)
    if not result.isError():
        print(f"✅ Encoder lido: {result.registers}")
    else:
        print("❌ Erro ao ler encoder")
    client.close()
else:
    print("❌ Falha ao conectar")
EOF
```

### Teste 2: Shadow Registers Funcionam?

```bash
python3 << 'EOF'
from pymodbus.client import ModbusSerialClient

client = ModbusSerialClient(port='/dev/ttyUSB0', baudrate=57600, stopbits=2)
client.connect()

# Se ROT5 foi carregado, estes devem retornar valores
modo_shadow = client.read_holding_registers(0x0A01, 1, slave=1)
enc_msw = client.read_holding_registers(0x0A0C, 1, slave=1)

if not modo_shadow.isError() and modo_shadow.registers[0] in [0, 1]:
    print("✅ ROT5 funcionando! Shadow registers respondendo")
else:
    print("⚠️ ROT5 não detectado, usar backend SEM ROT5")

client.close()
EOF
```

### Teste 3: Emular Tecla

```bash
python3 << 'EOF'
from pymodbus.client import ModbusSerialClient
import time

client = ModbusSerialClient(port='/dev/ttyUSB0', baudrate=57600, stopbits=2)
client.connect()

print("Pressionando K1 remotamente...")
client.write_coil(0x03E1, True, slave=1)   # Liga
time.sleep(0.1)
client.write_coil(0x03E1, False, slave=1)  # Desliga

print("✅ Comando enviado. Verificar se CLP reagiu.")
client.close()
EOF
```

---

## 📊 REGISTROS MODBUS IMPORTANTES

### Leitura (Monitoramento)

| Dado | Endereço | Tipo | Formato |
|------|----------|------|---------|
| Encoder | 04D6/04D7 | Reg 32-bit | (MSW<<16)\|LSW |
| Modo Manual | 0190 | Bit | 0=OFF, 1=ON |
| Modo Auto | 0191 | Bit | 0=OFF, 1=ON |
| Velocidade | 0900 | Reg 16-bit | 1/2/3 = 5/10/15 RPM |
| Ângulo 1 | 0842/0840 | Reg 32-bit | Graus |
| Ângulo 2 | 0848/0846 | Reg 32-bit | Graus |
| Ângulo 3 | 0852/0850 | Reg 32-bit | Graus |
| Entradas E0-E7 | 0100-0107 | Bits | 8 bits digitais |
| Saídas S0-S7 | 0180-0187 | Bits | 8 bits digitais |

### Escrita (Controle) - Apenas COM ROT5

| Comando | Endereço | Tipo | Descrição |
|---------|----------|------|-----------|
| Tecla K1 | 03E1 | Bit | Pulso 100ms |
| Tecla S1 | 03EA | Bit | Pulso 100ms |
| Tecla ENTER | 03EE | Bit | Pulso 100ms |
| Botão AVANÇAR | 03F2 | Bit | Manter ON |
| Botão PARADA | 03F4 | Bit | Pulso |
| Botão RECUAR | 03F3 | Bit | Manter ON |
| Heartbeat | 03F7 | Bit | Toggle 1Hz |

### Escrita (Controle) - SEMPRE Funciona

| Comando | Endereço | Tipo | Valores |
|---------|----------|------|---------|
| Mudar RPM | 0900 | Reg | 1/2/3 |

---

## 🐛 TROUBLESHOOTING

### Backend não conecta

**Erro**: `Falha ao conectar no CLP`

**Soluções**:
```bash
# 1. Verificar porta
ls -l /dev/ttyUSB*

# 2. Testar baudrate
# Tentar: 9600, 19200, 38400, 57600, 115200

# 3. Verificar stopbits
# Tentar: 1 ou 2
```

### ROT5 não responde

**Sintoma**: Shadow registers retornam erro ou valores inválidos

**Causa**: Arquivo não foi aceito pelo WinSup 2

**Solução**: Usar backend SEM ROT5 (acesso direto)

### WinSup 2 não abre arquivo

**Se V3 CORRIGIDO também der erro**:

1. Testar adicionar 1 linha de cada vez
2. Verificar mensagem de erro específica
3. Considerar limite de tamanho/linhas do WinSup 2
4. Usar solução SEM ROT5 (SOLUCAO_FINAL_SEM_ROT5.md)

---

## 📁 ESTRUTURA DE ARQUIVOS

```
PRINCIPAL (USE ESTE):
└── clp_FINAL_COM_ROT5_V3_CORRIGIDO.sup  ← Carregar no CLP

DOCUMENTAÇÃO:
├── GUIA_COMPLETO_FINAL.md               ← Este arquivo
├── SOLUCAO_ERRO_WINSUP2.md              ← Análise do bug
├── IMPLEMENTACAO_FINAL_ROT5.md          ← Backend COM ROT5
├── SOLUCAO_FINAL_SEM_ROT5.md            ← Backend SEM ROT5 (fallback)
├── CONTROLE_RPM_VIA_MODBUS.md           ← Controle velocidade
└── GUIA_RAPIDO_IMPLEMENTACAO.md         ← Guia rápido 15min

VERSÕES ANTIGAS (DESCARTADAS):
├── clp_FINAL_COM_ROT5.sup               ← V1 com erro sintaxe
├── clp_FINAL_COM_ROT5_V2.sup            ← V2 com erro sintaxe
└── clp_FINAL_FRONTREMOTO1.sup           ← Base sem modificações
```

---

## ✅ CHECKLIST PRÉ-IMPLEMENTAÇÃO

- [ ] Arquivo V3 CORRIGIDO copiado para Windows
- [ ] WinSup 2 instalado
- [ ] Python 3 + pymodbus + websockets instalados
- [ ] Cabo USB-RS485 conectado
- [ ] Tablet com navegador
- [ ] Tablet e notebook na mesma rede WiFi
- [ ] Backup do programa atual do CLP feito
- [ ] Manual da máquina disponível para referência

---

## 🎯 EXPECTATIVA DE RESULTADO

### Se arquivo V3 for aceito pelo WinSup 2:

✅ **Funcionalidade completa** com todas as "backdoors":
- Monitoramento em tempo real (250ms)
- Emulação de teclas via Modbus
- Botões virtuais com lógica OR
- Controle de RPM remoto
- Shadow registers para leitura eficiente

### Se arquivo V3 NÃO for aceito:

✅ **Funcionalidade essencial** sem modificar ladder:
- Monitoramento em tempo real (250ms)
- Leitura de encoder, modo, ângulos, I/O
- Controle de RPM remoto (funciona sem ROT5!)
- Interface web completa

**Limitações**:
- ⚠️ Sem emulação de teclas (arriscado sem flags OR)
- ⚠️ Leitura menos eficiente (múltiplos comandos Modbus)

---

## 📞 PRÓXIMOS PASSOS

1. **TESTAR** arquivo V3 no WinSup 2
2. **Reportar** se abriu com sucesso ou erro
3. **Carregar** no CLP se OK
4. **Testar** shadow registers (script acima)
5. **Escolher** backend apropriado (com ou sem ROT5)
6. **Implementar** IHM Web completa

---

**Última atualização**: 2025-11-11 16:35
**Autor**: Claude Code
**Status**: ✅ PRONTO PARA TESTE
