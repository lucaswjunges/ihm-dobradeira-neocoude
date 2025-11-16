# ⚠️ CHECKLIST CRÍTICO - INSTALAÇÃO NA FÁBRICA (SEGUNDA-FEIRA)

**ATENÇÃO:** Se algo falhar, você pode ser demitido. Siga EXATAMENTE esta ordem.

---

## 📋 ANTES DE SAIR DE CASA

### 1. Hardware Necessário
- [ ] Notebook Ubuntu 25.04 (COM BATERIA CARREGADA!)
- [ ] Cabo USB-RS485-FTDI
- [ ] Cabo USB sobressalente (caso o RS485 quebre)
- [ ] Tablet com WiFi (vai virar hotspot)
- [ ] Carregador de notebook
- [ ] Carregador de tablet
- [ ] Pen drive com backup do código (`/home/lucas-junges/Documents/clientes/w&co/ihm/`)

### 2. Verificar Software no Notebook
```bash
cd /home/lucas-junges/Documents/clientes/w&co/ihm
ls -la *.py static/index.html
```

Deve mostrar:
- `modbus_client.py`
- `modbus_map.py`
- `state_manager.py`
- `main_server.py`
- `static/index.html`

### 3. Testar Conexão CLP (EM CASA, SE TIVER CLP)
```bash
python3 test_factory_scenario.py
```

Todos os 6 testes devem **PASSAR** ✅.

---

## 🏭 NA FÁBRICA - PARTE 1: HARDWARE

### 4. Conectar RS485
1. **DESLIGUE** o CLP antes de conectar!
2. Identifique porta **RS485-B** no CLP (pode estar marcada "B+" e "B-")
3. Conecte fios:
   - **Verde** (A+) → Terminal **B+** do CLP
   - **Branco** (B-) → Terminal **B-** do CLP
4. Conecte USB-RS485 no notebook
5. **LIGUE** o CLP

### 5. Verificar Porta Serial
```bash
ls -l /dev/ttyUSB*
```

Deve mostrar `/dev/ttyUSB0` ou `/dev/ttyUSB1`.

**SE NÃO APARECER:**
```bash
sudo dmesg | tail -20
```

Procure por `FTDI` ou `USB Serial`. Se não aparecer, cabo está com problema.

---

## 🏭 NA FÁBRICA - PARTE 2: CLP

### 6. Verificar Estado 00BE (Modbus Habilitado)

**CRÍTICO:** Ladder do CLP deve ter estado `00BE` (190 decimal) **FORÇADO EM ON**.

Para verificar:
```bash
cd /home/lucas-junges/Documents/clientes/w&co/ihm
python3 -c "from modbus_client import *; c = ModbusClientWrapper(port='/dev/ttyUSB0'); print('Estado 00BE:', c.read_coil(190)); c.close()"
```

**Resultado esperado:** `Estado 00BE: True`

**SE FALHAR (False ou None):**
1. Abra WinSUP no PC com CLP
2. Entre em modo RUN
3. Force estado `00BE` = ON (clique direito > Forçar > ON)
4. Salve programa

### 7. Testar Comunicação Básica
```bash
python3 test_clp_connection.py
```

**Resultado esperado:**
```
✓ Encoder lido com sucesso!
✓ Estado 00BE = ON (Modbus habilitado)
✓✓✓ SUCESSO! CLP responde no endereço slave 1 ✓✓✓
```

**SE FALHAR:**
- Verifique baudrate do CLP (deve ser 57600)
- Verifique slave ID do CLP (deve ser 1)
- Verifique fios A+/B- (inverter se necessário)

---

## 🏭 NA FÁBRICA - PARTE 3: WIFI E SERVIDOR

### 8. Configurar Hotspot no Tablet
1. Abrir **Configurações** no tablet
2. **Rede e Internet** > **Hotspot Wi-Fi**
3. Ligar hotspot
4. **ANOTAR NOME DA REDE E SENHA**

### 9. Conectar Notebook ao Hotspot
1. Clicar ícone WiFi no Ubuntu
2. Selecionar rede do tablet
3. Digitar senha
4. Aguardar conectar

### 10. Verificar IP do Notebook
```bash
ip addr show | grep "inet " | grep -v 127.0.0.1
```

**Resultado esperado:** algo como `192.168.43.xxx` ou `192.168.137.xxx`

---

