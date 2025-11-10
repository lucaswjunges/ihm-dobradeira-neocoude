# 📚 Índice Completo da Documentação - Retrofit IHM Expert Series

## 🚀 COMECE AQUI

### Primeira Leitura (ordem recomendada)
1. **`LEIA_AGORA.md`** ← Resumo executivo de 1 página (comece por aqui!)
2. **`GUIA_RETROFIT_IHM_EXPERT.md`** ← Guia mestre completo (passo a passo)
3. **`MAPEAMENTO_IHM_EXPERT.md`** ← Especificações da IHM física
4. **`REGISTROS_MODBUS_IHM.md`** ← Todos os endereços Modbus mapeados

---

## 📋 GUIAS PRINCIPAIS

### Para Implementação
| Arquivo | Tamanho | Conteúdo | Quando Usar |
|---------|---------|----------|-------------|
| **LEIA_AGORA.md** | 1 página | Resumo executivo + próximos passos | Início do projeto |
| **GUIA_RETROFIT_IHM_EXPERT.md** | Completo | Guia mestre com código de exemplo | Durante implementação |
| **MAPEAMENTO_IHM_EXPERT.md** | Referência | 11 telas + 18 teclas + navegação | Desenvolvimento frontend |
| **REGISTROS_MODBUS_IHM.md** | Referência | Endereços Modbus + exemplos Python | Desenvolvimento backend |

### Navegação Rápida por Tema

**🖥️ FRONTEND (Display LCD + Teclado)**
- Telas: `MAPEAMENTO_IHM_EXPERT.md` → Seção "Telas Programadas (11 telas)"
- Teclas: `MAPEAMENTO_IHM_EXPERT.md` → Seção "Mapeamento Modbus das Teclas"
- Código HTML/CSS: `GUIA_RETROFIT_IHM_EXPERT.md` → Seção "2.1 Display LCD" e "2.2 Teclado"
- JavaScript: `GUIA_RETROFIT_IHM_EXPERT.md` → Seção "2.3 Máquina de Estados"

**🔧 BACKEND (Modbus + WebSocket)**
- Registros gerais: `REGISTROS_MODBUS_IHM.md` → Seção "1-7"
- Encoder: `REGISTROS_MODBUS_IHM.md` → Seção "1. ENCODER"
- Ângulos: `REGISTROS_MODBUS_IHM.md` → Seção "2. SETPOINTS DE ÂNGULOS"
- Velocidade: `REGISTROS_MODBUS_IHM.md` → Seção "5. ESTADOS INTERNOS"
- Código Python: `REGISTROS_MODBUS_IHM.md` → Seção "10. CÓDIGO DE EXEMPLO"
- Polling: `GUIA_RETROFIT_IHM_EXPERT.md` → Seção "2.4 Backend"

**🧪 TESTES E VALIDAÇÃO**
- Checklist: `GUIA_RETROFIT_IHM_EXPERT.md` → Seção "FASE 3: TESTES E VALIDAÇÃO"
- Calibração: `GUIA_RETROFIT_IHM_EXPERT.md` → Seção "FASE 4: CALIBRAÇÃO"

**📐 CRONOGRAMA E PLANEJAMENTO**
- Estimativas: `GUIA_RETROFIT_IHM_EXPERT.md` → Seção "CRONOGRAMA ESTIMADO"
- Fases: `LEIA_AGORA.md` → Seção "CRONOGRAMA"

---

## 📖 DOCUMENTAÇÃO TÉCNICA DETALHADA

### Especificações da IHM Física

**Arquivo**: `MAPEAMENTO_IHM_EXPERT.md`

**Índice interno**:
- Especificações da IHM Física → Hardware da Expert Series 4004.95C
- Mapeamento Modbus das Teclas → Tabela com 18 teclas e endereços
- Telas Programadas (11 telas) → Tela 0 a Tela 10 com layouts
- Navegação Entre Telas → Padrões de navegação e atalhos
- LEDs Físicos → Indicadores K1-K5, S1, S2
- Notas do Engenheiro → Requisitos de retrofit profissional

**Exemplo de navegação**:
- Ver layout da Tela 3 (Encoder): `MAPEAMENTO_IHM_EXPERT.md` linha 86
- Ver endereço da tecla K1: `MAPEAMENTO_IHM_EXPERT.md` linha 25
- Ver navegação entre telas: `MAPEAMENTO_IHM_EXPERT.md` linha 207

### Registros Modbus Completos

**Arquivo**: `REGISTROS_MODBUS_IHM.md`

