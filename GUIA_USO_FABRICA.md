# 🏭 GUIA DE USO - FÁBRICA

## ⚡ INÍCIO RÁPIDO (30 segundos)

### 1. Ligar o Sistema
```bash
# Terminal 1 - Iniciar servidor
cd /home/lucas-junges/Documents/clientes/w\&co
python3 ihm_v6_server.py --port /dev/ttyUSB0 --ws-port 8086 &

# Terminal 2 - Abrir IHM
firefox ihm_production.html
```

### 2. Verificar Status
Na tela da IHM, verifique:
- ✅ **WebSocket**: LED verde = Online
- ✅ **CLP**: LED verde = Conectado
- ✅ **Sistema OK**: Sempre verde

## 🎮 USAR A IHM

### Navegação Entre Telas
- **↑ ↓**: Navegar entre 11 telas
- **Tela 0**: Splash inicial
- **Tela 3**: Encoder em tempo real (atualiza automaticamente)

### Teclado Numérico
- **K1-K9, K0**: Números
- **S1, S2**: Funções
- **ENTER**: Confirmar
- **ESC**: Cancelar
- **EDIT**: Editar
- **LOCK**: Travar

### Feedback Visual
- ✅ Botão **pisca verde** quando pressionado
- ✅ Notificação **canto superior direito**
- ✅ Mensagem mostra: "Tecla XXX enviada"

## 🔧 SOLUÇÃO DE PROBLEMAS

### WebSocket Offline (LED vermelho)
```bash
# Reiniciar servidor
pkill -f ihm_v6_server.py
python3 ihm_v6_server.py --port /dev/ttyUSB0 --ws-port 8086 &
```

### CLP Offline
1. Verificar cabo USB-RS485 conectado
2. Verificar CLP ligado
3. Verificar porta: `ls -l /dev/ttyUSB*`
4. Se porta mudou, ajustar comando

### Teclas Não Respondem
- Verificar se **WebSocket está Online**
- Recarregar página (F5)
- Verificar logs: `tail -f ihm_v6_server.log`

## 📊 DADOS TÉCNICOS

### Portas
- **WebSocket**: localhost:8086
- **Modbus RTU**: /dev/ttyUSB0
- **Baudrate**: 57600
- **Stop bits**: 2

### Ciclo de Atualização
- **Encoder**: 250ms (4 Hz)
- **Entradas/Saídas**: 250ms
- **Tela**: Atualiza automaticamente

## ✅ CHECKLIST PRÉ-USO

- [ ] CLP ligado (24V)
- [ ] Cabo USB-RS485 conectado ao notebook
- [ ] Servidor rodando (`ps aux | grep ihm_v6`)
- [ ] Firefox com IHM aberta
- [ ] LEDs WebSocket e CLP verdes
- [ ] Navegação funcionando (↑↓)
- [ ] Tela 3 mostrando encoder

## 🚨 EMERGÊNCIA

Se algo der errado, **REINICIAR TUDO**:
```bash
# Parar tudo
pkill -f ihm_v6_server.py

# Aguardar 5 segundos

# Reiniciar
python3 ihm_v6_server.py --port /dev/ttyUSB0 --ws-port 8086 &
firefox ihm_production.html
```

## 📞 SUPORTE

Logs em tempo real:
```bash
tail -f ihm_v6_server.log
```

Verificar comunicação Modbus:
```bash
# Ver últimas 50 linhas
tail -50 ihm_v6_server.log | grep Tecla
```

---

**Versão**: Production 1.0  
**Data**: 2025-11-09  
**Testado**: ✅ Pronto para fábrica
