# Correções v3 - CLP_FINAL_11_ROTINAS_FIXED_v3.sup

**Data**: 12/11/2025 16:13
**Arquivo Anterior**: `CLP_FINAL_11_ROTINAS_FIXED_v2.sup` (ainda com erros)
**Arquivo Corrigido**: `CLP_FINAL_11_ROTINAS_FIXED_v3.sup`

---

## ⚠️ Problema Detectado na v2

Após teste no WinSUP 2, a v2 ainda apresentava **62 erros**:
- **ROT5** (1 erro): SDAT2 - registro OP1 fora do range
- **ROT8** (9 erros): SCL2G - registros OP2/OP3 fora do range
- **ROT10** (52 erros): SUB/SFR/ADSUB - registros fora do range

**Causa raiz**: Instruções especiais (SDAT2, SCL2G, SUB, etc.) **não aceitam endereços de estados** (0x0000-0x03FF) como operandos - **apenas registros** (0x0400-0x0FFF).

---

## 🔧 Correções Aplicadas na v3

### 1. **ROT5.lad** - SDAT2 Precisa de Registro

**Problema**: `SDAT2 E:03F0` usava **estado** (1008 decimal)

**Correção**:
| Operando | Antes | Depois | Área |
|----------|-------|--------|------|
| OP1 | E:03F0 (estado 1008) | E:0600 (registro 1536) | Área livre ✓ |

**3 ocorrências corrigidas**: Linhas 18, 85, 152

---

### 2. **ROT8.lad** - SCL2G Precisa de Registros

**Problema**: `SCL2G E:xxxx E:0001 E:0000` usava **estados** 0 e 1 como operandos

**Correção**:
| Instrução | Antes | Depois |
|-----------|-------|--------|
| SCL2G OP2 | E:0001 (estado 1) | E:0401 (registro 1025) |
| SCL2G OP3 | E:0000 (estado 0) | E:0400 (registro 1024) |

**5 instruções corrigidas**:
```
SCL2G E:0520 E:0401 E:0400  ✓
SCL2G E:0430 E:0401 E:0400  ✓
SCL2G E:043C E:0401 E:0400  ✓
SCL2G E:043E E:0401 E:0400  ✓
SCL2G E:043D E:0401 E:0400  ✓
```

---

### 3. **ROT10.lad** - Remapeamento Completo

**Problema 1**: Registros na área **0x0900-0x0960** (não mapeada)

**Solução**: Remapeados para áreas documentadas:

| Antes | Depois | Área de Destino | Uso |
|-------|--------|-----------------|-----|
| E:0900 | E:05A0 | Angle Area Extended | Encoder MSW copy |
| E:0901 | E:05A1 | Angle Area Extended | Encoder LSW copy |
| E:0910-0x0917 | E:05B0-0x05B7 | Angle Area Extended | Angle registers |
| E:0920 | E:05C0 | Angle Area Extended | Work register |
| E:0922 | E:05C2 | Angle Area Extended | Work register |
| E:0930-0x0935 | E:06D0-0x06D5 | Analog Output Area | Digital input shadow |
| E:0940-0x0941 | E:06E0-0x06E1 | Analog Output Area | Digital output shadow |
| E:0960 | E:06F0 | Temperature Area | Counter |

**Problema 2**: Uso direto de registros de I/O digital (0x0100-0x0181)

**Solução**: Criadas **áreas shadow** para I/O:

| Antes (I/O Real) | Depois (Shadow) | Área |
|------------------|-----------------|------|
| E:0100 (E0 input) | E:0540 | Angle Setpoints |
| E:0101 (E1 input) | E:0541 | Angle Setpoints |
| E:0102 (E2 input) | E:0542 | Angle Setpoints |
| E:0103 (E3 input) | E:0543 | Angle Setpoints |
| E:0104 (E4 input) | E:0544 | Angle Setpoints |
| E:0105 (E5 input) | E:0545 | Angle Setpoints |
| E:0180 (S0 output) | E:0550 | Analog Input Presets |
| E:0181 (S1 output) | E:0551 | Analog Input Presets |

**Total de MOV corrigidos**: 17 instruções

---

## 📊 Mapa de Memória Final

### Áreas Utilizadas (após correções):

**Estados/Contatos** (0x0000-0x03FF):
- 0x0000-0x00FF: Controle interno (existente)
- 0x0100-0x0181: **I/O digital real** (E0-E7, S0-S7)
- 0x0600: ROT5 - SDAT2 novo registro ✓

