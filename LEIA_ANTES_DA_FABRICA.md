# 🏭 LEIA ANTES DE IR À FÁBRICA

## ⚡ INÍCIO EM 30 SEGUNDOS

```bash
cd /home/lucas-junges/Documents/clientes/w\&co
./start_ihm.sh
```

**Pronto!** Firefox abre automaticamente com a IHM rodando.

---

## ✅ O QUE FOI CORRIGIDO (Última Versão)

### 1. ✅ Botões Piscam Verde Corretamente
- **Antes**: Botões ficavam verdes PARA SEMPRE
- **Agora**: Botões piscam verde por 150ms e voltam ao normal
- **Como testar**: Clique em qualquer botão, ele deve piscar verde e voltar

### 2. ✅ Mapeamento Completo das Teclas
- **Arquivo**: `MAPEAMENTO_COMPLETO_TECLAS.md`
- **Conteúdo**: Todas as 18 teclas documentadas com:
  - Endereço Modbus
  - Função em cada contexto (tela, modo, estado)
  - Comportamento dos LEDs
  - Combinações especiais (K1+K7 para velocidade)

### 3. ✅ Interface Final com Tooltips e Hints
- **Arquivo**: `ihm_final.html` (usado pelo start_ihm.sh)
- **Melhorias**:
  - Tooltips ao passar mouse (ex: "1 / Vai p/ Ângulo 01")
  - Hints visuais abaixo dos botões (ex: "Ang1", "←", "→", "Vel")
  - Texto de ajuda explicando combinações especiais
  - Feedback visual aprimorado

---

## 🎯 FUNCIONALIDADES GARANTIDAS

### Navegação
- ✅ Setas ↑↓ navegam entre 11 telas (local, não depende do CLP)
- ✅ Teclado do PC também funciona (setas, Enter, Esc, números 0-9)
- ✅ Navegação circular (Tela 10 → Tela 0)

### Encoder em Tempo Real
- ✅ Tela 3 mostra posição angular atualizada a cada 250ms
- ✅ Leitura 32-bit de registros 1238/1239 (MSW/LSW)
- ✅ Formato: "PV=  90° (    90)"

### Envio de Teclas ao CLP
- ✅ Todas as 18 teclas mapeadas corretamente
- ✅ Protocolo: Force Coil ON (100ms) → OFF
- ✅ Feedback: Botão pisca verde + notificação + log

### Status e Reconexão
- ✅ LEDs indicam: WebSocket (servidor) e CLP (Modbus)
- ✅ Reconexão automática a cada 2 segundos se cair
- ✅ Logs salvos em `ihm_v6_server.log`

---

## 🔑 TECLAS ESPECIAIS (Contexto-Dependente)

### S1 (220) - Modo AUTO/MAN
- **Onde**: Tela 2 (SELECAO DE AUTO/MAN)
- **Quando**: Somente quando máquina PARADA
- **Função**: Alterna entre modo AUTOMÁTICO ↔ MANUAL
- **LED**: S1 acende em modo AUTO

### S2 (221) - Reset Encoder
- **Onde**: Tela 3 (DESLOCAMENTO ANGULAR)
- **Quando**: Máquina em posição zero física
- **Função**: Zera o encoder (PV=0°)

### K1+K7 - Velocidade
- **Onde**: Tela 7 (SELECAO DA ROTACAO)
- **Quando**: Modo MANUAL e máquina PARADA
- **Função**: Cicla classe de velocidade: 5 → 10 → 15 → 5 RPM
- **Como**: Pressionar K1 e K7 SIMULTANEAMENTE

### K1, K2, K3 - Navegação para Ângulos
- **De**: Qualquer tela
- **Para**: Tela 4 (K1), Tela 5 (K2), Tela 6 (K3)
- **Uso**: Acesso rápido aos ajustes de ângulos
- **LEDs**: K1/K2/K3 acendem quando na respectiva tela ou dobra ativa

