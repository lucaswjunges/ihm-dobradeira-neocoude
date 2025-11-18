# 🧪 INSTRUÇÕES DE TESTE - IHM Web ESP32

**Objetivo:** Testar completamente a interface web da IHM para dobradeira NEOCOUDE-HD-15.

**Data:** 18 de Novembro de 2025
**Versão:** IHM ESP32 v2.0 - Modo LIVE com CLP Atos MPC4004
**URL:** http://192.168.0.106

---

## 📋 PRÉ-REQUISITOS

Antes de iniciar os testes:

- [x] ESP32 conectado e ligado
- [x] ESP32 conectado no WiFi (192.168.0.106)
- [x] Servidor HTTP rodando no ESP32
- [x] Modo: **LIVE** (comunicação com CLP real via Modbus RTU)
- [x] CLP Atos MPC4004 ligado e respondendo
- [x] Navegador web disponível (Chrome, Firefox, Edge)

---

## 🎯 CHECKLIST DE TESTES

### 1. ✅ Teste de Conectividade Básica

**Objetivo:** Verificar se a interface web está acessível.

**Comandos:**
```bash
# 1.1 - Ping no ESP32
ping -c 3 192.168.0.106

# 1.2 - Teste API de estado
curl -s http://192.168.0.106/api/state | python3 -m json.tool

# 1.3 - Teste API de diagnóstico Modbus
curl -s http://192.168.0.106/api/test_modbus | python3 -m json.tool
```

**Resultado esperado:**
- Ping: ✅ 0% packet loss
- API state: ✅ Retorna JSON com `connected: true`
- API test_modbus: ✅ Retorna JSON válido

---

### 2. ✅ Teste da Interface Web Visual

**Objetivo:** Verificar se a interface carrega corretamente no navegador.

**Passos:**
1. Abrir navegador web
2. Acessar: `http://192.168.0.106`
3. Aguardar carregamento completo (5-10 segundos)

**Verificações visuais:**

#### 2.1 - Header (topo da página)
- [ ] Título "IHM WEB - NEOCOUDE-HD-15" visível
- [ ] Logo ou ícone aparece
- [ ] Barra de status no canto superior direito
- [ ] Indicador "CLP" presente

#### 2.2 - Status da conexão
- [ ] **"CLP ✓"** aparece em **VERDE** (não vermelho)
- [ ] **NÃO** deve mostrar overlay vermelho com "DESLIGADO"
- [ ] **NÃO** deve mostrar overlay com "FALHA CLP"
- [ ] Indicador de conexão HTTP ativo

#### 2.3 - Valores em tempo real
- [ ] Encoder exibe valor numérico (ex: "11.9°")
- [ ] RPM exibe valor válido: **5, 10 ou 15** (não valores como 2380, 2560)
- [ ] Ângulos das dobras exibem valores numéricos

---

### 3. ✅ Teste de Dados do CLP

**Objetivo:** Verificar se os dados do CLP estão sendo lidos e exibidos corretamente.

**Comando para monitorar:**
```bash
# Loop para monitorar estado a cada 2 segundos
while true; do
    echo "=== $(date +%H:%M:%S) ==="
    curl -s http://192.168.0.106/api/state | python3 -c "
import sys, json
d = json.load(sys.stdin)
print(f'Connected: {d[\"connected\"]}')
print(f'Encoder: {d[\"encoder_angle\"]}°')
print(f'Bend 1: {d[\"bend_1_angle\"]}°')
print(f'Bend 2: {d[\"bend_2_angle\"]}°')
print(f'Bend 3: {d[\"bend_3_angle\"]}°')
print(f'RPM: {d[\"speed_class\"]}')
"
    echo ""
    sleep 2
done
```

**Verificações:**

#### 3.1 - Campo `connected`
- [ ] Valor deve ser: `true`
- [ ] Se `false`: Sistema mostrará "FALHA CLP" → **PROBLEMA**

#### 3.2 - Campo `encoder_angle`
- [ ] Valor numérico entre 0-360°
- [ ] Valor deve atualizar se encoder girar
- [ ] Formato: float com 1 casa decimal (ex: 11.9)

#### 3.3 - Campo `speed_class` (RPM)
- [ ] Valor deve ser: **5, 10 ou 15** (apenas esses valores)
- [ ] **NÃO** pode ser: 1, 2, 3 (classes brutas)
- [ ] **NÃO** pode ser: 2380, 2560 (endereço de registro)

#### 3.4 - Campos `bend_X_angle`
- [ ] Valores numéricos
- [ ] Formato: float com 1 casa decimal (ex: 38.0)
- [ ] Valores razoáveis: 0-180° típico
- [ ] Se > 360°: pode indicar registro incorreto

