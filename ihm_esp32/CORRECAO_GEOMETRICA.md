# Correção Geométrica e Compensação de Inércia

**Data:** 06/Jan/2026
**Status:** ✅ IMPLEMENTADO E TESTADO

---

## Problema Identificado

### 1. Zero não era zero absoluto
- **Antes:** Colocar 0° na IHM gravava 0 no CLP, mas ao ler voltava 24.3°
- **Causa:** Compensação de inércia (138) estava sendo aplicada mesmo para zero
- **Solução:** Tratamento especial para zero absoluto (sem compensação)

### 2. Erro geométrico da máquina
- **Descoberta:** Para dobrar vergalhão em 90° REAL, precisa programar 78.9°
- **Relação:** 78.9° programado = 90° real (fator: 78.9/90 = 0.8767)
- **Solução:** Aplicar fator de correção geométrica em todas as conversões

---

## Implementação

### Fórmula de Escrita (IHM → CLP)

```python
def real_angle_to_clp(real_degrees: float) -> int:
    # CASO ESPECIAL: Zero absoluto (sem compensação)
    if real_degrees <= 0:
        return 0

    # PASSO 1: Correção geométrica
    FATOR_GEOMETRICO = 78.9 / 90.0  # = 0.8767
    angulo_interno = real_degrees * FATOR_GEOMETRICO

    # PASSO 2: Converter para escala 2048
    valor_ideal = int((angulo_interno / 360.0) * 2048)

    # PASSO 3: Compensação de inércia (27 pulsos = 138 escala)
    COMPENSACAO_INERCIA = 138
    valor_compensado = valor_ideal - COMPENSACAO_INERCIA

    return max(0, min(valor_compensado, 2048))
```

### Fórmula de Leitura (CLP → IHM)

```python
def clp_to_real_angle(clp_value: int) -> float:
    # CASO ESPECIAL: Zero absoluto
    if clp_value == 0:
        return 0.0

    # PASSO 1: Adicionar compensação de volta
    COMPENSACAO_INERCIA = 138
    valor_real = clp_value + COMPENSACAO_INERCIA

    # PASSO 2: Converter escala 2048 → interno
    angulo_interno = (valor_real / 2048.0) * 360.0

    # PASSO 3: Correção geométrica inversa
    FATOR_GEOMETRICO_INVERSO = 90.0 / 78.9  # = 1.1407
    angulo_usuario = angulo_interno * FATOR_GEOMETRICO_INVERSO

    return angulo_usuario
```

---

## Tabela de Conversão

| IHM (°) | Interno (°) | CLP (decimal) | Volta IHM (°) | Erro (°) |
|---------|-------------|---------------|---------------|----------|
| **0**   | 0.00        | **0**         | **0.00**      | 0.00     |
| 45      | 39.45       | 86            | 44.91         | 0.09     |
| 78.9    | 69.17       | 255           | 78.80         | 0.10     |
| **90**  | **78.90**   | **310**       | **89.83**     | 0.17     |
| 135     | 118.35      | 535           | 134.94        | 0.06     |
| 180     | 157.80      | 759           | 179.86        | 0.14     |

**Precisão:** < 0.2° devido a arredondamentos (aceitável para aplicação industrial)

---

## Validação

### Testes Realizados

```bash
✓ Zero: IHM 0° → CLP 0 → IHM 0.0° ✅
✓ 90°: IHM 90° → CLP 310 → IHM 89.8° ✅
✓ Bidirecionabilidade 45°: erro 0.09° ✅
✓ Bidirecionabilidade 78.9°: erro 0.10° ✅
✓ Bidirecionabilidade 90°: erro 0.17° ✅
✓ Bidirecionabilidade 135°: erro 0.06° ✅
```

### Como Testar na Máquina Real

1. **Teste de Zero:**
   ```
   IHM: Gravar 0° → Verificar CLP em 0x0842 = 0x0000 (0 decimal)
   ```

2. **Teste de 90°:**
   ```
   IHM: Gravar 90° → Verificar CLP em 0x0842 = 0x0136 (310 decimal)
   Máquina: Disco deve dobrar vergalhão em 90° REAL
   ```

3. **Teste de 78.9° (antiga calibração):**
   ```
   IHM: Gravar 78.9° → CLP = 255 decimal
   Máquina: Disco deve dobrar vergalhão em 78.9° REAL
   ```

---

## Fluxo Completo

### Exemplo: Usuário quer dobrar 90°

```
1. Usuário digita: 90° na IHM
2. Correção geométrica: 90° × 0.8767 = 78.9° (interno)
3. Escala 2048: (78.9/360) × 2048 = 448
4. Compensação: 448 - 138 = 310
5. Grava no CLP (0x0842): 310 decimal (0x0136)
6. CLP ladder × 2: 78.9° → disco 157.8°
7. Máquina dobra: vergalhão sai com 90° REAL ✅
```

### Exemplo: Leitura do CLP

```
1. CLP retorna (0x0842): 310 decimal
2. Adiciona compensação: 310 + 138 = 448
3. Converte escala: (448/2048) × 360 = 78.9° (interno)
4. Correção geométrica: 78.9° × 1.1407 = 90° (usuário)
5. IHM mostra: 90° ✅
```

---

## Constantes Importantes

```python
# Correção geométrica (baseada em medição real)
FATOR_GEOMETRICO = 78.9 / 90.0           # = 0.8767 (escrita)
FATOR_GEOMETRICO_INVERSO = 90.0 / 78.9  # = 1.1407 (leitura)

# Compensação de inércia (motor hidráulico)
COMPENSACAO_INERCIA = 138  # 27 pulsos encoder = 24.3° disco = 138 escala

# Escala do CLP
ESCALA_CLP = 2048  # 12 bits (0-2048 = 0-360°)
```

---

## Arquivos Modificados

- ✅ `modbus_map.py` - Funções `real_angle_to_clp()` e `clp_to_real_angle()`
- ✅ Todas as conversões automáticas (escrita/leitura via Modbus)
- ✅ Interface web (mostra ângulos corretos ao usuário)

---

## Notas Importantes

⚠️ **Zero Absoluto:** Sempre tratado especialmente (sem compensação)
⚠️ **CLP Ladder:** Já faz conversão 2:1 (disco gira o dobro) internamente
⚠️ **Precisão:** Erro máximo < 0.2° (aceitável para dobradeira industrial)
⚠️ **Calibração:** Fator 78.9/90 baseado em medição real do chefe

---

**Implementado por:** Claude Code
**Validado por:** Lucas William Junges
**Aprovado por:** Chefe (medição real: 78.9° = 90°)
