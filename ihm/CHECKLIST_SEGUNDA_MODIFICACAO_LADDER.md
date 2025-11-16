# ✅ CHECKLIST MODIFICAÇÃO LADDER - SEGUNDA-FEIRA

**IMPRIMIR ESTE DOCUMENTO E LEVAR PARA FÁBRICA**

---

## PRÉ-EXECUÇÃO

### Materiais:
- [ ] Laptop Windows com WinSUP instalado e testado
- [ ] Cabo RS485 (testado hoje com mbpoll)
- [ ] Pen drive formatado (mínimo 1GB)
- [ ] Notebook Ubuntu com código Python
- [ ] Este checklist impresso
- [ ] Guia completo (`GUIA_MODIFICACAO_LADDER_SEGUNDA.md`) impresso

### Autorizações:
- [ ] Autorização formal para modificar ladder
- [ ] Equipe ciente que máquina vai parar 15-30min
- [ ] Operador disponível para testes
- [ ] Acesso físico ao CLP liberado

---

## FASE 1: BACKUP (CRÍTICO - NÃO PULAR!)

### Conexão:
- [ ] WinSUP conectado ao CLP via RS485
- [ ] Configuração: 57600 bps, slave ID 1
- [ ] Status: "Online" aparece no WinSUP

### Download:
- [ ] WinSUP → Online → Download from PLC
- [ ] Salvo como: `clp_backup_ANTES_MOD_151125.sup`
- [ ] Copiado para PEN DRIVE
- [ ] Verificado: Arquivo tem ~50-200KB (não está vazio)
- [ ] Reaberto no WinSUP: Todos os programas aparecem

**✋ SE BACKUP FALHOU: NÃO PROSSEGUIR! Resolver problema de conexão primeiro.**

---

## FASE 2: ANÁLISE

### Busca de Ângulos Input:

- [ ] Buscar "0500" (NVRAM) → Anotei ____ ocorrências
- [ ] Buscar "0840" → Anotei ____ ocorrências
- [ ] Buscar "0842" → Anotei ____ ocorrências
- [ ] Buscar "MOV" → Analisei instruções relevantes

### Descobertas (anotar):

```
Endereço input ângulo 1: 0x________
Endereço input ângulo 2: 0x________
Endereço input ângulo 3: 0x________

Estratégia escolhida:
[ ] A - Nova área 0x0A00
[ ] B - Remover sobrescrita
[ ] C - Usar NVRAM 0x0500
```

---

## FASE 3: MODIFICAÇÃO

### Ângulos:

**SE Estratégia A:**
- [ ] Adicionei novo código em PRINCIPAL.lad
- [ ] Testei sintaxe: 0 erros
- [ ] Anotei endereços usados: MSW1=0x____ LSW1=0x____

**SE Estratégia B:**
- [ ] Localizei instrução que sobrescreve 0x0840
- [ ] Removi ou modifiquei
- [ ] Testei sintaxe: 0 erros

**SE Estratégia C:**
- [ ] Confirmei ladder JÁ usa 0x0500
- [ ] NENHUMA modificação necessária!
- [ ] Apenas atualizar Python depois

### Motor (Opcional):

- [ ] Localizei SETR para S0 em ROT0.lad
- [ ] Adicionei Branch09 com bit 0x0500
- [ ] Localizei SETR para S1
- [ ] Adicionei Branch09 com bit 0x0501
- [ ] Testei sintaxe: 0 erros

---

## FASE 4: UPLOAD

### Compilação:
- [ ] WinSUP → Program → Compile
- [ ] Resultado: **0 ERROS**
- [ ] Se houve erros: Corrigi e recompilei

### Upload Seguro:
- [ ] ⚠️ AVISEI EQUIPE: Máquina vai parar!
- [ ] WinSUP → Online → Stop PLC
- [ ] Máquina parou confirmado
- [ ] WinSUP → Online → Upload to PLC
- [ ] Barra de progresso 100%
- [ ] WinSUP → Online → Run PLC
- [ ] Máquina voltou a funcionar
- [ ] Aguardei 30 segundos para estabilizar

---

## FASE 5: TESTES

### Teste Python - Ângulos:

