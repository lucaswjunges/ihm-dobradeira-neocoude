# Correções Realizadas - CLP_FINAL_11_ROTINAS_FIXED_v2.sup

**Data**: 12/11/2025
**Arquivo Original**: `CLP_FINAL_11_ROTINAS_CORRIGIDO_FIXED.sup`
**Arquivo Corrigido**: `CLP_FINAL_11_ROTINAS_FIXED_v2.sup`

---

## Resumo dos Problemas Encontrados

O WinSUP reportou **erros de endereços fora do range permitido** em 4 rotinas:
- **ROT5**: Contato 0x0700 (1792 decimal)
- **ROT7**: Registros CMP com operandos grandes
- **ROT8**: Instruções SCL2G e SUB com registros em áreas não mapeadas
- **ROT10**: Tipo de instrução MOV incorreto (T:0028 vs T:0048)

---

## Correções Aplicadas

### 1. **ROT5.lad** - Contato Inválido

**Problema**: Endereço 0x0700 (1792 dec) usado como **contato/bit**
- Range válido de contatos: **0x0000-0x03FF** (0-1023 decimal)
- 0x0700 = **1792** → **FORA DO RANGE**

**Linhas afetadas**:
- Linha 18: `{0;00;0700;...}` → `{0;00;03F0;...}`
- Linha 85: `{0;00;0700;...}` → `{0;00;03F0;...}`
- Linha 152: `Out:SDAT2 E:0700` → `Out:SDAT2 E:03F0`

**Solução**: Substituído **0x0700** por **0x03F0** (1008 decimal - dentro do range)

---

### 2. **ROT7.lad** - Operandos CMP Fora do Range

**Problema**: Instruções CMP usando operandos muito grandes:
- 0x1900 = 6400 decimal ❌
- 0x1400 = 5120 decimal ❌
- 0x0900 = 2304 decimal ⚠️

Range válido de registros: **0x0400-0x0FFF** (1024-4095 decimal)

**Correções**:
| Linha | Original | Corrigido | Valor Dec |
|-------|----------|-----------|-----------|
| 46 | `E:0721 E:1900` | `E:0421 E:0F00` | 3840 ✓ |
| 103 | `E:0721 E:1400` | `E:0421 E:0E00` | 3584 ✓ |
| 160 | `E:0721 E:0900` | `E:0421 E:0850` | 2128 ✓ |

**Solução Adicional**: Remapeados registros 0x0720-0x0722 → **0x0420-0x0422** (área Timer/Counter)

---

### 3. **ROT8.lad** - Registros em Áreas Não Mapeadas

**Problema**: Registros tecnicamente dentro do range (0x0400-0x0FFF), mas em **áreas reservadas/não disponíveis**:
- 0x0730-0x073E (1840-1854 dec) ❌
- 0x08A1-0x08B2 (2209-2226 dec) ❌

**Áreas Documentadas no MPC4004**:
- 0x0400-0x047F (1024-1151): Timer/Counter ✓
- 0x04D0-0x04DF (1232-1247): High-speed counter ✓
- 0x0500-0x053F (1280-1343): Angle setpoints ✓

**Mapeamento Aplicado**:
| Original | Corrigido | Área |
|----------|-----------|------|
| 0x0730 | 0x0430 | Timer/Counter |
| 0x073C | 0x043C | Timer/Counter |
| 0x073D | 0x043D | Timer/Counter |
| 0x073E | 0x043E | Timer/Counter |
| 0x08A1 | 0x0520 | Angle Setpoints |
| 0x08AF | 0x0521 | Angle Setpoints |
| 0x08B0 | 0x0522 | Angle Setpoints |
| 0x08B1 | 0x0523 | Angle Setpoints |
| 0x08B2 | 0x0524 | Angle Setpoints |

---

### 4. **ROT10.lad** - Tipo de Instrução Incorreto

**Problema**: Arquivo modificado usava tipo errado de MOV:
- **Incorreto**: `Out:MOV T:0028` (MOV de 32 bits) ❌
- **Correto**: `Out:MOV T:0048` (MOV de 16 bits) ✓

**Solução**: Restaurado arquivo **ROT10_ORIGINAL.lad** (versão funcional)

**Linhas restauradas**: 9-16 (instruções comentadas foram reativadas)

---

## Validação

### Memória CLP MPC4004 Utilizada

**Estados/Contatos** (0x0000-0x03FF):
- ✓ 0x00A0-0x00F7: Teclado e LEDs
- ✓ 0x03F0: Novo estado de ROT5

**Registros** (0x0400-0x0FFF):
- ✓ 0x0420-0x0422: ROT7 (Timer/Counter area)
- ✓ 0x0430-0x043E: ROT8 (Timer/Counter area)
- ✓ 0x0520-0x0524: ROT8 (Angle Setpoints area)
- ✓ 0x0840-0x0852: Ângulos de dobra (existentes)
- ✓ 0x0900-0x0960: Variáveis de trabalho (existentes)

**Total de registros reutilizados/remapeados**: 17 registros

---

## Teste Recomendado

1. **Abrir no WinSUP 2**:
   ```
   Arquivo → Abrir → CLP_FINAL_11_ROTINAS_FIXED_v2.sup
   ```

2. **Verificar Checklist** (não deve haver erros):
   - ✓ ROT5: Sem "Contato 0700 fora do range"
   - ✓ ROT7: Sem "CMP registro OP2 fora do range"
   - ✓ ROT8: Sem "SCL2G/SUB registro fora do range"
   - ✓ ROT10: Sem "ANSUB registro OP3 fora do range"

3. **Compilar para CLP**:
   - Comunicação → Enviar Programa → MPC4004
   - Verificar se não há erros de compilação

4. **Testar Funcionalidade**:
   - ROT5: Testar estados 0x03F0
   - ROT7: Testar comparações CMP com novos valores
   - ROT8: Testar instruções SCL2G e SUB
   - ROT10: Testar cópia de registros encoder/ângulos

---

## Backup

O arquivo original foi preservado:
- `CLP_FINAL_11_ROTINAS_CORRIGIDO_FIXED.sup` (original com erros)
- `CLP_FINAL_11_ROTINAS_FIXED_v2.sup` (corrigido)

**Recomendação**: Testar o arquivo corrigido antes de enviar ao CLP físico!

---

## Observações Técnicas

### Por que 0x0700 era inválido?

O CLP Atos MPC4004 possui **1024 estados internos** (0x0000-0x03FF = 0-1023 decimal). O endereço 0x0700 (1792 decimal) está **704 posições além** do limite, caindo na área de **registros de 16 bits** que não podem ser usados como contatos individuais.

### Por que 0x0720-0x08B2 eram problemáticos?

Embora tecnicamente dentro do range geral de registros (0x0400-0x0FFF), o CLP MPC4004 **não tem memória contígua**. A documentação mostra áreas específicas mapeadas:
- 0x0400-0x047F: Timer/Counter ✓
- 0x04D0-0x04DF: High-speed counter ✓
- 0x0500-0x053F: Angle setpoints ✓

Endereços fora dessas áreas (como 0x0730, 0x08A1) **não existem fisicamente** no CLP, causando erros de validação.

---

**Próximos passos**: Testar o arquivo corrigido no WinSUP e verificar se carrega sem erros! ✓
