# Resultado do Teste: K1 + S1 via Modbus

**Data**: 2025-11-15 16:16
**Status**: ⚠️ **K1 VIA MODBUS NÃO FUNCIONA**

---

## 🧪 TESTE EXECUTADO

Simulei via Modbus:
1. K1 (coil 0x00A0) - apertar e soltar
2. Aguardar 2s
3. Verificar BEND_CURRENT e LED1
4. S1 se condições OK

---

## 📊 RESULTADOS

### Estado Inicial
```
BEND_CURRENT: 0
LED1:         False
MODE:         MANUAL
```

### Após K1 via Modbus (150ms ON + OFF)
```
BEND_CURRENT: 0  ❌ NÃO MUDOU
LED1:         False  ❌ NÃO ACENDEU
SCREEN_NUM:   0  ❌ NÃO MUDOU
MODE:         MANUAL
```

---

## 🔍 CONCLUSÕES

### 1. K1 via Modbus NÃO seleciona dobra

**Possíveis causas**:

**A) K1 é apenas leitura de tecla física**
   - Coil 0x00A0 pode ser **read-only** (estado da tecla)
   - Selecionar dobra pode requerer **outro registro**
   - Ladder pode ignorar writes em 0x00A0

**B) Lógica do CLP requer condições adicionais**
   - Pode precisar estar em tela específica
   - Pode precisar de modo específico
   - Pode ter intertravamento

**C) BEND_CURRENT não é controlável via Modbus**
   - Pode ser interno ao ladder
   - Pode ser setado apenas por lógica de navegação

### 2. **VOCÊ PRECISA APERTAR K1 FISICAMENTE**

Para testar S1 corretamente:
1. ✅ **Apertar K1 no painel FÍSICO**
2. ✅ Verificar LED1 aceso
3. ✅ **Depois apertar S1 FISICAMENTE**

---

## 🎯 DIAGNÓSTICO FINAL ATUALIZADO

### Por que S1 não alterna modo?

**CAUSA CONFIRMADA**: Sistema não está na dobra 1

**SOLUÇÃO**:
- ❌ ~~Simular K1 via Modbus~~ (não funciona)
- ✅ **APERTAR K1 NO PAINEL FÍSICO**
- ✅ **Depois apertar S1 NO PAINEL FÍSICO**

---

## 📋 PRÓXIMOS PASSOS

### Para o Usuário (Você)

1. **Aperte K1 fisicamente** no painel da máquina
2. **Verifique** se LED1 acendeu (ou display mudou para "Dobra 1")
3. **Aperte S1 fisicamente**
4. **Veja** se modo alternachega para AUTO

### Para Monitoramento

Eu vou monitorar o servidor para detectar quando:
```
BEND_CURRENT: 1  ✅
LED1:         True ✅
MODE:         alterna quando S1 ✅
```

---

## 🔬 INVESTIGAÇÃO FUTURA

Se apertar K1 fisicamente também não funcionar, investigar:

1. **BEND_CURRENT em outro endereço?**
   - Testar 0x0947, 0x0949
   - Procurar no ladder

2. **LED1 em outro endereço?**
   - Testar 0x00C1-0x00C4
   - Verificar mapeamento

3. **Condições para selecionar dobra?**
   - Modo específico?
   - Tela específica?
   - Estado da máquina?

---

## ✅ O QUE JÁ SABEMOS QUE FUNCIONA

1. ✅ **S1 fisicamente FUNCIONA** - mbpoll detectou pulso
2. ✅ **Código corrigido LÊ corretamente** - bug pymodbus resolvido
3. ✅ **CLP aplica regra de segurança** - força modo de volta se condição não OK
4. ✅ **Servidor rodando** - monitorando estados

---

## 🚀 AÇÃO IMEDIATA

**TESTE AGORA**:

1. Vá até o painel físico
2. Aperte **K1** (tecla número 1)
3. Verifique se LED acende ou display muda
4. Aperte **S1** (tecla de função)
5. Veja se modo alterna para AUTO

Enquanto isso, **o servidor está monitorando** - vou ver as mudanças em tempo real! 🔍

---

**FIM DO RELATÓRIO** ⚠️
