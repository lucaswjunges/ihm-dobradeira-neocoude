# TESTE DO LADDER MODIFICADO COM ROT5

## Arquivo Modificado
**Arquivo:** `clp_MODIFICADO_IHM_WEB_COM_ROT5.sup`
**Tamanho:** 27 KB
**Data:** 2025-11-18

## Modificação Realizada
Adicionado **CALL ROT5** no arquivo `Principal.lad` como **Line00007**, entre CALL ROT4 e OUT 0x00C5.

### Linha Adicionada:
```
[Line00007]
  [Features]
    Out:CALL    T:-001 Size:001 E:ROT5
    Condition: bit 0x00F7 (sempre ativo)
```

## O Que ROT5 Faz
ROT5 contém a lógica de interface Modbus que copia dados da área de entrada (0x0A00) para a área de trabalho (0x0840):

```
Trigger 0x0390 (Ângulo Esquerda 1):
  MOV 0x0A00 → 0x0842 [MSW]
  MOV 0x0A02 → 0x0840 [LSW]

Trigger 0x0391 (Ângulo Direita 1):
  MOV 0x0A04 → 0x0848 [MSW]
  MOV 0x0A06 → 0x0846 [LSW]

Trigger 0x0392 (Ângulo Esquerda 2):
  MOV 0x0A08 → 0x0852 [MSW]
  MOV 0x0A0A → 0x0850 [LSW]
```

## Próximos Passos

### 1. Upload do Ladder para o CLP
```bash
# Usar WinSUP2 no Windows:
# 1. Abrir WinSUP2
# 2. File → Open Project → clp_MODIFICADO_IHM_WEB_COM_ROT5.sup
# 3. PLC → Download
# 4. Verificar bit 0x00F7 está ON (para ROT5 executar)
```

### 2. Teste da Funcionalidade ROT5
```bash
# Via Ubuntu com mbpoll conectado no CLP:

# Teste 1: Escrever ângulo na área Modbus (0x0A00/0x0A02)
echo "=== Escrevendo ângulo 90° em 0x0A00 ==="
mbpoll -m rtu -a 1 -b 57600 -P none -s 2 -t 4 -r 0x0A00 -1 /dev/ttyUSB1 -- 0
mbpoll -m rtu -a 1 -b 57600 -P none -s 2 -t 4 -r 0x0A02 -1 /dev/ttyUSB1 -- 90

# Teste 2: Ativar trigger 0x0390 (pulso 100ms)
echo "=== Ativando trigger 0x0390 ==="
mbpoll -m rtu -a 1 -b 57600 -P none -s 2 -t 0 -r 0x0390 -1 /dev/ttyUSB1 -- 1
sleep 0.1
mbpoll -m rtu -a 1 -b 57600 -P none -s 2 -t 0 -r 0x0390 -1 /dev/ttyUSB1 -- 0

# Teste 3: Verificar shadow area atualizou (0x0840/0x0842)
echo "=== Lendo shadow area 0x0840 ==="
mbpoll -m rtu -a 1 -b 57600 -P none -s 2 -t 4 -r 0x0840 -c 2 -1 /dev/ttyUSB1
# Resultado esperado: [2112]: 90, [2113]: 0
```

### 3. Teste Completo de Todos os 3 Ângulos
```bash
#!/bin/bash
# teste_rot5_completo.sh

# Ângulo Esquerda 1: 90°
echo "=== Testando Ângulo Esquerda 1: 90° ==="
mbpoll -m rtu -a 1 -b 57600 -P none -s 2 -t 4 -r 0x0A00 -1 /dev/ttyUSB1 -- 0
mbpoll -m rtu -a 1 -b 57600 -P none -s 2 -t 4 -r 0x0A02 -1 /dev/ttyUSB1 -- 90
mbpoll -m rtu -a 1 -b 57600 -P none -s 2 -t 0 -r 0x0390 -1 /dev/ttyUSB1 -- 1
sleep 0.1
mbpoll -m rtu -a 1 -b 57600 -P none -s 2 -t 0 -r 0x0390 -1 /dev/ttyUSB1 -- 0
sleep 0.5
echo "Lendo shadow 0x0840/0x0842:"
mbpoll -m rtu -a 1 -b 57600 -P none -s 2 -t 4 -r 0x0840 -c 2 -1 /dev/ttyUSB1

# Ângulo Direita 1: 120°
echo "=== Testando Ângulo Direita 1: 120° ==="
mbpoll -m rtu -a 1 -b 57600 -P none -s 2 -t 4 -r 0x0A04 -1 /dev/ttyUSB1 -- 0
mbpoll -m rtu -a 1 -b 57600 -P none -s 2 -t 4 -r 0x0A06 -1 /dev/ttyUSB1 -- 120
mbpoll -m rtu -a 1 -b 57600 -P none -s 2 -t 0 -r 0x0391 -1 /dev/ttyUSB1 -- 1
sleep 0.1
mbpoll -m rtu -a 1 -b 57600 -P none -s 2 -t 0 -r 0x0391 -1 /dev/ttyUSB1 -- 0
sleep 0.5
echo "Lendo shadow 0x0846/0x0848:"
mbpoll -m rtu -a 1 -b 57600 -P none -s 2 -t 4 -r 0x0846 -c 2 -1 /dev/ttyUSB1

# Ângulo Esquerda 2: 45°
echo "=== Testando Ângulo Esquerda 2: 45° ==="
mbpoll -m rtu -a 1 -b 57600 -P none -s 2 -t 4 -r 0x0A08 -1 /dev/ttyUSB1 -- 0
mbpoll -m rtu -a 1 -b 57600 -P none -s 2 -t 4 -r 0x0A0A -1 /dev/ttyUSB1 -- 45
mbpoll -m rtu -a 1 -b 57600 -P none -s 2 -t 0 -r 0x0392 -1 /dev/ttyUSB1 -- 1
sleep 0.1
mbpoll -m rtu -a 1 -b 57600 -P none -s 2 -t 0 -r 0x0392 -1 /dev/ttyUSB1 -- 0
sleep 0.5
echo "Lendo shadow 0x0850/0x0852:"
mbpoll -m rtu -a 1 -b 57600 -P none -s 2 -t 4 -r 0x0850 -c 2 -1 /dev/ttyUSB1

echo "=== TESTE COMPLETO ==="
```