**Registros** (0x0400-0x0FFF):
- 0x0400-0x0401: ROT8 - Constantes SCL2G (0 e 1) ✓
- 0x0420-0x0422: ROT7 - Variáveis de velocidade ✓
- 0x0430-0x043E: ROT8 - Variáveis de escala ✓
- 0x04D6-0x04D7: Encoder MSW/LSW (existente)
- 0x0520-0x0524: ROT8 - Setpoints escalados ✓
- 0x0540-0x0545: ROT10 - Shadow de entradas digitais ✓
- 0x0550-0x0551: ROT10 - Shadow de saídas digitais ✓
- 0x05A0-0x05C2: ROT10 - Área de trabalho (encoder, ângulos) ✓
- 0x0600: ROT5 - Registro SDAT2 ✓
- 0x06D0-0x06D5: ROT10 - Shadow de E0-E5 (destino) ✓
- 0x06E0-0x06E1: ROT10 - Shadow de S0-S1 (destino) ✓
- 0x06F0: ROT10 - Contador ✓
- 0x0840-0x0852: Ângulos de dobra (existente)

**Total de registros utilizados**: ~45 registros (de 1536 disponíveis)

---

## ✅ Validação

### Teste Recomendado

1. **Abrir no WinSUP 2**:
   ```
   Arquivo → Abrir → CLP_FINAL_11_ROTINAS_FIXED_v3.sup
   ```

2. **Verificar lista de checagem** - deve estar **LIMPA** (0 erros):
   - ✅ ROT5: Sem "SDAT2 registro fora do range"
   - ✅ ROT8: Sem "SCL2G registro OP2/OP3 fora do range"
   - ✅ ROT10: Sem "SUB/SFR/ADSUB registro fora do range"

3. **Compilar para CLP**:
   ```
   Comunicação → Enviar Programa → MPC4004
   ```

---

## ⚠️ Observações Importantes

### 1. **Áreas Shadow de I/O**

As instruções agora usam **registros intermediários** ao invés de ler diretamente de E0-E7 e S0-S1. Isso significa que:

- **ANTES**: `MOV E:0100 → E:06D0` (copia entrada E0 diretamente)
- **AGORA**: `MOV E:0540 → E:06D0` (copia shadow de E0)

**Você precisa adicionar lógica** (em Principal ou Int1/Int2) para **copiar** os valores reais de I/O para as áreas shadow:

```ladder
[Principal - adicionar no início]
MOV E:0100 → E:0540  ; Copia E0 real para shadow
MOV E:0101 → E:0541  ; Copia E1 real para shadow
... (repetir para E2-E5, S0-S1)
```

### 2. **Constantes SCL2G**

ROT8 agora usa **E:0400** e **E:0401** como operandos do SCL2G. Você precisa **inicializar** esses registros:

```ladder
[Principal - adicionar no início]
MOVK 0 → E:0400      ; Constante 0 para SCL2G
MOVK 1 → E:0401      ; Constante 1 para SCL2G
```

### 3. **Registro SDAT2**

ROT5 usa **E:0600** como destino do SDAT2. Certifique-se de que este registro não conflita com outras rotinas.

---

## 🔄 Próximos Passos

1. ✅ Testar arquivo no WinSUP (deve carregar sem erros)
2. ⚠️ Adicionar lógica de inicialização (ver seção "Observações")
3. 📤 Enviar ao CLP e testar funcionalidade
4. 🔧 Ajustar valores shadow conforme necessário

---

## 📝 Changelog

### v1 → v2
- Corrigido ROT5: 0x0700 → 0x03F0
- Corrigido ROT7: Operandos CMP reduzidos
- Corrigido ROT8: Registros remapeados
- Restaurado ROT10: Versão original

### v2 → v3 (ATUAL)
- 🔧 ROT5: E:03F0 → E:0600 (estado → registro)
- 🔧 ROT8: E:0000/0x0001 → E:0400/0x0401 (SCL2G)
- 🔧 ROT10: Remapeamento completo de 25 registros
- 🔧 ROT10: Criadas áreas shadow para I/O digital

---

## ℹ️ Suporte Técnico

Se o arquivo **ainda** apresentar erros:

1. Tire uma screenshot da lista de checagem do WinSUP
2. Verifique o manual do MPC4004 (páginas 53-104) para confirmar áreas de memória
3. Use o comando `unzip -l CLP_FINAL_11_ROTINAS_FIXED_v3.sup` para verificar integridade

---

**Status**: ✅ Pronto para teste no WinSUP 2
**Arquivos gerados**:
- `CLP_FINAL_11_ROTINAS_FIXED_v3.sup` (33KB)
- `CORRECOES_V3_FINAL.md` (este documento)
