# MAPEAMENTO COMPLETO DAS TECLAS - IHM EXPERT SERIES

## 📚 FONTES
- MAPEAMENTO_IHM_EXPERT.md
- GUIA_USO_IHM.md  
- Manual NEOCOUDE-HD-15
- Ladder extraído (clp.sup)

---

## 🎮 TECLAS E SUAS FUNÇÕES

### NAVEGAÇÃO

#### ↑ (SETA CIMA) - Endereço: 00AC (172 decimal)
**Funções**:
1. **Modo Normal**: Vai para tela anterior
2. **Modo EDIT**: Incrementa o valor sendo editado (+1)

**Comportamento**:
- Navegação circular: Tela 10 → ↑ → Tela 2
- Telas 0 e 1 são puladas (splash screens)

---

#### ↓ (SETA BAIXO) - Endereço: 00AD (173 decimal)
**Funções**:
1. **Modo Normal**: Vai para próxima tela
2. **Modo EDIT**: Decrementa o valor sendo editado (-1)

**Comportamento**:
- Navegação circular: Tela 2 → ↓ → Tela 3 → ... → Tela 10 → Tela 2
- Telas 0 e 1 são puladas

---

### TECLADO NUMÉRICO

#### K0 - Endereço: 00A9 (169 decimal)
**Funções**:
1. **Modo EDIT**: Digite número "0"
2. **Outras telas**: Sem função específica

---

#### K1 - Endereço: 00A0 (160 decimal)
**Funções**:
1. **Modo EDIT**: Digite número "1"
2. **Qualquer tela**: Navegação direta para **Tela 4** (Ajuste Ângulo 01)
3. **Tela 7 + K7 simultâneo**: Muda classe de velocidade (só MANUAL)

**LED K1**:
- Acende quando: Tela 4 ativa OU Dobra 1 selecionada

---

#### K2 - Endereço: 00A1 (161 decimal)
**Funções**:
1. **Modo EDIT**: Digite número "2"
2. **Qualquer tela**: Navegação direta para **Tela 5** (Ajuste Ângulo 02)

**LED K2**:
- Acende quando: Tela 5 ativa OU Dobra 2 selecionada

---

#### K3 - Endereço: 00A2 (162 decimal)
**Funções**:
1. **Modo EDIT**: Digite número "3"
2. **Qualquer tela**: Navegação direta para **Tela 6** (Ajuste Ângulo 03)

**LED K3**:
- Acende quando: Tela 6 ativa OU Dobra 3 selecionada

---

#### K4 - Endereço: 00A3 (163 decimal)
**Funções**:
1. **Modo EDIT**: Digite número "4"
2. **Modo AUTO**: Seleciona sentido ANTI-HORÁRIO (Esquerda)

**LED K4**:
- Acende quando: Sentido anti-horário selecionado

---

#### K5 - Endereço: 00A4 (164 decimal)
**Funções**:
1. **Modo EDIT**: Digite número "5"
2. **Modo AUTO**: Seleciona sentido HORÁRIO (Direita)

**LED K5**:
- Acende quando: Sentido horário selecionado

---

#### K6 - Endereço: 00A5 (165 decimal)
**Funções**:
1. **Modo EDIT**: Digite número "6"
2. **Outras telas**: Sem função específica

---

#### K7 - Endereço: 00A6 (166 decimal)
**Funções**:
1. **Modo EDIT**: Digite número "7"
2. **Tela 7 + K1 simultâneo**: Muda classe de velocidade (só MANUAL)

---

#### K8 - Endereço: 00A7 (167 decimal)
**Funções**:
1. **Modo EDIT**: Digite número "8"
2. **Outras telas**: Sem função específica

---

#### K9 - Endereço: 00A8 (168 decimal)
**Funções**:
1. **Modo EDIT**: Digite número "9"
2. **Outras telas**: Sem função específica

---

### FUNÇÕES ESPECIAIS

#### S1 - Endereço: 00DC (220 decimal)
**Funções DEPENDEM DA TELA ATIVA**:

**Tela 2 (Seleção Modo)**:
- Alterna entre AUTO ↔ MANUAL
- **Regra**: Só pode alternar quando máquina PARADA

**Outras telas**:
- Função contexto-dependente definida no ladder
- Normalmente sem função

**LED S1**:
- Acende quando: Modo AUTOMÁTICO ativo

---

#### S2 - Endereço: 00DD (221 decimal)
**Funções**:
1. **Tela 3 (Encoder)**: Reset do encoder para zero
2. **Outras telas**: Função contexto-dependente

**LED S2**:
- Normalmente apagado
- Pode acender em condições específicas (definido no ladder)

---

### CONTROLES

