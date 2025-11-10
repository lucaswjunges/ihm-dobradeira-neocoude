# 🔌 TESTE DE ENTRADAS DIGITAIS - TIPO N vs TIPO P

## 📋 DIAGNÓSTICO

O PLC **não detectou E0 como ativo** quando conectado a 24VDC.
Isso indica que o CLP provavelmente tem **entradas TIPO N**.

## 🔧 TIPOS DE ENTRADA

### Tipo N (Negativo - mais comum)
```
Fonte 24V:
  [+24V] ────┬──> Terminal COMUM (COM)
             │
             └──> [CARGA/BOTÃO] ──> [E0]
                                     │
  [0V/GND] ───────────────────────────┘
```
**Para ativar**: Conectar E0 ao **0V (GND)**

### Tipo P (Positivo)
```
Fonte 24V:
  [+24V] ────┬──> [CARGA/BOTÃO] ──> [E0]
             │                        │
             │                        │
  [0V/GND] ──┴──> Terminal COMUM (COM)
                                     │
                  ───────────────────┘
```
**Para ativar**: Conectar E0 ao **+24V**

---

## ✅ TESTE TIPO N (Recomendado - testar primeiro)

### Passo 1: Verificar borne do CLP
Procure no borne de entradas:
- Terminal **COM** (comum das entradas E0-E7)
- Terminais **E0**, **E1**, **E2**, etc.

### Passo 2: Conectar comum
```
[+24V da fonte] ──> [Terminal COM]
```

### Passo 3: Testar E0
```
[0V/GND da fonte] ──> [Terminal E0]
```

### Passo 4: Verificar
Execute o script de teste:
```bash
python3 test_e0_direct.py
```

**Resultado esperado**: E0 deve aparecer como **ON (ACTIVE)**

---

## ✅ TESTE TIPO P (Se tipo N não funcionar)

### Passo 1: Conectar comum
```
[0V/GND da fonte] ──> [Terminal COM]
```

### Passo 2: Testar E0
```
[+24V da fonte] ──> [Terminal E0]
```

### Passo 3: Verificar
Execute:
```bash
python3 test_e0_direct.py
```

---

## 🔍 VERIFICAÇÃO VISUAL

Alguns CLPs Atos têm indicadores LED para cada entrada:
- LED aceso = entrada ativa
- LED apagado = entrada inativa

Se seu CLP tem LEDs, verifique se o LED de E0 acende ao conectar.

---

## 📊 IDENTIFICAÇÃO DO MODELO

Verifique a etiqueta do módulo de CPU:
- **4004.09** ou **4004.09E**: Pode ser N ou P (configurável)
- **4004.02**, **4004.06E**, **4004.12**: Tipo P
- Outros modelos: Verificar manual específico

---

## ⚠️ IMPORTANTE

1. **NÃO inverta +24V e 0V** - pode danificar o CLP
2. **Certifique-se** de usar a mesma fonte para COM e para o sinal
3. **Aperte bem** os parafusos dos terminais
4. **Desligue** o comando geral antes de fazer conexões

---

## 🎯 PRÓXIMOS PASSOS

Após E0 funcionar:
1. ✅ Verificar que aparece na IHM web
2. ✅ Testar E1, E2, etc. da mesma forma
3. ✅ Mapear quais entradas correspondem a quais botões físicos
