# 🏭 IHM NEOCOUDE-HD-15 - VERSÃO DE PRODUÇÃO

## ⚡ INÍCIO RÁPIDO

### Opção 1: Script Automático (RECOMENDADO)
```bash
cd /home/lucas-junges/Documents/clientes/w\&co
./start_ihm.sh
```

### Opção 2: Manual
```bash
cd /home/lucas-junges/Documents/clientes/w\&co
python3 ihm_v6_server.py --port /dev/ttyUSB0 --ws-port 8086 &
firefox ihm_production.html
```

## ✅ O QUE ESTÁ PRONTO

### Backend
- ✅ Servidor Python (ihm_v6_server.py)
- ✅ Comunicação Modbus RTU (57600, 2 stop bits)
- ✅ Leitura de encoder (32-bit, 250ms)
- ✅ Leitura de I/Os (E0-E7, S0-S7)
- ✅ Envio de comandos (teclas)

### Frontend
- ✅ IHM web responsiva (ihm_production.html)
- ✅ 11 telas navegáveis (↑↓)
- ✅ 18 teclas funcionais (K0-K9, S1/S2, etc.)
- ✅ Feedback visual (botões piscam verde)
- ✅ Notificações em tempo real
- ✅ Display LCD simulado (verde fosforescente)

### Funcionalidades
- ✅ Navegação local entre telas
- ✅ Encoder em tempo real (Tela 3)
- ✅ Envio de teclas ao CLP
- ✅ Auto-reconexão WebSocket
- ✅ Indicadores de status (WS, CLP)

## 🎮 COMO USAR

### Navegação
- **↑** ou **Seta Cima**: Tela anterior
- **↓** ou **Seta Baixo**: Próxima tela
- Funciona com botões da tela OU teclado do PC

### Teclado Numérico
- **K1-K9**: Números 1-9
- **K0**: Número 0
- **S1, S2**: Funções especiais
- **ENTER**: Confirmar
- **ESC**: Cancelar
- **EDIT**: Modo edição
- **LOCK**: Travar teclado

### Feedback
Quando você pressiona uma tecla:
1. ✅ Botão **pisca verde**
2. ✅ Notificação **canto direito** mostra "Tecla XXX enviada"
3. ✅ Log do servidor registra o comando

## 📺 AS 11 TELAS

| # | Nome | Conteúdo |
|---|------|----------|
| 0 | Splash | TRILLOR MAQUINAS / DOBRADEIRA HD |
| 1 | Cliente | CAMARGO CORREIA CONS |
| 2 | Modo | SELECAO DE AUTO/MAN |
| 3 | **Encoder** | **Posição angular em tempo real** |
| 4 | Ângulo 1 | AJUSTE DO ANGULO 01 |
| 5 | Ângulo 2 | AJUSTE DO ANGULO 02 |
| 6 | Ângulo 3 | AJUSTE DO ANGULO 03 |
| 7 | Rotação | SELECAO DA ROTACAO |
| 8 | Carenagem | CARENAGEM DOBRADEIRA |
| 9 | Timer | TOTALIZADOR DE TEMPO |
| 10 | Status | ESTADO DA MAQUINA |

## 🔧 SOLUÇÃO DE PROBLEMAS

### LED WebSocket Vermelho
```bash
pkill -f ihm_v6_server.py
./start_ihm.sh
```

### LED CLP Vermelho
1. Verificar cabo USB-RS485
2. Verificar CLP ligado (24V)
3. Verificar porta: `ls -l /dev/ttyUSB*`

### Teclas Não Respondem
- Verificar LED WebSocket verde
- Recarregar página (F5)
- Ver logs: `tail -f ihm_v6_server.log`

### Servidor Não Inicia
```bash
# Ver erro
tail -30 ihm_v6_server.log

# Tentar porta alternativa
python3 ihm_v6_server.py --port /dev/ttyUSB1 --ws-port 8086 &
```

## 📊 ESPECIFICAÇÕES TÉCNICAS

### Hardware
- **CLP**: Atos MPC4004 (Slave ID: 1)
- **Baudrate**: 57600
- **Parity**: None
- **Stop bits**: 2
- **Porta**: /dev/ttyUSB0 ou /dev/ttyUSB1

### Software
- **Backend**: Python 3.x + pymodbus + websockets
- **Frontend**: HTML5 + JavaScript (vanilla)
- **WebSocket**: localhost:8086
- **Navegador**: Firefox (recomendado)

### Performance
- **Encoder**: Atualiza a cada 250ms (4 Hz)
- **I/Os**: Atualiza a cada 250ms
- **Navegação**: Instantânea (local)
- **Latência teclas**: < 100ms

## 📁 ARQUIVOS IMPORTANTES

```
/home/lucas-junges/Documents/clientes/w&co/
├── start_ihm.sh              ← USAR ESTE para iniciar
├── ihm_production.html       ← Interface web final
├── ihm_v6_server.py         ← Servidor Python
├── modbus_client.py         ← Cliente Modbus
├── ihm_v6_server.log        ← Logs do sistema
├── GUIA_USO_FABRICA.md      ← Guia detalhado
└── README_FABRICA.md        ← Este arquivo
```

## ✅ CHECKLIST FÁBRICA

Antes de usar na máquina:
- [ ] Notebook carregado (bateria ou fonte)
- [ ] CLP ligado e funcionando
- [ ] Cabo USB-RS485 conectado
- [ ] Executar `./start_ihm.sh`
- [ ] Verificar LEDs verdes (WS + CLP)
- [ ] Testar navegação (↑↓)
- [ ] Testar Tela 3 (encoder atualiza?)
- [ ] Testar uma tecla (K1, ver feedback)

## 🚨 EM CASO DE PROBLEMAS NA FÁBRICA

### Reiniciar Tudo
```bash
pkill -f ihm_v6_server.py
sleep 5
./start_ihm.sh
```

### Ver Últimas Mensagens
```bash
tail -50 ihm_v6_server.log
```

### Testar Comunicação
```bash
# Ver se teclas chegam ao servidor
tail -f ihm_v6_server.log | grep Tecla
```

## 📞 INFORMAÇÕES DE SUPORTE

**Sistema**: IHM Web para NEOCOUDE-HD-15  
**Versão**: Production 1.0  
**Data**: 09/11/2025  
**Status**: ✅ Testado e pronto para fábrica

---

**Desenvolvido para**: W&CO / Camargo Steel  
**Máquina**: Trillor NEOCOUDE-HD-15 (2007)  
**CLP**: Atos Expert MPC4004