#### ENTER - Endereço: 0025 (37 decimal)
**Funções**:
1. **Modo EDIT**: Confirma o valor digitado e salva
2. **Modo Normal**: Sem efeito
3. **Menu/Seleção**: Confirma opção

---

#### ESC (Escape) - Endereço: 00BC (188 decimal)
**Funções**:
1. **Modo EDIT**: Cancela edição, volta valor anterior
2. **Qualquer tela**: Volta para tela inicial (Tela 2 ou 3)
3. **Menu**: Sai do menu sem salvar

---

#### EDIT - Endereço: 0026 (38 decimal)
**Funções**:
1. **Telas 4/5/6 (Ângulos)**: Entra em modo edição do campo AJ
2. **Outras telas editáveis**: Ativa modo edição
3. **Modo EDIT ativo**: Sem efeito (já está editando)

**Indicação visual**:
- Cursor piscando no campo editável
- Valor atual pisca

---

#### LOCK - Endereço: 00F1 (241 decimal)
**Funções**:
1. **Teclado destravado**: Trava o teclado (desabilita todas as teclas)
2. **Teclado travado**: Destrava o teclado

**Estado**:
- Bit 00F1 = 1: Teclado travado
- Bit 00F1 = 0: Teclado normal

**Indicação**:
- Mensagem no display quando travado
- Apenas LOCK funciona quando travado

---

## 🔄 SEQUÊNCIAS ESPECIAIS

### Mudança de Velocidade (K1 + K7)
**Pré-requisitos**:
- Modo MANUAL ativo
- Máquina PARADA
- Tela 7 ativa

**Procedimento**:
1. Navegar até Tela 7 (Seleção de Rotação)
2. Pressionar K1 + K7 SIMULTANEAMENTE
3. Display mostra classe atual
4. Cicla: Classe 1 (5 RPM) → 2 (10 RPM) → 3 (15 RPM) → 1...

---

### Seleção de Sentido (K4 ou K5)
**Pré-requisitos**:
- Modo AUTOMÁTICO ativo
- Máquina PARADA (botão PARADA pressionado no painel físico)

**Procedimento**:
1. Pressionar botão PARADA (painel físico)
2. Pressionar K4 (esquerda) ou K5 (direita) na IHM
3. LED correspondente acende
4. Sentido selecionado

---

### Reset Encoder (S2 na Tela 3)
**Quando usar**:
- Quando display não mostra zero e máquina está na posição zero

**Procedimento**:
1. Navegar até Tela 3 (Deslocamento Angular)
2. Máquina em posição zero física
3. Pressionar S2
4. Encoder reseta para 0

---

## 📊 RESUMO POR CONTEXTO

### Modo EDIT Ativo
| Tecla | Função |
|-------|--------|
| K0-K9 | Digite dígitos |
| ↑ | Incrementa +1 |
| ↓ | Decrementa -1 |
| ENTER | Confirma e salva |
| ESC | Cancela |
| Outras | Sem efeito |

### Modo MANUAL
| Tecla | Função |
|-------|--------|
| S1 | Alterna AUTO/MAN (Tela 2) |
| K1+K7 | Muda velocidade (Tela 7) |
| ↑↓ | Navega telas |
| K1/K2/K3 | Vai para tela ângulo |

### Modo AUTOMÁTICO
| Tecla | Função |
|-------|--------|
| S1 | Alterna AUTO/MAN (Tela 2) |
| K4 | Sentido esquerda |
| K5 | Sentido direita |
| ↑↓ | Navega telas |
| K1/K2/K3 | Vai para tela ângulo |

---

## ⚠️ RESTRIÇÕES IMPORTANTES

1. **S1 (Modo)**: Só funciona se máquina PARADA
2. **K1+K7 (Velocidade)**: Só em MANUAL e PARADO
3. **K4/K5 (Sentido)**: Só em AUTO após PARADA
4. **EDIT**: Só em telas com campos editáveis
5. **LOCK**: Bloqueia TODAS as teclas exceto ela mesma

---

## 🔴 NOTAS DO LADDER

Do arquivo ladder extraído:
- `00DC` (S1) está conectada ao bit `0106` e condicional `02FF`
- `00DD` (S2) aparece em condições específicas de reset/função
- `00A0` (K1) + `00A6` (K7) combinados com `02FF` (modo)

Isso confirma que S1 e as teclas K têm comportamento DEPENDENTE DO CONTEXTO/MODO.

---

**Conclusão**: As teclas NÃO são simplesmente "números" - elas têm funções INTELIGENTES que dependem de:
1. Qual tela está ativa
2. Qual modo está ativo (AUTO/MANUAL)
3. Se está em modo EDIT
4. Estado da máquina (parada/rodando)

A IHM WEB precisa RESPEITAR esses contextos!
