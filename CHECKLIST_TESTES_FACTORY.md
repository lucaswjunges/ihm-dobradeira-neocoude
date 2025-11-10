# CHECKLIST DE TESTES - IHM WEB NEOCOUDE-HD-15

## Preparação Pré-Teste

### Hardware
- [ ] Notebook Ubuntu conectado ao conversor USB-RS485-FTDI
- [ ] Conversor RS485 conectado ao Canal B do CLP (terminais corretos A/B)
- [ ] Identificar porta serial: `/dev/ttyUSB0` ou `/dev/ttyUSB1`
- [ ] Tablet configurado como hotspot WiFi
- [ ] Notebook conectado ao WiFi do tablet

### Software
- [ ] Python 3 instalado (`python3 --version`)
- [ ] Bibliotecas instaladas: `pip3 install websockets pymodbus`
- [ ] Arquivos presentes:
  - `ihm_server_final.py`
  - `ihm_completa.html`
  - `modbus_client.py`

### Verificação Inicial
```bash
# Verificar porta serial disponível
ls -l /dev/ttyUSB*

# Testar permissões
sudo chmod 666 /dev/ttyUSB0

# Verificar se porta não está em uso
lsof /dev/ttyUSB0
```

---

## FASE 1: Teste de Comunicação Modbus

### 1.1 Teste Básico de Leitura
**Objetivo**: Verificar comunicação com CLP

**Comando**:
```bash
python3 -c "
from modbus_client import ModbusClient, ModbusConfig
config = ModbusConfig(port='/dev/ttyUSB0')
client = ModbusClient(stub_mode=False, config=config)
if client.connect():
    print('✓ Conectado ao CLP')
    encoder = client.get_encoder_angle()
    print(f'Encoder: {encoder}')
    client.disconnect()
else:
    print('✗ Falha ao conectar')
"
```

**Resultado Esperado**:
```
✓ Conectado ao CLP
Encoder: <valor numérico>
```

**Se falhar**:
- [ ] Verificar baudrate: 57600
- [ ] Verificar stop bits: 2 (CRÍTICO!)
- [ ] Verificar slave ID no registro 6536 (0x1988)
- [ ] Inverter cabos A/B do RS485
- [ ] Verificar bit 00BE (190) está ON no CLP

---

### 1.2 Teste de Leitura de Ângulos
**Objetivo**: Verificar leitura dos 3 ângulos configurados

**Comando**:
```bash
python3 << 'EOF'
from modbus_client import ModbusClient, ModbusConfig
config = ModbusConfig(port='/dev/ttyUSB0')
client = ModbusClient(stub_mode=False, config=config)
client.connect()

angle1 = client.read_angle_1()
angle2 = client.read_angle_2()
angle3 = client.read_angle_3()

print(f"Ângulo 1: {angle1}°")
print(f"Ângulo 2: {angle2}°")
print(f"Ângulo 3: {angle3}°")

client.disconnect()
EOF
```

**Resultado Esperado**:
```
Ângulo 1: <0-360>°
Ângulo 2: <0-360>°
Ângulo 3: <0-360>°
```

**Checklist**:
- [ ] Ângulo 1 lido corretamente (registros 2114/2112)
- [ ] Ângulo 2 lido corretamente (registros 2120/2118)
- [ ] Ângulo 3 lido corretamente (registros 2130/2128)

---

### 1.3 Teste de Escrita de Ângulo
**Objetivo**: Verificar escrita de ângulo no CLP

**Comando**:
```bash
python3 << 'EOF'
from modbus_client import ModbusClient, ModbusConfig
import time

config = ModbusConfig(port='/dev/ttyUSB0')
client = ModbusClient(stub_mode=False, config=config)
client.connect()

# Escrever ângulo de teste (90°)
print("Escrevendo Ângulo 1 = 90°...")
success = client.write_angle_1(90)
print(f"Escrita: {'✓ OK' if success else '✗ FALHOU'}")

time.sleep(0.5)

# Ler de volta
angle1 = client.read_angle_1()
print(f"Leitura: {angle1}°")
print(f"Validação: {'✓ PASSOU' if angle1 == 90 else '✗ FALHOU'}")

client.disconnect()
EOF
```

**Resultado Esperado**:
```
Escrevendo Ângulo 1 = 90°...
Escrita: ✓ OK
Leitura: 90°
Validação: ✓ PASSOU
```

**Checklist**:
- [ ] Escrita bem-sucedida
- [ ] Valor lido de volta confere (90°)
- [ ] Repetir teste para Ângulo 2 e 3

---

### 1.4 Teste de Teclas
**Objetivo**: Verificar simulação de pressão de teclas

**Comando**:
```bash
python3 << 'EOF'
from modbus_client import ModbusClient, ModbusConfig
import time

config = ModbusConfig(port='/dev/ttyUSB0')
client = ModbusClient(stub_mode=False, config=config)
client.connect()

# Testar tecla K1
print("Pressionando K1...")
success = client.press_key('K1')
print(f"K1: {'✓ OK' if success else '✗ FALHOU'}")
time.sleep(1)

# Testar S1
print("Pressionando S1...")
success = client.press_key('S1')
print(f"S1: {'✓ OK' if success else '✗ FALHOU'}")

client.disconnect()
EOF
```

