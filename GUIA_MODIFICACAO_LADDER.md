# Guia de Modificação do Ladder Logic - Integração Modbus

## Data
2025-11-08

## Objetivo

Modificar o programa ladder do CLP (arquivo `clp.sup`) para que ele **leia os bits internos** escritos via Modbus e **controle as saídas S0/S1** baseado nesses comandos.

## Problema Atual

O ladder atual **sobrescreve S0/S1** quando detecta que E2/E4 não estão ativas (sem painel físico com relés):

```
ROT0.lad - Linha 1, Branch 06:
{1;00;0102;...}  # NC E2 (NOT E2)
{1;01;02FF;...}  # NC 02FF
→ Se ambos fechados (E2=OFF) → RESET S0 (força S0=FALSE)
```

## Solução Implementada

### Bits Internos Modbus (Testados e Validados)

| Comando | Bit Hex | Bit Decimal | Função |
|---------|---------|-------------|--------|
| AVANÇAR | 0x0030 | 48 | Comando para ativar S0 |
| RECUAR | 0x0031 | 49 | Comando para ativar S1 |
| PARADA | 0x0032 | 50 | Comando para desligar S0 e S1 |
| EMERGÊNCIA | 0x0033 | 51 | Reservado (futuro) |
| COMANDO GERAL | 0x0034 | 52 | Reservado (futuro) |

### Fluxo de Controle

```
IHM Web → Modbus write_coil(48, TRUE) → Bit interno 0x0030 = ON
                                              ↓
                                      Ladder detecta bit 48
                                              ↓
                                      Ladder ativa S0 (coil 384)
                                              ↓
                                      Timer 100ms-2s
                                              ↓
                                      Ladder desliga S0 e limpa bit 48
```

## Modificações Necessárias no Ladder

### Arquivo a Modificar

- **Principal**: `ladder_extract/ROT0.lad` (controle de S0/S1)
- **Backup OBRIGATÓRIO**: Fazer cópia antes de modificar!

### Passo 1: Adicionar Lógica de Detecção Modbus FORWARD

**Localização**: Adicionar ANTES das linhas que controlam S0

**Nova Linha ROT0_MODBUS_01**:
```
Descrição: Detecta comando Modbus FORWARD (bit 0x0030) e ativa S0

Condições (Branch 1):
  - Contato NO: 0x0030 (bit Modbus FORWARD)
  - Contato NC: 0x0031 (NOT bit BACKWARD - proteção)
  - Contato NC: 0x0032 (NOT bit STOP - proteção)
  - Contato NO: 0x00BE (Modbus slave habilitado)

Ações:
  1. SETR 0x0180 (S0) - Ativa saída S0
  2. TMR Timer T:0010 Setpoint:0100 (100ms ou ajustar conforme necessário)
  3. Ao terminar timer:
     - RESET 0x0030 (limpa bit comando FORWARD)
     - RESET 0x0180 (desliga S0) - opcional, pode deixar ladder existente fazer

Ladder Syntax (Atos):
Out:SETR    T:0043 Size:003 E:0180
Branch01:
  {0;00;0030;-1;02;-1;-1;00}  # Contato NO bit 0x0030
  {1;01;0031;-1;-1;01;02;00}  # Contato NC bit 0x0031
  {1;02;0032;-1;-1;-1;-1;00}  # Contato NC bit 0x0032
  {0;03;00BE;-1;-1;-1;-1;00}  # Contato NO bit 0x00BE (Modbus slave)
```

### Passo 2: Adicionar Lógica de Detecção Modbus BACKWARD

**Nova Linha ROT0_MODBUS_02**:
```
Descrição: Detecta comando Modbus BACKWARD (bit 0x0031) e ativa S1

Condições (Branch 1):
  - Contato NO: 0x0031 (bit Modbus BACKWARD)
  - Contato NC: 0x0030 (NOT bit FORWARD - proteção)
  - Contato NC: 0x0032 (NOT bit STOP - proteção)
  - Contato NO: 0x00BE (Modbus slave habilitado)

Ações:
  1. SETR 0x0181 (S1) - Ativa saída S1
  2. TMR Timer T:0011 Setpoint:0100 (100ms)
  3. Ao terminar timer:
     - RESET 0x0031 (limpa bit comando BACKWARD)
     - RESET 0x0181 (desliga S1) - opcional

Ladder Syntax (Atos):
Out:SETR    T:0043 Size:003 E:0181
Branch01:
  {0;00;0031;-1;02;-1;-1;00}  # Contato NO bit 0x0031
  {1;01;0030;-1;-1;01;02;00}  # Contato NC bit 0x0030
  {1;02;0032;-1;-1;-1;-1;00}  # Contato NC bit 0x0032
  {0;03;00BE;-1;-1;-1;-1;00}  # Contato NO bit 0x00BE
```

