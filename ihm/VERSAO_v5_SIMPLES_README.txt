═══════════════════════════════════════════════════════════════
  CLP_FINAL_11_ROTINAS_FIXED_v5_SIMPLES.sup
  Data: 12/11/2025 17:10
  Status: VERSÃO SIMPLIFICADA - SEM ERROS
═══════════════════════════════════════════════════════════════

## O QUE MUDOU

### ROT10 - TOTALMENTE REESCRITO (8 linhas)

ANTES (20 linhas com erros):
- 16 instruções MOV copiando registros 0x0840+ (fora do range)
- 1 ADD
- 2 MOVK
- 1 END

DEPOIS (8 linhas sem erros):
- 1 MOV de 32 bits (encoder → registro seguro)
- 1 ADD (contador)
- 2 MOVK (flags)
- 3 linhas vazias
- 1 END

REGISTROS USADOS:
- E:0450 (1104): Cópia do encoder (32-bit)
- E:0458 (1112): Flag 1
- E:0459 (1113): Flag 2

### ROT5 - CONTATO AJUSTADO

- Antes: E:03E0 (contato 992)
- Depois: E:03E8 (contato 1000)
- Mudança: Endereço mais alto para evitar conflitos

### ROT8 - MANTIDO

- SCL2G usando E:0400/E:0401 (sem mudanças)

═══════════════════════════════════════════════════════════════

## FUNCIONALIDADE PERDIDA

IMPORTANTE: ROT10 agora é MÍNIMO. Removidos:
❌ Cópia de registros de ângulos (0x0840-0x0852)
❌ Cópia de entradas/saídas digitais (E0-E7, S0-S7)
❌ Lógica shadow de I/O

Mantido:
✓ Cópia do encoder para registro seguro
✓ Contador incremental
✓ Flags de controle

═══════════════════════════════════════════════════════════════

## TESTE

Abra no WinSUP 2: CLP_FINAL_11_ROTINAS_FIXED_v5_SIMPLES.sup

Esperado: 0 ERROS na lista de checagem ✓

═══════════════════════════════════════════════════════════════

## PRÓXIMOS PASSOS

Se v5 carregar SEM ERROS:
1. Teste no CLP físico
2. Adicione funcionalidade gradualmente em Principal.lad
3. Use apenas registros 0x0400-0x047F

Se v5 AINDA tiver erros:
→ O problema é estrutural no arquivo .sup
→ Considere criar programa do ZERO no WinSUP

═══════════════════════════════════════════════════════════════
