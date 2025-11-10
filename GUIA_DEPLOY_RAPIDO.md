# GUIA DE IMPLANTAÇÃO RÁPIDA - IHM WEB NEOCOUDE-HD-15

## 📋 Pré-requisitos

### Hardware
- ✅ Notebook Ubuntu com WiFi
- ✅ Conversor USB-RS485-FTDI
- ✅ Cabo RS485 conectado ao Canal B do CLP
- ✅ Tablet (configurado como hotspot WiFi)

### Software
```bash
# Verificar Python 3
python3 --version

# Instalar dependências (se necessário)
pip3 install websockets pymodbus
```

---

## 🚀 Início Rápido (3 passos)

### PASSO 1: Conectar Hardware
```bash
# Conectar USB-RS485 ao notebook
# Verificar porta serial
ls -l /dev/ttyUSB*

# Dar permissões (se necessário)
sudo chmod 666 /dev/ttyUSB0
```

### PASSO 2: Iniciar Servidor
```bash
# Navegar até diretório do projeto
cd /home/lucas-junges/Documents/clientes/w&co

# Iniciar servidor WebSocket
python3 ihm_server_final.py --port /dev/ttyUSB0 --ws-port 8086
```

**Saída esperada**:
```
================================================================================
IHM SERVIDOR FINAL - NEOCOUDE-HD-15
================================================================================
Porta serial: /dev/ttyUSB0
WebSocket: localhost:8086
Modo: LIVE (CLP real)
================================================================================
✓ Conectado ao CLP via Modbus RTU
Iniciando servidor WebSocket na porta 8086...
✓ Servidor WebSocket rodando em ws://localhost:8086
Iniciando polling do CLP...
```

### PASSO 3: Abrir Interface Web
1. Abrir navegador (Chrome/Firefox)
2. Abrir arquivo: `ihm_completa.html`
3. Verificar status "LIGADO" (verde)
4. Pronto para usar!

---

## 🧪 Teste Antes de Usar

### Teste Automatizado (Recomendado)
```bash
# Teste completo do sistema
python3 test_ihm_completa.py --port /dev/ttyUSB0
```

**Se tudo estiver OK, verá**:
```
╔════════════════════════════════════════╗
║   ✓ TODOS OS TESTES PASSARAM!         ║
║   Sistema pronto para produção        ║
╚════════════════════════════════════════╝
```

### Teste Manual Rápido
```bash
# Teste de conexão básica
python3 -c "
from modbus_client import ModbusClient, ModbusConfig
config = ModbusConfig(port='/dev/ttyUSB0')
client = ModbusClient(stub_mode=False, config=config)
if client.connect():
    print('✓ CLP conectado')
    print(f'Encoder: {client.get_encoder_angle()}')
    client.disconnect()
else:
    print('✗ Falha na conexão')
"
```

---

## 📱 Como Usar a Interface Web

### Navegação Entre Telas
- **Seta ↑**: Tela anterior
- **Seta ↓**: Próxima tela

### Telas Disponíveis (11 telas)
| Tela | Descrição | Conteúdo |
|------|-----------|----------|
| 0 | Splash screen | **TRILLOR MAQUINAS** |
| 1 | Encoder | Mostra ângulo atual do encoder |
| 2 | Modo | Seleção AUTO/MANUAL |
| 3 | Velocidade | Classe de velocidade (5/10/15 RPM) |
| 4 | **Ângulo 1** | **Editável** - Clique para alterar |
| 5 | **Ângulo 2** | **Editável** - Clique para alterar |
| 6 | **Ângulo 3** | **Editável** - Clique para alterar |
| 7 | Dobra Atual | Mostra qual dobra está ativa (1/2/3) |
| 8 | Contador | Contador de peças |
| 9 | Quantidade | Quantidade desejada |
| 10 | Status | Status geral do sistema |

### Editar Ângulos (Telas 4, 5, 6)
1. Navegar até tela desejada (4, 5 ou 6)
2. **Clicar** no valor do ângulo (campo `AJ=`)
3. Digitar novo valor (0-360)
4. Confirmar
5. ✅ Valor atualizado no CLP

### Teclado Virtual
**Numérico**:
- K0, K1, K2, K3, K4, K5, K6, K7, K8, K9

**Funções**:
- S1, S2 (funções especiais)

**Navegação**:
- ↑ (seta cima)
- ↓ (seta baixo)

**Controle**:
- ENTER (confirmar)
- ESC (cancelar)
- EDIT (editar)
- LOCK (travar teclado)

---

## ⚙️ Opções de Linha de Comando

### Modo LIVE (com CLP)
```bash
python3 ihm_server_final.py --port /dev/ttyUSB0 --ws-port 8086
```

### Modo STUB (simulação, sem CLP)
```bash
python3 ihm_server_final.py --stub --ws-port 8086
```

### Porta Serial Alternativa
```bash
python3 ihm_server_final.py --port /dev/ttyUSB1
```

### WebSocket em Porta Diferente
```bash
python3 ihm_server_final.py --port /dev/ttyUSB0 --ws-port 8087
```

---

## 🔧 Troubleshooting Rápido

### ❌ "Erro ao conectar ao CLP"
**Soluções**:
```bash
# 1. Verificar porta existe
ls -l /dev/ttyUSB*

# 2. Dar permissões
sudo chmod 666 /dev/ttyUSB0

# 3. Verificar se porta não está em uso
lsof /dev/ttyUSB0

# 4. Tentar porta alternativa
python3 ihm_server_final.py --port /dev/ttyUSB1
```