---

### 4. ✅ Teste de APIs REST

**Objetivo:** Verificar se todas APIs estão funcionando.

#### 4.1 - GET /api/state
```bash
curl -s http://192.168.0.106/api/state | python3 -m json.tool
```

**Campos obrigatórios:**
- [ ] `connected` (boolean)
- [ ] `encoder_angle` (float)
- [ ] `bend_1_angle` (float)
- [ ] `bend_2_angle` (float)
- [ ] `bend_3_angle` (float)
- [ ] `speed_class` (int: 5, 10 ou 15)

#### 4.2 - GET /api/test_modbus
```bash
curl -s http://192.168.0.106/api/test_modbus | python3 -m json.tool
```

**Campos obrigatórios:**
- [ ] `connected` (boolean)
- [ ] `encoder_test` → `success` (boolean)
- [ ] `bend1_test` → `success` (boolean)

#### 4.3 - GET /api/read_test?address=XXXX
```bash
# Ler ângulo da dobra 1 (endereço 1280)
curl -s "http://192.168.0.106/api/read_test?address=1280" | python3 -m json.tool
```

**Resultado esperado:**
```json
{
    "success": true,
    "address": 1280,
    "value": 380,        // Exemplo: 38.0° * 10
    "hex": "0x017C"
}
```

#### 4.4 - GET /api/write_test?address=XXXX&value=YYYY
```bash
# Escrever 45° (450) na dobra 1
curl -s "http://192.168.0.106/api/write_test?address=1280&value=450" | python3 -m json.tool

# Verificar se escrita funcionou
sleep 1
curl -s "http://192.168.0.106/api/read_test?address=1280" | python3 -m json.tool
```

**Resultado esperado:**
- Escrita: `"success": true, "message": "OK"`
- Leitura: `"value": 450` (confirmando escrita)

---

### 5. ✅ Teste de Performance

**Objetivo:** Verificar se o sistema não trava ou fica lento.

#### 5.1 - Teste de stress - Requisições sequenciais
```bash
# 20 requisições seguidas
for i in {1..20}; do
    echo -n "Req $i: "
    time curl -s http://192.168.0.106/api/state > /dev/null
done
```

**Verificações:**
- [ ] Nenhuma requisição deve levar > 2 segundos
- [ ] ESP32 não deve travar
- [ ] Não deve aparecer timeout

#### 5.2 - Teste de stress - Requisições paralelas
```bash
# 5 requisições simultâneas
for i in {1..5}; do
    curl -s http://192.168.0.106/api/state > /dev/null &
done
wait
echo "✓ Todas completaram"
```

**Verificações:**
- [ ] Todas requisições devem completar
- [ ] ESP32 não deve reiniciar
- [ ] Navegador deve continuar atualizando

---

### 6. ✅ Teste de Atualização em Tempo Real

**Objetivo:** Verificar se a interface atualiza automaticamente.

**Passos:**
1. Abrir interface web no navegador: `http://192.168.0.106`
2. Deixar aberta por 1 minuto
3. Observar console do navegador (F12 → Console)

**Verificações:**
- [ ] Valores numéricos devem atualizar a cada ~500ms
- [ ] Não deve aparecer erros no console
- [ ] Indicador "CLP ✓" deve permanecer verde
- [ ] Não deve aparecer overlay de erro

**Comando para forçar mudança (teste):**
```bash
# Escrever valor diferente para ver atualização
curl -s "http://192.168.0.106/api/write_test?address=1280&value=600"
```

**Resultado esperado:**
- [ ] Valor de bend_1_angle deve mudar para 60.0° na interface
- [ ] Mudança deve aparecer em até 1 segundo

---

### 7. ✅ Teste de Abas/Tabs da Interface

**Objetivo:** Verificar se todas abas funcionam.

**Passos:**
1. Clicar na aba "Operação"
   - [ ] Mostra encoder, ângulos, velocidade
   - [ ] Teclado virtual visível

2. Clicar na aba "Diagnóstico"
   - [ ] Mostra entradas/saídas digitais
   - [ ] LEDs indicadores visíveis

3. Clicar na aba "Logs e Produção"
   - [ ] Área de logs visível
   - [ ] Contador presente

4. Clicar na aba "Configuração"
   - [ ] Configurações visíveis
   - [ ] Sem erros ao carregar

---

### 8. ✅ Teste de Responsividade

**Objetivo:** Verificar se interface funciona em diferentes tamanhos de tela.

**Passos:**
1. Abrir navegador em tela cheia
   - [ ] Layout correto