## 🏭 NA FÁBRICA - PARTE 4: INICIAR SERVIDOR

### 11. Iniciar Servidor Principal
```bash
cd /home/lucas-junges/Documents/clientes/w&co/ihm
python3 main_server.py --port /dev/ttyUSB0
```

**Resultado esperado:**
```
============================================================
IHM WEB - DOBRADEIRA NEOCOUDE-HD-15
============================================================

Modo: LIVE (CLP real)
✓ Modbus conectado: /dev/ttyUSB0 @ 57600 bps (slave 1)

✓ Servidor iniciado com sucesso
  WebSocket: ws://localhost:8765
  HTTP: http://localhost:8080

Abra http://localhost:8080 no navegador do tablet
```

**SE FALHAR "Modbus não conectado":**
- Volte ao passo 6 (verificar estado 00BE)
- Verifique cabo RS485

**SE FALHAR "Porta em uso":**
```bash
pkill -9 -f "main_server.py"
```
Depois rode novamente.

### 12. Verificar Logs do Servidor

No terminal deve aparecer:
```
✓ Encoder lido: XXX raw, XX.X°
```

Se aparecer `✗ Encoder retornou None`, **PARE** e volte ao passo 7.

---

## 📱 NA FÁBRICA - PARTE 5: TABLET

### 13. Descobrir IP do Notebook

No notebook:
```bash
hostname -I | awk '{print $1}'
```

**Exemplo de resultado:** `192.168.43.42`

### 14. Abrir Interface no Tablet

No navegador do tablet (Chrome), digite:
```
http://192.168.43.42:8080
```

(Substitua `192.168.43.42` pelo IP do passo 13)

### 15. Verificar Interface Carregou

Deve aparecer:
- **Status Bar:**
  - `WebSocket: Conectado` (verde)
  - `CLP Modbus: Online` (verde)
  - `Motor: Parado`

- **Encoder:** Mostrando ângulo atual (ex: `11.9°`)

**SE APARECER "DESLIGADO" (overlay vermelho):**
1. Pressione F5 (refresh)
2. Verifique se servidor está rodando (passo 11)
3. Verifique IP está correto (passo 13)

**SE APARECER "WebSocket Conectado" mas "CLP Modbus: Offline":**
- Servidor conectou mas CLP não responde
- Volte ao passo 6 (verificar estado 00BE)

---

## ✅ NA FÁBRICA - PARTE 6: TESTES FINAIS

### 16. Testar Leitura de Encoder

Na interface, ângulo deve **atualizar em tempo real** quando você girar o prato manualmente.

**SE NÃO ATUALIZAR:**
- Encoder não está conectado ao CLP
- Verifique fiação do encoder

### 17. Testar Escrita de Ângulo

1. Clicar em "Editar" em **Dobra 1**
2. Digitar `90` (90 graus)
3. Clicar "Salvar"
4. Verificar no display do CLP se mudou para 90°

**SE NÃO MUDAR:**
- CLP está em modo READ-ONLY
- Ladder está bloqueando escritas via Modbus

### 18. Testar Controle de Motor

⚠️ **ATENÇÃO:** Este teste vai ligar o motor!

1. Garantir que **NÃO HÁ FERRO** no prato
2. Clicar em **"Avançar"** (botão verde)
3. Motor deve girar no sentido anti-horário
4. Clicar novamente para parar
5. Clicar em **"Recuar"** (botão azul)
6. Motor deve girar no sentido horário
7. Clicar novamente para parar

**SE MOTOR NÃO GIRAR:**
- Verificar se saídas S0/S1 estão mapeadas corretamente no ladder
- Verificar se inversor está configurado corretamente

---

## 🚨 PROBLEMAS CRÍTICOS E SOLUÇÕES

### PROBLEMA 1: "Could not exclusively lock port"
**Causa:** Outro programa está usando `/dev/ttyUSB0`

**Solução:**
```bash
pkill -9 -f "python3"
sudo fuser -k /dev/ttyUSB0
```

Depois rode servidor novamente.

---

### PROBLEMA 2: "Modbus timeout errors"
**Causa:** CLP não está respondendo

**Checklist:**
1. Estado 00BE está ON? (passo 6)
2. Baudrate 57600? (verificar no WinSUP)
3. Slave ID 1? (verificar no WinSUP)
4. Fios A+/B- invertidos? (trocar e testar)