### K4, K5 - Sentido de Rotação
- **Modo**: AUTOMÁTICO apenas
- **Quando**: Após pressionar botão PARADA (painel físico)
- **K4**: Sentido ANTI-HORÁRIO (esquerda)
- **K5**: Sentido HORÁRIO (direita)
- **LEDs**: K4/K5 acendem quando sentido selecionado

---

## 📺 AS 11 TELAS

| # | Nome | Linha 1 | Linha 2 |
|---|------|---------|---------|
| 0 | Splash | **TRILLOR MAQUINAS** | **DOBRADEIRA HD    ** |
| 1 | Cliente | CAMARGO CORREIA CONS | AQUISICAO AGOSTO- 06 |
| 2 | **Modo** | SELECAO DE AUTO/MAN | (S1 alterna aqui) |
| 3 | **Encoder** | DESLOCAMENTO ANGULAR | PV=  90° (    90) |
| 4 | Ângulo 1 | AJUSTE DO ANGULO  01 | AJ=    °    PV=    ° |
| 5 | Ângulo 2 | AJUSTE DO ANGULO  02 | AJ=    °    PV=    ° |
| 6 | Ângulo 3 | AJUSTE DO ANGULO  03 | AJ=    °    PV=    ° |
| 7 | **Rotação** | *SELECAO DA ROTACAO* | (K1+K7 muda classe) |
| 8 | Carenagem | CARENAGEM DOBRADEIRA | (vazio) |
| 9 | Timer | TOTALIZADOR DE TEMPO | *****     :  h ***** |
| 10 | Status | ESTADO DA MAQUINA | (vazio) |

**Telas importantes marcadas em negrito**

---

## 🔧 ESPECIFICAÇÕES TÉCNICAS

### Hardware
- **CLP**: Atos MPC4004 (Slave ID: 1)
- **Porta**: /dev/ttyUSB0 ou /dev/ttyUSB1
- **Baudrate**: 57600
- **Parity**: None
- **Stop bits**: 2 (CRÍTICO!)
- **Data bits**: 8

### Software
- **Backend**: ihm_v6_server.py (Python 3 + pymodbus + websockets)
- **Frontend**: ihm_final.html (HTML5 + JavaScript vanilla)
- **WebSocket**: localhost:8086
- **Polling**: 250ms (encoder, I/Os)

### Protocolo
- **Leitura Encoder**: Read Holding Registers (0x03) @ 1238/1239
- **Leitura I/Os**: Read Holding Registers (0x03) @ 256-263 (E0-E7), 384-391 (S0-S7)
- **Envio Teclas**: Force Single Coil (0x05) @ endereços 37-241
- **Timing**: ON (100ms) → OFF

---

## 🚨 PROCEDIMENTO NA FÁBRICA

### 1. Montagem (5 min)
1. CLP → Fonte 24V
2. Notebook → CLP via USB-RS485 (canal B)
3. Verificar: `ls -l /dev/ttyUSB*` (deve aparecer /dev/ttyUSB0 ou /dev/ttyUSB1)

### 2. Inicialização (30 seg)
```bash
cd /home/lucas-junges/Documents/clientes/w\&co
./start_ihm.sh
```

### 3. Verificação (1 min)
- [ ] LEDs WebSocket e CLP VERDES
- [ ] Navegar Tela 0 → Tela 3
- [ ] Encoder atualizando (mover placa manualmente)
- [ ] Pressionar K1: botão pisca verde

### 4. Teste com Operador (3 min)
- Mostrar navegação (↑↓)
- Mostrar Tela 3 (encoder)
- Explicar S1 (modo, Tela 2)
- Explicar K1/K2/K3 (ângulos)
- Demonstrar feedback visual (botão pisca)

---

## 🛠️ SOLUÇÃO DE PROBLEMAS RÁPIDA

### LED WebSocket Vermelho
```bash
pkill -f ihm_v6_server.py && ./start_ihm.sh
```

