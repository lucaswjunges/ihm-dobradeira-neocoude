# Diagnóstico: Problema de Mudança de Modo AUTO/MANUAL
**Data**: 2025-11-15 (continuação)
**Teste**: Investigação da reversão de modo

---

## 🔍 PROBLEMA IDENTIFICADO

### Sintoma
- Interface envia comando para alternar modo MANUAL → AUTO
- Servidor escreve em bit 02FF com sucesso
- **CLP reverte para MANUAL imediatamente** (em 100ms)
- Mesmo escrita contínua não mantém AUTO

### Causa Raiz: **Entrada E6 INATIVA**

**Evidência do diagnóstico**:
```
Entrada E6 (0x0106): INATIVA
⚠️ E6 inativa pode ser a causa da reversão!
```

**Documentação confirma**:
> "S1 depende de E6" (conforme CLAUDE.md e análise de ladder)

---

## 📊 ESTADO ATUAL DAS ENTRADAS/SAÍDAS

### Entradas Digitais (E0-E7)
| Entrada | Endereço | Estado  | Observação |
|---------|----------|---------|------------|
| E0      | 0x0100   | INATIVA | Emergência? |
| E1      | 0x0101   | INATIVA | Sensor? |
| E2      | 0x0102   | INATIVA | |
| E3      | 0x0103   | INATIVA | |
| E4      | 0x0104   | INATIVA | |
| **E5**  | 0x0105   | **ATIVA ✓** | Única ativa |
| **E6**  | 0x0106   | **INATIVA** | ← **PROBLEMA!** |
| E7      | 0x0107   | INATIVA | |

### Saídas Digitais (S0-S7)
Todas inativas (máquina parada).

### Estados Críticos
- ✅ **00BE** (Modbus habilitado): ON
- ⚠️ **02FF** (Modo): MANUAL (não muda para AUTO)

---

## 🧪 TESTES REALIZADOS

### Teste 1: Monitoramento de Bit 02FF
**Procedimento**:
1. Ler estado inicial: MANUAL
2. Escrever 02FF = True (AUTO)
3. Monitorar 02FF por 5 segundos (leitura a cada 100ms)

**Resultado**:
```
T=0.0s: Escrita 02FF = True → ✓ Sucesso
T=0.1s: Leitura 02FF → False (MANUAL)
T=0.2s até T=4.9s: False (MANUAL)
```

**Conclusão**: CLP reverte **imediatamente** (< 100ms).

---

### Teste 2: Escrita Contínua
**Procedimento**:
- Escrever 02FF = True a cada 100ms por 2 segundos
- Ler logo após cada escrita

**Resultado**:
```
T+0.0s: Escrita → Leitura = MANUAL ⚠️
T+0.1s: Escrita → Leitura = MANUAL ⚠️
...
T+1.9s: Escrita → Leitura = MANUAL ⚠️
```

**Conclusão**: Ladder **sobrescreve 02FF ativamente**. Não é questão de timing.

---

### Teste 3: Botão S1 (Método Correto)
**Procedimento**:
1. Ler modo inicial
2. Pressionar S1 (pulso: ON → 100ms → OFF)
3. Aguardar 500ms
4. Ler modo final
5. Monitorar por 3 segundos

**Resultado**:
```
Modo inicial: MANUAL
S1 pressionado: ✓ Sucesso
Modo após S1: MANUAL (não mudou!)
Modo final (T+3s): MANUAL (permaneceu estável)
```

**Conclusão**: S1 **também não funciona** porque E6 está inativa.

---

### Teste 4: Verificação de E6
**Resultado**:
```
E6 (0x0106): INATIVA
```

**Possíveis causas da E6 inativa**:
1. **Física**: Sensor/chave não conectado ou danificado
2. **Condicional**: E6 ativa apenas quando:
   - Máquina está parada
   - Dobra 1 ativa (LED K1 ON)
   - Emergência não acionada
   - Outras condições de segurança
3. **Ladder**: E6 pode ser saída virtual (não física), dependente de estados internos

---

## 💡 ANÁLISE DA LÓGICA LADDER

### Hipótese: Proteção de Segurança
Ladder provavelmente implementa:

```ladder
// Pseudocódigo da lógica ladder
IF (E6 == ACTIVE) AND (K1_LED == ON) AND (NOT EMERGENCY) THEN
    ALLOW S1 to toggle 02FF
ELSE
    FORCE 02FF = False (MANUAL)
END IF
```

**Evidências que suportam**:
1. Escrita direta em 02FF não persiste (watchdog reseta)
2. S1 aceita comando mas não altera modo (condição bloqueada)
3. Manual menciona: "Modo change (Manual↔Auto) only allowed when K1 LED active (1st bend)"