**Índice interno**:
1. ENCODER (Posição Angular) → Registros 04D6/04D7
2. SETPOINTS DE ÂNGULOS (Dobras) → Registros 0840-0853
3. ENTRADAS E SAÍDAS DIGITAIS → E0-E7, S0-S7
4. TECLAS DA IHM → Endereços coil 00A0-00F1
5. ESTADOS INTERNOS (Bits de Controle) → 00F7-00F9, 0360-0363
6. BITS INTERNOS LIVRES → 0030-0034 (não usados neste projeto)
7. REGISTROS A MAPEAR → Totalizador, modo AUTO/MAN
8. MAPEAMENTO POR TELA DA IHM → Checklist de registros por tela
9. PRIORIDADES DE IMPLEMENTAÇÃO → Fases 1-4
10. CÓDIGO DE EXEMPLO (Python) → Funções prontas para usar
11. NOTAS TÉCNICAS IMPORTANTES → Conversões, endereçamento, polling
12. CHECKLIST DE VALIDAÇÃO → Testes com CLP

**Exemplo de navegação**:
- Ver endereço do encoder: `REGISTROS_MODBUS_IHM.md` linha 14
- Ver ângulo dobra 1: `REGISTROS_MODBUS_IHM.md` linha 43
- Ver código Python leitura encoder: `REGISTROS_MODBUS_IHM.md` linha 411
- Ver polling recomendado: `REGISTROS_MODBUS_IHM.md` linha 562

### Guia de Implementação Completo

**Arquivo**: `GUIA_RETROFIT_IHM_EXPERT.md`

**Índice interno**:
- SUMÁRIO EXECUTIVO → Decisão estratégica + arquitetura
- FASE 1: ANÁLISE COMPLETA ✅ → O que foi feito
- FASE 2: IMPLEMENTAÇÃO DA IHM WEB ⏳ → Próxima etapa
  - 2.1. Componente Display LCD → HTML/CSS + JavaScript
  - 2.2. Componente Teclado Virtual → Layout + Código
  - 2.3. Máquina de Estados → ScreenManager class
  - 2.4. Backend → Atualizar main_server.py
- FASE 3: TESTES E VALIDAÇÃO → Checklists
- FASE 4: CALIBRAÇÃO E AJUSTES FINOS → Procedimentos
- FASE 5: DOCUMENTAÇÃO FINAL E ENTREGA → Manuais
- CRONOGRAMA ESTIMADO → 3-5 dias
- RISCOS E MITIGAÇÕES → Tabela de riscos
- PRÓXIMOS PASSOS IMEDIATOS → Tarefas sequenciais

**Exemplo de navegação**:
- Ver código HTML display: `GUIA_RETROFIT_IHM_EXPERT.md` linha 100
- Ver código CSS teclas: `GUIA_RETROFIT_IHM_EXPERT.md` linha 200
- Ver JavaScript navegação: `GUIA_RETROFIT_IHM_EXPERT.md` linha 300
- Ver testes de validação: `GUIA_RETROFIT_IHM_EXPERT.md` linha 600

---

## 🗂️ ARQUIVOS CONTEXTUAIS (Histórico)

### Sobre a Tentativa Anterior (Bits Internos)

Esses arquivos documentam a solução anterior que foi **descartada**. São úteis para entender o contexto, mas NÃO devem ser seguidos.

| Arquivo | Status | Conteúdo |
|---------|--------|----------|
| `LEIA_PRIMEIRO.md` | ⚠️ Obsoleto | Resumo da solução com bits internos (descartada) |
| `SOLUCAO_BITS_INTERNOS.md` | ⚠️ Obsoleto | Explicação técnica dos bits 48-52 (não usados) |
| `GUIA_MODIFICACAO_LADDER.md` | ⚠️ Obsoleto | Passo a passo WinSUP (não vamos modificar ladder) |
| `CHECKLIST_PROXIMOS_PASSOS.md` | ⚠️ Obsoleto | Checklist para modificar ladder (descartado) |
| `RESUMO_SOLUCAO_FINAL.md` | 📚 Histórico | Cronologia do diagnóstico (contexto) |

**Por que foram descartados?**
Após análise, decidiu-se **NÃO modificar o ladder** por segurança. A solução atual (retrofit completo da IHM Expert Series) é mais profissional e segura.

**Quando consultar?**
- Se quiser entender o diagnóstico inicial do problema
- Se quiser ver como chegamos à solução atual
- Se tiver curiosidade sobre a alternativa descartada

---

## 🔍 BUSCA RÁPIDA

### Por Assunto

**Display LCD**
- Especificações: `MAPEAMENTO_IHM_EXPERT.md` → "Especificações da IHM Física"
- Código HTML/CSS: `GUIA_RETROFIT_IHM_EXPERT.md` → "2.1. Componente Display LCD"
- Atualizar texto: `GUIA_RETROFIT_IHM_EXPERT.md` → função `updateLCD()`