### ❌ "WebSocket não conecta"
**Soluções**:
```bash
# 1. Verificar servidor rodando
ps aux | grep ihm_server_final

# 2. Verificar porta livre
netstat -tuln | grep 8086

# 3. Tentar porta diferente
python3 ihm_server_final.py --port /dev/ttyUSB0 --ws-port 8087
```

### ❌ "Encoder sempre zero"
**Verificar**:
- Encoder físico conectado (E100/E101)
- Bit 00D2 (210 decimal) = OFF no CLP
- Registros 1238/1239 (0x04D6/0x04D7)

### ❌ "Teclas não fazem nada"
**Verificar**:
- Bit 00F1 (241 decimal - LOCK) = OFF
- Ladder implementa lógica para teclas
- Ver logs: `tail -f ihm_server_final.log`

### ❌ "Ângulos não salvam"
**Verificar**:
- Registros corretos (ver `COMANDOS_MODBUS_IHM_WEB.md`)
- Formato 32-bit: MSW + LSW
- Logs: `grep "write_angle" ihm_server_final.log`

---

## 📊 Monitoramento

### Logs em Tempo Real
```bash
# Ver logs do servidor
tail -f ihm_server_final.log

# Ver apenas erros
tail -f ihm_server_final.log | grep ERROR

# Ver comandos de escrita
tail -f ihm_server_final.log | grep "write"
```

### Status do Servidor
```bash
# Verificar se servidor está rodando
ps aux | grep ihm_server_final

# Ver uso de CPU/memória
top -p $(pgrep -f ihm_server_final.py)
```

### Teste de Comunicação
```bash
# Ping rápido ao CLP
python3 -c "
from modbus_client import ModbusClient, ModbusConfig
config = ModbusConfig(port='/dev/ttyUSB0')
client = ModbusClient(stub_mode=False, config=config)
if client.connect():
    print('✓ Comunicação OK')
    client.disconnect()
else:
    print('✗ Sem comunicação')
"
```

---

## 🔐 Configuração Modbus

### Parâmetros do CLP
- **Baudrate**: 57600
- **Paridade**: None
- **Stop bits**: 2 ⚠️ **CRÍTICO**
- **Data bits**: 8
- **Slave ID**: Lido do registro 6536 (0x1988)

### Verificar Configuração no CLP
- **Bit 00BE (190 dec)**: DEVE estar ON (habilita Modbus slave)
- **Registro 6536 (0x1988)**: Contém Slave ID
- **Registro 6535 (0x1987)**: Contém baudrate (57600)

---

## 📚 Documentação Completa

### Arquivos de Referência
- **COMANDOS_MODBUS_IHM_WEB.md**: Especificação completa de comandos Modbus
- **SOLUCAO_COMPLETA_IHM.md**: Arquitetura e visão geral do sistema
- **CHECKLIST_TESTES_FACTORY.md**: Checklist completo de testes
- **ihm_server_final.py**: Código do servidor WebSocket
- **ihm_completa.html**: Interface web completa
- **modbus_client.py**: Cliente Modbus (leitura/escrita)

### Manuais
- `manual_MPC4004.pdf`: Manual técnico do CLP Atos
- `NEOCOUDE-HD 15 - Camargo 2007 (1).pdf`: Manual da máquina

---

## 🎯 Checklist de Implantação

### Antes de Ligar
- [ ] Cabo RS485 conectado corretamente (A/B não invertidos)
- [ ] Conversor USB conectado ao notebook
- [ ] Porta serial identificada (`/dev/ttyUSB0` ou `/dev/ttyUSB1`)
- [ ] Dependências Python instaladas (`websockets`, `pymodbus`)
- [ ] Arquivos do projeto presentes (`ihm_server_final.py`, `ihm_completa.html`)

### Inicialização
- [ ] Servidor iniciado sem erros
- [ ] Conexão Modbus estabelecida (mensagem "✓ Conectado ao CLP")
- [ ] WebSocket rodando (mensagem "✓ Servidor WebSocket rodando")
- [ ] Polling iniciado (mensagem "Iniciando polling do CLP")

### Validação Frontend
- [ ] `ihm_completa.html` aberto no navegador
- [ ] Status "LIGADO" em verde
- [ ] Encoder atualizando em tempo real
- [ ] Navegação funciona (setas ↑/↓)
- [ ] Teclado virtual responde (feedback verde ao clicar)

### Teste Funcional
- [ ] Edição de Ângulo 1 funciona (Tela 4)
- [ ] Edição de Ângulo 2 funciona (Tela 5)
- [ ] Edição de Ângulo 3 funciona (Tela 6)
- [ ] Valores validados (0-360)
- [ ] Teclas K0-K9, S1, S2 funcionam
- [ ] Teclas de controle (ENTER, ESC) funcionam

### Validação com Máquina
- [ ] Encoder reflete movimento real do prato
- [ ] Ângulos escritos são reconhecidos pelo CLP
- [ ] Comandos de teclas afetam lógica do CLP
- [ ] Sistema reconecta após desconexão temporária
- [ ] Sem erros nos logs

---

## ✅ Sistema Pronto!

Se todos os itens acima foram verificados, o sistema está pronto para operação em produção.

### Suporte
Para problemas não cobertos neste guia, consulte:
- `CHECKLIST_TESTES_FACTORY.md` - Troubleshooting detalhado
- `SOLUCAO_COMPLETA_IHM.md` - Arquitetura completa
- Logs: `ihm_server_final.log`

---

**Última atualização**: 09/11/2025
**Versão**: 1.0 - Sistema completo implementado
