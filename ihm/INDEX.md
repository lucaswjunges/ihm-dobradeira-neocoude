# 📚 Índice de Documentação - IHM Web Dobradeira

**Projeto**: IHM Web para Dobradeira NEOCOUDE-HD-15
**CLP**: Atos MPC4004
**Última atualização**: 16/Novembro/2025

---

## 🎯 COMECE AQUI

### Para Desenvolvimento
1. **CLAUDE.md** - Instruções completas para Claude Code
2. **RESUMO_VALIDACOES_16NOV2025.md** - Resumo de todas as descobertas
3. **modbus_map.py** - Mapa completo de 95 registros validados

### Para Testes
1. **test_write_complete_mbpoll.sh** - Menu interativo (RECOMENDADO)
2. **test_new_angles.py** - Teste automatizado de ângulos
3. **test_speed_rpm.py** - Teste automatizado de velocidade

---

## 📂 Estrutura de Arquivos

```
ihm/
├── DOCUMENTAÇÃO
│   ├── CLAUDE.md ⭐ Guia principal
│   ├── README.md ⭐ Instruções de uso
│   ├── INDEX.md (este arquivo)
│   │
│   ├── RESUMO_VALIDACOES_16NOV2025.md ✅ Resumo completo
│   ├── SOLUCAO_FINAL_ANGULOS.md ✅ Solução ângulos
│   ├── DESCOBERTA_RPM_MODBUS.md ✅ Solução velocidade
│   ├── ANALISE_BYTE_099_LADDER.md 🔍 Análise problema
│   ├── RESULTADO_TESTE_GRAVACAO.md 📊 Relatório testes
│   └── TESTES_GRAVACAO_MBPOLL.md 📖 Guia mbpoll
│
├── CÓDIGO PYTHON
│   ├── modbus_map.py ⭐ Mapa de endereços (95 registros)
│   ├── modbus_client.py ⭐ Cliente Modbus (stub + live)
│   ├── state_manager.py ⏳ Gerenciador de estado (a atualizar)
│   ├── main_server.py ⏳ Servidor WebSocket (a atualizar)
│   └── requirements.txt
│
├── INTERFACE WEB
│   └── static/
│       └── index.html ⏳ Interface web (a atualizar)
│
├── TESTES PYTHON
│   ├── test_new_angles.py ✅ Teste ângulos
│   ├── test_speed_rpm.py ✅ Teste velocidade
│   ├── test_clp_connection.py
│   └── test_screen_register.py
│
├── TESTES BASH/MBPOLL
│   ├── test_write_complete_mbpoll.sh ⭐ Menu completo
│   ├── test_write_angles_mbpoll.sh
│   └── test_write_speed_mbpoll.sh
│
└── LADDER (REFERÊNCIA)
    ├── Principal.lad
    ├── ROT0.lad - ROT5.lad
    ├── Int1.lad, Int2.lad
    └── clp_MODIFICADO_IHM_WEB.sup
```

---

## 🔑 Arquivos-Chave

### 1. CLAUDE.md
**O que é**: Instruções completas para Claude Code
**Quando usar**: Primeira leitura, contexto do projeto
**Conteúdo**:
- Arquitetura do sistema
- Especificações da máquina
- Mapeamento Modbus
- Regras de negócio
- Comandos úteis

### 2. modbus_map.py
**O que é**: Constantes Python com todos os endereços Modbus
**Quando usar**: Desenvolvimento, referência rápida
**Conteúdo**:
- 95 endereços validados
- Botões (K0-K9, S1, S2, etc.)
- LEDs (1-5)
- I/O Digital (E0-E7, S0-S7)
- Encoder (32-bit)
- Ângulos (0x0500 - validado)
- Velocidade (0x094C - validado)

### 3. modbus_client.py
**O que é**: Biblioteca cliente Modbus com modo stub
**Quando usar**: Desenvolvimento, testes
**Recursos**:
- Modo stub (sem CLP)
- Modo live (com CLP)
- 5 novos métodos validados:
  - `write_bend_angle()`
  - `read_bend_angle()`
  - `read_all_bend_angles()`
  - `write_speed_class()`
  - `read_speed_class()`

### 4. RESUMO_VALIDACOES_16NOV2025.md
**O que é**: Resumo de todas as validações
**Quando usar**: Referência rápida de descobertas
**Conteúdo**:
- Tabela resumo de endereços
- Descobertas críticas
- Código validado
- Estatísticas de testes

---

## 📖 Guias Temáticos

### Ângulos de Dobra

**Documentos principais**:
1. SOLUCAO_FINAL_ANGULOS.md
2. ANALISE_BYTE_099_LADDER.md

**Código**:
- `modbus_map.py`: BEND_ANGLES (0x0500-0x0504)
- `modbus_client.py`: write_bend_angle(), read_bend_angle()

**Testes**:
- `test_new_angles.py` (Python)
- `test_write_angles_mbpoll.sh` (Bash)

**Comandos rápidos**:
```bash
# Gravar 90° na Dobra 1
mbpoll -a 1 -b 57600 -P none -s 2 -r 1280 -t 4 -1 /dev/ttyUSB0 900
```

---

### Mudança de Velocidade (RPM)

**Documentos principais**:
1. DESCOBERTA_RPM_MODBUS.md

**Código**:
- `modbus_map.py`: SUPERVISION_AREA['SPEED_CLASS'] (0x094C)
- `modbus_client.py`: write_speed_class(), read_speed_class()

