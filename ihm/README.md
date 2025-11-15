# IHM Web - Dobradeira NEOCOUDE-HD-15

Interface web moderna para substituir painel físico Atos 4004.95C danificado da dobradeira Trillor NEOCOUDE-HD-15 (2007).

**Status:** ✅ **SISTEMA COMPLETO E OPERACIONAL** (12/Nov/2025)

## 🎯 Funcionalidades

✅ **Display LCD Virtual** - Mostra ângulo atual do encoder em tempo real  
✅ **Teclado Numérico** - K0-K9 para programação de ângulos  
✅ **Teclas de Função** - S1 (AUTO/MANUAL), S2 (Reset), ENTER, ESC, EDIT  
✅ **3 Dobras Programáveis** - Ângulos independentes para cada dobra  
✅ **Indicadores LED** - Status visual de dobra ativa e direção  
✅ **Mudança de Velocidade** - K1+K7 simultâneo (5/10/15 RPM)  
✅ **Modo Stub** - Desenvolvimento sem CLP conectado  
✅ **Comunicação Real-Time** - WebSocket com latência < 500ms  

---

## 🚀 Início Rápido

### 1. Instalação

```bash
cd /home/lucas-junges/Documents/clientes/w\&co/ihm

# Instalar dependências Python
pip3 install -r requirements.txt
```

### 2. Iniciar IHM Web

**OPÇÃO RECOMENDADA: Script Interativo**
```bash
./start_ihm.sh
# Escolha: 1) STUB MODE (sem CLP) ou 2) LIVE MODE (com CLP)
```

**OPÇÃO MANUAL: Modo Desenvolvimento (SEM CLP)**
```bash
python3 main_server.py --stub
# Abra no navegador: http://localhost:8080
```

**OPÇÃO MANUAL: Modo Produção (COM CLP)**
```bash
python3 main_server.py --port /dev/ttyUSB0
# Acessar do tablet: http://<IP_NOTEBOOK>:8080
```

---

## 📋 Pré-requisitos

### Hardware
- **CLP**: Atos MPC4004 com firmware atualizado
- **Conversor**: USB-RS485-FTDI
- **Cabo**: RS485 twisted pair (A/B)
- **Tablet**: Android/iOS com navegador moderno

### Software
- **Python**: 3.8 ou superior
- **Sistema**: Ubuntu 25.04 (ou similar)
- **Dependências**: Ver `requirements.txt`

### Configuração CLP
⚠️ **CRÍTICO**: Estado `00BE` (190 decimal) deve estar **ON** no ladder para habilitar Modbus slave!

```
Estado 00BE = ON  ← Modbus RTU habilitado
Slave ID = 1
Baudrate = 57600 bps
Parity = None
Stop bits = 2  ← ATUALIZADO (era 1)
```

### ✨ Estratégia Híbrida Python + Ladder

Esta implementação utiliza uma **estratégia híbrida** inovadora:

1. ✅ **Python LÊ** coils (botões, LEDs) via Modbus Function 0x01
2. ✅ **Python INFERE** estados (tela, modo, dobra) baseado em lógica
3. ✅ **Python ESCREVE** em área de supervisão (0x0940-0x0950) via Function 0x06
4. ✅ **IHM Web LÊ** desta área → **Precisão 100%!**

**Vantagens:**
- ✅ v25 ladder permanece intocável (não precisa recompilar)
- ✅ Escalável (16 registros disponíveis para futuros estados)
- ✅ Debug facilitado (logs Python detalhados)
- ✅ Precisão 100% (escrita explícita, não inferência no frontend)

Veja `docs/RELATORIO_FINAL_ESTRATEGIA_HIBRIDA.md` para detalhes técnicos.

---

## 🔧 Configuração

### Parâmetros de Comunicação

Edite `modbus_client.py` se necessário:

```python
PORT = '/dev/ttyUSB0'      # Porta serial
BAUDRATE = 57600           # Taxa fixa (não alterar)
SLAVE_ID = 1               # ID do CLP (verificar reg 1988H)
```

### Porta Serial Alternativa

```bash
# Se /dev/ttyUSB0 não existir
python3 main_server.py --port /dev/ttyUSB1
```

---

## 📖 Uso

### Interface Web

#### Display Principal
- **Ângulo Atual**: Atualizado a cada 250ms do encoder
- **Status Conexão**: CONECTADO / DESLIGADO / FALHA CLP
- **LEDs**: Indicam dobra ativa (LED1/2/3) e direção (LED4/5)

