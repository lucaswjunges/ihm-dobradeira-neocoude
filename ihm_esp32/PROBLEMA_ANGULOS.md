# ⚠️ PROBLEMA: Ângulos e Velocidade Não Estão Sendo Salvos

## 🔍 DIAGNÓSTICO

### O que NÃO está funcionando:
- ✗ Escrever ângulos no CLP
- ✗ Ler ângulos do CLP
- ✗ Valores não persistem ao recarregar a página

### Causa Raiz:
**Os registros configurados no código NÃO EXISTEM no ladder atual do CLP:**

| Endereço | Função | Status |
|----------|--------|--------|
| 0x0A00 (2560) | Escrita de ângulos | ❌ TIMEOUT |
| 0x0B00 (2816) | Leitura de ângulos (SCADA) | ❌ TIMEOUT |
| 0x0840 (2112) | Leitura de ângulos (SHADOW) | ❌ ERRO |
| 0x094C (2380) | Velocidade | ❌ ERRO |

---

## 📋 PRÓXIMAS AÇÕES NECESSÁRIAS

### Opção 1: Identificar Endereços Corretos no Ladder Atual

Precisamos descobrir **onde no seu CLP** os ângulos e velocidade estão armazenados.

**Teste manual:**
```bash
# Testar faixa de registros conhecida
mbpoll -a 1 -b 57600 -P none -s 1 -t 3 -r 1280 -c 10 /dev/ttyUSB0

# Testar área 0x0500 (mencionada em alguns logs)
mbpoll -a 1 -b 57600 -P none -s 1 -t 3 -r 1280 -c 6 /dev/ttyUSB0
```

### Opção 2: Usar Área Temporária na RAM

Se o CLP não tem área específica para ângulos, podemos:
1. Armazenar ângulos na **memória do servidor** (RPi3)
2. Enviar ângulos para CLP apenas **no momento da dobra**
3. Ler ângulos do CLP **se existirem** ou usar valores salvos no RPi

**Vantagens:**
- ✅ Funciona com qualquer ladder
- ✅ Valores persistem entre sessões (salvar em arquivo JSON)
- ✅ Não depende de endereços específicos do CLP

**Desvantagens:**
- ⚠️ Servidor e CLP podem ficar dessincronizados
- ⚠️ Não reflete alterações feitas pelo painel físico

### Opção 3: Atualizar Ladder com ROT5

Se você tem acesso ao ladder (arquivo `.sup`), podemos:
1. Adicionar rotina ROT5 conforme documentação
2. Configurar área 0x0A00 para escrita
3. Configurar área 0x0B00 para leitura

---

## 🚀 SOLUÇÃO IMEDIATA (Opção 2)

Enquanto você identifica os endereços corretos, vou implementar **armazenamento local** no servidor:

### Mudanças:
1. **Servidor salva ângulos em JSON** no RPi3
2. **Interface lê/escreve do servidor** (não do CLP diretamente)
3. **Servidor sincroniza com CLP** quando possível

### Arquivos modificados:
- `main_server_threaded.py` - Adicionar persistência local
- `machine_state.json` - Novo arquivo para salvar estado

---

## 📊 TESTE RÁPIDO

Para descobrir quais registros FUNCIONAM no seu CLP:

```bash
# Testar área 0x0500-0x0510 (mencionada em alguns logs)
cd /home/lucas-junges/Documents/wco/ihm_esp32
mbpoll -a 1 -b 57600 -P none -s 1 -t 3 -r 1280 -c 16 /dev/ttyUSB0
```

Se **algum registro** retornar valores (não timeout), me informe o endereço e vou configurar o código para usar.

---

## ❓ QUAL OPÇÃO VOCÊ PREFERE?

1. **Opção 1:** Identificar endereços corretos no ladder atual (preciso do arquivo `.sup`)
2. **Opção 2:** Armazenamento local no servidor (funciona agora)
3. **Opção 3:** Atualizar ladder com ROT5 (preciso de acesso ao CLP)

---

**Status Atual:** Interface web funcionando, mas valores não persistem ❌
**Recomendação:** Opção 2 (armazenamento local) enquanto investigamos
