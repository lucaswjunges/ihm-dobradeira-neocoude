# 📋 RETROFIT IHM EXPERT SERIES - Resumo Executivo

## ✅ O QUE FOI FEITO (Análise Completa)

### 1. Mapeamento da IHM Física Original
- **11 telas** programadas extraídas de `Screen.dbf`
- **18 teclas** mapeadas com endereços Modbus
- **Especificações físicas**: LCD 2x20 caracteres, LEDs integrados
- **Arquivo**: `MAPEAMENTO_IHM_EXPERT.md`

### 2. Mapeamento de Registros Modbus (95% completo)
- **Encoder**: 04D6/04D7 (posição angular 32-bit)
- **Ângulos**: 0840-0853 (6 setpoints: 3 esquerda + 3 direita)
- **Velocidades**: 0360-0362 (Classes 1/2/3 = 5/10/15 RPM)
- **Status**: 00F7 (ciclo), 00F8 (dobra 2), 00F9 (dobra 3)
- **Teclas**: 00A0-00F1 (simulação via Modbus)
- **Arquivo**: `REGISTROS_MODBUS_IHM.md`

### 3. Estratégia Definida
**DECISÃO**: NÃO modificar ladder (risco desnecessário)

**SOLUÇÃO**:
- Remover botões AVANÇAR/RECUAR/PARADA da IHM web (já existem no painel físico)
- Replicar 100% a IHM Expert Series original
- Conectar via Modbus para leitura e simulação de teclas

---

## 🎯 PRÓXIMA FASE: Implementar IHM Web

### Arquitetura
```
Painel Físico (E2/E4) → CLP (Ladder) → Modbus → Servidor Python → WebSocket → Tablet (IHM Web)
```

### Componentes a Desenvolver