### LED CLP Vermelho
1. Cabo USB-RS485 conectado?
2. CLP ligado (24V)?
3. Porta correta? `ls -l /dev/ttyUSB*`
4. Tentar porta alternativa:
```bash
pkill -f ihm_v6_server.py
python3 ihm_v6_server.py --port /dev/ttyUSB1 --ws-port 8086 &
```

### Botões Não Piscam Verde
- Recarregar página (F5)
- Ver: `CHECKLIST_FABRICA.md` item 3

### Encoder Não Atualiza
- Ir para Tela 3
- Mover placa manualmente
- Ver logs: `tail -f ihm_v6_server.log | grep encoder`

---

## 📁 ARQUIVOS IMPORTANTES

| Arquivo | Descrição |
|---------|-----------|
| `start_ihm.sh` | **USAR ESTE** para iniciar tudo |
| `ihm_final.html` | Interface web FINAL (com tooltips) |
| `ihm_v6_server.py` | Servidor Python |
| `modbus_client.py` | Cliente Modbus RTU |
| `MAPEAMENTO_COMPLETO_TECLAS.md` | **Documentação completa das teclas** |
| `CHECKLIST_FABRICA.md` | **Checklist de verificação** |
| `README_FABRICA.md` | Guia geral |
| `ihm_v6_server.log` | Logs do sistema |

---

## 📋 CHECKLIST PRÉ-FÁBRICA (Fazer HOJE)

- [ ] Testar localmente: `./start_ihm.sh`
- [ ] Verificar feedback dos botões (piscam verde?)
- [ ] Verificar tooltips (passar mouse sobre K1, S1, etc.)
- [ ] Testar navegação (↑↓)
- [ ] Se tiver CLP aqui: testar encoder na Tela 3
- [ ] Ler `MAPEAMENTO_COMPLETO_TECLAS.md` (5 min)
- [ ] Ler `CHECKLIST_FABRICA.md` (10 min)
- [ ] Carregar bateria do notebook
- [ ] Separar cabo USB-RS485

---

## 🎯 DIFERENÇAS DA VERSÃO ANTERIOR

| Aspecto | Versão Anterior (v5) | Versão Atual (FINAL) |
|---------|---------------------|----------------------|
| Navegação | Dependia do CLP | **Local (JavaScript)** |
| Botões | Ficavam verdes | **Piscam 150ms** |
| Tooltips | Não tinha | **Tem (hover)** |
| Hints | Não tinha | **Tem (Ang1, ←, →, Vel)** |
| Documentação | Incompleta | **Completa (MAPEAMENTO)** |
| Arquivo usado | ihm_production.html | **ihm_final.html** |

---

## ⚠️ PONTOS CRÍTICOS

1. **Stop bits = 2**: Configuração Modbus RTU no código
2. **Botão feedback**: Deve piscar e VOLTAR (não ficar verde)
3. **S1 contexto**: Só funciona na Tela 2 quando máquina parada
4. **K1+K7 simultâneo**: Para mudar velocidade (Tela 7, MANUAL)
5. **Navegação local**: Não depende do CLP (funciona offline)
6. **Encoder 32-bit**: Lê 2 registros (1238 MSW + 1239 LSW)

---

## 📞 COMANDOS DE EMERGÊNCIA

**Ver logs em tempo real**:
```bash
tail -f ihm_v6_server.log
```

**Reiniciar tudo**:
```bash
pkill -f ihm_v6_server.py && pkill firefox && sleep 3 && ./start_ihm.sh
```

**Ver processos**:
```bash
ps aux | grep ihm_v6_server
```

**Matar travado**:
```bash
pkill -9 -f ihm_v6_server.py
```

---

## ✅ STATUS FINAL

**Sistema**: ✅ PRONTO PARA FÁBRICA

**Versão**: Production Final 1.0

**Data**: 09/11/2025

**Testado**: Localmente (aguardando teste de fábrica)

**Próximo passo**: Testar checklist HOJE, levar à fábrica AMANHÃ

---

**Boa sorte na fábrica! 🏭**
