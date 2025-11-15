# RESUMO EXECUTIVO - v25 CLP 10 ROTINAS

**Data:** 12 de Novembro de 2025
**Versão Final:** v25 (MD5: f04fb1e8cb9c3e45181cfd13e56031d6)
**Status:** ✅ COMPILA SEM ERROS
**Tempo Total:** 18+ horas, 25 versões

---

## POR QUE 24 VERSÕES FALHARAM

| Fase | Versões | Problema | Sintoma |
|------|---------|----------|---------|
| **1. Estrutura** | v1-v18 | Formato .sup inválido | Arquivo não abria |
| **2. Instruções** | v19-v20 | NOT, ADD, MUL não existem | Erro ao abrir |
| **3. Destinos** | v21-v22 | 0800-0966 não são graváveis | "Registro fora do range" |
| **4. Origens** | v23-v24 | MOV não lê I/O (0100-0107, 0180-0187) | "Registro Origem fora do range" |
| **5. Solução** | v25 | Apenas ângulos (0840-0852) | ✅ FUNCIONA |

---

## POR QUE v25 FUNCIONA

```
✅ Estrutura: Copiada EXATAMENTE de ROT4
✅ Instrução: Apenas MOV (validada em ROT4)
✅ Destinos: Apenas 0942, 0944 (únicos válidos)
✅ Origens: Apenas 0840-0852 (ângulos validados em ROT4)
✅ Python: Lê I/O diretamente via Modbus (0x03)
```

---

## DESCOBERTA CRÍTICA

**MOV no ladder NÃO consegue ler I/O, MAS Python via Modbus CONSEGUE!**

| Registro | MOV (Ladder) | Modbus (Python) |
|----------|--------------|-----------------|
| 0100-0107 (E0-E7) | ❌ | ✅ Function 0x03 |
| 0180-0187 (S0-S7) | ❌ | ✅ Function 0x03 |
| 0840-0852 (ângulos) | ✅ | ✅ Function 0x03 |
| 04D6-04D7 (encoder) | ✅ | ✅ Function 0x03 |

**Solução:** Ladder espelha ângulos, Python lê I/O diretamente.

---

## REGRAS ABSOLUTAS

### Instruções Válidas
```
✅ MOV, MOVK, SETR, OUT, CMP, CNT, RET
❌ NOT, ADD, SUB, MUL, DIV, OR, AND, RSTR
```

### Registros MOV Válidos
**Origens:** 0840, 0842, 0846, 0848, 0850, 0852, 04D6, 05F0
**Destinos:** 0942, 0944
**TUDO MAIS É INVÁLIDO!**

### Estrutura Linha Ladder
```ladder
[LineNNNNN]
  [Features]
    Branchs:01
    Type:0
    Label:0
    Comment:0
    Out:MOV     T:0028 Size:003 E:0840 E:0944
    Height:03          ← SEMPRE 03!
  [Branch01]
    X1position:00
    X2position:13
    Yposition:00
    Height:01
    B1:00
    B2:00
    BInputnumber:00    ← SEMPRE 00 (sem condição)
    {0;00;00F7;-1;-1;-1;-1;00}  ← 00F7 = ALWAYS TRUE
    ###

```

---

## CHECKLIST v26+

### Antes
```
□ Backup de v25
□ Validar registros (consultar REFERENCIA_DEFINITIVA)
□ Se registro não é MOV-acessível, usar Python
```

### Durante
```
□ Copiar estrutura de ROT4 ou v25
□ APENAS origens 0840-0852
□ APENAS destinos 0942, 0944
□ Height:03, BInputnumber:00, {0;00;00F7;...}
□ CRLF endings, ZIP -X
```

### Depois
```
□ Contar linhas: head -1 ROT5.lad
□ Compilar no WinSUP
□ 0 erros = sucesso ✅
□ Documentar MD5
```

---

## COMANDOS ÚTEIS

```bash
# Validar instruções usadas
grep -h "Out:" arquivo.lad | sed 's/Out:\([A-Z]*\).*/\1/' | sort -u

# Listar origens MOV
grep "Out:MOV" arquivo.lad | grep -o "E:[0-9A-F]*" | awk 'NR%2==1' | sort -u

# Listar destinos MOV
grep "Out:MOV" arquivo.lad | grep -o "E:[0-9A-F]*" | awk 'NR%2==0' | sort -u

# Validar line counts
for f in ROT*.lad; do
  header=$(head -1 $f | grep -o '[0-9]*')
  actual=$(grep -c '^\[Line' $f)
  [ "$header" -eq "$actual" ] && echo "$f ✅" || echo "$f ❌"
done

# Criar .sup
zip -q -X arquivo.sup Project.spr Projeto.txt Screen.dbf Screen.smt \
  Perfil.dbf Conf.dbf Conf.smt Conf.nsx Principal.lad Principal.txt \
  Int1.lad Int1.txt Int2.lad Int2.txt ROT*.lad ROT*.txt Pseudo.lad
```

---

## PYTHON MODBUS

```python
# Ler E0-E7 (entradas digitais)
for addr in range(0x0100, 0x0108):
    reg = client.read_holding_registers(addr, 1)
    status = reg.registers[0] & 0x0001  # Bit 0

# Ler S0-S7 (saídas digitais)
for addr in range(0x0180, 0x0188):
    reg = client.read_holding_registers(addr, 1)
    status = reg.registers[0] & 0x0001  # Bit 0

# Ler encoder (32-bit)
msw = client.read_holding_registers(0x04D6, 1).registers[0]
lsw = client.read_holding_registers(0x04D7, 1).registers[0]
encoder = (msw << 16) | lsw

# Ler mirrors
mirror_a = client.read_holding_registers(0x0942, 1).registers[0]
mirror_b = client.read_holding_registers(0x0944, 1).registers[0]

# Simular botão K1
client.write_coil(0x00A0, True)   # ON
time.sleep(0.1)
client.write_coil(0x00A0, False)  # OFF
```

---

## LIÇÕES-CHAVE

1. **NÃO INVENTAR** - Copie de ROT4
2. **VALIDAR TUDO** - Se não está em ROT4, não funciona
3. **SEPARAR CAMADAS** - Ladder faz o mínimo, Python faz o resto
4. **TESTAR INCREMENTAL** - Uma mudança por vez
5. **DOCUMENTAR FALHAS** - Aprender com erros

### Regra de Ouro
> **"Se ROT4 não faz, você provavelmente não deveria fazer no ladder. Faça em Python."**

---

## ARQUIVOS IMPORTANTES

```
CLP_10_ROTINAS_v25_SAFE.sup          ← Arquivo funcional
REFERENCIA_DEFINITIVA_CLP_10_ROTINAS.md  ← Documentação completa (este doc)
USAR_v25_FINAL.txt                    ← Guia de uso
gerar_rot5_9_final.py                 ← Script gerador
```

---

## MÉTRICAS

```
Tempo: 18+ horas
Versões: 25 (24 falharam, 1 sucesso)
Linhas MOV: 71
Registros validados: 10
Registros invalidados: 30+
Taxa de sucesso: 100% (objetivo alcançado)
```

---

**Para detalhes completos, consulte:** `REFERENCIA_DEFINITIVA_CLP_10_ROTINAS.md`

**Versão documento:** 1.0
**Última atualização:** 12/Nov/2025
