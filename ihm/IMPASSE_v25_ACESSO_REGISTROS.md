# IMPASSE CRÍTICO - v25 e Acesso a Registros

**Data:** 12 de Novembro de 2025
**Status:** ⚠️ BLOQUEADO - VALIDAÇÃO NECESSÁRIA
**Versão:** v25 (MD5: f04fb1e8cb9c3e45181cfd13e56031d6)

---

## 📋 RESUMO DO IMPASSE

### Situação Atual

**v25 compila sem erros ✅ MAS:**
- ❌ NÃO atende aos objetivos originais
- ❌ Apenas copia ângulos repetidamente (inútil)
- ❌ Nenhum espelhamento Modbus implementado
- ❌ Nenhuma lógica WEG inverter
- ❌ Nenhuma supervisão avançada
- ❌ Nenhuma emulação de teclas

### Objetivo Original (do usuário)

> "lembre-se do que falamos sobre weg inverter, espelhamento de memória modbus, deixar ihm web mais poderosa e com mais capacidade de gerenciamento e supervisão, menos intrusivo possível"

**Recursos esperados:**
1. **Espelhamento Modbus**: I/O digital (E0-E7, S0-S7), encoder, status
2. **WEG Inverter**: Tensão, corrente, RPM, classe velocidade
3. **Supervisão**: Contadores de peças, timers, alarmes, estatísticas
4. **Teclas remotas**: Emular K0-K9, S1, S2 via Modbus
5. **IHM Web poderosa**: Mais capacidade que IHM física original

---

## 🔍 DESCOBERTAS DAS 24 VERSÕES ANTERIORES

### Restrições do MOV (Ladder Interno)

**MOV CONSEGUE ler (validado em ROT4):**
```
✅ 0840, 0842, 0846, 0848, 0850, 0852 (ângulos)
✅ 04D6, 05F0 (especiais)
```

**MOV NÃO CONSEGUE ler (testado v19-v24):**
```
❌ 0100-0107 (E0-E7 entradas digitais)
❌ 0180-0187 (S0-S7 saídas digitais)
❌ 0191 (ciclo ativo)
❌ 02FF (modo manual)
❌ 00BE (Modbus slave)
❌ 0400-041A (timers)
❌ 04D7 (encoder LSW)
❌ 05F1, 05F2 (inversor)
❌ 06E0 (tensão inversor)
❌ 0900 (classe velocidade)
```

**Erro obtido:** "MOV - registro Origem fora do range permitido"

---

## 💡 ASSUNÇÃO FEITA (NÃO VALIDADA!)

### Hipótese

Assumimos que **Python via Modbus RTU externo** teria acesso MAIOR que MOV interno:

```python
# Hipótese (NÃO TESTADA):
client.read_holding_registers(0x0100, 8)  # E0-E7
client.read_holding_registers(0x0180, 8)  # S0-S7
client.read_holding_registers(0x04D6, 2)  # Encoder MSW+LSW
client.read_holding_registers(0x0400, 27) # Timers
client.read_holding_registers(0x06E0, 1)  # Tensão inversor
```

**Base da hipótese:**
- Manual MPC4004 lista "Read Holding Registers (0x03)"
- CLAUDE.md dizia: `0x0100-0x0107 (E0-E7)` acessíveis
- Modbus protocol deveria ter acesso completo

### Questionamento do Usuário

> "Pelo que me lembro, esses valores também não são acessíveis pelo modbus rtu."

**CRÍTICO:** Se Modbus RTU também NÃO consegue acessar esses registros:
- ❌ Python não pode implementar espelhamento
- ❌ Objetivo original é impossível sem modificar ROT0-4
- ❌ v25 (ou qualquer versão) não consegue fazer o que foi pedido

---

## 🧪 TESTE NECESSÁRIO (AGORA)

### CLP Ligado - Testar com mbpoll

**Registros críticos a validar:**

| Registro | Hex | Decimal | Descrição | Expectativa |
|----------|-----|---------|-----------|-------------|
| E0 | 0x0100 | 256 | Entrada digital E0 | Modbus lê? |
| E1 | 0x0101 | 257 | Entrada digital E1 | Modbus lê? |
| S0 | 0x0180 | 384 | Saída digital S0 | Modbus lê? |
| S1 | 0x0181 | 385 | Saída digital S1 | Modbus lê? |
| Encoder MSW | 0x04D6 | 1238 | Encoder high word | Modbus lê? |
| Encoder LSW | 0x04D7 | 1239 | Encoder low word | Modbus lê? |
| Timer 0 | 0x0400 | 1024 | Timer 0 | Modbus lê? |
| Ciclo ativo | 0x0191 | 401 | Estado ciclo | Modbus lê? (coil?) |
| Modo manual | 0x02FF | 767 | Estado modo | Modbus lê? (coil?) |
| Tensão inv | 0x06E0 | 1760 | Tensão inversor | Modbus lê? |
| Classe vel | 0x0900 | 2304 | Velocidade classe | Modbus lê? |

**Comandos mbpoll a executar:**

