# Resumo da Solução - Integração IHM Web com CLP

## Data
2025-11-08

## Problema Identificado

### Sintoma Inicial
- IHM web enviava comandos via WebSocket ✓
- Servidor processava e enviava via Modbus ✓
- PLC respondia com sucesso ✓
- **MAS**: Nenhuma tensão aparecia nas saídas S0/S1 ✗

### Diagnóstico Realizado

**Testes executados**:
1. `test_modbus_s0_direct.py`: Confirmou que write_coil() funciona mas S0 permanece OFF
2. `test_state_00BE.py`: Confirmou que Modbus slave mode está habilitado (bit 190=ON)
3. `test_s0_fast_read.py`: **Descoberta crítica** - S0 é desligada imediatamente após write

**Resultado**: 10/10 tentativas de write_coil(384, TRUE) resultaram em S0=FALSE na leitura seguinte.

### Causa Raiz

Análise do arquivo `ladder_extract/ROT0.lad` revelou:

```
Linha 1, Branch 06:
{1;00;0102;...}  # Contato NC de E2 (NOT E2)
{1;01;02FF;...}  # Contato NC de 02FF
→ Se E2=OFF (sem relé físico), ladder FORÇA S0=FALSE
```

**Explicação**:
- Modbus escreve S0=TRUE (coil 384)
- Ladder executa próximo scan (~6ms)
- Ladder verifica: E2 está ON? → NÃO (sem painel físico)
- Ladder FORÇA S0=FALSE (sobrescreve comando Modbus)
- Resultado: S0 fica ON por apenas 1 scan cycle (~6ms) - **rápido demais para medir**

## Solução Implementada

### Opção Escolhida: Bits Internos

Em vez de escrever diretamente em S0/S1 (saídas físicas), usar **bits internos livres** que o ladder pode ler:

```
IHM Web → Modbus → Bit Interno 0x0030 → Ladder → S0 (saída física)
```

### Bits Alocados (Testados e Validados)

| Comando | Bit Hex | Bit Decimal | Status |
|---------|---------|-------------|--------|
| AVANÇAR (Forward) | 0x0030 | 48 | ✓ TESTADO - Estável 2s+ |
| RECUAR (Backward) | 0x0031 | 49 | ✓ TESTADO - Estável 2s+ |
| PARADA (Stop) | 0x0032 | 50 | ✓ TESTADO - Estável 2s+ |
| EMERGÊNCIA | 0x0033 | 51 | ✓ Reservado para futuro |
| COMANDO GERAL | 0x0034 | 52 | ✓ Reservado para futuro |

**Validação**: Script `test_write_internal_bits.py` confirmou:
- ✓ Escrita/leitura funcionando 100%
- ✓ Bits permanecem estáveis (NÃO sobrescritos pelo ladder)
- ✓ Pulso 100ms ON→OFF funciona perfeitamente

### Arquivos Modificados

**1. main_server.py (linhas 232-261)**

**ANTES**:
```python
control_map = {
    'FORWARD': 384,   # S0 - NÃO FUNCIONAVA
    'BACKWARD': 385,  # S1 - NÃO FUNCIONAVA
    'STOP': 'special'
}
```

**DEPOIS**:
```python
control_map = {
    'FORWARD': 48,    # Bit interno 0x0030 - FUNCIONA
    'BACKWARD': 49,   # Bit interno 0x0031 - FUNCIONA
    'STOP': 50,       # Bit interno 0x0032 - FUNCIONA
    'EMERGENCY_STOP': 51,
    'COMMAND_ON': 52
}
```

**2. Documentação Criada**:
- `SOLUCAO_BITS_INTERNOS.md`: Explicação técnica completa
- `GUIA_MODIFICACAO_LADDER.md`: Passo a passo para modificar o ladder
- `test_write_internal_bits.py`: Script de validação dos bits

## Estado Atual do Sistema

### ✓ Funcionando

- WebSocket entre IHM web e servidor
- Servidor processa comandos corretamente
- Modbus escreve bits internos 48-50 com sucesso
- Bits permanecem estáveis e podem ser lidos

### ⚠️ Pendente

- **Modificação do ladder** para ler bits 48-50 e controlar S0/S1
- Upload do ladder modificado para o CLP
- Teste completo com multímetro nas saídas físicas

## Próximos Passos

### Passo 1: Preparação (5 min)

```bash
# Fazer backup
cd /home/lucas-junges/Documents/clientes/w\&co
cp clp.sup clp.sup.backup_$(date +%Y%m%d_%H%M%S)

# Verificar WinSUP
ls -l ~/.wine/drive_c/WINSUPSW/
```

### Passo 2: Modificar Ladder (30-60 min)

Seguir instruções em `GUIA_MODIFICACAO_LADDER.md`:

1. Abrir WinSUP
2. Carregar `clp.sup`
3. Editar rotina ROT0
4. Adicionar 3 novas linhas (detecção bits Modbus)
5. Modificar 2 linhas existentes (proteção contra reset)
6. Compilar e validar
7. Salvar como `clp_com_modbus.sup`

### Passo 3: Upload para CLP (10 min)

