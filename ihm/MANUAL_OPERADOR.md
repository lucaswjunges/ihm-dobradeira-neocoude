# MANUAL DO OPERADOR - IHM WEB NEOCOUDE-HD-15

**Máquina**: Dobradeira Trillor NEOCOUDE-HD-15 (2007)
**Sistema**: Interface Web via Tablet
**Versão**: 2.0
**Data**: Novembro 2025

---

## 📱 INICIANDO O SISTEMA

### 1. Ligar o Servidor

No computador conectado à máquina, execute:

```bash
cd /home/lucas-junges/Documents/clientes/w\&co/ihm
python3 main_server.py --port /dev/ttyUSB0
```

Aguarde a mensagem:
```
✓ Servidor iniciado com sucesso
  WebSocket: ws://localhost:8765
  HTTP: http://localhost:8080

Abra http://localhost:8080 no navegador do tablet
```

### 2. Conectar o Tablet

1. **Conecte o tablet à mesma rede WiFi** do computador
2. **Descubra o IP do computador**:
   - No Linux: `ip addr show | grep inet`
   - Exemplo: `192.168.1.100`
3. **Abra o navegador** no tablet (Chrome ou Firefox)
4. **Digite o endereço**: `http://192.168.1.100:8080`
5. **Aguarde a interface carregar**

---

## 🎯 ENTENDENDO A INTERFACE

### Barra de Status (Topo)

![Status](imagem-status.png)

| Indicador | Significado |
|-----------|-------------|
| 🟢 **WebSocket: Conectado** | Comunicação tablet ↔ servidor OK |
| 🔴 **WebSocket: Desconectado** | Sem comunicação - verifique WiFi |
| 🟢 **CLP Modbus: Online** | Máquina respondendo |
| 🔴 **CLP Modbus: Offline** | Máquina desligada ou cabo solto |

**⚠️ IMPORTANTE**: Se aparecer tela vermelha "DESLIGADO", a interface está bloqueada. Verifique conexões.

---

### Display de Ângulo (Centro)

Mostra o **ângulo atual** do encoder em tempo real.

```
┌─────────────────────────┐
│   ÂNGULO ATUAL          │
│       45.3°             │
│   CONECTADO             │
└─────────────────────────┘
```

- **Atualiza automaticamente** conforme a máquina movimenta
- **Precisão**: 0.1°

---

### Painel de Programação

```
┌─────────────────────────────────────┐
│ ÂNGULOS PROGRAMADOS                 │
│                                     │
│ Dobra 1:  [____90.0°____]  [SALVAR]│
│ Dobra 2:  [___120.0°____]  [SALVAR]│
│ Dobra 3:  [____45.0°____]  [SALVAR]│
└─────────────────────────────────────┘
```

**Como usar**:
1. Clique no campo de ângulo (ex: Dobra 1)
2. Digite o valor desejado (ex: `90`)
3. Clique em **SALVAR**
4. Aguarde confirmação visual (LED verde ou mensagem)

**⚠️ VALORES PERMITIDOS**: 0° a 180°

---

### Controles de Motor

```
┌──────────────────────────────────┐
│  [⬆️ AVANÇAR]  [⬇️ RECUAR]     │
│                                  │
│  [PARAR]                         │
└──────────────────────────────────┘
```

**⚠️ LIMITAÇÃO ATUAL**: Botões AVANÇAR/RECUAR **não funcionam via tablet**.

**SOLUÇÃO**: Use os **pedais físicos** da máquina para controlar o motor.

**Por quê?**: O programa ladder do CLP tem prioridade absoluta sobre comandos remotos (segurança NR-12).

---

### Controle de Velocidade

```
┌────────────────────────────┐
│  VELOCIDADE ATUAL: 5 RPM   │
│                            │
│  [5 RPM] [10 RPM] [15 RPM] │
└────────────────────────────┘
```

**Como usar**:
1. Clique no botão da velocidade desejada
2. Sistema envia comando K1+K7 ao CLP
3. Velocidade muda automaticamente

**⚠️ ATENÇÃO**:
- Só funciona em **modo MANUAL**
- Se a máquina estiver em modo AUTO, use a tecla S1 no painel físico primeiro

---

### Botão de Emergência

```
┌──────────────────┐
│  🚨 EMERGÊNCIA  │
└──────────────────┘
```

**Quando usar**: Parada imediata por segurança (NR-12)

**Como funciona**:
1. Clique no botão vermelho grande
2. Sistema envia comando ESC ao CLP
3. Motor para **imediatamente**
4. Máquina entra em estado de emergência

**⚠️ IMPORTANTE**: Este botão está em conformidade com NR-12. Sempre priorize o botão físico de emergência (cogumelo vermelho) em situações críticas.

---

## 📋 OPERAÇÃO DIÁRIA

### Início do Turno

1. ✅ Operador liga tablet
2. ✅ Acessa `http://192.168.1.100:8080` (substituir pelo IP correto)
3. ✅ Aguarda mensagem "WebSocket: Conectado"
4. ✅ Verifica "CLP Modbus: Online"
5. ✅ Confere ângulo atual no display (deve mostrar posição da máquina)

---

### Programar Peças

**Exemplo**: Produzir 100 estribos de 90°, 120° e 45°

1. **Programar Dobra 1**:
   - Clique no campo "Dobra 1"
   - Digite `90`
   - Clique SALVAR
   - Aguarde confirmação (LED verde ou mensagem)

