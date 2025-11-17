# Resultado do Teste de Gravação - 16/Nov/2025

**CLP**: Atos MPC4004 - Slave ID 1
**Porta**: /dev/ttyUSB0 @ 57600 bps, 8N2
**Status**: ✅ CONEXÃO OK

---

## ✅ Testes Bem-Sucedidos

### 1. Leitura de Encoder
```
Registro 1238/1239 (0x04D6/0x04D7)
MSW: 0
LSW: 119
Valor: 11.9°
```
**Status**: ✅ Funcionando perfeitamente

### 2. Leitura de Área de Supervisão
```
Registro 2380 (velocidade): 10 rpm
Registro 2368 (tela): 0
```
**Status**: ✅ Funcionando, dados consistentes

### 3. Leitura de I/O Digital (Coils)
```
Entradas E0-E7: E0=1, demais=0
Saídas S0-S7: Todas=0
LEDs 1-5: Todos=0
```
**Status**: ✅ Funcionando corretamente

### 4. Escrita de Coils (Botões)
```
K1 (160): ✅ Written 1 references
K7 (166): ✅ Written 1 references
```
**Status**: ✅ Comandos aceitos pelo CLP

---

## ⚠️ Testes com Comportamento Inesperado

### 1. Gravação de Ângulos de Dobra

**Mapeamento utilizado**:
- Dobra 1: LSW=2112, MSW=2114
- Dobra 2: LSW=2118, MSW=2120
- Dobra 3: LSW=2128, MSW=2130

**Valores gravados vs lidos**:

| Dobra | Graus | Valor CLP | LSW Gravado | LSW Lido | Diferença |
|-------|-------|-----------|-------------|----------|-----------|
| 1     | 90°   | 900       | 900         | 921      | +21       |
| 2     | 120°  | 1200      | 1200        | 1024     | -176      |
| 3     | 45°   | 450       | 450         | 256      | -194      |

**Análise**:
- ❌ Valores não são mantidos exatamente como gravados
- Os valores lidos são **próximos** mas não idênticos
- Possíveis causas:
  1. O ladder está processando/convertendo os valores
  2. Os registros podem ser intermediários (não setpoints finais)
  3. Há lógica de correção automática
  4. Encoder se movendo após gravação

**Valores de MSW**:
- Todos mantiveram MSW=0 corretamente ✅

### 2. Mudança de Velocidade (K1+K7)

**Teste realizado**:
```
1. Velocidade inicial: 10 rpm
2. Pressionado K1+K7 simultaneamente (150ms)
3. Velocidade após: 10 rpm (sem mudança)
```

**Análise**:
- ❌ Velocidade não mudou
- Possíveis causas:
  1. Máquina não está em MODO MANUAL (requisito)
  2. Máquina não está PARADA
  3. LEDs todos apagados sugerem estado não-operacional
  4. Pode haver condições adicionais no ladder

---

## 📊 Dump Completo de Registros Testados

### Ângulos (região 2112-2131)
```
[2112]: 921      ← LSW Dobra 1
[2113]: 32768
[2114]: 0        ← MSW Dobra 1 ✅
[2115]: 12288
[2116]: 4096
[2117]: 12288
[2118]: 1024     ← LSW Dobra 2
[2119]: 4096
[2120]: 0        ← MSW Dobra 2 ✅
[2121]: 4096
[2122]: 12288
[2123]: 12288
[2124]: 12288
[2125]: 8192
[2126]: 12288
[2127]: 12288
[2128]: 256      ← LSW Dobra 3
[2129]: 4096
[2130]: 0        ← MSW Dobra 3 ✅
```

**Padrões observados**:
- Valores 4096 (0x1000), 8192 (0x2000), 12288 (0x3000) aparecem frequentemente
- Sugerem flags ou máscaras de bits
- MSW todos gravados como 0 foram mantidos

