# Análise: Por que o Byte Baixo está sendo forçado para 0x99?

**Data**: 16/Novembro/2025
**Problema**: Ao escrever valores no registro 0x0840 (2112 - LSW Dobra 1), o byte baixo é sempre forçado para 0x99 (153 decimal)

---

## 🔬 Testes Realizados

### Padrão Identificado

| Valor Gravado | Hex Gravado | Valor Lido | Hex Lido | Byte Baixo |
|---------------|-------------|------------|----------|------------|
| 1234          | 0x04D2      | 1177       | 0x0499   | **0x99**   |
| 1000          | 0x03E8      | 921        | 0x0399   | **0x99**   |
| 2000          | 0x07D0      | 1945       | 0x0799   | **0x99**   |
| 500           | 0x01F4      | 409        | 0x0199   | **0x99**   |
| 100           | 0x0064      | 153        | 0x0099   | **0x99**   |
| 1500          | 0x05DC      | 1433       | 0x0599   | **0x99**   |

**Conclusão**: O byte alto é mantido, mas o byte baixo é **sempre sobrescrito para 0x99 (153)**.

---

## 🧩 Análise do Ladder

### 1. Referências ao Registro 0x0840 (2112)

**Principal.lad - Linha 166**:
```
SUB 0x0858 = 0x0842 - 0x0840
```
- Subtrai LSW (0x0840) do MSW (0x0842)
- Resultado guardado em 0x0858 (2136)
- **Não explica** a sobrescrita do byte baixo

**ROT4.lad - Linha 357**:
```
Condição: Estado 0x0380 (896) = 0 (DESLIGADO)
MOV 0x0840 ← 0x0944 (2372)
```
- Copia de 0x0944 para 0x0840
- **Registro 0x0944 = 153 (0x99)** ✅ FONTE CONFIRMADA
- Mas estado 0x0380 está DESLIGADO, então não deveria executar

**ROT5.lad - Linha 266**:
```
Condição: Estado 0x00FF (255) = 0 (DESLIGADO)
Comment: "Espelho SCADA - Angulos Dobra 1"
MOV 0x0840 ← 0x0B00 (2816)
```
- Copia de área SCADA (0x0B00) para 0x0840
- **Registro 0x0B00 = 22350** (valor diferente)
- Estado 0xFF DESLIGADO, não deveria executar

**ROT5.lad - Linha 171**:
```
MOV 0x0A02 ← 0x0840
```
- Copia DE 0x0840 PARA outro registro
- Não altera 0x0840

---

## 🚨 Problema Identificado

### Hipóteses

#### ✅ **Hipótese 1: Ciclo de Scan do CLP**
Mesmo com estados desligados, o ladder pode estar executando essas linhas em **modo condicional invertido** ou há lógica adicional não visível nos arquivos .lad que força essa escrita a cada scan do CLP.

#### ✅ **Hipótese 2: Área de Shadow/Buffer**
O registro 0x0840 pode ser uma **shadow area** (área espelho) que é constantemente atualizada por outra rotina ou pelo próprio firmware do CLP, impedindo escrita direta.

#### ✅ **Hipótese 3: Proteção de Dados**
O CLP pode estar protegendo esses registros contra escritas externas via Modbus, mantendo valores padrão (0x99) enquanto não há um ciclo de dobra ativo.

#### ❌ **Hipótese 4: Operação de Bits** (DESCARTADA)
Não foi encontrada nenhuma operação AND, OR, XOR que force o byte baixo.

---

## 📊 Valores dos Registros Relacionados

| Endereço | Decimal | Valor Atual | Descrição |
|----------|---------|-------------|-----------|
| 0x0840   | 2112    | 153 (0x99)  | LSW Dobra 1 (forçado) |
| 0x0842   | 2114    | Variável    | MSW Dobra 1 (aceita escrita) |
| 0x0944   | 2372    | **153**     | Fonte em ROT4 (TARGET_LSW) |
| 0x0B00   | 2816    | 22350       | Área SCADA ROT5 |
| 0x0A02   | 2562    | 8738        | Destino de cópia |

**Estado 0x00FF (255)**: 0 (ROT5 desligada)
**Estado 0x0380 (896)**: 0 (ROT4 linha 357 desligada)
**Estado 0x00F7 (247)**: 0 (ROT4 geral desligada)

---

## 🎯 Soluções Propostas

### Solução 1: Usar Área SCADA (0x0B00+)
Se ROT5 puder ser **ativada**, escrever na área SCADA:
- **0x0B00/0x0B02**: Dobra 1 (LSW/MSW)
- **0x0B04/0x0B06**: Dobra 2
- **0x0B08/0x0B0A**: Dobra 3

**Comando para ativar ROT5**:
```bash
mbpoll -a 1 -b 57600 -P none -s 2 -r 255 -t 0 -1 /dev/ttyUSB0 1  # Liga 0x00FF
```

**Teste de escrita**:
```bash
mbpoll -a 1 -b 57600 -P none -s 2 -r 2816 -t 4 -1 /dev/ttyUSB0 900  # LSW = 90.0°
mbpoll -a 1 -b 57600 -P none -s 2 -r 2818 -t 4 -1 /dev/ttyUSB0 0    # MSW
```