---

## 🎯 SOLUÇÕES POSSÍVEIS

### Solução 1: Ativar E6 (Hardware)
**Se E6 for entrada física**:
- Verificar conexão do sensor/chave correspondente a E6
- Consultar esquema elétrico da máquina
- Pode ser "Máquina Parada" ou "Segurança OK"

**Passos**:
1. Identificar terminal E6 no CLP
2. Medir tensão no terminal
3. Conectar/corrigir sinal se necessário

---

### Solução 2: Forçar E6 via Modbus (Software)
**⚠️ CUIDADO: Pode comprometer segurança!**

```python
# Forçar E6 = True
client.write_coil(0x0106, True)
time.sleep(0.1)

# Então tentar S1
client.press_key(0x00DC)
```

**Riscos**:
- Bypass de segurança (E6 pode ser sensor de porta, emergência, etc.)
- Pode causar operação insegura

**Recomendação**: **NÃO USAR** sem entender função de E6.

---

### Solução 3: Aceitar Limitação e Documentar
**Mais seguro**:
1. Documentar na interface que **modo AUTO requer E6 ativa**
2. Mostrar estado de E6 no diagnóstico
3. Alertar usuário quando tentar mudar modo com E6 inativa
4. Adicionar instrução: "Verifique condições da máquina"

**Implementação**:
```javascript
// Na interface web
if (!state.input_e6) {
    showWarning("Modo AUTO bloqueado: Entrada E6 inativa. Verifique máquina.");
}
```

---

### Solução 4: Investigar Ladder (Análise Profunda)
**Procedimento**:
1. Ler arquivo `clp.sup` ou `.lad` da ladder
2. Buscar lógica que escreve em 02FF
3. Identificar condições para E6
4. Entender requisitos completos

**Ferramentas**:
- Software Atos para análise de ladder
- Ou parsing manual dos arquivos `.txt` de ladder

---

## 📋 ESTADO FINAL DO SISTEMA

### Funcionalidades Testadas
| Funcionalidade | Status | Observação |
|----------------|--------|------------|
| Conexão Modbus | ✅ OK | Estável |
| Leitura encoder | ✅ OK | Atualiza |
| Escrita em 02FF | ✅ OK | Mas CLP reverte |
| Botão S1 | ⚠️ Parcial | Aceita comando, não altera modo |
| Entrada E6 | ❌ Inativa | **Bloqueio principal** |

### Taxa de Sucesso Geral
- **Comunicação**: 100% ✅
- **Mudança de modo**: 0% ❌ (bloqueada por E6)
- **Outras funções**: 78% ⚠️ (conforme teste anterior)

---

## 🚀 PRÓXIMOS PASSOS RECOMENDADOS

### ALTA Prioridade
1. **Identificar função de E6**:
   - Consultar documentação da máquina
   - Analisar esquema elétrico
   - Verificar se E6 = "Máquina OK" ou condição de segurança

2. **Testar condição de ativação de E6**:
   ```python
   # Monitorar E6 durante operação manual
   while True:
       e6 = client.read_coil(0x0106)
       print(f"E6: {e6}")
       time.sleep(0.5)
   # Operar máquina fisicamente, ver quando E6 ativa
   ```

3. **Atualizar interface web**:
   - Adicionar indicador de E6 no diagnóstico
   - Mostrar aviso quando E6 inativa
   - Desabilitar botão S1 quando E6 = False

### MÉDIA Prioridade
4. Analisar ladder completo (`PRINCIPA.LAD`)
5. Documentar todas as condições para mudança de modo
6. Criar guia de operação baseado em condições reais

---

## 📝 CONCLUSÃO

### Problema NÃO É da Interface ✅
- Interface V2 funciona perfeitamente
- S1 envia comando correto
- Display atualiza estado
- WebSocket estável

### Problema É do CLP/Ladder ⚠️
- **Entrada E6 inativa** bloqueia mudança de modo
- Ladder tem proteção ativa que reseta 02FF
- Comportamento é **intencional** (segurança)

### Recomendação Final
**NÃO forçar modo AUTO sem E6 ativa.**

Isso pode indicar:
- Máquina não está em condição segura
- Porta/proteção aberta
- Emergência latente
- Outro bloqueio de segurança

**Próxima ação**: Identificar **o que E6 representa fisicamente** antes de prosseguir.

---

**Arquivos gerados**:
- `diagnostico_modo_reversion.log` - Log do teste de monitoramento
- `test_mode_reversion.py` - Script de diagnóstico
- `test_check_all_inputs.py` - Script de verificação de I/O
- Este relatório

**Sistema continua funcional** para todas as outras operações (leitura de encoder, programação de ângulos, teclas, etc.).
