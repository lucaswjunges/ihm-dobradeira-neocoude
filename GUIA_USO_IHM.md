# 📱 GUIA DE USO - IHM WEB NEOCOUDE-HD-15

**Versão**: 2.0
**Data**: 08/11/2025

---

## 🎯 VISÃO GERAL

A IHM web replica a funcionalidade da IHM física original (modelo 4004.95) que está danificada, permitindo controlar a dobradeira através de qualquer tablet ou computador conectado na rede WiFi.

---

## 📺 TELA PRINCIPAL

A tela principal mostra o status em tempo real da máquina:

### Display LCD (Verde):
```
┌─────────────────────────────────┐
│ ÂNGULO ATUAL:          243°     │
│ MODO:                MANUAL     │
│ VELOCIDADE:     5 RPM (CLASSE1) │
│ DOBRA ATIVA:    ●①  ○②  ○③     │
│ DIREÇÃO:        ○ESQ  ○DIR      │
└─────────────────────────────────┘
```

**Legenda dos LEDs:**
- ●①●②●③ = Dobra atual (K1, K2 ou K3)
- ○ESQ = Esquerda (K4), ○DIR = Direita (K5)
- ● aceso = ativo, ○ apagado = inativo

---

## ⌨️ TECLADO VIRTUAL

### Teclas Numéricas (K0-K9):
```
┌────┬────┬────┬────┐
│ 7  │ 8  │ 9  │ ▲  │
├────┼────┼────┼────┤
│ 4  │ 5  │ 6  │ ▼  │
├────┼────┼────┼────┤
│ 1  │ 2  │ 3  │ESC │
├────┼────┼────┼────┤
│ S1 │ 0  │ S2 │ENT │
└────┴────┴────┴────┘
```

### Função das Teclas:

| Tecla | Função |
|-------|--------|
| **0-9** | Entrada numérica / Seleção de dobras |
| **S1** | Trocar modo Manual ↔ Automático |
| **S2** | Resetar encoder para zero |
| **▲▼** | Navegar nos menus (setas) |
| **ESC** | Voltar ao menu anterior |
| **ENT** | Confirmar seleção / Entrar no item |

---

## 🔧 CONFIGURAÇÃO DE ÂNGULOS

### Como Configurar:

1. **Abra o Menu**:
   - Use setas ▲▼ para navegar
   - Pressione **ENTER** para selecionar

2. **Escolha o Tipo**:
   - **"Configurar Ângulos Esquerda"** (K4) - dobras anti-horário
   - **"Configurar Ângulos Direita"** (K5) - dobras horário

3. **Edite os Valores**:
   - Clique no campo de entrada
   - Digite o ângulo desejado (ex: 90, 120, 45)
   - Os valores são salvos automaticamente

4. **Volte ao Menu**:
   - Pressione **ESC**

### Exemplo de Configuração:
```
[ ÂNGULOS ESQUERDA (K4) ]
Dobra 1 (K1):  [90°]
Dobra 2 (K2): [120°]
Dobra 3 (K3):  [45°]
```

**IMPORTANTE**:
- **AJ** = Ângulo configurado pelo usuário (editável)
- **PV** = Calculado automaticamente pelo CLP (NÃO MEXER)

---

## 🔄 MODOS DE OPERAÇÃO

### MODO MANUAL (Padrão):
- **Velocidade**: Apenas 5 RPM (Classe 1)
- **Operação**: Manter botão AVANÇAR/RECUAR pressionado
- **Parada**: Soltar o botão antes do zero + S2 para resetar

### MODO AUTOMÁTICO:
1. **Ativar**: Pressione **S1** (só com K1 aceso!)
2. **Selecionar Direção**:
   - Botão **PARADA** no painel físico
   - LED K4 (esquerda) ou K5 (direita) acende
3. **Executar**: Pressione AVANÇAR ou RECUAR
4. **Sequência**: K1 → K2 → K3 (não volta!)

**ATENÇÃO**:
- ⚠️ Para voltar à dobra 1: desligar COMANDO GERAL, aguardar display apagar, religar
- ⚠️ Trocar Manual↔Auto: só com K1 aceso (1ª dobra)

