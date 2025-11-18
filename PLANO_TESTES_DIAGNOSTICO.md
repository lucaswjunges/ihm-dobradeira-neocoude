# 🔬 PLANO DE TESTES - DIAGNÓSTICO WINSUP 2

**Data**: 2025-11-11
**Objetivo**: Identificar EXATAMENTE o que o WinSup 2 não aceita

---

## 📋 ARQUIVOS CRIADOS PARA TESTE

Criei 7 arquivos de teste em ordem de complexidade crescente:

### Série A: Testes Incrementais (ROT4 Expandido)

1. **TESTE_00_BASE_IDENTICA.sup**
   - Idêntico ao TESTE_BASE_SEM_MODIFICACAO.sup
   - ROT4: 21 linhas (original)
   - **Deve abrir**: ✅ SIM (já testado)

2. **TESTE_01_MOV_SIMPLES.sup**
   - ROT4: 22 linhas (21 + 1 nova)
   - Nova linha: MOV simples copiando registro existente
   - Instrução: `MOV E:04D6 → E:05F0`

3. **TESTE_02_MOVK.sup**
   - ROT4: 23 linhas (21 + 2 novas)
   - Nova linha: MOVK (move constante)
   - Instrução: `MOVK E:05F1 ← 0x0005`

4. **TESTE_03_SHADOW_0A01.sup**
   - ROT4: 24 linhas (21 + 3 novas)
   - Nova linha: Testa shadow register
   - Instrução: `MOVK E:0A01 ← 0x0001`
   - **IMPORTANTE**: Testa registro 0A01 (shadow)

5. **TESTE_04_BIT_ALTO_03FF.sup**
   - ROT4: 25 linhas (21 + 4 novas)
   - Nova linha: Testa bit alto
   - Instrução: `SETR E:03FF`
   - **IMPORTANTE**: Testa bit 1023 (último bit disponível)

### Série B: ROT5 Separado

6. **TESTE_COM_ROT5_SEPARADO_V2.sup**
   - ROT4: 21 linhas (não modificado)
   - **ROT5: 1 linha** (NOP - instrução vazia)
   - Project.spr modificado para reconhecer ROT5
   - **IMPORTANTE**: Testa se WinSup 2 aceita 6ª rotina

### Série C: Versão Corrigida Completa

7. **clp_FINAL_COM_ROT5_V3_CORRIGIDO.sup** (já testado - falhou)
   - ROT4: 32 linhas (21 + 11 incluindo separador + 10 ROT5)
   - Sintaxe validada (0 erros)

---

## 🧪 PROTOCOLO DE TESTE

### Passo a Passo

Execute os testes **NA ORDEM** e PARE no primeiro que falhar:

```
1. Abrir WinSup 2
2. Arquivo → Abrir Projeto
3. Selecionar TESTE_00_BASE_IDENTICA.sup
4. Resultado esperado: ✅ Abre

5. Fechar projeto
6. Arquivo → Abrir Projeto
7. Selecionar TESTE_01_MOV_SIMPLES.sup
8. Resultado: ❓

Se TESTE_01 ABRIR:
  → Continuar para TESTE_02
  
Se TESTE_01 FALHAR:
  → PARAR e anotar: "WinSup 2 não aceita NENHUMA modificação em ROT4"
  → Pular para TESTE_COM_ROT5_SEPARADO_V2.sup (teste 6)

Se TESTE_02 ABRIR:
  → Continuar para TESTE_03

Se TESTE_03 FALHAR:
  → PARAR e anotar: "WinSup 2 não aceita registros 0A01 (shadow)"
  → Causa identificada!

Se TESTE_04 FALHAR:
  → PARAR e anotar: "WinSup 2 não aceita bits 03FF (alto)"
  → Causa identificada!

Se todos (01-04) ABRIREM:
  → Problema é quantidade de linhas (32 é muito)
  → OU problema é combinação específica de instruções

Depois testar:
9. TESTE_COM_ROT5_SEPARADO_V2.sup
   Se ABRIR: WinSup 2 aceita ROT5 separado!
   Se FALHAR: WinSup 2 não aceita 6ª rotina
```

---

## 📊 TABELA DE RESULTADOS

Por favor, preencha após cada teste:

| Arquivo | Abriu? | Observações |
|---------|--------|-------------|
| TESTE_00_BASE_IDENTICA | ✅ | Base funcional |
| TESTE_01_MOV_SIMPLES | ❓ | 1 linha adicional |
| TESTE_02_MOVK | ❓ | 2 linhas adicionais |
| TESTE_03_SHADOW_0A01 | ❓ | Testa shadow register |
| TESTE_04_BIT_ALTO_03FF | ❓ | Testa bit alto |
| TESTE_COM_ROT5_SEPARADO_V2 | ❓ | ROT5 como 6ª rotina |
| clp_FINAL_COM_ROT5_V3_CORRIGIDO | ❌ | 32 linhas (já testado) |

---

## 🎯 INTERPRETAÇÃO DOS RESULTADOS

### Cenário 1: TESTE_01 falha
**Causa**: WinSup 2 não aceita modificações em ROT4 existente  
**Solução**: Usar ROT5 separado (TESTE_COM_ROT5_SEPARADO_V2)

### Cenário 2: TESTE_01 OK, TESTE_02 OK, TESTE_03 falha
**Causa**: Registros 0A00-0AFF (shadow) não permitidos  
**Solução**: Usar registros alternativos (05F0-05FF)

### Cenário 3: TESTE_01-02 OK, TESTE_03 OK, TESTE_04 falha
**Causa**: Bits 03E0-03FF (alto) não permitidos  
**Solução**: Usar bits alternativos (02E0-02FF)

### Cenário 4: Todos OK até TESTE_04, mas V3 CORRIGIDO falha
**Causa**: Limite de linhas por rotina (máx ~25 linhas?)  
**Solução**: Dividir funcionalidades entre ROT4 e ROT5 separado

### Cenário 5: TESTE_COM_ROT5_SEPARADO_V2 OK
**Causa**: WinSup 2 aceita ROT5 se for arquivo separado!  
**Solução**: Usar ROT5.lad separado com funcionalidades completas

### Cenário 6: TESTE_COM_ROT5_SEPARADO_V2 falha
**Causa**: WinSup 2 não suporta 6ª rotina (limite hardware/software)  
**Solução**: Usar backend SEM ROT5 (acesso direto aos registros)

---

## 🔧 PRÓXIMOS PASSOS BASEADOS NO RESULTADO

### Se encontrar solução COM ladder modificado:
1. Criar arquivo final otimizado com as restrições descobertas
2. Implementar backend que usa shadow registers (se disponíveis)
3. IHM Web com funcionalidade completa

### Se NÃO for possível modificar ladder:
1. Usar `TESTE_BASE_SEM_MODIFICACAO.sup` (original)
2. Backend acessa registros diretos (sem shadow)
3. IHM Web com funcionalidade essencial
4. Documentação: `SOLUCAO_FINAL_SEM_ROT5.md`

---

## 📁 LOCALIZAÇÃO DOS ARQUIVOS

Todos os arquivos estão em:
```
/home/lucas-junges/Documents/clientes/w&co/
```

Arquivos:
- TESTE_00_BASE_IDENTICA.sup
- TESTE_01_MOV_SIMPLES.sup
- TESTE_02_MOVK.sup
- TESTE_03_SHADOW_0A01.sup
- TESTE_04_BIT_ALTO_03FF.sup
- TESTE_COM_ROT5_SEPARADO_V2.sup
- clp_FINAL_COM_ROT5_V3_CORRIGIDO.sup

---

## 💡 INFORMAÇÃO IMPORTANTE

**Todos os registros usados estão dentro dos limites do MPC4004:**
- Bits 03E0-03FF (992-1023): ✅ Válido
- Registros 0A00-0AFF (2560-2815): ✅ Válido
- Sintaxe ladder: ✅ Corrigida (Out: apenas em Features)

**O problema NÃO é**:
- ❌ Endereços fora do range
- ❌ Sintaxe incorreta (já corrigida na V3)
- ❌ Formato de arquivo (ZIP, CRLF, etc.)

**O problema PODE SER**:
- ⚠️ Limite de linhas por rotina
- ⚠️ Registros específicos não permitidos
- ⚠️ Bits específicos não permitidos
- ⚠️ WinSup 2 não suporta ROT5
- ⚠️ Versão específica do WinSup 2

---

**Por favor, teste na ordem e reporte os resultados!**

Isso nos dirá EXATAMENTE o que fazer a seguir.