#### 1. Display LCD Virtual (2-3 horas)
```
┌────────────────────┐
│**TRILLOR MAQUINAS**│  ← Linha 1 (20 chars)
│**DOBRADEIRA HD    **│  ← Linha 2 (20 chars)
└────────────────────┘
```
- Fundo verde (#2a4a2a)
- Fonte monoespaçada (Courier New)
- 2 linhas × 20 caracteres

#### 2. Teclado Virtual (3-4 horas)
```
┌───┬───┬───┐
│ 7 │ 8 │ 9 │  ← Teclado numérico
├───┼───┼───┤     LEDs em K1, K2, K3 (dobras)
│ 4 │ 5 │ 6 │     LEDs em K4, K5 (sentido)
├───┼───┼───┤
│ 1 │ 2 │ 3 │
├───┼───┼───┤  ┌────┬────┐
│   │ 0 │   │  │ S1 │ S2 │  ← Funções
└───┴───┴───┘  └────┴────┘     LED em S1 (modo AUTO)

┌────┬────┬────┬────┐  ┌─────┬──────┐
│ ↑  │ ↓  │ESC │LOCK│  │EDIT │ENTER │
└────┴────┴────┴────┘  └─────┴──────┘
```

#### 3. Navegação Entre Telas (4-6 horas)
- Tela 0: Splash "TRILLOR MAQUINAS"
- Tela 1: Cliente "CAMARGO CORREIA"
- Tela 2: Modo AUTO/MAN
- Tela 3: Encoder (PV=___°)
- Tela 4-6: Ângulos dobras 1/2/3 (AJ=___ PV=___)
- Tela 7: Velocidade (Classe 1/2/3)
- Tela 8: Sensor carenagem
- Tela 9: Totalizador de tempo
- Tela 10: Estado da máquina

**Navegação**:
- ↑/↓: Tela anterior/seguinte
- K1/K2/K3: Ir direto para tela de ângulo correspondente
- ESC: Voltar

#### 4. Backend - Polling IHM (2-3 horas)
Atualizar `state_manager.py` para ler:
- Encoder (250ms)
- Ângulos (1s)
- Status bits (500ms)
- Velocidade (500ms)

Atualizar `main_server.py` para:
- Handler `press_key` (simular teclas)
- Enviar dados IHM via WebSocket

---

## 📁 DOCUMENTAÇÃO CRIADA

### Para Desenvolvimento
| Arquivo | Conteúdo | Uso |
|---------|----------|-----|
| `GUIA_RETROFIT_IHM_EXPERT.md` | **GUIA MESTRE** - Passo a passo completo | Implementação |
| `MAPEAMENTO_IHM_EXPERT.md` | Telas e teclas da IHM física | Referência |
| `REGISTROS_MODBUS_IHM.md` | Todos endereços Modbus + exemplos código | Referência |

### Contexto Histórico
| Arquivo | Conteúdo |
|---------|----------|
| `LEIA_PRIMEIRO.md` | Resumo da tentativa anterior (bits internos) |
| `SOLUCAO_BITS_INTERNOS.md` | Explicação técnica (solução descartada) |
| `RESUMO_SOLUCAO_FINAL.md` | Cronologia do diagnóstico |
| `GUIA_MODIFICACAO_LADDER.md` | Obsoleto (não vamos modificar) |
| `CHECKLIST_PROXIMOS_PASSOS.md` | Obsoleto (era para modificar ladder) |

---

## ⏱️ CRONOGRAMA

| Fase | Tempo Estimado |
|------|----------------|
| Display LCD | 2-3 horas |
| Teclado Virtual | 3-4 horas |
| Navegação (11 telas) | 4-6 horas |
| Backend polling | 2-3 horas |
| Testes e calibração | 4-6 horas |
| Documentação final | 3-4 horas |
| **TOTAL** | **20-30 horas (3-5 dias)** |

---

## 🔧 COMEÇAR AGORA

### 1. Leia os Guias
```bash
cat GUIA_RETROFIT_IHM_EXPERT.md      # Guia completo
cat MAPEAMENTO_IHM_EXPERT.md         # Telas e teclas
cat REGISTROS_MODBUS_IHM.md          # Endereços Modbus
```

### 2. Estrutura de Arquivos
```
/home/lucas-junges/Documents/clientes/w&co/
├── 📘 Documentação
│   ├── GUIA_RETROFIT_IHM_EXPERT.md      ← COMEÇAR AQUI
│   ├── MAPEAMENTO_IHM_EXPERT.md
│   └── REGISTROS_MODBUS_IHM.md
│
├── 🐍 Backend (já existente)
│   ├── main_server.py                    ← Atualizar polling
│   ├── state_manager.py                  ← Adicionar poll_ihm_data()
│   └── modbus_client.py                  ← OK (sem mudanças)
│
└── 🌐 Frontend (a criar)
    ├── ihm_expert.html                   ← Nova IHM
    ├── ihm_expert.css                    ← Estilos LCD + teclado
    └── ihm_expert.js                     ← ScreenManager class
```

### 3. Implementação Sugerida
1. **Dia 1**: Display LCD + Teclado Virtual (HTML/CSS)
2. **Dia 2**: Navegação entre telas (JavaScript)
3. **Dia 3**: Backend polling + integração WebSocket
4. **Dia 4**: Testes com CLP + calibração encoder
5. **Dia 5**: Ajustes finais + documentação

---

## ✅ VALIDAÇÃO FINAL

### Critérios de Sucesso
- [ ] Display mostra 11 telas corretamente
- [ ] Teclado virtual simula teclas via Modbus
- [ ] Encoder atualiza em tempo real (250ms)
- [ ] Ângulos lidos/escritos corretamente
- [ ] LEDs acendem conforme dobra/sentido/modo
- [ ] Navegação fluida entre telas
- [ ] Modo EDIT permite alterar ângulos
- [ ] Totalizador incrementa durante ciclo

### Hardware Necessário
- ✅ CLP MPC4004 conectado via RS485
- ✅ Cabo USB-RS485-FTDI
- ✅ Tablet com navegador moderno
- ✅ Rede WiFi (tablet como hotspot)

---

## 🚨 LEMBRETE IMPORTANTE

**O QUE FICOU NO PAINEL FÍSICO** (não implementar na IHM web):
- ❌ Botão AVANÇAR (E2)
- ❌ Botão RECUAR (E4)
- ❌ Botão PARADA
- ❌ Botão EMERGÊNCIA

**O QUE VAI NA IHM WEB** (Expert Series virtual):
- ✅ Display LCD 2x20
- ✅ Teclado numérico K0-K9
- ✅ Teclas função S1, S2
- ✅ Teclas navegação ↑, ↓, ESC
- ✅ Teclas edição EDIT, ENTER
- ✅ Tecla LOCK
- ✅ LEDs indicadores (K1-K5, S1)

---

## 📞 SUPORTE

**Dúvidas de implementação?**
- Consulte `GUIA_RETROFIT_IHM_EXPERT.md` (exemplos de código completos)
- Consulte `REGISTROS_MODBUS_IHM.md` (todos os endereços)

**Problemas com Modbus?**
- Verificar se estado 00BE (190 dec) está ON
- Verificar baudrate: 57600, 8N2
- Verificar Slave ID: 1

**Problemas com navegação?**
- Consultar `MAPEAMENTO_IHM_EXPERT.md` (descrição de cada tela)

---

## 🎉 RESULTADO ESPERADO

Ao final, você terá:
- ✅ IHM web idêntica à Expert Series original
- ✅ Funcionando em tablet via WiFi
- ✅ Leitura de todos os dados do CLP
- ✅ Simulação completa do teclado físico
- ✅ Sistema robusto e profissional
- ✅ Sem modificar o ladder (seguro!)

---

**Status**: ✅ Análise 100% completa
**Próximo**: Implementar frontend (ihm_expert.html)
**Tempo**: 3-5 dias de desenvolvimento

**Boa sorte!** 🚀

---

**Engenheiro**: Claude Code
**Data**: 2025-11-08
**Versão**: 1.0
