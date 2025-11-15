# Análise: IHM Física Desabilitada no WinSUP2

**Data**: 2025-11-15 16:22
**Status**: 🔍 **INVESTIGAÇÃO CRÍTICA**

---

## ⚠️ INFORMAÇÃO CRÍTICA DO USUÁRIO

> "A IHM física está desativada na configuração de hardware no WinSUP2. Não sei nem por que o visor LCD ainda mostra algo."

### Implicações

Se a IHM física está **desabilitada** no WinSUP2:

1. ❌ **Teclas físicas NÃO funcionam** (K1-K9, S1, S2, ENTER, ESC)
2. ❌ **LEDs físicos NÃO funcionam** (ou são apenas visualização)
3. ⚠️ **LCD mostra dados** mas pode ser **read-only** (apenas visualização)
4. ✅ **Modbus continua funcionando** (comunicação serial independente)

---

## 🔍 POR QUE LCD AINDA MOSTRA ALGO?

### Hipóteses

**A) Modo Visualização (Display-Only)**
   - LCD conectado mas apenas mostra dados
   - CLP atualiza LCD mas ignora teclas
   - Comum em retrofit de IHM

**B) Configuração Parcial**
   - Display habilitado, teclas desabilitadas
   - Separação entre entrada/saída

**C) Hardware vs Software**
   - Hardware fisicamente conectado
   - Software (ladder) ignora entradas
   - Display continua recebendo dados

---

## 🎯 O QUE ISSO SIGNIFICA PARA S1/MODO?

### Cenário Atual

```
IHM Física:     DESABILITADA
Tecla S1:       NÃO FUNCIONA (ignorada pelo CLP)
Tecla K1:       NÃO FUNCIONA (ignorada pelo CLP)
LCD Display:    FUNCIONA (somente leitura?)
```

### Por Que S1 Não Alterna Modo?

**NÃO É porque falta dobra 1!**

**É porque a IHM física está DESABILITADA!**

- CLP ignora coil 0x00DC (S1)
- CLP ignora coil 0x00A0 (K1)
- Ladder não processa essas entradas

---

## 🔧 SOLUÇÕES POSSÍVEIS

### Opção 1: Habilitar IHM no WinSUP2 ⚠️

**Prós**:
- S1, K1 funcionariam
- Teste com painel físico possível

**Contras**:
- Requer reconfigurar hardware
- Pode conflitar com projeto de IHM web
- Pode quebrar configuração atual

### Opção 2: Controlar Modo DIRETAMENTE via Modbus ✅ RECOMENDADO

Se IHM desabilitada, modo AUTO/MANUAL pode ser:

**A) Escrito diretamente no bit**
```python
# Testar escrever direto
client.write_coil(0x02FF, True)  # AUTO
client.write_coil(0x02FF, False) # MANUAL
```

**B) Escrito em registro de configuração**
```python
# Testar registro MODE_STATE
client.write_register(0x0946, 1)  # AUTO
client.write_register(0x0946, 0)  # MANUAL
```

**C) NÃO controlável**
- Modo fixo (sempre MANUAL ou AUTO)
- Definido por outra lógica
- Não relevante para operação

### Opção 3: Modo Não É Necessário? 🤔

**Pergunta crítica**:

**O que a máquina FAZ em AUTO vs MANUAL?**

Se a resposta é "nada diferente quando controlado via Modbus", então:
- ✅ **Ignore o modo completamente**
- ✅ **Controle direto via Modbus**
- ✅ **IHM web substitui toda lógica**

---

## 📊 TESTES REALIZADOS

### 1. Simular S1 via Modbus
```
write_coil(0x00DC, True)  → CLP ignora (IHM desabilitada)
write_coil(0x00DC, False) → CLP ignora
```
**Resultado**: Não funciona ❌

### 2. Simular K1 via Modbus
```
write_coil(0x00A0, True)  → CLP ignora
write_coil(0x00A0, False) → CLP ignora
BEND_CURRENT permanece 0
LED1 permanece OFF
```
**Resultado**: Não funciona ❌

### 3. Escrever Direto em MODE_BIT (NÃO TESTADO)
```
write_coil(0x02FF, True)  → ?
```
**Status**: Precisa testar sem servidor rodando

### 4. Escrever Direto em MODE_STATE (NÃO TESTADO)
```
write_register(0x0946, 1) → ?
```
**Status**: Precisa testar sem servidor rodando

---

## 🚀 PRÓXIMOS PASSOS

### URGENTE: Testar Escrita Direta

1. **Parar servidor**
2. **Testar**: `write_coil(0x02FF, True)`
3. **Ler de volta**: `read_coil(0x02FF)`
4. **Verificar**: Mudou para AUTO?

Se funcionar:
- ✅ **SOLUÇÃO**: IHM web escreve direto em 0x02FF
- ✅ **IGNORA**: S1, K1, dobras, LEDs
- ✅ **CONTROLE TOTAL**: Via Modbus

Se não funcionar:
- **Opção A**: Habilitar IHM no WinSUP2
- **Opção B**: Ignorar modo (pode não ser necessário)
- **Opção C**: Investigar ladder para encontrar registro correto

---

## 🔬 INVESTIGAÇÃO: O Que É "Modo AUTO/MANUAL"?

### Da Documentação NEOCOUDE

**Modo MANUAL**:
- Operador controla com botões AVANÇAR/RECUAR
- Velocidade fixa (5 rpm)
- Parada manual

**Modo AUTO**:
- Sistema executa sequência automaticamente
- Velocidades variáveis (5/10/15 rpm)
- Para em ângulo programado

### Relevância para IHM Web?

**SE** você está controlando **TUDO** via Modbus:
- ✅ Escreve ângulos direto
- ✅ Comanda motor direto (S0/S1)
- ✅ Controla velocidade direto

**ENTÃO**: Modo AUTO/MANUAL pode ser **irrelevante**!

A IHM web **substitui completamente** a lógica AUTO/MANUAL original.

---

## ✅ RECOMENDAÇÃO FINAL

### Teste Imediato

```bash
# Parar servidor
pkill -f main_server.py

# Testar escrita direta
python3 << 'EOF'
from modbus_client import ModbusClientWrapper
client = ModbusClientWrapper(stub_mode=False)

# Tentar escrever AUTO
print("Tentando MODE=AUTO...")
result = client.write_coil(0x02FF, True)
print(f"Write result: {result}")

import time
time.sleep(0.5)

# Ler de volta
mode = client.read_coil(0x02FF)
print(f"Mode agora: {'AUTO' if mode else 'MANUAL'}")
EOF
```

### Se Funcionar

🎉 **SUCESSO!** IHM web controla modo direto

### Se NÃO Funcionar

🤔 **Investigar**:
1. Modo é read-only?
2. Modo não existe de verdade?
3. Ladder bloqueia mudanças?

**Ou simplesmente**:

✅ **IGNORE O MODO** e controle máquina direto via Modbus

---

## 📝 CONCLUSÃO PROVISÓRIA

**Com IHM física desabilitada**:
- ❌ S1 físico nunca vai funcionar
- ❌ K1 físico nunca vai funcionar
- ❌ Regras de "dobra 1" são irrelevantes
- ✅ **Tudo deve ser controlado via Modbus direto**

**Próximo teste crítico**:
Escrever direto em 0x02FF ou 0x0946 para mudar modo, **OU** descobrir que modo não importa para controle via Modbus.

---

**FIM DA ANÁLISE** 🔍