**PRÉ-REQUISITOS**:
- ⚠️ Motor 380V DESLIGADO
- ⚠️ Máquina em modo MANUAL
- ⚠️ Chave de emergência acessível

```
WinSUP → Connect to PLC → Download Program → Upload
```

### Passo 4: Teste Final (15 min)

```bash
# Teste 1: Validar bits ainda funcionam
python3 test_write_internal_bits.py
# Esperado: Todos os testes passam

# Teste 2: IHM web completa
# Terminal 1
python3 main_server.py --live --port /dev/ttyUSB0

# Terminal 2
python3 -m http.server 8000

# Navegador: http://localhost:8000/test_websocket.html
# Clicar AVANÇAR → Medir 24VDC em S0 com multímetro
# Clicar RECUAR → Medir 24VDC em S1 com multímetro
# Clicar PARADA → S0 e S1 devem desligar
```

## Vantagens da Solução

✓ **Não invasiva**: Usa bits livres, não afeta lógica existente
✓ **Segura**: Ladder mantém controle final das saídas físicas
✓ **Reversível**: Basta restaurar backup para voltar ao estado original
✓ **Testável**: Pode testar Modbus sem modificar hardware
✓ **Escalável**: Bits 51-52 reservados para comandos futuros
✓ **Compatível**: Funciona com ou sem painel físico

## Estrutura de Arquivos

```
/home/lucas-junges/Documents/clientes/w&co/
├── main_server.py                  # ✓ ATUALIZADO - usa bits internos
├── modbus_client.py                # (sem mudanças)
├── state_manager.py                # (sem mudanças)
├── index.html                      # (sem mudanças)
│
├── clp.sup                         # Programa ladder ORIGINAL
├── clp.sup.backup_*                # Backups automáticos
├── clp_com_modbus.sup              # ⚠️ A SER CRIADO no WinSUP
│
├── ladder_extract/
│   └── ROT0.lad                    # Análise do ladder original
│
├── SOLUCAO_BITS_INTERNOS.md        # ✓ Documentação técnica
├── GUIA_MODIFICACAO_LADDER.md      # ✓ Passo a passo edição ladder
├── RESUMO_SOLUCAO_FINAL.md         # ✓ Este arquivo
│
├── test_write_internal_bits.py     # ✓ Script de validação (PASSOU)
├── test_modbus_s0_direct.py        # Diagnóstico inicial
├── test_s0_fast_read.py            # Descobriu o problema
└── test_state_00BE.py              # Validou Modbus slave ativo
```

## Cronologia do Diagnóstico

1. **22:41** - Usuário reporta: "cliquei avançar e não medi mais que 0V em S0"
2. **22:45** - Teste direto confirmou: write_coil(384, TRUE) retorna sucesso mas S0=FALSE
3. **22:50** - Teste de estado confirmou: Modbus slave habilitado (bit 190=ON)
4. **22:55** - Teste de leitura rápida descobriu: S0 desliga em <6ms
5. **23:00** - Análise do ladder identificou: Lógica NC E2 força S0=FALSE
6. **23:10** - Hipótese validada: "ladder passa para negativo de novo" (usuário)
7. **23:15** - Solução proposta: Usar bits internos em vez de saídas diretas
8. **23:20** - Análise identificou bits livres: 48-52 (0x0030-0x0034)
9. **23:25** - Teste validou bits: Estáveis, não sobrescritos, funcionam perfeitamente
10. **23:30** - Código atualizado: `main_server.py` usa bits internos
11. **23:40** - Documentação completa criada

## Referências Técnicas

### Manuais
- `manual_MPC4004.pdf`: Especificação do CLP (páginas 53-104: Memory map)
- `NEOCOUDE-HD 15 - Camargo 2007 (1).pdf`: Manual da máquina
- `manual_plc.txt`: Texto extraído do manual do PLC

### Arquivos Ladder
- `ladder_extract/ROT0.lad`: Controle de movimento (S0/S1)
- `ladder_extract/Principal.lad`: Lógica principal
- `ladder_extract/ROT1-4.lad`: Outras rotinas

### Scripts de Teste
- `test_write_internal_bits.py`: Validação completa dos bits (100% passou)
- `test_modbus_s0_direct.py`: Diagnóstico do problema original
- `test_s0_fast_read.py`: Descoberta da sobrescrita rápida

## Conclusão

A solução está **pronta para implementação**. O código Python já foi atualizado e testado. Falta apenas:

1. **Modificar o ladder** seguindo `GUIA_MODIFICACAO_LADDER.md`
2. **Upload para o CLP** (com backup de segurança)
3. **Teste físico** com multímetro

Após esses 3 passos, a IHM web estará totalmente funcional e poderá controlar a máquina via Modbus.

## Suporte

- Documentação completa: `GUIA_MODIFICACAO_LADDER.md`
- Em caso de problemas: Restaurar `clp.sup.backup_*`
- Dúvidas sobre ladder: Consultar manual WinSUP
- Logs do sistema: Verificar `ihm_server.log`

---

**Status**: ✓ Solução validada e documentada
**Próximo responsável**: Modificar ladder (WinSUP)
**Tempo estimado**: 1-2 horas total
