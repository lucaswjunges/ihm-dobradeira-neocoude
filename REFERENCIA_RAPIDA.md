# 🎯 REFERÊNCIA RÁPIDA - IHM NEOCOUDE

## ⚡ COMANDOS ESSENCIAIS

```bash
# INICIAR SISTEMA
cd /home/lucas-junges/Documents/clientes/w\&co && ./start_ihm.sh

# VER LOGS
tail -f ihm_v6_server.log

# REINICIAR
pkill -f ihm_v6_server.py && ./start_ihm.sh

# VERIFICAR PORTA
ls -l /dev/ttyUSB*
```

---

## 🎮 MAPA DE TECLAS

### Navegação
| Tecla | Código | Função |
|-------|--------|--------|
| ↑ | 172 | Tela anterior |
| ↓ | 173 | Próxima tela |

### Numérico
| Tecla | Código | Extra |
|-------|--------|-------|
| K1 | 160 | → Tela 4 (Ang1) |
| K2 | 161 | → Tela 5 (Ang2) |
| K3 | 162 | → Tela 6 (Ang3) |
| K4 | 163 | Esq (AUTO) |
| K5 | 164 | Dir (AUTO) |
| K6 | 165 | - |
| K7 | 166 | Vel (c/ K1) |
| K8 | 167 | - |
| K9 | 168 | - |
| K0 | 169 | - |

### Funções
| Tecla | Código | Função |
|-------|--------|--------|
| S1 | 220 | AUTO/MAN (T2) |
| S2 | 221 | Reset Enc (T3) |
| ENTER | 37 | Confirma |
| ESC | 188 | Cancela |
| EDIT | 38 | Edita |
| LOCK | 241 | Trava |

---

## 📺 TELAS

| # | Nome | S1 | S2 | K1+K7 |
|---|------|----|----|-------|
| 0 | Splash | - | - | - |
| 1 | Cliente | - | - | - |
| 2 | **Modo** | ✅ | - | - |
| 3 | **Encoder** | - | ✅ | - |
| 4 | Ângulo 1 | - | - | - |
| 5 | Ângulo 2 | - | - | - |
| 6 | Ângulo 3 | - | - | - |
| 7 | **Rotação** | - | - | ✅ |
| 8 | Carenagem | - | - | - |
| 9 | Timer | - | - | - |
| 10 | Status | - | - | - |

---

## ⚙️ CONFIGURAÇÕES

### Modbus RTU
```
Porta: /dev/ttyUSB0 ou /dev/ttyUSB1
Baudrate: 57600
Parity: None
Stop bits: 2 ⚠️ CRÍTICO
Data bits: 8
Slave ID: 1
```

### WebSocket
```
URL: ws://localhost:8086
Reconexão: Auto (2s)
```

### Polling
```
Encoder: 250ms (registros 1238/1239)
I/Os: 250ms
Envio tecla: ON (100ms) → OFF
```

---

## 🔴 PROBLEMAS COMUNS

### LED WS Vermelho
```bash
pkill -f ihm_v6_server.py
./start_ihm.sh
```

### LED CLP Vermelho
1. CLP ligado?
2. Cabo conectado?
3. `ls -l /dev/ttyUSB*`

### Encoder Não Atualiza
- Ir Tela 3
- Mover placa
- `tail -f ihm_v6_server.log | grep encoder`

### Botões Não Piscam
- F5 (recarregar)
- Ver navegador: F12 → Console

---

## ✅ VERIFICAÇÃO RÁPIDA

```
[ ] ./start_ihm.sh → Sistema inicia
[ ] LED WS verde
[ ] LED CLP verde (se conectado)
[ ] ↑↓ navegam telas
[ ] K1 pisca verde 150ms
[ ] Tooltip em K1 mostra "Ang1"
[ ] Tela 3 mostra encoder
```

---

## 📞 COMANDOS DEBUG

```bash
# Processos rodando
ps aux | grep ihm_v6

# Matar travado
pkill -9 -f ihm_v6_server.py

# Últimas 50 linhas do log
tail -50 ihm_v6_server.log

# Seguir teclas enviadas
tail -f ihm_v6_server.log | grep Tecla

# Porta serial info
dmesg | grep ttyUSB
```

---

## 🎯 TESTE DE 2 MINUTOS

1. `./start_ihm.sh` (30s)
2. ↑↓ navegar telas (10s)
3. K1 → pisca verde? (5s)
4. Tela 3 → encoder atualiza? (30s)
5. S1 na Tela 2 → modo muda? (15s)
6. Logs OK? `tail ihm_v6_server.log` (30s)

**✅ Passou = Pronto para produção**

---

**Versão**: Final 1.0 | **Data**: 09/11/2025