2. Redimensionar janela para 50% da largura
   - [ ] Layout se adapta
   - [ ] Botões acessíveis

3. Simular tablet (F12 → Toggle Device Toolbar → iPad)
   - [ ] Interface utilizável
   - [ ] Botões grandes o suficiente

---

### 9. ✅ Teste de Erros e Recovery

**Objetivo:** Verificar comportamento em caso de falhas.

#### 9.1 - Simular desconexão do CLP
```bash
# Parar ESP32 temporariamente (CTRL+C no serial)
# OU desconectar cabo RS485
```

**Resultado esperado:**
- [ ] Interface deve mostrar "FALHA CLP" em vermelho
- [ ] Deve indicar "connected: false"
- [ ] Não deve travar o navegador

#### 9.2 - Reconectar CLP
```bash
# Resetar ESP32 (botão RESET)
# OU reconectar cabo RS485
```

**Resultado esperado:**
- [ ] Overlay de erro deve sumir
- [ ] "CLP ✓" deve voltar para verde
- [ ] Valores devem voltar a atualizar

---

## 📊 CRITÉRIOS DE APROVAÇÃO

### ✅ MÍNIMO ACEITÁVEL (Aprovado)
- [x] Interface carrega sem erros
- [x] "CLP ✓" aparece em verde
- [x] RPM mostra valor correto (5, 10 ou 15)
- [x] Valores numéricos aparecem
- [x] Pelo menos 1 API funciona

### 🎯 IDEAL (Excelente)
- [x] Todas verificações passam
- [x] Nenhum erro no console
- [x] Atualização em tempo real funciona
- [x] Performance < 1s por requisição
- [x] Interface responsiva

### ❌ REPROVADO (Precisa correção)
- [ ] Interface não carrega
- [ ] "FALHA CLP" permanente
- [ ] RPM mostra valores errados
- [ ] ESP32 trava frequentemente
- [ ] Nenhuma API funciona

---

## 🐛 PROBLEMAS CONHECIDOS E SOLUÇÕES

### Problema 1: "FALHA CLP" em vermelho
**Causa:** `connected: false` na API
**Verificação:**
```bash
curl -s http://192.168.0.106/api/state | grep connected
```
**Solução:**
- Verificar cabo RS485 (A/B)
- Verificar CLP ligado
- Verificar state 00BE = ON no CLP

### Problema 2: RPM mostra valores errados (ex: 2380)
**Causa:** Código não está convertendo classe → RPM
**Verificação:**
```bash
curl -s http://192.168.0.106/api/state | python3 -c "import sys,json; print('RPM:', json.load(sys.stdin)['speed_class'])"
```
**Solução:**
- Verificar se main.py tem conversão: `speed_map = {1: 5, 2: 10, 3: 15}`

### Problema 3: ESP32 trava ao acessar interface
**Causa:** Modbus com timeout muito longo
**Solução:**
- Mudar para STUB_MODE temporariamente
- Verificar qualidade dos cabos RS485

### Problema 4: Valores não atualizam
**Causa:** Polling parado ou conexão perdida
**Verificação:** Abrir console do navegador (F12)
**Solução:** Recarregar página (F5)

---

## 📝 RELATÓRIO DE TESTE

Após completar os testes, preencher:

**Data do teste:** ____/____/____
**Testador:** ________________
**Navegador:** ________________

**Resultados:**
- Testes passados: _____ / _____
- Testes falhados: _____
- Bugs encontrados: _____

**Status geral:**
- [ ] ✅ APROVADO - Sistema pronto para produção
- [ ] ⚠️ APROVADO COM RESSALVAS - Funciona mas tem problemas menores
- [ ] ❌ REPROVADO - Precisa correções antes de usar

**Observações adicionais:**
```
(escrever aqui quaisquer observações, bugs encontrados, sugestões)
```

---

## 🔗 ARQUIVOS DE REFERÊNCIA

- **API_TESTE_MODBUS.md** - Documentação completa das APIs
- **TESTE_SUCESSO_17NOV2025.md** - Relatório de testes anteriores
- **DIAGNOSTICO_COMPLETO.md** - Troubleshooting de hardware
- **CLAUDE.md** - Documentação do projeto

---

## 🆘 SUPORTE

Se encontrar problemas:

1. Verificar logs do ESP32 via serial (Thonny)
2. Verificar console do navegador (F12)
3. Executar testes das APIs via curl
4. Consultar documentação de referência

**Em caso de dúvidas, consultar o desenvolvedor ou abrir issue no repositório.**

---

**Versão:** 1.0
**Última atualização:** 18/Nov/2025 04:50
**Status:** ✅ Pronto para testes
