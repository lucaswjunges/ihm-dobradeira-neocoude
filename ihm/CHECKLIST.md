# ✅ Checklist de Validação - IHM Web

Use esta checklist para validar se tudo está funcionando corretamente.

---

## 🔧 Pré-requisitos

- [ ] Python 3.8+ instalado (`python3 --version`)
- [ ] pip3 instalado (`pip3 --version`)
- [ ] Dependências instaladas (`pip3 install -r requirements.txt`)
- [ ] Permissões serial configuradas (`sudo usermod -a -G dialout $USER`)

---

## 🧪 Testes em Modo Stub (SEM CLP)

### Servidor
- [ ] `python3 main_server.py --stub` inicia sem erros
- [ ] Mensagem "✓ Modo STUB ativado" aparece
- [ ] WebSocket abre em `ws://localhost:8765`
- [ ] HTTP abre em `http://localhost:8080`

### Interface Web
- [ ] Navegador abre `http://localhost:8080`
- [ ] Display LCD mostra ângulo (ex: 45.7°)
- [ ] Status mostra "CONECTADO"
- [ ] 3 campos de ângulos aparecem (Dobra 1/2/3)
- [ ] Teclado virtual renderiza (K0-K9, S1/S2, etc.)
- [ ] LEDs aparecem no canto superior direito

### Interatividade
- [ ] Clicar em botão K1 gera feedback visual
- [ ] Console JavaScript não mostra erros
- [ ] Encoder atualiza periodicamente (stub pode oscilar)
- [ ] Duplo clique em ângulo permite edição

---

## 🔌 Testes com CLP Real (LIVE)

### Hardware
- [ ] CLP ligado e em modo RUN
- [ ] Cabo RS485 conectado (conversor USB-FTDI)
- [ ] Porta serial detectada (`ls -l /dev/ttyUSB*`)
- [ ] LED TX/RX do conversor pisca durante comunicação

### Comunicação Modbus
- [ ] `python3 tests/test_modbus.py` executa sem erros
- [ ] Estado 00BE = ON (Modbus slave habilitado)
- [ ] Encoder retorna valor válido (0-3600 = 0-360°)
- [ ] Ângulos retornam valores (ex: 900 = 90.0°)
- [ ] Entradas E0-E7 retornam ON/OFF
- [ ] Saídas S0-S7 retornam ON/OFF

### Servidor LIVE
- [ ] `python3 main_server.py --port /dev/ttyUSB0` inicia
- [ ] Mensagem "✓ Modbus conectado" aparece
- [ ] Polling 250ms funciona sem timeouts
- [ ] Estado `modbus_connected = True`

### Interface LIVE
- [ ] Encoder atualiza com valor real do CLP
- [ ] Ângulos programados aparecem corretamente
- [ ] Pressionar K1 no navegador altera estado no CLP
- [ ] LEDs refletem estado real (dobra ativa, direção)
- [ ] Sem overlays de erro (DESLIGADO/FALHA CLP)

---

## 🎯 Testes Funcionais Avançados

### Leitura de Ângulos
- [ ] `python3 tests/test_angles.py` lê valores corretos
- [ ] Conversão graus→CLP está correta (90° = 900)
- [ ] Conversão CLP→graus está correta (1200 = 120.0°)

### Escrita de Ângulos
- [ ] `python3 tests/test_angles.py --write` funciona
- [ ] Valor escrito é lido de volta corretamente
- [ ] Valores originais são restaurados
- [ ] Display físico do CLP reflete mudança (se disponível)

### Mudança de Velocidade
- [ ] `python3 tests/test_speed.py` simula K1+K7
- [ ] Comando é aceito pelo CLP (sem timeout)
- [ ] Verificar visualmente se classe mudou (5→10→15→5)
- [ ] ⚠️ Só funciona se máquina em MANUAL e PARADA

### Botões via WebSocket
- [ ] Pressionar K1 no navegador executa ação no CLP
- [ ] Pressionar S1 alterna modo (se implementado)
- [ ] Pressionar ENTER confirma edição
- [ ] Pressionar ESC cancela operação

---

## 🌐 Testes de Rede (Tablet)

### Configuração WiFi
- [ ] Notebook conectado à rede WiFi do tablet
- [ ] IP do notebook obtido (`ip addr show`)
- [ ] Firewall permite portas 8080/8765

### Acesso Remoto
- [ ] Tablet acessa `http://<IP_NOTEBOOK>:8080`
- [ ] Interface carrega completamente
- [ ] WebSocket conecta (`ws://<IP_NOTEBOOK>:8765`)
- [ ] Dados atualizam em tempo real

### Performance
- [ ] Latência WebSocket < 500ms
- [ ] Encoder atualiza sem lag perceptível
- [ ] Botões respondem instantaneamente (feedback < 100ms)
- [ ] Sem desconexões frequentes

---

## 🛡️ Testes de Robustez

### Desconexões
- [ ] Desconectar cabo USB → Interface mostra "FALHA CLP"
- [ ] Reconectar cabo → Interface recupera automaticamente
- [ ] Desligar CLP → Overlay vermelho "FALHA CLP"
- [ ] Ligar CLP → Interface normaliza

### Erros de Comunicação
- [ ] Endereço Modbus inválido → Não trava servidor
- [ ] Timeout Modbus → Servidor continua rodando
- [ ] Valor fora de range → Validação no frontend

### Múltiplos Clientes
- [ ] 2 tablets conectados simultaneamente
- [ ] Ambos recebem atualizações
- [ ] Comando de um afeta estado no outro

---

## 📊 Métricas de Performance

| Métrica | Esperado | Real | Status |
|---------|----------|------|--------|
| Polling CLP | 250ms | ___ | ⬜ |
| Broadcast WebSocket | 500ms | ___ | ⬜ |
| Latência botão | < 100ms | ___ | ⬜ |
| Uso CPU servidor | < 10% | ___ | ⬜ |
| Uso RAM servidor | < 100MB | ___ | ⬜ |

---

## 🚀 Checklist de Deploy Produção

- [ ] Testes stub 100% OK
- [ ] Testes live 100% OK
- [ ] Testes tablet 100% OK
- [ ] Documentação lida e compreendida
- [ ] Backup do programa ladder original (clp.sup)
- [ ] Notebook configurado como servidor dedicado
- [ ] WiFi isolado (hotspot dedicado)
- [ ] Tablet instalado próximo à máquina
- [ ] Operador treinado no uso da interface
- [ ] Procedimento de emergência definido (IHM física de backup?)

---

**Data de Validação**: ___/___/2025  
**Validado por**: ________________  
**Assinatura**: __________________