**Checklist**:
- [ ] K1 enviado com sucesso
- [ ] S1 enviado com sucesso
- [ ] Observar reação no display físico do CLP (se houver)

---

## FASE 2: Teste do Servidor WebSocket

### 2.1 Iniciar Servidor
**Comando**:
```bash
python3 ihm_server_final.py --port /dev/ttyUSB0 --ws-port 8086
```

**Resultado Esperado**:
```
================================================================================
IHM SERVIDOR FINAL - NEOCOUDE-HD-15
================================================================================
Porta serial: /dev/ttyUSB0
WebSocket: localhost:8086
Modo: LIVE (CLP real)
================================================================================
✓ Conectado ao CLP via Modbus RTU
Iniciando servidor WebSocket na porta 8086...
✓ Servidor WebSocket rodando em ws://localhost:8086
Iniciando polling do CLP...
```

**Checklist**:
- [ ] Servidor iniciou sem erros
- [ ] Conexão Modbus estabelecida
- [ ] Polling iniciado (verificar logs a cada 250ms)

---

### 2.2 Teste do Frontend
**Instruções**:
1. Abrir `ihm_completa.html` no navegador (Chrome/Firefox)
2. Verificar conexão WebSocket (status "LIGADO" em verde)
3. Observar atualização em tempo real do encoder

**Checklist Visual**:
- [ ] Status "LIGADO" aparece em verde
- [ ] Valor do encoder atualiza a cada ~250ms
- [ ] Tela 0 exibe "**TRILLOR MAQUINAS**"
- [ ] Navegação funciona (setas ↑/↓)

---

### 2.3 Teste de Edição de Ângulos
**Instruções**:
1. Navegar até Tela 4 (seta para baixo 4x)
2. Clicar no valor do ângulo (campo destacado)
3. Digitar novo valor (ex: 120)
4. Confirmar entrada

**Checklist**:
- [ ] Tela 4: "AJUSTE DO ANGULO  01"
- [ ] Campo `AJ=` é clicável (cursor vira mão)
- [ ] Prompt aparece ao clicar
- [ ] Valor aceito (0-360)
- [ ] Feedback visual (✓ Ângulo 1 = 120°)
- [ ] Valor atualiza no display
- [ ] Repetir para Tela 5 (Ângulo 2) e Tela 6 (Ângulo 3)

---

### 2.4 Teste de Teclas Virtuais
**Instruções**:
1. Voltar para Tela 0
2. Pressionar teclas virtuais na interface

**Checklist de Teclas**:
- [ ] K1 - pulso verde visível
- [ ] K2 - pulso verde visível
- [ ] K3 - pulso verde visível
- [ ] K4 - pulso verde visível
- [ ] K5 - pulso verde visível
- [ ] K6 - pulso verde visível
- [ ] K7 - pulso verde visível
- [ ] K8 - pulso verde visível
- [ ] K9 - pulso verde visível
- [ ] K0 - pulso verde visível
- [ ] S1 - pulso verde visível
- [ ] S2 - pulso verde visível
- [ ] ENTER - pulso verde visível
- [ ] ESC - pulso verde visível

---

## FASE 3: Testes Funcionais com Máquina

⚠️ **ATENÇÃO**: Testes abaixo devem ser feitos com máquina em condições seguras

### 3.1 Teste de Monitoramento
**Objetivo**: Verificar se IHM web reflete estado real da máquina

**Procedimento**:
1. Deixar IHM web aberta na Tela 1 (ENCODER)
2. Usar botões físicos da máquina para movimentar prato
3. Observar atualização do encoder na IHM web

**Checklist**:
- [ ] Encoder atualiza em tempo real (<250ms de atraso)
- [ ] Valor corresponde ao mostrado no display físico (se houver)
- [ ] Sem erros de comunicação (nenhum overlay vermelho)

---

### 3.2 Teste de Escrita de Ângulo em Operação
**Objetivo**: Verificar se alteração de ângulo via web é reconhecida pelo CLP

**Procedimento**:
1. IHM web: Navegar para Tela 4
2. Editar ângulo para um valor de teste (ex: 45°)
3. Verificar no programa ladder ou display físico se valor foi atualizado

**Checklist**:
- [ ] Ângulo escrito com sucesso
- [ ] CLP reconhece novo valor
- [ ] Máquina opera com novo ângulo (se testado em ciclo)

---

### 3.3 Teste de Envio de Comandos
**Objetivo**: Verificar se teclas virtuais afetam lógica do CLP

**Procedimento**:
1. Observar estado atual da máquina (modo, tela, etc.)
2. Enviar comando via tecla virtual (ex: S1 para mudar modo)
3. Verificar se ação foi executada

**Checklist**:
- [ ] S1 muda modo Manual/Automático (se implementado no ladder)
- [ ] S2 reseta display para zero (se implementado)
- [ ] K1-K9 executam funções programadas no ladder

---

## FASE 4: Testes de Robustez