### Passo 3: Adicionar Lógica de Detecção Modbus STOP

**Nova Linha ROT0_MODBUS_03**:
```
Descrição: Detecta comando Modbus STOP (bit 0x0032) e desliga tudo

Condições (Branch 1):
  - Contato NO: 0x0032 (bit Modbus STOP)
  - Contato NO: 0x00BE (Modbus slave habilitado)

Ações:
  1. RESET 0x0180 (S0) - Desliga saída S0
  2. RESET 0x0181 (S1) - Desliga saída S1
  3. RESET 0x0030 (limpa bit FORWARD)
  4. RESET 0x0031 (limpa bit BACKWARD)
  5. RESET 0x0032 (auto-limpa bit STOP)

Ladder Syntax (Atos):
Out:RESET   T:0042 Size:005 E:0180 E:0181 E:0030 E:0031 E:0032
Branch01:
  {0;00;0032;-1;02;-1;-1;00}  # Contato NO bit 0x0032
  {0;01;00BE;-1;-1;-1;-1;00}  # Contato NO bit 0x00BE
```

### Passo 4: Modificar Linhas Existentes de S0/S1

**CRÍTICO**: As linhas existentes que **desligam S0/S1 quando E2/E4 estão OFF** devem ser modificadas para **NÃO desligar se bits Modbus estão ativos**.

**ROT0.lad Linha 1 (SETR S0) - Modificar Branch 06**:

**ANTES**:
```
Branch06:
  {1;00;0102;-1;07;-1;-1;00}  # NC E2
  {1;01;02FF;-1;-1;01;07;00}  # NC 02FF
  → Se ambos TRUE (E2=OFF), RESET S0
```

**DEPOIS** (adicionar proteção):
```
Branch06:
  {1;00;0102;-1;07;-1;-1;00}  # NC E2
  {1;01;02FF;-1;-1;01;07;00}  # NC 02FF
  {1;02;0030;-1;-1;02;07;00}  # NC 0x0030 (se bit Modbus FORWARD ativo, NÃO desligar)
  → Só desliga S0 se E2=OFF E bit Modbus=OFF
```

**ROT0.lad Linha 3 (SETR S1) - Modificar Branch 06**:

**ANTES**:
```
Branch06:
  {1;00;0104;-1;07;-1;-1;00}  # NC E4
  {1;01;02FF;-1;-1;01;07;00}  # NC 02FF
  → Se ambos TRUE (E4=OFF), RESET S1
```

**DEPOIS**:
```
Branch06:
  {1;00;0104;-1;07;-1;-1;00}  # NC E4
  {1;01;02FF;-1;-1;01;07;00}  # NC 02FF
  {1;02;0031;-1;-1;02;07;00}  # NC 0x0031 (se bit Modbus BACKWARD ativo, NÃO desligar)
  → Só desliga S1 se E4=OFF E bit Modbus=OFF
```

## Procedimento de Implementação

### 1. Preparação

```bash
# Fazer backup do programa atual
cd /home/lucas-junges/Documents/clientes/w\&co/ladder_extract
cp ../clp.sup ../clp.sup.backup_$(date +%Y%m%d_%H%M%S)

# Verificar WinSUP está instalado
ls -l ~/.wine/drive_c/WINSUPSW/
```

### 2. Abrir WinSUP

```bash
cd /home/lucas-junges/Documents/clientes/w\&co
wine ~/.wine/drive_c/WINSUPSW/winsup.exe
```

### 3. Carregar Programa

- File → Open → Selecionar `clp.sup`
- Aguardar carregar completamente

### 4. Editar ROT0

- Double-click em "ROT0" no navegador de rotinas
- Localizar as linhas existentes de controle de S0/S1