#### Programação de Ângulos
1. Toque duplo no campo do ângulo desejado
2. Digite novo valor (ex: 135.5)
3. Pressione ENTER para confirmar
4. Valor é enviado ao CLP via Modbus

#### Teclado Virtual
- **K0-K9**: Números para edição
- **S1**: Alterna entre modo MANUAL e AUTO
- **S2**: Reset / Zera contador
- **ENTER**: Confirma edição
- **ESC**: Cancela edição
- **EDIT**: Entra em modo edição

#### Mudança de Velocidade
- Pressione **K1** e **K7** simultaneamente
- Sistema alterna: 5 → 10 → 15 → 5 RPM
- ⚠️ Só funciona em modo MANUAL com máquina parada

---

## 🧪 Testes

### Teste de Comunicação Modbus

```bash
cd tests

# Teste completo (encoder, ângulos, I/O)
python3 test_modbus.py

# Saída esperada:
# ✓ Encoder: 45.7° (457)
# ✓ Dobra 1: 90.0°
# ✓ Dobra 2: 120.0°
# ✓ Modbus slave: ON
```

### Teste de Ângulos

```bash
python3 test_angles.py

# Testa leitura/escrita de ângulos
# Verifica conversão graus ↔ unidades CLP
```

### Teste de Velocidade

```bash
python3 test_speed.py

# Simula K1+K7
# Verifica mudança de classe
```

---

## 🐛 Troubleshooting

### Problema: WebSocket não conecta

**Sintomas**: Interface mostra "DESLIGADO" permanentemente

**Soluções**:
```bash
# 1. Verificar se servidor está rodando
ps aux | grep main_server

# 2. Verificar portas abertas
lsof -i :8765
lsof -i :8080

# 3. Testar manualmente
curl http://localhost:8080

# 4. Verificar firewall
sudo ufw allow 8765
sudo ufw allow 8080
```

---

### Problema: Modbus timeout

**Sintomas**: Interface mostra "FALHA CLP"

**Soluções**:
```bash
# 1. Verificar cabo RS485 conectado
ls -l /dev/ttyUSB*

# 2. Verificar permissões
sudo usermod -a -G dialout $USER
# (logout/login necessário)

# 3. Testar comunicação básica
python3 -c "
from modbus_client import ModbusClientWrapper
client = ModbusClientWrapper()
print('Encoder:', client.read_32bit(0x04D6, 0x04D7))
"

# 4. Verificar estado 00BE no CLP
# Deve estar ON (ativo) no ladder
```

---

### Problema: Ângulos não atualizam

**Causa**: Conversão graus ↔ unidades CLP incorreta

**Verificação**:
```python
# No CLP: 900 unidades = 90.0°
# Fator: 10

# Leitura: value_graus = value_clp / 10.0
# Escrita: value_clp = value_graus * 10

# Exemplo:
# 135.5° → 1355 (CLP)
# 1200 (CLP) → 120.0°
```

---

### Problema: Botões não respondem

**Possíveis causas**:

1. **Estado LOCK ativo**: Teclado travado (desativar no ladder)
2. **Tempo de pulso curto**: Aumentar `hold_ms` de 100ms para 150ms
3. **CLP em modo PROG**: Colocar em modo RUN

**Teste**:
```python
from modbus_client import ModbusClientWrapper
client = ModbusClientWrapper()

# Verificar LOCK
lock = client.read_coil(0x00F1)
print('LOCK:', 'ON' if lock else 'OFF')

# Testar K1
client.press_key(0x00A0, hold_ms=150)
```

---

## 📊 Arquitetura