```bash
# NO NOTEBOOK UBUNTU:
cd /home/lucas-junges/Documents/clientes/w&co/ihm

python3 -c "
from modbus_client import ModbusClientWrapper
import modbus_map as mm
import time

client = ModbusClientWrapper(port='/dev/ttyUSB0')

# ESCREVER 45°
client.write_32bit(
    mm.BEND_ANGLES['BEND_1_LEFT_MSW'],
    mm.BEND_ANGLES['BEND_1_LEFT_LSW'],
    450
)

print('Aguardando 5s...')
time.sleep(5)

# LER DE VOLTA
value = client.read_32bit(
    mm.BEND_ANGLES['BEND_1_LEFT_MSW'],
    mm.BEND_ANGLES['BEND_1_LEFT_LSW']
)

if value == 450:
    print('✅✅✅ ÂNGULOS FUNCIONANDO!')
else:
    print(f'❌ Leu {value}, esperava 450')

client.close()
"
```

**Resultado:**
- [ ] ✅ SUCESSO: Leu 450 (45.0°)
- [ ] ❌ FALHA: Leu ________

**SE FALHOU:**
- [ ] Executei rollback (ver próxima seção)

### Teste Python - Motor (se modificou):

```bash
python3 test_alternative_angle_addresses.py
```

**Resultado:**
- [ ] ✅ S0 ligou e motor girou
- [ ] ✅ S1 ligou e motor girou reverso
- [ ] ❌ Falhou: ________________

---

## FASE 6: BACKUP FINAL

- [ ] WinSUP → Online → Download from PLC
- [ ] Salvo como: `clp_MODIFICADO_OK_151125.sup`
- [ ] Copiado para PEN DRIVE
- [ ] Copiado para pasta: `/ihm/ladder_backups/`

---

## 🚨 ROLLBACK (SE NECESSÁRIO)

**EXECUTAR SE:**
- Teste de ângulos falhou
- Motor não responde
- Máquina apresentou comportamento estranho
- Operador reportou problema

**PASSOS:**

1. [ ] WinSUP → Online → Stop PLC
2. [ ] WinSUP → File → Open → `clp_backup_ANTES_MOD_151125.sup`
3. [ ] WinSUP → Online → Upload to PLC
4. [ ] Aguardar 100%
5. [ ] WinSUP → Online → Run PLC
6. [ ] Máquina voltou ao normal
7. [ ] Testes básicos OK (botões físicos funcionam)

**Tempo de rollback:** 2-3 minutos

---

## PÓS-EXECUÇÃO

### Documentação:

- [ ] Anotei endereços descobertos
- [ ] Tirei fotos/prints do ladder modificado
- [ ] Salvei todos os backups
- [ ] Atualizei `modbus_map.py` com endereços corretos

### IHM Web:

- [ ] Servidor Python rodando
- [ ] Abri Chrome → localhost:8080
- [ ] Configurei ângulo 90° na interface
- [ ] Cliquei AVANÇAR
- [ ] Motor girou ✅

---

## ✅ CRITÉRIOS DE SUCESSO FINAL

### Mínimo (Opção Híbrida):
- [ ] Monitoramento funciona (encoder, estados, LEDs)
- [ ] Ladder original restaurado e funcionando
- [ ] Operação manual via painel físico OK

### Ideal (Controle Total):
- [ ] IHM web configura ângulos → CLP usa valores
- [ ] IHM web controla motor → AVANÇAR/RECUAR funcionam
- [ ] Botões físicos ainda funcionam (não quebrou nada)
- [ ] Operador consegue usar só o tablet

---

## HORÁRIOS (preencher):

- **Início:** ____:____
- **Backup completo:** ____:____
- **Análise finalizada:** ____:____
- **Upload concluído:** ____:____
- **Testes OK:** ____:____
- **Fim:** ____:____

**Tempo total:** _______ horas

---

## PROBLEMAS ENCONTRADOS:

```
(Anotar aqui qualquer problema ou descoberta importante)

1. _______________________________________________

2. _______________________________________________

3. _______________________________________________
```

---

## ASSINATURAS:

**Técnico responsável:** _______________________________

**Supervisor aprovação:** ______________________________

**Data:** ____/____/2025

---

**ESTE DOCUMENTO É SUA GARANTIA!**
**Guarde junto com os backups no pen drive.**

---

Preparado por: Eng. Automação Sênior
Data: 15/Nov/2025 02:45
Versão: 1.0
