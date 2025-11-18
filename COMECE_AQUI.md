# 🚀 COMECE AQUI - Guia Rápido de Uso

**Última atualização**: 2025-11-10
**Status**: ✅ Projeto COMPLETO

---

## 📁 ARQUIVO PRINCIPAL

### Para carregar no CLP:

```
📦 clp_FINAL_COM_ROT5.sup  (28 KB)
```

Este é o **ÚNICO ARQUIVO** que você precisa para carregar no CLP via WinSup 2.

---

## 📚 DOCUMENTAÇÃO - LEIA NESTA ORDEM

### 1️⃣ **RESUMO_EXECUTIVO_ENTREGA.md** (Leia PRIMEIRO)
- Visão geral do projeto
- O que foi entregue
- Como começar (3 passos simples)
- Checklist completo

### 2️⃣ **IMPLEMENTACAO_FINAL_ROT5.md** (Guia de Implementação)
- Como carregar o .sup no CLP
- Como configurar comunicação Modbus
- Código Python de teste
- Checklist antes/durante/depois instalação
- Troubleshooting

### 3️⃣ **ROT5_FINAL_PROFISSIONAL.md** (Referência Técnica)
- Especificação completa das 33 linhas do ROT5
- Mapeamento de memória detalhado (0A00-0AFF, 03E0-03FF)
- Exemplos de código Python para cada funcionalidade
- Arquitetura shadow register

### 4️⃣ **CONTROLE_RPM_VIA_MODBUS.md** (Controle de Velocidade)
- Como mudar RPM (5/10/15) remotamente
- Código Python completo backend
- Código HTML/JavaScript completo frontend
- Validações de segurança

---

## ⚡ INÍCIO RÁPIDO (5 MINUTOS)

### Passo 1: Carregar no CLP (2 minutos)

1. Abrir **WinSup 2** no Windows
2. Menu → **Arquivo** → **Abrir Projeto**
3. Selecionar: `clp_FINAL_COM_ROT5.sup`
4. Verificar que abre sem erros ✅
5. Menu → **Transferir** → **Computador para CLP**
6. Aguardar transferência e reiniciar CLP

### Passo 2: Testar Comunicação (2 minutos)

```bash
# No Linux/Ubuntu
pip3 install pymodbus

python3 - << 'EOF'
from pymodbus.client import ModbusSerialClient

client = ModbusSerialClient(
    port='/dev/ttyUSB0',  # ou COM3 no Windows
    baudrate=57600,
    stopbits=2,
    parity='N'
)

if client.connect():
    print("✅ Conectado ao CLP")

    # Ler modo do sistema (shadow register 0A01)
    result = client.read_holding_registers(0x0A01, 1, slave=1)
    if not result.isError():
        modo = result.registers[0]
        print(f"Modo: {'AUTO' if modo == 1 else 'MANUAL'}")
    else:
        print("❌ Erro ao ler registro")

    client.close()
else:
    print("❌ Falha ao conectar")
EOF
```

### Passo 3: Simular uma Tecla (1 minuto)

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

# Simular K1 (navegar para Tela 4 - Ângulo 1)
print("Simulando K1...")
client.write_coil(993, True, slave=1)   # MB_K1 (03E1) = ON
time.sleep(0.1)
client.write_coil(993, False, slave=1)  # MB_K1 = OFF
print("✅ Comando enviado!")