### Área de Supervisão (2368-2382)
```
[2368]: 0        ← Tela atual
[2374]: 32768    ← Modo (?)
[2376]: 12288    ← Dobra atual (?)
[2380]: 10       ← Velocidade (RPM) ✅
[2382]: ?        ← Ciclo ativo (não testado)
```

---

## 🎯 Recomendações

### Para Gravação de Ângulos
1. **Investigar registros alternativos**: Os endereços 2112/2114 podem não ser setpoints finais
2. **Testar display físico**: Verificar se os valores aparecem na IHM original
3. **Ler ladder completo**: Analisar linha por linha onde os ângulos são usados
4. **Testar com WinSUP**: Comparar com software oficial Atos

### Para Mudança de Velocidade
1. **Forçar MODO MANUAL**: Garantir que a máquina está no modo correto
2. **Verificar condições**: Pode haver intertravamentos de segurança
3. **Testar fisicamente**: Pressionar K1+K7 no painel físico para confirmar lógica
4. **Ler estados de modo**: Mapear coils/registros que indicam MANUAL/AUTO

### Para Leitura Contínua
1. **Polling a 250ms**: Implementar loop no servidor Python
2. **Foco em registros confiáveis**:
   - ✅ Encoder (1238/1239)
   - ✅ Velocidade (2380)
   - ✅ I/O Digital (256-263, 384-391)
   - ✅ LEDs (192-196)
3. **Monitorar área de supervisão**: Valores parecem mais estáveis

---

## 🔧 Próximos Testes Necessários

1. [ ] Verificar ângulos no display físico da IHM
2. [ ] Pressionar K1, K2, K3 fisicamente e monitorar LEDs
3. [ ] Testar mudança MANUAL/AUTO com S1
4. [ ] Mapear estados de modo (coils ou registers)
5. [ ] Executar dobra física e monitorar encoder em tempo real
6. [ ] Comparar valores com WinSUP (se disponível)
7. [ ] Analisar ladder para encontrar setpoints reais
8. [ ] Testar escrita direta em área de supervisão (2370-2382)

---

## 📋 Comandos Úteis para Referência

### Ler encoder
```bash
mbpoll -a 1 -b 57600 -P none -s 2 -r 1238 -t 4 -c 2 -1 /dev/ttyUSB0
```

### Gravar ângulo Dobra 1 (90°)
```bash
mbpoll -a 1 -b 57600 -P none -s 2 -r 2112 -t 4 -1 /dev/ttyUSB0 900  # LSW
mbpoll -a 1 -b 57600 -P none -s 2 -r 2114 -t 4 -1 /dev/ttyUSB0 0    # MSW
```

### Ler velocidade
```bash
mbpoll -a 1 -b 57600 -P none -s 2 -r 2380 -t 4 -c 1 -1 /dev/ttyUSB0
```

### Mudar velocidade (K1+K7)
```bash
mbpoll -a 1 -b 57600 -P none -s 2 -r 160 -t 0 -1 /dev/ttyUSB0 1
mbpoll -a 1 -b 57600 -P none -s 2 -r 166 -t 0 -1 /dev/ttyUSB0 1
sleep 0.1
mbpoll -a 1 -b 57600 -P none -s 2 -r 160 -t 0 -1 /dev/ttyUSB0 0
mbpoll -a 1 -b 57600 -P none -s 2 -r 166 -t 0 -1 /dev/ttyUSB0 0
```

### Ler LEDs
```bash
mbpoll -a 1 -b 57600 -P none -s 2 -r 192 -t 0 -c 5 -1 /dev/ttyUSB0
```

### Ler I/O completo
```bash
# Entradas
mbpoll -a 1 -b 57600 -P none -s 2 -r 256 -t 0 -c 8 -1 /dev/ttyUSB0
# Saídas
mbpoll -a 1 -b 57600 -P none -s 2 -r 384 -t 0 -c 8 -1 /dev/ttyUSB0
```

---

**Data**: 16/Novembro/2025
**Hora**: ~21:30
**Testado por**: Claude Code
**Revisão**: v1.0