```bash
# Porta serial (descobrir qual)
PORT="/dev/ttyUSB0"  # ou ttyUSB1
SLAVE=1              # Endereço slave do CLP

# Teste 1: E0-E7 (Holding Registers)
mbpoll -a $SLAVE -r 256 -c 8 -t 3 $PORT -b 57600 -P none -s 2

# Teste 2: S0-S7 (Holding Registers)
mbpoll -a $SLAVE -r 384 -c 8 -t 3 $PORT -b 57600 -P none -s 2

# Teste 3: Encoder MSW+LSW
mbpoll -a $SLAVE -r 1238 -c 2 -t 3 $PORT -b 57600 -P none -s 2

# Teste 4: Timers 0400-0406
mbpoll -a $SLAVE -r 1024 -c 7 -t 3 $PORT -b 57600 -P none -s 2

# Teste 5: Tensão inversor
mbpoll -a $SLAVE -r 1760 -c 1 -t 3 $PORT -b 57600 -P none -s 2

# Teste 6: Ângulos (sabemos que funciona via Modbus)
mbpoll -a $SLAVE -r 2112 -c 6 -t 3 $PORT -b 57600 -P none -s 2

# Teste 7: Coils - Ciclo ativo
mbpoll -a $SLAVE -r 401 -c 1 -t 0 $PORT -b 57600 -P none -s 2

# Teste 8: Coils - Modo manual
mbpoll -a $SLAVE -r 767 -c 1 -t 0 $PORT -b 57600 -P none -s 2
```

**Tipos mbpoll:**
- `-t 0` = Coil (0x01 Read Coils)
- `-t 1` = Discrete Input (0x02)
- `-t 3` = Holding Register (0x03)
- `-t 4` = Input Register (0x04)

---

## 🎯 CENÁRIOS POSSÍVEIS

### Cenário A: Modbus CONSEGUE ler (Melhor Caso)

**Se mbpoll retornar valores válidos:**
```
✅ Python pode implementar TUDO
✅ v25 (ou v26 com RET) + Python = objetivo alcançado
✅ Espelhamento via Python, não via ladder
✅ IHM Web poderosa (toda lógica em Python)
```

**Próximos passos:**
1. Criar `state_manager.py` com polling Modbus direto
2. ROT5-9 podem ficar com RET ou lógica mínima
3. Python implementa espelhamento, WEG, supervisão, teclas

### Cenário B: Modbus NÃO consegue ler (Pior Caso)

**Se mbpoll retornar Illegal Data Address (0x02):**
```
❌ Registros não são Holding Registers via Modbus
❌ Python também não consegue acessar
❌ Dados estão "presos" dentro do CLP
❌ Única solução: Modificar ROT0-4 (intrusivo!)
```

**Próximos passos:**
1. Revisar manual MPC4004 para mapeamento REAL
2. Tentar outros Function Codes (0x01, 0x02, 0x04)
3. Verificar se existe área de memória compartilhada
4. Última opção: Modificar ROT0-4 para espelhar em área acessível

### Cenário C: Alguns SIM, outros NÃO (Caso Misto)

**Se alguns registros funcionam e outros não:**
```
⚠️ Implementação parcial possível
⚠️ Identificar o que é acessível
⚠️ Adaptar objetivos ao possível
```

**Próximos passos:**
1. Mapear exatamente o que é acessível
2. Priorizar funcionalidades com dados disponíveis
3. Avaliar se vale implementação parcial

---

## 📊 TESTE A EXECUTAR AGORA

### Preparação

1. **CLP ligado:** ✅ (usuário confirmou)
2. **Porta serial:** Descobrir `/dev/ttyUSB0` ou `/dev/ttyUSB1`
3. **Slave ID:** Provavelmente 1 (ler do registro 1988H se necessário)
4. **Baudrate:** 57600
5. **Paridade:** None
6. **Stop bits:** 2

### Testes Prioritários

**1. E0-E7 (entradas digitais) - CRÍTICO**
```bash
mbpoll -a 1 -r 256 -c 8 -t 3 /dev/ttyUSB0 -b 57600 -P none -s 2
```

**2. S0-S7 (saídas digitais) - CRÍTICO**
```bash
mbpoll -a 1 -r 384 -c 8 -t 3 /dev/ttyUSB0 -b 57600 -P none -s 2
```

**3. Encoder (posição angular) - CRÍTICO**
```bash
mbpoll -a 1 -r 1238 -c 2 -t 3 /dev/ttyUSB0 -b 57600 -P none -s 2
```

**4. Ângulos (validação - deve funcionar)**
```bash
mbpoll -a 1 -r 2112 -c 6 -t 3 /dev/ttyUSB0 -b 57600 -P none -s 2
```

### Respostas Esperadas

**Sucesso:**
```
[256]: 1          # E0 está ON
[257]: 0          # E1 está OFF
[258]: 1          # E2 está ON
...
```

**Falha:**
```
mbpoll: Illegal Data Address (0x02)
```
ou
```
mbpoll: Timeout
```

---

## 📝 REGISTRO DE RESULTADOS