---

## ⚡ TROCA DE VELOCIDADE

**Somente no MODO MANUAL:**

1. Pressione **K1** + **K7** **simultaneamente**
2. Observe a velocidade no display
3. Cicla entre: 5 rpm → 10 rpm → 15 rpm → 5 rpm

**Classes de Velocidade**:
- **Classe 1**: 5 RPM (ferros finos e grossos)
- **Classe 2**: 10 RPM (ferros médios)
- **Classe 3**: 15 RPM (ferros finos - máxima produtividade)

---

## 🔍 DIAGNÓSTICO I/O

Para verificar entradas e saídas digitais em tempo real:

1. **Abrir Diagnóstico**:
   - Navegue até "Diagnóstico I/O"
   - Pressione **ENTER**

2. **Visualização**:
   ```
   Entradas (E0-E7): ○●○○●○○○
   Saídas (S0-S7):   ●○●○○●○○
   ```
   - ● = Ativo (ON)
   - ○ = Inativo (OFF)

### ✅ TESTE DE ENTRADAS:

**Para testar se o sistema está funcionando:**

1. **Pegue um fio**
2. **Conecte** E0 ao terminal **24VDC+** do borne
3. **Veja** o LED E0 acender na IHM! 🟢

---

## 📊 INFORMAÇÕES DO SISTEMA

Menu "Informações" mostra:
- Modelo da máquina
- Modelo do CLP
- Versão da IHM

---

## ⚠️ INDICADORES DE STATUS

### LED de Conexão (Topo Direito):
- 🟢 **Verde** = Conectado ao servidor
- 🔴 **Vermelho piscando** = Desconectado

### Overlay de Erro:
Se aparecer tela vermelha "DESCONECTADO":
1. Verificar se servidor está rodando
2. Aguardar reconexão automática (3 segundos)

---

## 🚀 OPERAÇÃO TÍPICA

### Fazer uma Dobra (Modo Manual):

1. ✅ Verificar modo: **MANUAL**
2. ✅ Verificar velocidade: **5 RPM**
3. ✅ Verificar ângulo configurado
4. ✅ **Manter** botão AVANÇAR/RECUAR pressionado
5. ✅ Soltar antes do zero
6. ✅ Pressionar **S2** se não zerou

### Produção em Série (Modo Auto):

1. ✅ Configurar 3 ângulos (K1, K2, K3)
2. ✅ Pressionar **S1** para modo AUTO
3. ✅ Pressionar **PARADA** (painel) para direção
4. ✅ Verificar LED K4 ou K5 aceso
5. ✅ Pressionar AVANÇAR ou RECUAR
6. ✅ Máquina executa automaticamente
7. ✅ Avança para próxima dobra (K1→K2→K3)
8. ✅ Para resetar: desligar COMANDO GERAL

---

## 🎮 ATALHOS DO TECLADO DO COMPUTADOR

Se estiver usando um computador, pode usar o teclado:

| Tecla PC | Função |
|----------|--------|
| **0-9** | Números K0-K9 |
| **↑** | Seta cima |
| **↓** | Seta baixo |
| **Esc** | ESC |
| **Enter** | ENTER |

---

## ❓ SOLUÇÃO DE PROBLEMAS

### Tela fica vermelha "DESCONECTADO":
- Verificar se servidor Python está rodando
- Comando: `ps aux | grep main_server`

### Botões não respondem:
- Verificar LED de conexão (verde)
- Ver logs: `tail -f server.log`

### Ângulo não atualiza:
- Verificar se encoder está conectado
- Ver diagnóstico I/O

### Não consigo mudar de modo:
- Só pode mudar com K1 aceso (1ª dobra)
- Reiniciar máquina se necessário

---

## 📞 SUPORTE

- **Logs do servidor**: `/home/lucas-junges/Documents/clientes/w&co/server.log`
- **Documentação técnica**: `STATUS.md`, `CLAUDE.md`

---

**Desenvolvido por**: Claude Code
**Cliente**: W&CO / Camargo Steel
**Máquina**: Trillor NEOCOUDE-HD-15 (2007)