---

### PROBLEMA 3: "WebSocket desconectado"
**Causa:** Tablet perdeu WiFi

**Solução:**
1. Verificar se tablet ainda está com hotspot ativo
2. Verificar se notebook ainda está conectado ao WiFi
3. Reiniciar servidor (passo 11)

---

### PROBLEMA 4: Ângulos não atualizam
**Causa:** Registros de ângulo não estão corretos

**Verificação:**
```bash
python3 test_factory_scenario.py
```

Se teste 3 (Ângulos) falhar, **problema no mapeamento**. Contate suporte.

---

### PROBLEMA 5: Motor liga mas não para
**PERIGO! EMERGÊNCIA!**

1. **Pressione BOTÃO VERMELHO DE EMERGÊNCIA** na máquina
2. **Desligue CLP**
3. **Não use interface web!**
4. Problema crítico no ladder - **NÃO USAR** até corrigir

---

## 📝 COMANDOS RÁPIDOS DE EMERGÊNCIA

### Parar Servidor:
```bash
pkill -9 -f "main_server.py"
```

### Reiniciar Tudo:
```bash
pkill -9 -f "python3"
cd /home/lucas-junges/Documents/clientes/w&co/ihm
python3 main_server.py --port /dev/ttyUSB0
```

### Testar CLP Rápido:
```bash
python3 test_clp_connection.py
```

### Ver Logs em Tempo Real:
```bash
# (Enquanto servidor roda, abra outro terminal)
tail -f server.log
```

---

## ✅ CHECKLIST FINAL ANTES DE SAIR DA FÁBRICA

- [ ] Interface web abre no tablet sem erro
- [ ] Encoder atualiza em tempo real
- [ ] Consegue escrever ângulos (teste com 45°, 90°, 120°)
- [ ] Botões K1-K9, S1, S2 funcionam (ver resposta no display do CLP)
- [ ] Motor liga e para corretamente (S0 e S1)
- [ ] Botão de emergência funciona (mata motor imediatamente)
- [ ] Deixar servidor rodando em background:
  ```bash
  nohup python3 main_server.py --port /dev/ttyUSB0 > server.log 2>&1 &
  ```
- [ ] Tablet conectado ao WiFi do notebook
- [ ] Anotar IP do notebook para operadores

---

## 🆘 SE TUDO FALHAR - PLANO B

1. **Usar modo stub (simulação) para demonstração:**
   ```bash
   python3 main_server.py --stub
   ```
   Isso vai rodar SEM CLP (valores simulados). Útil para mostrar interface.

2. **Ligar CLP com IHM física antiga:**
   - Se o painel físico ainda funciona parcialmente
   - Usar apenas para operação emergencial

3. **Contato de emergência:**
   - Anotar **ESTE NÚMERO** no celular antes de ir

---

## 📊 RESUMO EXECUTIVO

**O que foi testado com SUCESSO:**
- ✅ Conexão Modbus (slave ID 1, 57600 bps)
- ✅ Leitura de encoder (posição angular)
- ✅ Leitura de ângulos (3 dobras)
- ✅ Escrita de ângulos (testado 45°, funcionou)
- ✅ Pressionar botões via Modbus (K1 testado)
- ✅ Controle de motor S0/S1 (liga/desliga)

**O que NÃO foi testado (mas deve funcionar):**
- ⚠️ Mudança de velocidade (K1+K7)
- ⚠️ Mudança de modo Manual/Auto (S1+E6)
- ⚠️ Operação contínua por horas

**Pontos de falha críticos:**
1. **Estado 00BE OFF** → Modbus não funciona
2. **Cabo RS485 invertido** → Timeout
3. **WiFi instável** → WebSocket desconecta
4. **CLP trava durante escrita** → Reiniciar CLP

---

## 🎯 BOA SORTE NA SEGUNDA-FEIRA!

Se seguir este checklist **EXATAMENTE**, você vai conseguir.

**Lembre-se:**
- Testar CADA passo ANTES de passar para o próximo
- **NÃO pular etapas**
- Se algo falhar, **VOLTAR** ao passo anterior e verificar novamente
- **NÃO improvisar** - se não está neste checklist, NÃO faça

---

**Última atualização:** 15/Nov/2025 22:15
**Testado em:** Ubuntu 25.04 + CLP Atos MPC4004 + Cabo USB-RS485-FTDI