client.close()
```

---

## 🎯 FUNCIONALIDADES DISPONÍVEIS

### ✅ Espelhamento LCD (Leitura)
- **0A01**: Modo (0=Manual, 1=Auto)
- **0A03**: Velocidade (1=5rpm, 2=10rpm, 3=15rpm)
- **0A04**: Dobra atual (1=K1, 2=K2, 3=K3)
- **0A06/0A07**: Ângulo 1 (32-bit)
- **0A0C/0A0D**: Encoder (32-bit)

### ✅ Emulação de Teclas (Escrita)
- **992-1001**: K0-K9 (teclas numéricas)
- **1002-1003**: S1, S2 (funções)
- **1004-1005**: Setas ↑↓
- **1006-1009**: ENTER, ESC, EDIT, LOCK

### ✅ Controle Remoto (Escrita)
- **1010-1012**: AVANÇAR, PARADA, RECUAR
- **1013-1014**: Forçar AUTO/MANUAL
- **1015**: Heartbeat (pulsar a cada 2s)

### ✅ Mudança de RPM (Escrita)
- **Registro 0900**: Classe de velocidade (1/2/3)

---

## 📊 MAPA RÁPIDO DE MEMÓRIA

### Registros Shadow (Leitura)

| Registro | Hex  | Dec  | Nome | Valores |
|----------|------|------|------|---------|
| 0A01 | 0A01 | 2561 | Modo | 0=Manual, 1=Auto |
| 0A03 | 0A03 | 2563 | Velocidade | 1=5rpm, 2=10rpm, 3=15rpm |
| 0A04 | 0A04 | 2564 | Dobra | 1=K1, 2=K2, 3=K3 |
| 0A06 | 0A06 | 2566 | Ângulo1 MSW | 16-bit alto |
| 0A07 | 0A07 | 2567 | Ângulo1 LSW | 16-bit baixo |
| 0A0C | 0A0C | 2572 | Encoder MSW | 16-bit alto |
| 0A0D | 0A0D | 2573 | Encoder LSW | 16-bit baixo |

### Bits de Comando (Escrita)

| Bit | Hex | Dec | Função |
|-----|-----|-----|--------|
| 03E0 | 03E0 | 992 | K0 |
| 03E1 | 03E1 | 993 | K1 |
| 03EA | 03EA | 1002 | S1 |
| 03EB | 03EB | 1003 | S2 |
| 03F2 | 03F2 | 1010 | AVANÇAR |
| 03F3 | 03F3 | 1011 | RECUAR |
| 03F4 | 03F4 | 1012 | PARADA |
| 03F5 | 03F5 | 1013 | Forçar AUTO |
| 03F6 | 03F6 | 1014 | Forçar MANUAL |
| 03F7 | 03F7 | 1015 | Heartbeat |

---

## ⚠️ AVISOS IMPORTANTES

### Segurança

- ✅ Emergência física (E7) sempre tem prioridade
- ✅ Botões físicos continuam funcionando
- ⚠️ IHM Web DEVE enviar heartbeat (bit 1015) a cada 2 segundos
- ⚠️ Mudança de RPM apenas em modo MANUAL
- ⚠️ Comandos 1013/1014 (forçar modo) bypassam verificações - use com cuidado

### Configuração Modbus

```
Porta: /dev/ttyUSB0 (Linux) ou COM3 (Windows)
Baudrate: 57600
Stop bits: 2  ← IMPORTANTE!
Parity: None
Data bits: 8
Slave ID: 1
```

---

## 🆘 PROBLEMAS COMUNS

### "Erro ao ler registro"
- Verificar cabo RS485 conectado
- Confirmar baudrate 57600 e **2 stop bits**
- Verificar bit 00BE (Modbus Slave) está ON no CLP

### "Comando não funciona"
- Verificar bit 03FF (Status Interface) está ON
- IHM Web deve enviar heartbeat (bit 1015) a cada 2s
- Verificar modo MANUAL para mudanças de velocidade

### "WinSup 2 não abre .sup"
- Use arquivo `clp_FINAL_COM_ROT5.sup` (não outros)
- Projeto tem 5 subroutines (ROT0-ROT4, ROT5 está integrado no ROT4)
- ROT4 deve mostrar 55 linhas (não 21)

---

## 📞 PRÓXIMOS PASSOS

1. ✅ Ler **RESUMO_EXECUTIVO_ENTREGA.md**
2. ✅ Carregar **clp_FINAL_COM_ROT5.sup** no CLP
3. ✅ Testar comunicação Modbus
4. ✅ Implementar IHM Web (usar exemplos em CONTROLE_RPM_VIA_MODBUS.md)
5. ✅ Treinar operador

---

## 📁 OUTROS ARQUIVOS (REFERÊNCIA)

Estes arquivos contêm documentação de etapas anteriores do projeto:

- `PROTOCOLO_IHM_CLP_COMPLETO.md` - Análise completa do protocolo original
- `MAPEAMENTO_COMPLETO_TECLAS.md` - Mapeamento das 18 teclas
- `SOLUCAO_COMPLETA_IHM.md` - Arquitetura geral da solução
- `MUDANCAS_LADDER_CLP.md` - Especificação de mudanças no ladder
- `RELATORIO_IMPLEMENTACAO.md` - Relatório da primeira implementação

Não é necessário ler estes arquivos para usar a solução final.

---

**Dúvidas?** Consulte:
1. `RESUMO_EXECUTIVO_ENTREGA.md` - Visão geral
2. `IMPLEMENTACAO_FINAL_ROT5.md` - Troubleshooting detalhado
3. `ROT5_FINAL_PROFISSIONAL.md` - Referência técnica completa

---

**Status**: ✅ **PRONTO PARA USO**
**Última atualização**: 2025-11-10
**Desenvolvido por**: Claude Code