**Teclado Virtual**
- Mapeamento: `MAPEAMENTO_IHM_EXPERT.md` → "Mapeamento Modbus das Teclas"
- Layout: `GUIA_RETROFIT_IHM_EXPERT.md` → "2.2. Componente Teclado Virtual"
- Endereços Modbus: `REGISTROS_MODBUS_IHM.md` → "4. TECLAS DA IHM"

**Encoder**
- Endereço: `REGISTROS_MODBUS_IHM.md` → "1. ENCODER"
- Leitura 32-bit: `REGISTROS_MODBUS_IHM.md` → "Código de Exemplo"
- Conversão graus: `GUIA_RETROFIT_IHM_EXPERT.md` → "4.1. Calibração do Encoder"

**Ângulos de Dobra**
- Endereços: `REGISTROS_MODBUS_IHM.md` → "2. SETPOINTS DE ÂNGULOS"
- Telas: `MAPEAMENTO_IHM_EXPERT.md` → "Tela 4/5/6"
- Código Python: `REGISTROS_MODBUS_IHM.md` → "Leitura de Ângulo Setpoint"

**Velocidade (RPM)**
- Endereços: `REGISTROS_MODBUS_IHM.md` → "Estados de Velocidade"
- Tela: `MAPEAMENTO_IHM_EXPERT.md` → "Tela 7"
- Código Python: `REGISTROS_MODBUS_IHM.md` → "Leitura de Classe de Velocidade"

**LEDs Indicadores**
- Mapeamento: `MAPEAMENTO_IHM_EXPERT.md` → "LEDs Físicos"
- CSS: `GUIA_RETROFIT_IHM_EXPERT.md` → "CSS para teclas com LED"
- Lógica: `REGISTROS_MODBUS_IHM.md` → "Verificar Dobra Ativa (LED)"

**Navegação Entre Telas**
- Padrão: `MAPEAMENTO_IHM_EXPERT.md` → "Navegação Entre Telas"
- Código JavaScript: `GUIA_RETROFIT_IHM_EXPERT.md` → "class ScreenManager"
- Teclas: `MAPEAMENTO_IHM_EXPERT.md` → "Navegação direta (atalhos)"

**Backend (Python)**
- Polling: `GUIA_RETROFIT_IHM_EXPERT.md` → "2.4. Backend"
- Exemplos: `REGISTROS_MODBUS_IHM.md` → "10. CÓDIGO DE EXEMPLO"
- Arquivos: `main_server.py`, `state_manager.py`, `modbus_client.py`

**Testes**
- Comunicação: `GUIA_RETROFIT_IHM_EXPERT.md` → "3.1. Testes de Comunicação"
- Navegação: `GUIA_RETROFIT_IHM_EXPERT.md` → "3.2. Testes de Navegação"
- LEDs: `GUIA_RETROFIT_IHM_EXPERT.md` → "3.3. Testes de LEDs"
- Validação: `REGISTROS_MODBUS_IHM.md` → "12. CHECKLIST DE VALIDAÇÃO"

---

## 📊 RESUMO DA DOCUMENTAÇÃO

### Estatísticas
- **Total de arquivos**: 12 documentos
- **Guias principais**: 4 (LEIA_AGORA, GUIA_RETROFIT, MAPEAMENTO, REGISTROS)
- **Arquivos históricos**: 5 (contexto, não seguir)
- **Registros mapeados**: 95% completo
- **Telas mapeadas**: 11/11 (100%)
- **Teclas mapeadas**: 18/18 (100%)

### Tempo de Leitura Estimado
- `LEIA_AGORA.md`: 5 minutos
- `GUIA_RETROFIT_IHM_EXPERT.md`: 30-45 minutos
- `MAPEAMENTO_IHM_EXPERT.md`: 20-30 minutos
- `REGISTROS_MODBUS_IHM.md`: 30-45 minutos
- **Total**: ~2 horas para leitura completa

### Cobertura Técnica
- ✅ Hardware IHM física: 100%
- ✅ Registros Modbus: 95%
- ✅ Código frontend (exemplo): 100%
- ✅ Código backend (exemplo): 100%
- ✅ Testes e validação: 100%
- ⏳ Implementação: 0% (próxima fase)

---

## 🎯 MAPA MENTAL

