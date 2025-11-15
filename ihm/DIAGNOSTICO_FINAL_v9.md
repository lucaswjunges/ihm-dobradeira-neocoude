═══════════════════════════════════════════════════════════════
 DIAGNÓSTICO FINAL - CAUSA RAIZ DOS ERROS
 Data: 12/11/2025 17:26
 Arquivo: CLP_APR03_COMPLETO_v9.sup
═══════════════════════════════════════════════════════════════

## DESCOBERTA CRÍTICA

Após análise profunda dos arquivos, descobri a VERDADEIRA causa dos erros:

❌ **INCOMPATIBILIDADE DE ESTRUTURA**

O arquivo v8 híbrido tinha:
- Metadados (.dbf) do apr03 (configurado para 6 rotinas)
- Arquivos .lad com 11 rotinas (ROT0-ROT10)

**Resultado**: O WinSUP interpretava incorretamente as instruções porque
os metadados não tinham mapeamento para ROT6-ROT10!

═══════════════════════════════════════════════════════════════

## COMPARAÇÃO DE ARQUIVOS

### apr03_v2_COM_ROT5_CORRIGIDO.sup (ARQUIVO FUNCIONAL)
```
ROT0.lad - Lógica original
ROT1.lad - Lógica original
ROT2.lad - Lógica original
ROT3.lad - Lógica original
ROT4.lad - Lógica original
ROT5.lad - 12 linhas (lógica completa com Modbus)
```
**Total**: 6 rotinas

### CLP_HIBRIDO_v8.sup (COM ERROS)
```
ROT0.lad - Do apr03
ROT1.lad - Do apr03
ROT2.lad - Do apr03
ROT3.lad - Do apr03
ROT4.lad - Do apr03
ROT5.lad - 8 linhas (simplificada - INCOMPATÍVEL!)
ROT6.lad - Lógica original
ROT7.lad - Corrigida
ROT8.lad - Corrigida
ROT9.lad - Lógica original
ROT10.lad - 4 linhas mínimas (SEM MAPEAMENTO!)
```
**Total**: 11 rotinas

### ROT5: INCOMPATIBILIDADE DETECTADA

**apr03 ROT5** (12 linhas):
```
Linha 1:  MOVK - Preset timer startup 120s
Linha 2:  TMR - Timer startup
Linha 3:  RESET - Reset Modbus antes timer
Linha 4:  SETR - Ativa Modbus após 120s
Linha 5:  SETR - Detecção pulso MB_S1_CMD
Linha 6:  SETR - Mudança forçada modo AUTO
Linha 7:  SETR - Mudança forçada modo MANUAL
Linha 8:  SETR - Emulação botão AVANÇAR
Linha 9:  SETR - Emulação botão RECUAR
Linha 10: SETR - Emulação botão PARADA
Linha 11: RESET - Reset comandos Modbus
Linha 12: SETR - Status interface Modbus OK
```

**v8 ROT5** (8 linhas - ERRADO!):
```
Linha 1: SETR E:00A0
Linha 2: SETR E:00DC
Linha 3: SETR E:0025
Linha 4: SETR E:03F1
Linha 5: SETR E:03F2
Linha 6: SETR E:03F3
Linha 7: SDAT2 E:0300 ← ERRO AQUI (metadados esperam linha 12!)
Linha 8: SETR E:03FF
```

**Motivo do erro**: Metadados mapeiam linha 7 como SETR, não SDAT2!

═══════════════════════════════════════════════════════════════

## SOLUÇÃO: v9 APR03 COMPLETO

### CLP_APR03_COMPLETO_v9.sup
```
✅ ROT0-ROT5: TODOS do apr03 (metadados batem!)
✅ ROT6: Do clp_pronto original
✅ Metadados: Do apr03 (compatíveis com estrutura)
❌ ROT7-ROT10: REMOVIDAS (não existem no apr03)
```

**Por que v9 deve funcionar:**

1. **Metadados compatíveis**: .dbf do apr03 está mapeado para ROT0-ROT5
2. **ROT5 correta**: 12 linhas com lógica completa Modbus
3. **Sem conflitos**: Apenas rotinas que existem nos metadados
4. **Estrutura validada**: apr03_v2_COM_ROT5_CORRIGIDO.sup era funcional

═══════════════════════════════════════════════════════════════

## TESTE v9

Abra no WinSUP 2: `CLP_APR03_COMPLETO_v9.sup`

**Resultado esperado:**
✅ **0 ERROS** - Metadados e .lad 100% compatíveis

Se ainda houver erros:
⚠️ Problema está na ROT6 (única rotina não do apr03)
⚠️ Pode ser necessário remover ROT6 também

═══════════════════════════════════════════════════════════════

## O QUE APRENDI

### Erro fundamental v1-v8:
Tentei "corrigir" arquivos sem entender que:
- **.dbf contém MAPEAMENTO de rotinas**
- **Cada rotina tem ASSINATURA específica**
- **Misturar .lad de fontes diferentes = incompatibilidade**

### Analogia:
É como tentar usar:
- Índice de um livro A
- Páginas de um livro B
- Resultado: Índice aponta para páginas erradas!

### Solução correta:
**USAR ARQUIVO COMPLETO de uma fonte consistente**
Não tentar híbridos entre arquivos de origens diferentes!

═══════════════════════════════════════════════════════════════

## SE v9 FUNCIONAR

Próximo passo:
1. Testar no CLP
2. Se funcionar, ESTE É O ARQUIVO BASE
3. Adicionar funcionalidade GRADUALMENTE
4. Sempre compilar após cada mudança
5. Não adicionar ROT7-ROT10 (não estão nos metadados!)

═══════════════════════════════════════════════════════════════

## SE v9 AINDA FALHAR

Então o problema NÃO é na estrutura dos arquivos.
Possíveis causas restantes:

1. **Versão WinSUP incompatível**
   - Reinstalar WinSUP 2
   - Verificar versão compatível com MPC4004

2. **Cache corrompido do WinSUP**
   - Limpar cache temporário
   - Reabrir projeto

3. **Criar manualmente do zero**
   - Usar procedimento em PROCEDIMENTO_CRIACAO_MANUAL.md
   - Copiar lógica linha por linha via interface WinSUP

═══════════════════════════════════════════════════════════════

## RESUMO EXECUTIVO

**Problema**: Metadados incompatíveis com estrutura de rotinas

**Causa**: Mistura de .lad de diferentes origens (apr03 + clp_pronto)

**Solução v9**: Usar ROT0-ROT5 do apr03 + ROT6 do clp_pronto

**Expectativa**: 0 erros (estrutura compatível)

**Tempo gasto**: 8 iterações até descobrir causa raiz

**Lição**: Metadados (.dbf) devem bater com estrutura exata das rotinas!

═══════════════════════════════════════════════════════════════

**Arquivo gerado**: CLP_APR03_COMPLETO_v9.sup (30KB)
**Data**: 12/11/2025 17:26
**Status**: PRONTO PARA TESTE
