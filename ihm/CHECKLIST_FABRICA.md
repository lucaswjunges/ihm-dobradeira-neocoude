# ✅ CHECKLIST - Instalação IHM Web na Fábrica

## 📦 Material Necessário
- [ ] Notebook com Ubuntu (servidor rodando)
- [ ] Cabo USB-RS485-FTDI (já testado)
- [ ] Cabo de rede ou roteador WiFi
- [ ] Tablet Android carregado
- [ ] Extensão elétrica (se necessário)

## 🔌 Passo 1: Conexão Física (5 min)
- [ ] Desligar máquina (chave geral)
- [ ] Desconectar IHM física (se ainda conectada)
- [ ] Conectar cabo RS485-B no CLP:
  - [ ] Terminal A do FTDI → A do CLP
  - [ ] Terminal B do FTDI → B do CLP
  - [ ] Anotar: CLP Channel B (não é Channel A!)
- [ ] Ligar máquina novamente
- [ ] Aguardar CLP entrar em RUN (LED verde)

## 🖥️ Passo 2: Iniciar Servidor (2 min)
```bash
cd /home/lucas-junges/Documents/clientes/w\&co/ihm
python3 main_server.py --port /dev/ttyUSB0
```

**Verificar log:**
- [ ] "✓ Modbus conectado" apareceu
- [ ] "✓ Servidor iniciado com sucesso"
- [ ] Sem erros de timeout

**Se falhar:**
```bash
# Testar porta alternativa
python3 main_server.py --port /dev/ttyUSB1
```

## 📱 Passo 3: Conectar Tablet (3 min)
- [ ] Tablet e notebook na mesma rede WiFi
- [ ] Descobrir IP do notebook:
  ```bash
  ip addr show | grep "inet " | grep -v 127.0.0.1
  ```
- [ ] Abrir Chrome no tablet
- [ ] Acessar: `http://[IP_NOTEBOOK]:8080/index.html`
- [ ] Verificar se aparece "WS ✓" e "CLP ✓" (verde)

## 🧪 Passo 4: Testes Funcionais (10 min)

### Teste 1: Leitura de Dados
- [ ] Encoder mostra valor (pode ser 0.0° se parado)
- [ ] Ângulos aparecem (ex: 149.8°, 180.3°, 67.4°)
- [ ] Velocidade mostra "5 RPM" (ou 10/15)

### Teste 2: Escrita de Ângulos
- [ ] Clicar em ângulo da Dobra 1
- [ ] Alterar para 90.0
- [ ] Salvar
- [ ] Verificar se valor persiste após recarregar página

### Teste 3: Alterar Velocidade
- [ ] Clicar em "10 RPM"
- [ ] Verificar se botão fica destacado
- [ ] Aguardar 2 segundos
- [ ] Valor deve persistir

### Teste 4: Controle Motor (CRÍTICO!)
⚠️ **ATENÇÃO: Máquina vai MOVER!**
- [ ] Verificar área livre
- [ ] Avisar operadores
- [ ] Clicar "AVANÇAR" (motor CCW)
- [ ] Verificar se prato começa a girar
- [ ] Clicar "PARAR"
- [ ] Verificar parada imediata
- [ ] Testar "RECUAR" (motor CW)
- [ ] Verificar rotação oposta

## 🚨 Troubleshooting

### Problema: "DESLIGADO" na interface
**Causa:** WebSocket não conectou
**Solução:**
1. Verificar firewall: `sudo ufw allow 8765`
2. Recarregar página (Ctrl+F5)
3. Verificar IP correto no navegador

### Problema: "FALHA CLP" na interface
**Causa:** Modbus desconectado
**Solução:**
1. Verificar cabo RS485 (A↔A, B↔B)
2. Confirmar CLP em RUN
3. Testar com mbpoll:
   ```bash
   mbpoll -a 1 -b 57600 -P none -s 2 -r 1238 -c 2 -t 3 /dev/ttyUSB0
   ```

### Problema: Motor não liga
**Possíveis causas:**
1. Emergência acionada (verificar botão físico)
2. Relé de segurança desligado
3. Inversor em falha (verificar display WEG)
4. Saídas S0/S1 não conectadas ao inversor

**Teste manual (sem IHM):**
- Verificar se motor gira manualmente (sem força)
- Verificar se inversor está energizado (display aceso)
- Testar botões físicos do painel (se funcionarem)

### Problema: Encoder não muda valor
**Normal se:**
- Máquina parada (encoder só conta pulsos quando gira)
- Cabo encoder desconectado (verificar E100/E101 no CLP)

**Teste:**
- Girar prato manualmente (alguns graus)
- Verificar se valor atualiza na IHM

## 📋 Log de Testes (Preencher na Fábrica)

| Teste | Resultado | Observações |
|-------|-----------|-------------|
| Modbus conectou | ☐ OK ☐ Falhou | ___________________ |
| WebSocket conectou | ☐ OK ☐ Falhou | ___________________ |
| Leitura encoder | ☐ OK ☐ Falhou | Valor: ___________° |
| Leitura ângulos | ☐ OK ☐ Falhou | D1:___ D2:___ D3:___ |
| Escrita ângulo | ☐ OK ☐ Falhou | ___________________ |
| Mudança velocidade | ☐ OK ☐ Falhou | ___________________ |
| Motor AVANÇAR | ☐ OK ☐ Falhou | ___________________ |
| Motor RECUAR | ☐ OK ☐ Falhou | ___________________ |
| Motor PARAR | ☐ OK ☐ Falhou | ___________________ |

## ✅ Critérios de Aceitação

**Mínimo para aprovar:**
- [x] Modbus conecta
- [x] WebSocket conecta
- [x] Lê encoder (mesmo que zero)
- [x] Lê/escreve ângulos
- [x] Motor liga/desliga via IHM

**Opcional (pode debugar depois):**
- [ ] Encoder atualiza durante movimento
- [ ] Ciclo automático completo
- [ ] Mudança de modo AUTO/MANUAL

## 📞 Contato de Suporte
- **Desenvolvedor:** Eng. Lucas William Junges
- **Arquivos importantes:**
  - `/home/lucas-junges/Documents/clientes/w&co/ihm/`
  - Logs: `server_producao_new.log`

---
**Data:** _____________  
**Hora início:** _______  
**Hora fim:** _______  
**Status final:** ☐ APROVADO ☐ PENDÊNCIAS ☐ REPROVADO