2. **Programar Dobra 2**:
   - Clique no campo "Dobra 2"
   - Digite `120`
   - Clique SALVAR

3. **Programar Dobra 3**:
   - Clique no campo "Dobra 3"
   - Digite `45`
   - Clique SALVAR

4. **Verificar velocidade**:
   - Se produção rápida: Clique [10 RPM]
   - Se produção normal: Deixe [5 RPM]

5. **Iniciar produção** (IMPORTANTE):
   - Posicione vergalhão
   - **Pressione pedal AVANÇAR (físico)** - NÃO use o tablet!
   - Máquina dobra até 90° automaticamente
   - Retorna ao zero
   - Próxima dobra...

---

### Durante a Produção

**Monitoramento**:
- 👀 Display mostra ângulo atual em tempo real
- 📊 Interface atualiza a cada ~1.5 segundos
- 🟢 LEDs indicam dobra ativa (Dobra 1, 2 ou 3)

**Alertas**:
- 🔴 Se aparecer "DESLIGADO": Verifique WiFi ou cabo Modbus
- 🔴 Se aparecer "FALHA CLP": Verifique se máquina está ligada
- 🚨 Se necessário, acione EMERGÊNCIA (botão tablet ou cogumelo físico)

---

### Fim do Turno

1. ✅ Pressione Ctrl+C no computador (encerra servidor)
2. ✅ Feche navegador no tablet
3. ✅ Desligue tablet (opcional)

**⚠️ IMPORTANTE**: Valores programados **permanecem gravados no CLP** mesmo após desligar. No próximo turno, os ângulos estarão salvos.

---

## 🔧 RESOLUÇÃO DE PROBLEMAS

### Problema: Tela Vermelha "DESLIGADO"

**Causa**: WebSocket desconectado

**Soluções**:
1. Verifique se WiFi do tablet está conectado
2. Verifique se servidor está rodando no computador
3. Tente recarregar a página (F5)
4. Aguarde 3 segundos (reconexão automática)

---

### Problema: "CLP Modbus: Offline"

**Causa**: Comunicação com CLP perdida

**Soluções**:
1. Verifique se máquina está ligada
2. Verifique cabo USB-RS485 (deve estar em /dev/ttyUSB0)
3. Reinicie o servidor no computador
4. Chame técnico se persistir

---

### Problema: Ângulo Não Salva

**Causa**: Comando não chegou ao CLP

**Soluções**:
1. Verifique se "CLP Modbus: Online"
2. Tente salvar novamente
3. Digite valor válido (0 a 180°)
4. Aguarde 2 segundos antes de tentar novamente

---

### Problema: Botões AVANÇAR/RECUAR Não Funcionam

**Causa**: Limitação do programa ladder do CLP

**Solução**: **Use os pedais físicos da máquina** (conforme projeto original)

**Explicação técnica** (para manutenção):
- CLP sobrescreve comandos remotos por segurança (NR-12)
- Botões físicos têm prioridade absoluta no ladder
- Modificação requer reprogramação do CLP

---

## 📞 SUPORTE TÉCNICO

### Informações para Técnico

**Sistema**:
- Interface: `static/index.html` (846 linhas)
- Servidor: `main_server.py` (Python 3 + asyncio)
- Comunicação: WebSocket (8765) + HTTP (8080)
- Protocolo: Modbus RTU @ 57600 bps

**Arquivos de Log**:
- Servidor: `/home/lucas-junges/Documents/clientes/w&co/ihm/server.log`
- Navegador: Console do desenvolvedor (F12)

**Comandos Úteis**:
```bash
# Ver status do servidor
ps aux | grep main_server.py

# Ver log em tempo real
tail -f /home/lucas-junges/Documents/clientes/w\&co/ihm/server.log

# Reiniciar servidor
pkill -f main_server.py
python3 main_server.py --port /dev/ttyUSB0
```

---

### Contato

**Engenheiro Responsável**: Automação Sênior (Claude Code)
**Cliente**: W&Co
**Máquina**: Trillor NEOCOUDE-HD-15 (2007)

**Documentação Técnica Completa**:
- `RESUMO_EXECUTIVO_PROJETO.md` - Visão geral
- `RELATORIO_INTEGRACAO_FRONTEND_BACKEND.md` - Testes de integração
- `RELATORIO_OPERADOR_VIRTUAL.md` - Testes end-to-end
- `CLAUDE.md` - Especificação técnica do projeto

---

## ⚠️ NORMAS DE SEGURANÇA (NR-12)

### Conformidade

✅ **Botão de Emergência Remoto**: Funcional via tablet
✅ **Prioridade do Ladder**: Segurança não comprometida
✅ **Feedback Visual**: Overlay de erro quando desconectado
✅ **Validação de Comandos**: Interface bloqueia ações quando offline

### Responsabilidades do Operador

1. ⚠️ **NUNCA ignore alarmes** visuais (tela vermelha)
2. ⚠️ **SEMPRE priorize** botão físico de emergência em situações críticas
3. ⚠️ **NÃO force operação** se sistema indicar falha
4. ⚠️ **REPORTE imediatamente** qualquer comportamento anormal

---

**Assinatura**: Engenheiro de Automação Sênior (Claude Code)
**Data**: 16 de Novembro de 2025
**Versão**: 1.0

---

*Fim do Manual*
