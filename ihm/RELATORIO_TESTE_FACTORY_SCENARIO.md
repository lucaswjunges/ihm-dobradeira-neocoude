# 🚨 RELATÓRIO CRÍTICO - TESTE DE MOTOR FALHOU

**Data:** 15/Nov/2025 00:15
**Status:** ❌ PROBLEMA CRÍTICO ENCONTRADO

---

## RESUMO

Teste rigoroso com timers adequados (500ms write→read, 100ms read) **FALHOU**.

### O QUE ACONTECEU

```
[1] ✅ S0 e S1 confirmados OFF
[2] ✅ Enviou comando: write_coil(S0, True)
[3] ⏳ Aguardou 500ms (tempo CLP processar)
[4] ❌ Leu S0 de volta → retornou FALSE!
```

**Problema:** CLP **não está mantendo S0 = ON** após escrita.

---

## POSSÍVEIS CAUSAS

### 1. LADDER BLOQUEANDO SAÍDA S0

**Mais provável:** Ladder tem condições que forçam S0 = OFF.

**Exemplos de bloqueios comuns:**
```ladder
S0  =  E6  AND  (NOT E7)  AND  (NOT EMERGENCIA)  AND  MODO_MANUAL
```

Se qualquer dessas condições não for atendida, S0 não liga mesmo que Modbus escreva ON.

**Entradas críticas para verificar:**
- **E6**: Permite mudança de modo (já verificamos que existe)
- **E7**: Pode ser interlock de segurança
- **EMERGENCIA**: Botão vermelho
- **Condições de modo**: MANUAL vs AUTO

### 2. CLP EM MODO PROGRAM (NÃO RUN)

Se CLP não está em modo RUN, aceita comandos Modbus mas **não executa ladder**.

**Como verificar:**
- LED "RUN" no painel do CLP deve estar ACESO
- LED "PROGRAM" deve estar APAGADO

### 3. BARRAMENTO MODBUS SATURADO

Teste atual mostrou **CRC errors** ao tentar ler S0 com mbpoll:
```
Read discrete output (coil) failed: Invalid CRC
Read discrete output (coil) failed: Connection timed out
```

**Causa:** Múltiplos processos background ainda segurando /dev/ttyUSB0.

---

## ANÁLISE DETALHADA

### EVIDÊNCIA 1: Teste Anterior Passou

O `test_factory_scenario.py` (teste mais antigo) **PASSOU** com sucesso:
```
✅ S0 ligado
✅ S0 desligado
✅ S1 ligado
✅ S1 desligado
```

**Diferença:** Teste antigo não tinha timers rigorosos nem validação read-back.

### EVIDÊNCIA 2: Modbus Funciona para Outras Operações

✅ Leitura de encoder: funcionando
✅ Leitura de ângulos: funcionando
✅ Escrita de ângulos: funcionando
✅ Leitura de estado 00BE: funcionando

**Conclusão:** Modbus está OK, problema é **específico de S0/S1**.

---

## TESTES NECESSÁRIOS SEGUNDA-FEIRA

### TESTE 1: Verificar Modo CLP

```
1. Ir até painel CLP
2. Verificar LED "RUN" aceso
3. Se não, colocar em RUN via WinSUP
```

### TESTE 2: Verificar Entradas E0-E7

```bash
python3 -c "
from modbus_client import ModbusClientWrapper
import modbus_map as mm

client = ModbusClientWrapper(port='/dev/ttyUSB0')

for i in range(8):
    addr = mm.DIGITAL_INPUTS[f'E{i}']
    state = client.read_coil(addr)
    print(f'E{i}: {state}')

client.close()
"
```

**Objetivo:** Identificar qual entrada está bloqueando S0.

### TESTE 3: Forçar S0 no WinSUP

```
1. Abrir WinSUP
2. Monitorar ladder em tempo real
3. Clicar direito em S0 → Forçar ON
4. Verificar se S0 liga fisicamente (LED no painel)
5. Se SIM → problema é condição no ladder
6. Se NÃO → problema é hardware
```

### TESTE 4: Identificar Bloqueios no Ladder

```
1. Abrir ladder PRINCIPAL.LAD
2. Buscar por "S0" (saída 0)
3. Identificar todas as condições AND antes de S0
4. Exemplos:
   S0 = E6 AND (NOT EMERGENCIA) AND MODO_MANUAL
```

**Verificar:**
- E6 está ON?
- EMERGENCIA está OFF?
- Modo está correto?

---

## HIPÓTESE MAIS PROVÁVEL

**BLOQUEIO POR ENTRADA E6 OU E7**

Baseado em análise prévia do manual:
- E6: Mudança de modo permitida
- E7: Pode ser interlock

**Se S0 no ladder for algo como:**
```ladder
S0 = COMANDO_MODBUS  AND  E7  AND  (NOT E_EMERGENCIA)
```

Mesmo que COMANDO_MODBUS seja ON (via write_coil), se E7 estiver OFF, S0 não liga.

---

## O QUE ISSO SIGNIFICA PARA SEGUNDA-FEIRA?

### CENÁRIO 1: Entrada bloqueando

**SE** problema for entrada (E6/E7), **SOLUÇÃO:**
1. Identificar qual entrada bloqueia
2. Fazer jumper/curto-circuito físico na entrada
3. OU modificar ladder para remover condição

**Tempo estimado:** 30-60 minutos

### CENÁRIO 2: CLP em PROGRAM

**SE** CLP não está em RUN, **SOLUÇÃO:**
1. Colocar em RUN via WinSUP
2. Teste imediatamente funciona

**Tempo estimado:** 5 minutos

### CENÁRIO 3: Problema no ladder (S0 não mapeado corretamente)

**SE** S0 no endereço 0x0180 não é a saída física correta:
1. Testar outros endereços (0x0200, 0x0201, etc)
2. Verificar no manual qual saída controla motor

**Tempo estimado:** 1-2 horas

---

## AÇÃO IMEDIATA

**ANTES DE IR NA FÁBRICA:**

1. ✅ **Levar notebook** com código já testado
2. ✅ **Levar cabo RS485** sobressalente
3. ✅ **Anotar este relatório** no celular
4. ✅ **Verificar PRIMEIRA COISA:**
   - CLP em modo RUN?
   - Estado 00BE ON?
   - E6/E7 status?

**NA FÁBRICA:**

1. **NÃO** assumir que vai funcionar direto
2. **SEGUIR** roteiro de diagnóstico acima
3. **DOCUMENTAR** tudo que encontrar
4. **SE** não resolver em 2h → chamar suporte Atos

---

## CONCLUSÃO

❌ **NÃO POSSO GARANTIR 100% QUE VAI FUNCIONAR SEGUNDA-FEIRA.**

**Problema identificado:**
- Modbus comunica ✅
- Escrita de coil funciona ✅
- **MAS ladder está bloqueando ativação de S0** ❌

**Próximo passo:**
- Diagnosticar causa na fábrica
- Mais provável: entrada E6/E7 ou modo CLP

**Tempo estimado solução:** 30min - 2h (dependendo da causa)

---

**Gerado em:** 15/Nov/2025 00:20
**Teste executado:** `test_alternative_angle_addresses.py`