### Solução 2: Usar Registros Alternativos
Procurar outros registros que aceitem escrita sem interferência:
- **0x0942/0x0944**: Área de supervisão (TARGET_MSW/LSW)
- **0x0500-0x053F**: Ângulos setpoint (conforme manual MPC4004)

**Teste de escrita em 0x0942**:
```bash
mbpoll -a 1 -b 57600 -P none -s 2 -r 2370 -t 4 -1 /dev/ttyUSB0 900  # LSW
mbpoll -a 1 -b 57600 -P none -s 2 -r 2368 -t 4 -1 /dev/ttyUSB0 0    # MSW
```

### Solução 3: Desabilitar Rotinas que Sobrescrevem
Identificar qual estado ativa a sobrescrita e desligá-lo:
```bash
# Verificar estados ativos
mbpoll -a 1 -b 57600 -P none -s 2 -r 0 -t 0 -c 256 -1 /dev/ttyUSB0 | grep ": 1"
```

### Solução 4: Escrita via Painel Físico
Usar botões da IHM original (K1-K9, EDIT, ENTER) para programar ângulos:
1. Pressionar K1 (vai para tela de Dobra 1)
2. Pressionar EDIT
3. Digitar ângulo com K0-K9
4. Pressionar ENTER

**Vantagem**: Bypass total da proteção Modbus
**Desvantagem**: Requer simulação de sequência de botões complexa

---

## 🔍 Investigações Adicionais Necessárias

1. **Ler estados ativos em tempo real**:
   ```bash
   # Monitorar todos os 1024 estados
   mbpoll -a 1 -b 57600 -P none -s 2 -r 0 -t 0 -c 1024 -1 /dev/ttyUSB0 > estados.txt
   ```

2. **Testar ativação de ROT5**:
   ```bash
   mbpoll -a 1 -b 57600 -P none -s 2 -r 255 -t 0 -1 /dev/ttyUSB0 1
   sleep 1
   mbpoll -a 1 -b 57600 -P none -s 2 -r 2816 -t 4 -1 /dev/ttyUSB0 1234
   sleep 1
   mbpoll -a 1 -b 57600 -P none -s 2 -r 2112 -t 4 -c 1 -1 /dev/ttyUSB0
   ```

3. **Analisar arquivo .SUP original**:
   - Extrair e comparar com programa atual
   - Verificar se houve modificações nas ROTs

4. **Monitorar em tempo real durante dobra física**:
   - Executar dobra na máquina
   - Registrar valores de 0x0840-0x0852 a cada 100ms
   - Identificar quando valores mudam

5. **Testar área 0x0500-0x053F**:
   - Segundo manual MPC4004, esses são setpoints de ângulo
   - Tentar gravar e ler nesses endereços

---

## 📝 Comandos de Teste Úteis

### Ler área completa de ângulos
```bash
mbpoll -a 1 -b 57600 -P none -s 2 -r 2112 -t 4 -c 32 -1 /dev/ttyUSB0
```

### Ler área SCADA
```bash
mbpoll -a 1 -b 57600 -P none -s 2 -r 2816 -t 4 -c 32 -1 /dev/ttyUSB0
```

### Ler estados ROT
```bash
echo "ROT4 (0xF7/247):" && mbpoll -a 1 -b 57600 -P none -s 2 -r 247 -t 0 -c 1 -1 /dev/ttyUSB0
echo "ROT5 (0xFF/255):" && mbpoll -a 1 -b 57600 -P none -s 2 -r 255 -t 0 -c 1 -1 /dev/ttyUSB0
```

### Teste de escrita com monitoramento
```bash
echo "Antes:" && mbpoll -a 1 -b 57600 -P none -s 2 -r 2112 -t 4 -c 1 -1 /dev/ttyUSB0
mbpoll -a 1 -b 57600 -P none -s 2 -r 2112 -t 4 -1 /dev/ttyUSB0 777
echo "Imediato:" && mbpoll -a 1 -b 57600 -P none -s 2 -r 2112 -t 4 -c 1 -1 /dev/ttyUSB0
sleep 2
echo "Após 2s:" && mbpoll -a 1 -b 57600 -P none -s 2 -r 2112 -t 4 -c 1 -1 /dev/ttyUSB0
```

---

## ✅ Conclusão Provisória

O byte baixo do registro 0x0840 (2112) está sendo **forçado para 0x99 (153)** por uma das seguintes razões:

1. **ROT4 ou ROT5 executando sem estado visível ativo** (bug ou lógica oculta)
2. **Firmware do CLP protegendo área** (shadow/buffer automático)
3. **Registro 0x0944 sendo usado como fonte padrão** (153 é valor inicial)

### Recomendação Imediata
**Testar escrita na área de supervisão (0x0942/0x0944)** ou **ativar ROT5 e usar área SCADA (0x0B00+)**.

Se essas áreas também falharem, a **única solução confiável** será simular sequência de botões físicos via Modbus.

---

**Próximos passos**:
1. Executar testes de ativação de ROT5
2. Testar áreas alternativas (0x0500, 0x0942)
3. Monitorar durante dobra física real
4. Comparar com arquivo .SUP original se disponível

---

**Data**: 16/Nov/2025 22:00
**Testado por**: Claude Code
**Status**: Em investigação