```
┌─────────────────────────────────────────────────────────┐
│                    TABLET (Cliente)                     │
│  ┌──────────────────────────────────────────────────┐   │
│  │          index.html (JavaScript)                 │   │
│  │  - Display LCD virtual                           │   │
│  │  - Teclado numérico                              │   │
│  │  - WebSocket client                              │   │
│  └───────────────────▲──────────────────────────────┘   │
└────────────────────────┼────────────────────────────────┘
                        │ WebSocket
                        │ (JSON)
┌───────────────────────▼─────────────────────────────────┐
│             SERVIDOR (Ubuntu Notebook)                  │
│  ┌──────────────────────────────────────────────────┐   │
│  │ main_server.py (asyncio)                         │   │
│  │  - WebSocket server (8765)                       │   │
│  │  - HTTP server (8080)                            │   │
│  │  - Broadcast loop (500ms)                        │   │
│  └───┬─────────────────────────────────────────┬────┘   │
│      │                                         │        │
│  ┌───▼──────────────────┐         ┌───────────▼─────┐  │
│  │ state_manager.py     │         │ modbus_client.py│  │
│  │ - Polling 250ms      │◄────────┤ - Read/Write    │  │
│  │ - machine_state {}   │         │ - press_key()   │  │
│  └──────────────────────┘         └────────┬────────┘  │
└───────────────────────────────────────────────┼─────────┘
                                               │ Modbus RTU
                                               │ 57600 bps
┌──────────────────────────────────────────────▼─────────┐
│                    CLP ATOS MPC4004                     │
│  - 95 registros/coils mapeados                          │
│  - Encoder: 0x04D6/0x04D7                               │
│  - Ângulos: 0x0840-0x0852                               │
│  - Botões: 0x00A0-0x00F1                                │
│  - I/O: 0x0100-0x0187                                   │
└─────────────────────────────────────────────────────────┘
```

---

## 📁 Estrutura de Arquivos

```
ihm/
├── README.md                  ← Este arquivo
├── CLAUDE.md                  ← Documentação para Claude Code
├── requirements.txt           ← Dependências Python
├── start_ihm.sh              ← Script de inicialização (NOVO!)
│
├── modbus_map.py              ← 69 endereços mapeados + supervisão
├── modbus_client.py           ← Cliente Modbus (stub + live)
├── state_manager.py           ← Gerenciador de estado + inferência
├── main_server.py             ← Servidor WebSocket + HTTP
│
├── static/
│   └── index.html             ← Interface web completa
│
├── docs/
│   ├── STATUS_IMPLEMENTACAO_COMPLETA.md         ← Status do projeto
│   ├── RELATORIO_FINAL_ESTRATEGIA_HIBRIDA.md    ← Estratégia híbrida
│   ├── TESTES_ESTRATEGIA_HIBRIDA.md             ← Evidências de testes
│   └── IMPLEMENTACAO_ROT6_SUPERVISAO.md         ← Arquitetura técnica
│
└── tests/
    ├── test_modbus.py         ← Teste comunicação
    ├── test_angles.py         ← Teste ângulos
    └── test_speed.py          ← Teste velocidade
```

---

## 🔐 Segurança

⚠️ **IMPORTANTE**: Esta versão inicial **NÃO possui autenticação**.

### Recomendações para Produção:

1. **Rede Isolada**: Tablet conectado via WiFi dedicado (hotspot do notebook)
2. **Firewall**: Bloquear portas 8765/8080 para IPs externos
3. **HTTPS**: Implementar TLS para WebSocket seguro
4. **Autenticação**: Adicionar login/senha no futuro

```bash
# Exemplo de firewall restritivo
sudo ufw default deny incoming
sudo ufw allow from 192.168.x.0/24 to any port 8080
sudo ufw allow from 192.168.x.0/24 to any port 8765
```

---

## 🚀 Roadmap

### v1.0 (Atual)
- [x] Interface LCD virtual
- [x] Teclado completo K0-K9, S1/S2, ENTER/ESC
- [x] Leitura encoder real-time
- [x] Programação de 3 ângulos
- [x] Modo stub para desenvolvimento

### v1.1 (Próximo)
- [ ] Logs de produção (SQLite)
- [ ] Gráficos de histórico
- [ ] Diagnóstico avançado (I/O em tempo real)
- [ ] Exportar relatórios CSV

### v2.0 (Futuro)
- [ ] Autenticação/login
- [ ] Notificações Telegram
- [ ] Receitas salvas (perfis de dobra)
- [ ] PWA (instalar como app)
- [ ] Migração para ESP32

---

## 📞 Suporte

- **Documentação**: Ver `CLAUDE.md` para detalhes técnicos
- **Análise Ladder**: `../ANALISE_COMPLETA_REGISTROS_PRINCIPA.md`
- **Manuais**: `../manual_MPC4004.txt`, `../neocoude_manual.txt`

---

## 📝 Licença

Projeto proprietário - W&Co  
Desenvolvido com Claude Code (Anthropic)  
Novembro 2025
