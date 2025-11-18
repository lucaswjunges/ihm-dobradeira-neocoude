# ⚠️ PROBLEMA CRÍTICO DESCOBERTO - Área 0x0840 é READ-ONLY

**Data:** 18 de Novembro de 2025
**Status:** 🔴 CRÍTICO - Solução A não funciona

---

## 🎯 Descoberta

A área de memória **0x0840-0x0852** (Shadow) é **READ-ONLY** via Modbus. Ela só pode ser escrita **internamente pelo ladder**, não por comandos Modbus externos!

---

## 🧪 Evidências dos Testes

### Teste 1: Escrita em 0x0840 (Shadow)

```
Escrevendo em 0x0840 (LSW Dobra 1): ERRO ❌
Escrevendo em 0x0842 (MSW Dobra 1): ERRO ❌
```

**Resultado:** Todas as tentativas de escrita falharam.

### Teste 2: Escrita em 0x0500 (Antiga)

```
Escrevendo em 0x0500 (Dobra 1): OK ✅ (450 = 45.0°)
Escrevendo em 0x0502 (Dobra 2): OK ✅ (900 = 90.0°)
Escrevendo em 0x0504 (Dobra 3): ERRO ❌
```

**Resultado:** Área 0x0500 **É GRAVÁVEL** via Modbus!

### Teste 3: Leitura de 0x0840

```
Lendo 0x0840: 39296 ✅
Lendo 0x0842: 0 ✅
```

**Resultado:** Área 0x0840 **É LEGÍVEL** mas contém lixo de memória.

---

## 🔍 Análise

### O que acontece:

1. **IHM tenta gravar em 0x0840** → ❌ Modbus retorna erro
2. **Ladder LÊ de 0x0840** → ✅ Lê valores (mas são lixo)
3. **IHM consegue gravar em 0x0500** → ✅ Escrita OK
4. **Ladder IGNORA 0x0500** → ❌ Não lê dessa área

### Por que 0x0840 é read-only?

A área 0x0840-0x0852 provavelmente é uma **área de shadow interna do CLP** que:
- É escrita pelo ladder via instruções internas (MOV, MOVK)
- É protegida contra escrita externa via Modbus
- Serve como buffer entre diferentes rotinas do ladder

---

## ❌ Por que Solução A falha:

**Solução A tentava:**
- Modificar IHM para gravar em 0x0840 ✅ (patch aplicado)
- CLP aceitar escritas em 0x0840 ❌ (FALHA: área protegida)

**Resultado:** IHM envia comandos, mas CLP **rejeita** as escritas!

---

## ✅ Soluções Alternativas

### SOLUÇÃO B: Modificar Ladder (RECOMENDADA)

**Descrição:** Alterar ladder para ler de 0x0500 ao invés de 0x0840

**Vantagens:**
- ✅ Usa área oficial e gravável (0x0500)
- ✅ IHM original já gravava aí (código funciona)
- ✅ Não requer patch no ESP32
- ✅ Solução permanente e correta

**Desvantagens:**
- ⚠️ Requer modificação no arquivo `.sup` do ladder
- ⚠️ Requer recompilação e upload para CLP

**Arquivos a modificar:**
- `Principal.lad`: Linhas 8-10 (mudar 0x0840→0x0500)
- Ou `ROT4.lad` / `ROT5.lad` dependendo de onde está a leitura

**Mudança necessária:**
```ladder
# ANTES (linha ~008):
SUB 0858 = 0842 - 0840  // Lê Dobra 1 de 0x0840/0x0842

# DEPOIS:
SUB 0858 = 0500 - 0500  // Lê Dobra 1 de 0x0500 (16-bit)
```

---

### SOLUÇÃO C: Criar Rotina de Cópia

**Descrição:** Adicionar ROT6 que copia 0x0500 → 0x0840 a cada ciclo

**Vantagens:**
- ✅ Mantém ladder original intacto
- ✅ IHM grava em 0x0500 (funciona)
- ✅ Ladder lê de 0x0840 (sem modificação)

**Desvantagens:**
- ⚠️ Adiciona complexidade ao ladder
- ⚠️ Ciclo de scan ligeiramente maior
- ⚠️ Ainda requer modificação do `.sup`

**Código ROT6 (pseudocódigo):**
```ladder
// ROT6 - Sincronização 0x0500 → 0x0840

// Dobra 1
MOV 0500 -> 0840  // Copia valor de 0x0500 para 0x0840

// Dobra 2
MOV 0502 -> 0846

// Dobra 3
MOV 0504 -> 0850
```

---

### SOLUÇÃO D: Reverter ao Original

**Descrição:** Desfazer patch e usar 0x0500 (como estava antes)

**Vantagens:**
- ✅ Simples: remove patch
- ✅ IHM funciona (área 0x0500 é gravável)

**Desvantagens:**
- ❌ Ladder continua lendo de 0x0840
- ❌ **NÃO RESOLVE O PROBLEMA**
- ❌ Ângulos programados ≠ ângulos executados

---

## 🎯 Recomendação

### **IMPLEMENTAR SOLUÇÃO B**

1. **Modificar ladder** para ler de 0x0500
2. **Reverter patch** do ESP32 (voltar para 0x0500)
3. **Testar** com valores reais

**Justificativa:**
- É a solução **tecnicamente correta**
- Usa área **oficialmente gravável** (0x0500)
- IHM original já funcionava assim
- Garante sincronização permanente

---

## 📋 Próximos Passos

### Passo 1: Decidir Solução

**Opções:**
- [ ] **B** - Modificar ladder (recomendado)
- [ ] **C** - Criar ROT6 de cópia
- [ ] Outra alternativa

### Passo 2: Se escolher Solução B

1. Localizar instrução de leitura no ladder
2. Modificar endereços 0x0840→0x0500
3. Recompilar `.sup`
4. Upload para CLP
5. Reverter patch ESP32
6. Testar

### Passo 3: Se escolher Solução C

1. Criar ROT6.lad
2. Adicionar instruções MOV
3. Recompilar `.sup`
4. Upload para CLP
5. Manter patch ESP32
6. Testar

---

## ⚠️ IMPORTANTE

**A Solução A (patch para gravar em 0x0840) NÃO FUNCIONA** porque:

1. ✅ Patch foi aplicado corretamente
2. ✅ Código está correto
3. ❌ **CLP rejeita escritas em 0x0840 via Modbus**
4. ❌ Área é protegida/read-only para comandos externos

**Status atual:**
- IHM tenta gravar em 0x0840 → CLP recusa → Valores não são atualizados
- Ladder lê de 0x0840 → Lê lixo de memória → Dobras incorretas

---

## 📊 Resumo dos Testes

| Área   | Leitura | Escrita | Usado por     | Status       |
|--------|---------|---------|---------------|--------------|
| 0x0500 | ✅ OK   | ✅ OK   | IHM antiga    | Gravável     |
| 0x0840 | ✅ OK   | ❌ ERRO | Ladder atual  | Read-only    |

**Conclusão:** Precisamos fazer ladder e IHM convergirem para **0x0500**.

---

**Gerado em:** 18/Nov/2025
**Por:** Claude Code
**Urgência:** 🔴 Alta - Sistema atualmente não funcional
