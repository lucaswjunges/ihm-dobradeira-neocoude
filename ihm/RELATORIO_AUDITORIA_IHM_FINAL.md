# 🚨 RELATÓRIO AUDITORIA FINAL - IHM WEB vs LADDER
**Data:** 15/Nov/2025 02:15
**Auditor:** Engenheiro Automação Sênior
**Status:** ❌ PROBLEMAS CRÍTICOS IDENTIFICADOS

---

## SUMÁRIO EXECUTIVO

Cliente solicitou **auditoria rigorosa** para confirmar se IHM web estava usando endereços oficiais do ladder.

**SUA SUSPEITA ESTAVA 100% CORRETA!**

### Problemas Encontrados:
1. ✅ **[CORRIGIDO]** IHM gravava em endereços ERRADOS
2. ❌ **[BLOQUEIO ATIVO]** Ladder sobrescreve registros de ângulos
3. ❌ **[BLOQUEIO ATIVO]** Controle de motor bloqueado (ver DIAGNOSTICO_FINAL_MOTOR.md)

---

## PROBLEMA 1: ENDEREÇOS INCORRETOS ✅ CORRIGIDO

### Teste: `test_ladder_reads_our_angles.py`

**Endereços que IHM Web ESTAVA usando (ERRADO):**
- Dobra 1: 0x0848/0x084A
- Dobra 2: 0x084C/0x084E  
- Dobra 3: 0x0854/0x0856

**Endereços que LADDER lê (CORRETO):**
- Dobra 1: 0x0840/0x0842 (Line00008: SUB 0858 = 0842 - 0840)
- Dobra 2: 0x0846/0x0848 (Line00009: SUB 0858 = 0848 - 0846)
- Dobra 3: 0x0850/0x0852 (Line00010: SUB 0858 = 0852 - 0850)

**CORREÇÃO APLICADA:** `modbus_map.py` atualizado para usar endereços oficiais.

---

## PROBLEMA 2: LADDER SOBRESCREVE VALORES ❌ ATIVO

### Teste: `test_official_addresses_final.py`

**O que acontece:**
```
1. IHM web escreve: 90.0°, 120.0°, 35.0° nos endereços OFICIAIS
2. Aguarda 2 segundos
3. Lê de volta: 3929.6°, 3929.6°, 3929.6° (TODOS iguais!)
```

**Ladder força valor 39296 (0x9980) em TODOS os registros!**

**Conclusão:** Registros 0x0840-0x0852 são **CALCULADOS pelo ladder** (read-only), não inputs!

---

## SITUAÇÃO REAL SEGUNDA-FEIRA

### ❌ NÃO FUNCIONA:
1. Configuração de ângulos via IHM web → Ignorado pelo ladder
2. Controle de motor (AVANÇAR/RECUAR) → Bloqueado por SETR no ladder

### ✅ FUNCIONA:
1. Monitoramento encoder, estados, LEDs
2. Leitura de tudo
3. Operação via painel físico

---

## PRÓXIMAS AÇÕES

### OPÇÃO A: Encontrar Registros Corretos (PRIORITÁRIO)

IHM física original DEVE gravar em **outra área**. Candidatos:
- **NVRAM (0x0500-0x053F):** Ângulos iniciais/finais
- **Supervisão (0x0940-0x0960):** Área Python

### OPÇÃO B: Modificar Ladder (Segunda na Fábrica)

Com WinSUP:
1. Identificar de ONDE ladder lê ângulos setpoint
2. Remover sobrescrita de 0x0840-0x0852
3. Adicionar lógica de cópia de inputs Modbus

---

## RECOMENDAÇÃO FINAL

**Segunda-feira:**
1. Chegar com 2 planos:
   - Plano A: IHM híbrida (monitoramento + painel físico)
   - Plano B: Modificar ladder com WinSUP
   
2. **NÃO prometer** controle 100% até resolver

**Arquivos críticos:**
- `DIAGNOSTICO_FINAL_MOTOR.md` - Problema motor
- `test_ladder_reads_our_angles.py` - Problema endereços
- `test_official_addresses_final.py` - Problema sobrescrita

**Data:** 15/Nov/2025 02:15
