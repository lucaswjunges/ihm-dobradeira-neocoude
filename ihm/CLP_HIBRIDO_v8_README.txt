═══════════════════════════════════════════════════════════════
  CLP_HIBRIDO_v8.sup - SOLUÇÃO HÍBRIDA
  Data: 12/11/2025 17:17
  Tamanho: 32KB
═══════════════════════════════════════════════════════════════

## ABORDAGEM HÍBRIDA

Esta versão combina:

✅ Arquivos .LAD CORRIGIDOS (v6):
   - ROT10: 4 linhas (MOVK + END)
   - ROT5: SDAT2 E:0300
   - ROT0-9: corrigidos

✅ Metadados de ARQUIVO FUNCIONAL:
   - Conf.dbf (14KB)
   - Screen.dbf (41KB)
   - Perfil.dbf (178KB)
   - Conf.smt (4.8KB)
   - Screen.smt (512B)

Origem dos metadados: apr03_v2_COM_ROT5_CORRIGIDO.sup

═══════════════════════════════════════════════════════════════

## POR QUE v8 DEVE FUNCIONAR

PROBLEMA IDENTIFICADO:
- Os .LAD estavam CORRETOS (MOVK)
- O WinSUP interpretava como SFR/ADSUB
- CAUSA: Metadados corrompidos (.dbf/.smt)

SOLUÇÃO:
- Usar metadados de arquivo SEM ERROS
- Manter .LAD corrigidos
- WinSUP agora deve interpretar corretamente

═══════════════════════════════════════════════════════════════

## TESTE v8

Abra no WinSUP 2: CLP_HIBRIDO_v8.sup

Resultado esperado:
✅ 0 ERROS - Metadados corretos interpretam MOVK como MOVK
⚠️ Erros diferentes - Incompatibilidade de metadados
❌ Mesmos 4 erros - Problema mais profundo no WinSUP

═══════════════════════════════════════════════════════════════

## SE v8 FALHAR

Então o problema NÃO é nos arquivos.
O problema É no próprio WinSUP:

1. Versão do WinSUP incompatível
2. Cache interno corrompido
3. Configuração do WinSUP errada

SOLUÇÕES FINAIS:
1. Reinstalar WinSUP 2
2. Limpar cache do WinSUP (pasta temporária)
3. Criar projeto NOVO manualmente no WinSUP

═══════════════════════════════════════════════════════════════

## OBSERVAÇÃO IMPORTANTE

Os metadados (.dbf) contêm TABELAS que mapeiam:
- Endereços de registros
- Códigos de instruções
- Parâmetros de configuração

Se esses arquivos estiverem corrompidos ou incompatíveis,
o WinSUP pode interpretar MOVK (0x29) como SFR (0x??).

v8 usa metadados de arquivo FUNCIONAL testado,
então deve resolver esse problema.

═══════════════════════════════════════════════════════════════