### Data/Hora: _______________

**Porta usada:** _______________

**Slave ID:** _______________

### Resultados:

| Registro | Resultado | Valor | Observação |
|----------|-----------|-------|------------|
| 0x0100 (E0) | ☐ OK ☐ FAIL | _____ | ___________ |
| 0x0101 (E1) | ☐ OK ☐ FAIL | _____ | ___________ |
| 0x0180 (S0) | ☐ OK ☐ FAIL | _____ | ___________ |
| 0x0181 (S1) | ☐ OK ☐ FAIL | _____ | ___________ |
| 0x04D6 (Enc MSW) | ☐ OK ☐ FAIL | _____ | ___________ |
| 0x04D7 (Enc LSW) | ☐ OK ☐ FAIL | _____ | ___________ |
| 0x0400 (Timer 0) | ☐ OK ☐ FAIL | _____ | ___________ |
| 0x06E0 (Tensão) | ☐ OK ☐ FAIL | _____ | ___________ |
| 0x0840 (Ângulo 1) | ☐ OK ☐ FAIL | _____ | ___________ |

### Conclusão dos Testes:

☐ **Cenário A** - Modbus consegue ler (Python pode fazer tudo)
☐ **Cenário B** - Modbus NÃO consegue (modificar ROT0-4 necessário)
☐ **Cenário C** - Misto (implementação parcial)

---

## 🚨 DECISÃO PÓS-TESTE

### Se Cenário A (Modbus funciona):
- [ ] Manter v25 como está (compila)
- [ ] Implementar `state_manager.py` com leitura Modbus direta
- [ ] ROT5-9 podem ser RET puro ou lógica mínima
- [ ] Focar 100% em Python para espelhamento

### Se Cenário B (Modbus falha):
- [ ] Revisar manual MPC4004 para mapeamento correto
- [ ] Tentar outros Function Codes
- [ ] Avaliar necessidade de modificar ROT0-4
- [ ] Replanejar arquitetura completa

### Se Cenário C (Misto):
- [ ] Mapear registros acessíveis
- [ ] Priorizar funcionalidades possíveis
- [ ] Avaliar viabilidade da implementação

---

## 🎓 LIÇÕES APRENDIDAS

1. **NUNCA assumir sem testar empiricamente**
   - Achamos que Modbus teria acesso
   - Usuário questionou corretamente
   - Teste empírico é OBRIGATÓRIO

2. **Validar TODA a cadeia de acesso**
   - MOV interno: ❌ Testado e falhou
   - Modbus externo: ⚠️ NÃO testado ainda!
   - Manual: Insuficiente/incompleto

3. **Arquitetura depende de capacidades reais**
   - Se Modbus funciona: Python pode tudo
   - Se Modbus falha: Repensar TUDO

4. **Documentar impasses é essencial**
   - 24 versões documentadas salvaram tempo
   - Este impasse pode ser crítico
   - Retornar ao problema com contexto claro

---

## 📚 REFERÊNCIAS

- `REFERENCIA_DEFINITIVA_CLP_10_ROTINAS.md` - Histórico completo das 25 versões
- `RESUMO_EXECUTIVO_v25.md` - Descoberta MOV vs Modbus
- `COMPARACAO_VISUAL_VERSOES.txt` - Evolução v18-v25
- Manual MPC4004 página 133 - Modbus implementation
- CLAUDE.md seção 6.2 - Registros via Modbus (NÃO VALIDADO)

---

## 🔄 PRÓXIMOS PASSOS

1. ✅ Documentar impasse (este arquivo)
2. ⏳ Executar testes mbpoll (AGORA)
3. ⏳ Registrar resultados neste documento
4. ⏳ Tomar decisão baseada em dados reais
5. ⏳ Implementar solução validada empiricamente

---

## 🎉 ATUALIZAÇÃO FINAL - 12/Nov/2025, 22:30 BRT

**Status:** ✅ **IMPASSE RESOLVIDO!**

**Cenário confirmado:** **Cenário A** - Modbus RTU CONSEGUE ler dados que MOV interno não consegue!

**Descoberta crítica:** I/O digital (E0-E7, S0-S7) são **COILS** (Function 0x01), NÃO Holding Registers (Function 0x03).

**Resultados completos:** Ver `RESULTADOS_TESTES_MODBUS.md`

**Arquitetura validada:**
- ✅ CLP Ladder (ROT5-9): Lógica mínima ou RET
- ✅ Python Backend: Supervisão completa via Modbus
- ✅ Frontend Web: Mais poderosa que IHM física

**Documentação criada:** `CLAUDE2.md` - Guia definitivo para implementação da IHM Web

**Decisão:** Prosseguir com desenvolvimento da IHM Web usando arquitetura Python + HTML/JS.

**Risco:** Baixo - todos os dados críticos são acessíveis via Modbus RTU

---

**Criado:** 12 de Novembro de 2025
**Atualizado:** 12 de Novembro de 2025, 22:30 BRT
**Autor:** Claude Code (Anthropic)
**Versão:** 2.0 - RESOLVIDO
