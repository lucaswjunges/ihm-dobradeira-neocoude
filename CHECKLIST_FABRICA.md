# ✅ CHECKLIST FINAL - FÁBRICA

## 🚨 VERIFICAÇÃO PRÉ-FÁBRICA (Fazer HOJE, antes de ir)

### 1. Teste Local Completo

```bash
cd /home/lucas-junges/Documents/clientes/w\&co
./start_ihm.sh
```

**Verificar**:
- [ ] Servidor inicia sem erros
- [ ] Firefox abre `ihm_final.html` automaticamente
- [ ] LED WebSocket fica VERDE
- [ ] LED CLP fica VERDE (com CLP conectado) ou VERMELHO (sem CLP - normal)

---

### 2. Teste de Navegação

**Usar setas ↑ ↓ (botões OU teclado)**:
- [ ] Tela 0 → Tela 1 → Tela 2 → ... → Tela 10
- [ ] Navegação circular funciona
- [ ] Número da tela atualiza no display

---

### 3. Teste de Feedback Visual

**Pressionar cada botão e verificar**:
- [ ] K1: Botão pisca VERDE por 150ms e volta ao normal
- [ ] K2: Botão pisca VERDE por 150ms e volta ao normal
- [ ] S1: Botão pisca VERDE por 150ms e volta ao normal
- [ ] ENTER: Botão pisca VERDE por 150ms e volta ao normal
- [ ] ESC: Botão pisca VERDE por 150ms e volta ao normal

**Notificação**:
- [ ] Mensagem "✓ Tecla XXX" aparece no canto direito
- [ ] Notificação some após 1.2 segundos

---

### 4. Teste de Tooltips e Hints

**Passar mouse sobre cada botão**:
- [ ] K1 mostra tooltip "1 / Vai p/ Ângulo 01"
- [ ] K1 mostra hint "Ang1" abaixo do texto
- [ ] S1 mostra tooltip "Modo AUTO/MAN (Tela 2)"
- [ ] S1 mostra hint "Modo" abaixo do texto
- [ ] K4 mostra hint "←" (seta esquerda)
- [ ] K5 mostra hint "→" (seta direita)

---

### 5. Teste com CLP Conectado

**Conectar cabo USB-RS485 ao CLP**:
```bash
ls -l /dev/ttyUSB*
```

- [ ] Porta aparece como `/dev/ttyUSB0` ou `/dev/ttyUSB1`
- [ ] Reiniciar servidor: `pkill -f ihm_v6_server.py && ./start_ihm.sh`
- [ ] LED CLP fica VERDE
- [ ] Navegar até Tela 3 (DESLOCAMENTO ANGULAR)
- [ ] Encoder atualiza em tempo real (mover manualmente a placa da máquina)

---

### 6. Teste de Envio de Teclas ao CLP

**Com CLP conectado**:
- [ ] Pressionar K1: Verificar no log `tail -f ihm_v6_server.log | grep "Tecla 160"`
- [ ] Pressionar S1: Verificar no log `tail -f ihm_v6_server.log | grep "Tecla 220"`
- [ ] Verificar se CLP responde (observar máquina física)

---

### 7. Teste de Reconexão Automática

**Simular queda de conexão**:
- [ ] Parar servidor: `pkill -f ihm_v6_server.py`
- [ ] LED WebSocket fica VERMELHO
- [ ] Interface mostra status "Offline"
- [ ] Reiniciar servidor: `python3 ihm_v6_server.py --port /dev/ttyUSB0 --ws-port 8086 &`
- [ ] LED WebSocket volta a VERDE automaticamente (máximo 2 segundos)

---

## 📦 MATERIAIS PARA LEVAR À FÁBRICA

### Hardware
- [ ] Notebook carregado (bateria cheia + fonte)
- [ ] Cabo USB-RS485-FTDI
- [ ] CLP Atos MPC4004
- [ ] Fonte 24V para CLP
- [ ] Cabos de força

### Software (Já instalado)
- [ ] Python 3.x
- [ ] pymodbus (`pip3 show pymodbus`)
- [ ] websockets (`pip3 show websockets`)
- [ ] Firefox

### Arquivos Críticos (Verificar existência)
```bash
ls -lh ihm_final.html
ls -lh ihm_v6_server.py
ls -lh start_ihm.sh
ls -lh modbus_client.py
```

- [ ] `ihm_final.html` existe
- [ ] `ihm_v6_server.py` existe
- [ ] `start_ihm.sh` tem permissão de execução (`chmod +x start_ihm.sh`)
- [ ] `modbus_client.py` existe

