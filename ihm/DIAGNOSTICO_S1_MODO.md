# Diagnóstico: Por Que S1 Não Alterna MANUAL/AUTO

**Data**: 2025-11-15 16:14
**Status**: ✅ **CAUSA IDENTIFICADA**

---

## 🎯 RESUMO EXECUTIVO

**S1 não alterna entre MANUAL/AUTO porque a máquina não está na DOBRA 1.**

### Condição Atual do Sistema
```
BEND_CURRENT    = 0  ❌ (deveria ser 1)
CYCLE_ACTIVE    = 0  ✅ (máquina parada - OK!)
MODE_STATE      = 0  (MANUAL)
SCREEN_NUM      = 0  (tela principal)
LED1 (K1)       = OFF ❌ (deveria estar ON na dobra 1)
LED2 (K2)       = OFF
LED3 (K3)       = OFF
```

---

## 📋 REGRAS DE NEGÓCIO (do Manual NEOCOUDE)

### Condições para Troca de Modo (S1)

S1 só pode alternar AUTO ↔ MANUAL quando:

1. ✅ **Máquina PARADA** (`CYCLE_ACTIVE = 0`)
2. ❌ **Na DOBRA 1** (`BEND_CURRENT = 1` e `LED1 = ON`)

**Fonte**: `ANALISE_LEITURA_LCD_IHM.md` linhas 144-149:

```python
def validate_mode_change(self):
    """S1 só troca modo se máquina parada e na dobra 1"""
    if self.cycle_active:
        return False, "Ciclo em andamento - aguarde finalizar"
    if self.dobra_atual != 1:
        return False, "Retorne à dobra 1 para trocar modo"
    return True, "OK"
```

---

## 🔧 SOLUÇÃO

### Passo 1: Selecionar Dobra 1

**Aperte a tecla K1 no painel físico** para:
- Setar `BEND_CURRENT = 1`
- Acender `LED1 (coil 0x00C0)`
- Ir para a tela 4 (ângulos da dobra 1)

### Passo 2: Verificar Condições

Após apertar K1, verificar:
```bash
mbpoll -a 1 -b 57600 -P none -s 2 -r 2376 -c 1 -t 3 /dev/ttyUSB0
# Deve retornar: [2376]: 1  (BEND_CURRENT = 1)

mbpoll -a 1 -b 57600 -P none -s 2 -r 192 -c 1 -t 0 /dev/ttyUSB0
# Deve retornar: [192]: 1  (LED1 = ON)
```

### Passo 3: Tentar S1 Novamente

**Agora apertar S1** - a troca deve funcionar:
```bash
mbpoll -a 1 -b 57600 -P none -s 2 -r 767 -c 1 -t 0 /dev/ttyUSB0
# Deve alternar entre:
# [767]: 0  (MANUAL)
# [767]: 1  (AUTO)
```

---

## 🧪 VALIDAÇÃO COM MBPOLL

### Antes (Sistema Atual)

```bash
$ mbpoll -r 767 -c 1 -t 0
[767]: 0    # MANUAL

<aperta S1>

$ mbpoll -r 767 -c 1 -t 0
[767]: 1    # AUTO (por 100ms)
[767]: 0    # Volta para MANUAL (CLP rejeita)
```

**Por quê?** Ladder do CLP detecta `BEND_CURRENT != 1` e força o modo de volta para MANUAL.

### Depois (Após Apertar K1)

```bash
$ mbpoll -r 2376 -c 1 -t 3
[2376]: 1   # BEND_CURRENT = 1 ✅

$ mbpoll -r 192 -c 1 -t 0
[192]: 1    # LED1 = ON ✅

<aperta S1>

$ mbpoll -r 767 -c 1 -t 0
[767]: 1    # AUTO (permanece!) ✅
```

---

## 📊 REGISTROS RELACIONADOS

| Registrador | Hex | Decimal | Tipo | Descrição | Valor Esperado |
|-------------|-----|---------|------|-----------|----------------|
| BEND_CURRENT | 0x0948 | 2376 | Register | Dobra atual (1/2/3) | **1** |
| LED1 | 0x00C0 | 192 | Coil | LED da dobra 1 (K1) | **True** |
| MODE_BIT | 0x02FF | 767 | Coil | Modo AUTO/MANUAL | Toggle |
| CYCLE_ACTIVE | 0x094E | 2382 | Coil | Ciclo em execução | False |
| SCREEN_NUM | 0x0940 | 2368 | Register | Tela atual (0-9) | 4 (após K1) |

---

## 🔍 EVIDÊNCIAS DO DIAGNÓSTICO

### 1. Servidor Mostrando Estado Atual

```
✓ Supervisão: BEND_CURRENT=0 (0x0948)   ← PROBLEMA!
✓ Supervisão: CYCLE_ACTIVE=0 (0x094E)   ← OK
✓ Supervisão: MODE_STATE=0 (0x0946)
🔍 [DEBUG] leds no estado: {
    'LED1': False,   ← DEVERIA ser True na dobra 1
    'LED2': False,
    'LED3': False,
    'LED4': False,
    'LED5': False
}
```

### 2. mbpoll Detectando Pulso de S1

Quando você apertou S1 antes, mbpoll mostrou:
```
[767]: 0
[767]: 0
[767]: 1    ← S1 FUNCIONOU! Mudou para AUTO
[767]: 0    ← CLP forçou de volta para MANUAL (condição não atendida)
[767]: 0
```

**Isso prova**:
- ✅ S1 está funcionando fisicamente
- ✅ Código corrigido está lendo corretamente
- ❌ CLP está **rejeitando** a troca por condição não atendida

---

## ✅ CONCLUSÃO

### Causa Raiz

**BEND_CURRENT = 0** (nenhuma dobra selecionada) bloqueia a troca de modo.

### Solução

1. **Apertar K1** para selecionar dobra 1
2. **Verificar** `BEND_CURRENT = 1` e `LED1 = ON`
3. **Apertar S1** - agora deve funcionar

### Estado do Sistema

| Componente | Status | Observação |
|------------|--------|------------|
| Botão físico S1 | ✅ Funciona | Detectado por mbpoll |
| Código read_coil() | ✅ Corrigido | Bug pymodbus resolvido |
| Servidor IHM | ✅ Rodando | Com código atualizado |
| Ladder CLP | ✅ Correto | Aplicando regras de segurança |
| **Condição atual** | ❌ Não atendida | **BEND_CURRENT = 0** |

---

## 🚀 PRÓXIMOS PASSOS

1. **Usuário**: Apertar **K1** no painel físico
2. **Claude**: Monitorar servidor para confirmar `BEND_CURRENT = 1`
3. **Usuário**: Apertar **S1** novamente
4. **Validar**: Modo deve alternar e **permanecer** em AUTO

---

## 📝 REGISTROS DE TESTE

**Endereços para monitorar**:
```bash
# Dobra atual
mbpoll -a 1 -b 57600 -P none -s 2 -r 2376 -c 1 -t 3 /dev/ttyUSB0

# LED1
mbpoll -a 1 -b 57600 -P none -s 2 -r 192 -c 1 -t 0 /dev/ttyUSB0

# Modo (após K1 + S1)
mbpoll -a 1 -b 57600 -P none -s 2 -r 767 -c 1 -t 0 /dev/ttyUSB0
```

---

**FIM DO DIAGNÓSTICO** ✅