```
📚 DOCUMENTAÇÃO RETROFIT IHM
│
├── 🚀 INÍCIO RÁPIDO
│   └── LEIA_AGORA.md (1 página)
│
├── 📘 GUIAS PRINCIPAIS
│   ├── GUIA_RETROFIT_IHM_EXPERT.md (guia mestre)
│   ├── MAPEAMENTO_IHM_EXPERT.md (telas + teclas)
│   └── REGISTROS_MODBUS_IHM.md (endereços)
│
├── 🗂️ HISTÓRICO (não seguir)
│   ├── LEIA_PRIMEIRO.md
│   ├── SOLUCAO_BITS_INTERNOS.md
│   ├── GUIA_MODIFICACAO_LADDER.md
│   ├── CHECKLIST_PROXIMOS_PASSOS.md
│   └── RESUMO_SOLUCAO_FINAL.md
│
└── 🔧 IMPLEMENTAÇÃO (próxima fase)
    ├── Frontend: ihm_expert.html (a criar)
    ├── Backend: main_server.py (atualizar)
    └── Testes: validação completa
```

---

## ✅ CHECKLIST DE USO DA DOCUMENTAÇÃO

### Antes de Começar
- [ ] Li `LEIA_AGORA.md` (5 min)
- [ ] Entendi a decisão estratégica (não modificar ladder)
- [ ] Vi a arquitetura final (Painel → CLP → Modbus → Python → WebSocket → Tablet)

### Durante Implementação Frontend
- [ ] Consultei `MAPEAMENTO_IHM_EXPERT.md` para layout das telas
- [ ] Consultei `GUIA_RETROFIT_IHM_EXPERT.md` seção 2.1 para Display LCD
- [ ] Consultei `GUIA_RETROFIT_IHM_EXPERT.md` seção 2.2 para Teclado
- [ ] Consultei `GUIA_RETROFIT_IHM_EXPERT.md` seção 2.3 para Navegação
- [ ] Copiei/adaptei código de exemplo fornecido

### Durante Implementação Backend
- [ ] Consultei `REGISTROS_MODBUS_IHM.md` para endereços
- [ ] Consultei `GUIA_RETROFIT_IHM_EXPERT.md` seção 2.4 para polling
- [ ] Consultei `REGISTROS_MODBUS_IHM.md` seção 10 para exemplos Python
- [ ] Testei leitura de encoder (04D6/04D7)
- [ ] Testei leitura de ângulos (0840-0853)

### Durante Testes
- [ ] Segui checklist em `GUIA_RETROFIT_IHM_EXPERT.md` seção 3
- [ ] Validei comunicação Modbus
- [ ] Validei navegação entre telas
- [ ] Validei LEDs das teclas
- [ ] Calibrei encoder (seção 4.1)

### Ao Concluir
- [ ] Todos os testes passaram
- [ ] Display mostra dados reais do CLP
- [ ] Teclado simula teclas via Modbus
- [ ] Navegação funciona corretamente
- [ ] LEDs acendem conforme esperado

---

## 📞 SUPORTE E DÚVIDAS

### Consulta Rápida
| Dúvida | Onde Procurar |
|--------|---------------|
| "Como é a tela 5?" | `MAPEAMENTO_IHM_EXPERT.md` linha 123 |
| "Qual endereço do encoder?" | `REGISTROS_MODBUS_IHM.md` linha 14 |
| "Como ler ângulo em Python?" | `REGISTROS_MODBUS_IHM.md` linha 426 |
| "Como fazer navegação telas?" | `GUIA_RETROFIT_IHM_EXPERT.md` linha 350 |
| "Qual polling usar?" | `REGISTROS_MODBUS_IHM.md` linha 562 |

### Troubleshooting
| Problema | Solução |
|----------|---------|
| "Não sei por onde começar" | Leia `LEIA_AGORA.md` |
| "Preciso de código pronto" | Veja `GUIA_RETROFIT_IHM_EXPERT.md` seções 2.1-2.4 |
| "Não achei um registro" | Busque em `REGISTROS_MODBUS_IHM.md` |
| "Como funciona a tela X?" | Veja `MAPEAMENTO_IHM_EXPERT.md` |
| "Quanto tempo vai levar?" | Veja cronograma em `LEIA_AGORA.md` |

---

## 🔄 ATUALIZAÇÕES

**Versão**: 1.0
**Data**: 2025-11-08
**Status**: Análise completa ✅ / Implementação pendente ⏳

**Próximas atualizações previstas**:
- [ ] Documentação de implementação (quando frontend estiver pronto)
- [ ] Manual do operador (após testes)
- [ ] Manual de manutenção (após validação final)
- [ ] Diagrama de arquitetura visual

---

**Engenheiro**: Claude Code
**Cliente**: W&CO / Camargo Corrêa
**Máquina**: NEOCOUDE-HD-15 (2007)
**Projeto**: Retrofit IHM Expert Series → Web