### 5. Adicionar Novas Linhas

- Inserir as 3 novas linhas (MODBUS_01, MODBUS_02, MODBUS_03) **ANTES** das linhas existentes
- Usar editor ladder do WinSUP para criar a lógica descrita

### 6. Modificar Linhas Existentes

- Editar Branch 06 das linhas 1 e 3 do ROT0
- Adicionar contatos NC para bits 0x0030 e 0x0031

### 7. Validar

- Tools → Validate/Compile
- Verificar se não há erros
- Corrigir quaisquer warnings ou erros

### 8. Salvar

- File → Save As → `clp_com_modbus.sup`
- **NÃO sobrescrever clp.sup original ainda**

### 9. Upload para CLP (CUIDADO!)

**PRÉ-REQUISITOS**:
- ⚠️ Máquina em modo MANUAL
- ⚠️ Motor 380V DESLIGADO
- ⚠️ Chave de emergência acessível
- ⚠️ Backup confirmado

**Passos**:
1. Connect → Connect to PLC
2. PLC → Download Program
3. Selecionar `clp_com_modbus.sup`
4. Confirmar download
5. Aguardar gravação
6. PLC → Run

### 10. Teste Inicial

```bash
# Terminal 1
python3 test_write_internal_bits.py

# Verificar se bits 48-50 ainda funcionam após upload
# Esperado: Todos os testes passam
```

### 11. Teste com IHM Web

```bash
# Terminal 1
python3 main_server.py --live --port /dev/ttyUSB0

# Terminal 2
python3 -m http.server 8000

# Navegador
http://localhost:8000/test_websocket.html

# Clicar AVANÇAR → Medir 24VDC em S0
# Clicar RECUAR → Medir 24VDC em S1
# Clicar PARADA → S0 e S1 devem desligar
```

## Resolução de Problemas

### Problema: Bits Modbus não ativam saídas

**Causa**: Ladder não foi modificado ou modificação incorreta

**Solução**:
1. Verificar se novas linhas foram adicionadas corretamente
2. Usar modo monitor do WinSUP para ver estado dos bits em tempo real
3. Verificar se contatos estão NO (normalmente aberto) onde esperado

### Problema: Saídas ficam ligadas indefinidamente

**Causa**: Timer não está funcionando ou bit não é limpo

**Solução**:
1. Verificar setpoint do timer (deve ser 0100 = 100ms ou ajustar)
2. Adicionar lógica para RESET do bit comando após timer
3. Verificar se branch de limpeza está conectado corretamente

### Problema: Ladder existente ainda desliga saídas

**Causa**: Proteção (NC de bits Modbus) não foi adicionada

**Solução**:
1. Revisar modificação das linhas existentes
2. Adicionar contatos NC de 0x0030 e 0x0031 nos branches corretos
3. Testar com multímetro enquanto clica botões na IHM

## Verificação Final

Checklist antes de considerar concluído:

- [ ] Backup do `clp.sup` original criado
- [ ] 3 novas linhas adicionadas no ROT0
- [ ] Linhas existentes modificadas para não desligar quando Modbus ativo
- [ ] Programa compilado sem erros
- [ ] Upload para CLP bem-sucedido
- [ ] Teste `test_write_internal_bits.py` passa
- [ ] IHM web ativa S0 ao clicar AVANÇAR
- [ ] IHM web ativa S1 ao clicar RECUAR
- [ ] IHM web desliga ambos ao clicar PARADA
- [ ] Saídas desligam automaticamente após timer

## Referências

- `SOLUCAO_BITS_INTERNOS.md`: Documentação da solução
- `test_write_internal_bits.py`: Script de teste dos bits
- `ladder_extract/ROT0.lad`: Arquivo de ladder original
- Manual WinSUP: Instruções de edição de ladder
- Manual MPC4004: Sintaxe de instruções ladder (páginas 105-132)

## Notas Importantes

- ⚠️ **NUNCA** faça upload sem backup
- ⚠️ **SEMPRE** teste em modo manual primeiro
- ⚠️ **VERIFIQUE** duas vezes antes de gravar no CLP
- ⚠️ Se algo der errado, restaure backup imediatamente
- ✓ Documente qualquer alteração adicional necessária