## Resultado Esperado

### ANTES da modificação:
- ✅ Escrita em 0x0A00 funcionava
- ❌ Shadow area 0x0840 NÃO atualizava
- ❌ ROT5 não era chamado pelo Principal.lad

### DEPOIS da modificação:
- ✅ Escrita em 0x0A00 funciona
- ✅ Shadow area 0x0840 DEVE atualizar quando trigger ativado
- ✅ ROT5 é chamado a cada scan do CLP

## Verificação de Sucesso

1. **Bit 0x00F7 está ON?**
   ```bash
   mbpoll -m rtu -a 1 -b 57600 -P none -s 2 -t 0 -r 0x00F7 -1 /dev/ttyUSB1
   # Deve retornar: [247]: ON
   ```

2. **ROT5 está sendo executado?**
   - Verificar via WinSUP2 em modo monitor
   - Linha "CALL ROT5" deve estar piscando (verde) durante execução

3. **Cópia de dados funciona?**
   - Escrever valor em 0x0A00
   - Ativar trigger correspondente
   - Verificar valor aparece em 0x0840
   - **Importante:** Valores podem ser modificados pelo Principal.lad depois da cópia (comportamento normal)

## Troubleshooting

### Shadow area não atualiza
- ✅ Verificar bit 0x00F7 está ON
- ✅ Verificar trigger foi ativado e desativado (pulso)
- ✅ Verificar ladder foi recompilado e baixado no CLP
- ✅ Verificar Principal.lad tem Line00007 com CALL ROT5

### Valores mudam após cópia
- **Normal!** Principal.lad tem lógica que processa os ângulos
- ROT5 apenas copia de 0x0A00 → 0x0840
- Principal.lad pode modificar 0x0840 depois

### ROT5 não aparece no monitor
- Verificar arquivo SUP foi corretamente descomprimido pelo WinSUP2
- Verificar não há erros de compilação
- Verificar ROT5.lad existe no projeto

## Arquivos de Referência

- `/home/lucas-junges/Documents/clientes/w&co/ihm_esp32/clp_MODIFICADO_IHM_WEB_COM_ROT5.sup` - Ladder modificado
- `/home/lucas-junges/Documents/clientes/w&co/ihm_esp32/clp_temp_extract/Principal.lad` - Principal.lad com CALL ROT5
- `/home/lucas-junges/Documents/clientes/w&co/ihm_esp32/clp_temp_extract/ROT5.lad` - Rotina ROT5 original
- `/tmp/RELATORIO_TESTES_IHM_WORKFLOW.md` - Análise completa dos testes Ubuntu

## Próxima Etapa: Integração ESP32

Após confirmar que ROT5 funciona com mbpoll/Ubuntu, atualizar código ESP32:

1. **Atualizar modbus_map.py** com áreas corretas:
   ```python
   # Área de escrita (IHM → CLP)
   'MODBUS_INPUT_AREA': 0x0A00,  # 6 registros (3 ângulos x 2 registros)

   # Triggers
   'TRIGGER_ANGULO_ESQ_1': 0x0390,
   'TRIGGER_ANGULO_DIR_1': 0x0391,
   'TRIGGER_ANGULO_ESQ_2': 0x0392,
   ```

2. **Implementar sequência de escrita**:
   - Escrever MSW/LSW do ângulo em 0x0A00+offset
   - Ativar trigger correspondente (ON)
   - Aguardar 100ms
   - Desativar trigger (OFF)

3. **Usar FC 0x10 (Write Multiple Registers)**:
   - FC 0x06 não funciona no ESP32
   - FC 0x10 funciona perfeitamente (testado com valores pequenos)

---

**Desenvolvido por:** Eng. Lucas William Junges
**Data:** 2025-11-18
**Status:** ✅ Ladder modificado e pronto para teste