**Testes**:
- `test_speed_rpm.py` (Python)
- `test_write_speed_mbpoll.sh` (Bash)

**Comandos rápidos**:
```bash
# Mudar para 15 rpm
mbpoll -a 1 -b 57600 -P none -s 2 -r 2380 -t 4 -1 /dev/ttyUSB0 15
```

---

### Encoder (Posição Angular)

**Código**:
- `modbus_map.py`: ENCODER (0x04D6/0x04D7)
- `modbus_client.py`: read_32bit()

**Comandos rápidos**:
```bash
# Ler encoder (32-bit MSW+LSW)
mbpoll -a 1 -b 57600 -P none -s 2 -r 1238 -t 4 -c 2 -1 /dev/ttyUSB0
```

---

### Botões / Teclado

**Código**:
- `modbus_map.py`: KEYBOARD_NUMERIC, KEYBOARD_FUNCTION
- `modbus_client.py`: press_key(), simulate_key_press()

**Comandos rápidos**:
```bash
# Pressionar K1 (pulso 100ms)
mbpoll -a 1 -b 57600 -P none -s 2 -r 160 -t 0 -1 /dev/ttyUSB0 1
sleep 0.1
mbpoll -a 1 -b 57600 -P none -s 2 -r 160 -t 0 -1 /dev/ttyUSB0 0
```

---

### I/O Digital

**Código**:
- `modbus_map.py`: DIGITAL_INPUTS, DIGITAL_OUTPUTS

**Comandos rápidos**:
```bash
# Ler entradas E0-E7
mbpoll -a 1 -b 57600 -P none -s 2 -r 256 -t 0 -c 8 -1 /dev/ttyUSB0

# Ler saídas S0-S7
mbpoll -a 1 -b 57600 -P none -s 2 -r 384 -t 0 -c 8 -1 /dev/ttyUSB0
```

---

## 🧪 Como Executar os Testes

### Menu Interativo (RECOMENDADO)
```bash
cd /home/lucas-junges/Documents/clientes/w\&co/ihm
./test_write_complete_mbpoll.sh
```

### Testes Python
```bash
# Testar ângulos
python3 test_new_angles.py

# Testar velocidade
python3 test_speed_rpm.py

# Testar cliente Modbus
python3 modbus_client.py  # Modo stub
```

### Testes Bash/mbpoll
```bash
# Ângulos
./test_write_angles_mbpoll.sh

# Velocidade
./test_write_speed_mbpoll.sh
```

---

## 🛠️ Desenvolvimento

### Setup Inicial
```bash
# Instalar dependências
pip3 install -r requirements.txt

# Verificar porta serial
ls -l /dev/ttyUSB*

# Testar conexão
python3 test_clp_connection.py
```

### Desenvolvimento Web-First
```python
# Usar modo stub (sem CLP)
from modbus_client import ModbusClientWrapper

client = ModbusClientWrapper(stub_mode=True)
# Desenvolver/testar interface sem hardware
```

### Migração para Live
```python
# Trocar para modo live
client = ModbusClientWrapper(
    stub_mode=False,
    port='/dev/ttyUSB0'
)
# Teste com CLP conectado
```

---

## ⚠️ Avisos Importantes

### NÃO ESCREVER nestas áreas:
- ❌ 0x0840-0x0852 (ângulos shadow - protegidos por ROT4/ROT5)
- ❌ 0x04D6/0x04D7 (encoder - valor físico)
- ❌ 0x0100-0x0107 (entradas digitais - read-only)
- ❌ 0x0180-0x0187 (saídas digitais - controladas por ladder)

### SEGURO ESCREVER:
- ✅ 0x0500-0x0504 (ângulos setpoint - validado)
- ✅ 0x094C (velocidade - validado)
- ✅ 0x00A0-0x00F1 (botões - pulso 100ms)

---

## 📊 Estatísticas do Projeto

**Linhas de código**: ~2000
**Arquivos Python**: 8
**Arquivos de teste**: 6
**Documentação**: 8 arquivos markdown
**Registros mapeados**: 95
**Taxa de sucesso**: 100% (45/45 testes)

---

## 🔗 Links Úteis

### Manuais
- Manual CLP: `manual_MPC4004.txt`
- Manual Máquina: `NEOCOUDE-HD 15 - Camargo 2007 (1).pdf`

### Referências Online
- pyModbus: https://pymodbus.readthedocs.io/
- mbpoll: https://github.com/epsilonrt/mbpoll

---

## 🆘 Troubleshooting Rápido

**Problema**: Não conecta no CLP
```bash
# Verificar porta
ls -l /dev/ttyUSB*

# Testar com mbpoll
mbpoll -a 1 -b 57600 -P none -s 2 -r 190 -t 0 -c 1 /dev/ttyUSB0
```

**Problema**: Valores não gravam
```bash
# Confirmar área correta
# ✅ Ângulos: usar 0x0500, NÃO 0x0840
# ✅ Velocidade: usar 0x094C direto, NÃO K1+K7
```

**Problema**: Timeout Modbus
```bash
# Aumentar timeout
# Em Python: timeout=2.0 (padrão 1.0)
# Em mbpoll: -t 2.00
```

---

## 📞 Contato e Suporte

**Desenvolvedor**: Claude Code (Anthropic)
**Cliente**: W&Co
**Máquina**: Trillor NEOCOUDE-HD-15 (2007)
**Data**: Novembro 2025

---

**Última atualização**: 16/Nov/2025 23:45
**Versão**: 2.0 (Validações completas)