---

## 🏭 PROCEDIMENTO NA FÁBRICA

### 1. Montagem Física (10 min)
1. Conectar CLP à fonte 24V
2. Conectar cabo USB-RS485 do notebook ao CLP (canal B)
3. Verificar LEDs do CLP acesos
4. Verificar porta serial: `ls -l /dev/ttyUSB*`

### 2. Inicialização do Sistema (30 segundos)
```bash
cd /home/lucas-junges/Documents/clientes/w\&co
./start_ihm.sh
```

**Aguardar**:
- Mensagem "✅ SISTEMA PRONTO!"
- Firefox abre automaticamente
- LEDs WebSocket e CLP ficam VERDES

### 3. Verificação Funcional (2 min)
- [ ] Navegar entre telas (↑ ↓)
- [ ] Ir para Tela 3, verificar encoder atualizando
- [ ] Pressionar K1, verificar feedback verde
- [ ] Pressionar S1 na Tela 2 (tentar alternar modo AUTO/MAN)

### 4. Teste com Operador (5 min)
- [ ] Mostrar navegação com setas
- [ ] Explicar tooltips (passar mouse sobre botões)
- [ ] Demonstrar Tela 3 (encoder em tempo real)
- [ ] Explicar K1/K2/K3 (navegação para ângulos)
- [ ] Explicar S1 (modo AUTO/MAN na Tela 2)
- [ ] Explicar S2 (reset encoder na Tela 3)

---

## 🚨 PROBLEMAS COMUNS E SOLUÇÕES

### LED WebSocket Vermelho
```bash
pkill -f ihm_v6_server.py
sleep 2
./start_ihm.sh
```

### LED CLP Vermelho
1. Verificar cabo USB-RS485 conectado
2. Verificar CLP ligado (24V)
3. Verificar porta: `ls -l /dev/ttyUSB*`
4. Tentar porta alternativa: `python3 ihm_v6_server.py --port /dev/ttyUSB1 --ws-port 8086 &`

### Botões Não Respondem
- Verificar LED WebSocket VERDE
- Recarregar página (F5)
- Ver logs: `tail -f ihm_v6_server.log`

### Encoder Não Atualiza
- Verificar Tela 3 ativa
- Mover placa da máquina manualmente
- Verificar logs: `tail -f ihm_v6_server.log | grep encoder`

---

## 📊 MAPEAMENTO RÁPIDO DAS TECLAS

| Tecla | Função Principal | Contexto |
|-------|------------------|----------|
| ↑ ↓ | Navega telas | Sempre |
| K1 | Vai p/ Tela 4 (Ângulo 01) | Qualquer tela |
| K2 | Vai p/ Tela 5 (Ângulo 02) | Qualquer tela |
| K3 | Vai p/ Tela 6 (Ângulo 03) | Qualquer tela |
| K4 | Sentido Esquerda | Modo AUTO |
| K5 | Sentido Direita | Modo AUTO |
| K7 | Velocidade (c/ K1) | Modo MANUAL, Tela 7 |
| S1 | Alterna AUTO/MAN | Tela 2, máquina parada |
| S2 | Reset Encoder | Tela 3 |
| ENTER | Confirma | Modo EDIT |
| ESC | Cancela | Modo EDIT |
| EDIT | Edita valor | Telas 4/5/6 |
| LOCK | Trava teclado | Sempre |

---

## ✅ ASSINATURA DE APROVAÇÃO

**Data do teste local**: ___/___/2025

**Todos os itens verificados**: [ ] SIM [ ] NÃO

**Problemas encontrados**:
_________________________________________________________________
_________________________________________________________________

**Sistema aprovado para fábrica**: [ ] SIM [ ] NÃO

**Responsável**: Lucas Junges

---

## 📞 SUPORTE DE EMERGÊNCIA

**Ver logs em tempo real**:
```bash
tail -f ihm_v6_server.log
```

**Reiniciar tudo do zero**:
```bash
pkill -f ihm_v6_server.py
pkill firefox
sleep 5
./start_ihm.sh
```

**Verificar processos rodando**:
```bash
ps aux | grep ihm_v6_server
```

**Matar processo travado**:
```bash
pkill -9 -f ihm_v6_server.py
```

---

**Sistema**: IHM Web NEOCOUDE-HD-15
**Versão**: Final Production 1.0
**Data**: 09/11/2025
**Status**: ✅ Pronto para fábrica