### 4.1 Teste de Reconexão
**Procedimento**:
1. Com sistema funcionando, desconectar cabo RS485
2. Verificar overlay "FALHA CLP" aparece
3. Reconectar cabo RS485
4. Verificar recuperação automática

**Checklist**:
- [ ] Overlay vermelho aparece ao desconectar
- [ ] Sistema reconecta automaticamente
- [ ] Dados voltam a atualizar

---

### 4.2 Teste de Múltiplos Clientes
**Procedimento**:
1. Abrir `ihm_completa.html` em 2 navegadores diferentes
2. Verificar ambos recebem atualizações
3. Editar ângulo em um navegador
4. Verificar outro navegador atualiza

**Checklist**:
- [ ] Ambos clientes conectam simultaneamente
- [ ] Ambos recebem atualizações do encoder
- [ ] Edição de ângulo reflete em ambos

---

### 4.3 Teste de Validação
**Procedimento**:
1. Tentar editar ângulo com valor inválido (ex: 400)
2. Tentar editar com valor negativo (ex: -10)
3. Tentar editar com texto (ex: "abc")

**Checklist**:
- [ ] Valor 400 rejeitado (mensagem "fora da faixa")
- [ ] Valor -10 rejeitado
- [ ] Texto rejeitado
- [ ] Nenhum valor inválido é enviado ao CLP

---

## FASE 5: Testes de Performance

### 5.1 Latência de Atualização
**Procedimento**:
1. Movimentar prato manualmente (botões físicos)
2. Cronometrar tempo entre movimento e atualização na IHM web

**Resultado Esperado**: < 500ms (250ms de polling + 250ms de buffer)

**Checklist**:
- [ ] Latência aceitável para operação
- [ ] Sem "travamentos" na interface

---

### 5.2 Uso de CPU/Memória
**Comando**:
```bash
# Monitorar recursos do servidor
top -p $(pgrep -f ihm_server_final.py)
```

**Checklist**:
- [ ] CPU < 10% (média)
- [ ] Memória < 100MB
- [ ] Sem memory leaks (uso estável ao longo do tempo)

---

## TROUBLESHOOTING

### Problema: "Erro ao conectar ao CLP"
**Soluções**:
1. Verificar cabo RS485 conectado corretamente
2. Testar com `ls -l /dev/ttyUSB*` se porta existe
3. Verificar permissões: `sudo chmod 666 /dev/ttyUSB0`
4. Verificar configuração do CLP:
   - Bit 00BE (190) = ON (habilita Modbus slave)
   - Registro 6536 (0x1988) = Slave ID
   - Baudrate: 57600

### Problema: "WebSocket não conecta"
**Soluções**:
1. Verificar servidor rodando: `ps aux | grep ihm_server_final`
2. Verificar porta 8086 livre: `netstat -tuln | grep 8086`
3. Verificar firewall: `sudo ufw status`
4. Tentar porta diferente: `--ws-port 8087`

### Problema: "Encoder sempre zero ou não atualiza"
**Soluções**:
1. Verificar registros 1238/1239 (0x04D6/0x04D7)
2. Verificar encoder físico conectado (E100/E101)
3. Ver logs do servidor: `tail -f ihm_server_final.log`
4. Verificar bit 00D2 (210) = OFF (permite contagem)

### Problema: "Teclas não fazem nada"
**Soluções**:
1. Verificar bit 00F1 (241 - LOCK) = OFF
2. Verificar ladder implementa lógica para cada tecla
3. Verificar endereços no `COMANDOS_MODBUS_IHM_WEB.md`
4. Testar com ferramenta Modbus externa (QModMaster)

### Problema: "Ângulos não salvam"
**Soluções**:
1. Verificar registros MSW/LSW corretos:
   - Ângulo 1: 2114 (MSW) / 2112 (LSW)
   - Ângulo 2: 2120 (MSW) / 2118 (LSW)
   - Ângulo 3: 2130 (MSW) / 2128 (LSW)
2. Verificar formato 32-bit: `(MSW << 16) | LSW`
3. Ver logs de escrita: `grep "write_angle" ihm_server_final.log`

---

## APROVAÇÃO FINAL

### Critérios de Aceitação
- [ ] Todas as teclas (K0-K9, S1, S2, setas, ENTER, ESC) funcionam
- [ ] Edição de ângulos 1, 2 e 3 funciona
- [ ] Encoder atualiza em tempo real
- [ ] Sistema reconecta automaticamente após falhas
- [ ] Interface responsiva e sem travamentos
- [ ] Validação impede valores inválidos
- [ ] Logs não mostram erros críticos

### Assinaturas
```
[ ] Técnico Responsável: __________________ Data: __/__/____
[ ] Operador Treinado: ____________________ Data: __/__/____
[ ] Cliente Final: ________________________ Data: __/__/____
```

---

## DOCUMENTOS DE REFERÊNCIA
- `COMANDOS_MODBUS_IHM_WEB.md` - Especificação completa de comandos
- `SOLUCAO_COMPLETA_IHM.md` - Arquitetura e visão geral
- `manual_MPC4004.pdf` - Manual do CLP Atos
- `NEOCOUDE-HD 15 - Camargo 2007 (1).pdf` - Manual da máquina
