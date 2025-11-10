# ✅ Checklist - Próximos Passos

## 📋 Resumo Rápido

**Problema resolvido**: Descobrimos que o ladder sobrescreve S0/S1 quando E2/E4 estão OFF
**Solução implementada**: Usar bits internos 48-50 que o ladder vai ler
**Status atual**: ✅ Código Python atualizado e testado | ⏳ Falta modificar ladder

---

## ✅ O que JÁ ESTÁ PRONTO

- [x] Diagnóstico completo do problema (ladder sobrescreve saídas)
- [x] Bits internos identificados e validados (48-52)
- [x] Script de teste criado (`test_write_internal_bits.py`)
- [x] Teste executado com sucesso (100% passou)
- [x] Código `main_server.py` atualizado
- [x] Documentação completa criada:
  - [x] `SOLUCAO_BITS_INTERNOS.md` (explicação técnica)
  - [x] `GUIA_MODIFICACAO_LADDER.md` (passo a passo detalhado)
  - [x] `RESUMO_SOLUCAO_FINAL.md` (visão geral)
  - [x] `CHECKLIST_PROXIMOS_PASSOS.md` (este arquivo)

---

## 🔧 O que VOCÊ PRECISA FAZER

### Opção A: Com Acesso ao WinSUP (Modificar Ladder)

#### Passo 1: Backup (OBRIGATÓRIO)

```bash
cd /home/lucas-junges/Documents/clientes/w\&co
cp clp.sup clp.sup.backup_$(date +%Y%m%d_%H%M%S)
ls -lh clp.sup*
```

**Verificar**: Deve aparecer 2 arquivos (`clp.sup` e `clp.sup.backup_...`)

#### Passo 2: Abrir WinSUP

```bash
wine ~/.wine/drive_c/WINSUPSW/winsup.exe
```

**Se der erro**: Executar primeiro `./setup_winsup_wine.sh`

#### Passo 3: Seguir Guia Completo

Abrir e seguir **linha por linha**:
```bash
cat GUIA_MODIFICACAO_LADDER.md
```

**Resumo do que fazer**:
1. Carregar `clp.sup` no WinSUP
2. Editar rotina ROT0
3. Adicionar 3 novas linhas (leitura de bits Modbus)
4. Modificar 2 linhas existentes (proteção)
5. Salvar como `clp_com_modbus.sup`
6. Upload para o CLP

#### Passo 4: Teste Final

```bash
# Após upload, testar:
python3 test_write_internal_bits.py

# Depois testar com IHM:
python3 main_server.py --live --port /dev/ttyUSB0
```

**Esperado**: Clicar AVANÇAR → Multímetro mede 24VDC em S0

---

### Opção B: Sem Acesso ao Ladder (Testar Parcial)

Se você **não pode modificar o ladder agora**, ainda pode testar que a comunicação está funcionando:

```bash
# Terminal 1: Iniciar servidor
python3 main_server.py --live --port /dev/ttyUSB0

# Terminal 2: Monitorar logs
tail -f ihm_server.log

# Terminal 3: Servidor HTTP
python3 -m http.server 8000

# Navegador
xdg-open http://localhost:8000/test_websocket.html
```

**Clicar AVANÇAR e verificar log**:
- ✅ Deve mostrar: `Pulsing Modbus internal bit 48 (0x0030) for FORWARD`
- ✅ Resposta: `{"success": true, "control": "FORWARD"}`
- ⚠️ **Multímetro ainda não vai medir 24V** (precisa modificar ladder)

Mas confirma que **comunicação WebSocket → Modbus está OK!**

---

## 📊 Diagrama do Fluxo Completo

```
┌─────────────┐
│  Navegador  │
│  (Tablet)   │
└──────┬──────┘
       │ WebSocket
       │ ws://localhost:8080
       ▼
┌─────────────────┐
│ main_server.py  │
│ (Python)        │
└──────┬──────────┘
       │ Modbus RTU
       │ write_coil(48, TRUE)  ← Bit interno 0x0030
       ▼
┌─────────────────┐
│  CLP MPC4004    │
│                 │
│  ┌───────────┐  │
│  │ Ladder    │  │ ← PRECISA SER MODIFICADO
│  │ Logic     │  │    para ler bit 48 e ativar S0
│  └─────┬─────┘  │
│        │        │
│        ▼        │
│  ┌───────────┐  │
│  │ S0 (384)  │  │ ← Saída física
│  └─────┬─────┘  │
└────────┼────────┘
         │
         ▼
    24VDC (Multímetro)
```

**ATUALMENTE**:
- ✅ Navegador → main_server.py **FUNCIONA**
- ✅ main_server.py → CLP **FUNCIONA**
- ✅ CLP recebe bit 48 **FUNCIONA**
- ⏳ Ladder lê bit 48 e ativa S0 **PRECISA MODIFICAR**

---

## 🎯 Resultado Final Esperado

Após modificar o ladder:

1. **Clicar AVANÇAR** no navegador
2. WebSocket envia `{"action": "control_button", "control": "FORWARD"}`
3. main_server.py escreve Modbus: `write_coil(48, TRUE)`
4. **Ladder detecta bit 48 = ON**
5. **Ladder ativa S0 (coil 384)**
6. Multímetro mede **~24VDC** por 100ms-2s
7. Ladder desliga S0 automaticamente

---

## 📁 Arquivos Importantes

```
/home/lucas-junges/Documents/clientes/w&co/

Documentação:
  📄 RESUMO_SOLUCAO_FINAL.md        ← Leia primeiro (visão geral)
  📄 SOLUCAO_BITS_INTERNOS.md       ← Explicação técnica
  📄 GUIA_MODIFICACAO_LADDER.md     ← Passo a passo WinSUP
  📄 CHECKLIST_PROXIMOS_PASSOS.md   ← Este arquivo

Código (já atualizado):
  ✅ main_server.py                 ← Usa bits 48-50
  ✅ modbus_client.py               ← Sem mudanças
  ✅ state_manager.py               ← Sem mudanças

Testes:
  🧪 test_write_internal_bits.py   ← PASSOU 100%
  🧪 test_modbus_s0_direct.py      ← Diagnóstico
  🧪 test_s0_fast_read.py          ← Descobriu problema

Ladder (precisa modificar):
  ⏳ clp.sup                        ← Original
  🎯 clp_com_modbus.sup            ← Criar no WinSUP
```

---

## ⚙️ Comandos Rápidos

### Testar bits internos:
```bash
cd /home/lucas-junges/Documents/clientes/w\&co
python3 test_write_internal_bits.py
```
**Esperado**: Todos os testes passam (✓ PASS, ✓ ESTÁVEL)

### Iniciar sistema completo:
```bash
# Terminal 1
python3 main_server.py --live --port /dev/ttyUSB0

# Terminal 2
python3 -m http.server 8000

# Navegador
xdg-open http://localhost:8000/test_websocket.html
```

### Verificar logs:
```bash
tail -f ihm_server.log
```

### Backup do ladder:
```bash
cp clp.sup clp.sup.backup_$(date +%Y%m%d_%H%M%S)
```

---

## ❓ Perguntas Frequentes

### Q: Os bits 48-50 já funcionam?
**A**: Sim! O teste `test_write_internal_bits.py` confirmou que podemos escrever e ler esses bits sem problemas. Eles permanecem estáveis e não são sobrescritos pelo ladder.

### Q: Por que não medimos tensão em S0 ainda?
**A**: Porque o ladder atual **não sabe** que deve ler o bit 48 e ativar S0. Ele só conhece as entradas físicas E2/E4. Precisamos "ensinar" o ladder a ler os bits Modbus.

### Q: É seguro modificar o ladder?
**A**: Sim, desde que:
1. Faça backup antes (`cp clp.sup clp.sup.backup_...`)
2. Motor 380V esteja DESLIGADO
3. Siga o guia passo a passo
4. Teste em modo manual primeiro

### Q: E se der errado?
**A**: Basta restaurar o backup:
```bash
cp clp.sup.backup_* clp.sup
# Depois fazer upload do clp.sup via WinSUP
```

### Q: Quanto tempo leva?
**A**:
- Modificar ladder: 30-60 min (primeira vez)
- Upload para CLP: 5 min
- Teste: 10 min
- **Total: ~1-2 horas**

---

## 🚨 Avisos de Segurança

- ⚠️ **SEMPRE** faça backup antes de modificar
- ⚠️ **NUNCA** teste com motor 380V ligado sem supervisão
- ⚠️ **VERIFIQUE** que máquina está em modo MANUAL
- ⚠️ **TENHA** chave de emergência acessível
- ⚠️ Se não tem certeza, **PERGUNTE** antes de fazer upload

---

## ✉️ Precisa de Ajuda?

Se tiver dúvidas ao modificar o ladder:

1. **Consulte**: `GUIA_MODIFICACAO_LADDER.md` (passo a passo detalhado)
2. **Releia**: Seção específica que está com dúvida
3. **Verifique**: Manual WinSUP para sintaxe de instruções
4. **Teste**: Em modo stub antes de fazer upload

---

## 🎉 Quando Estiver Tudo Pronto

Você vai saber que funcionou quando:

1. ✅ Abrir IHM web no navegador
2. ✅ Clicar AVANÇAR
3. ✅ Ver no log: `Pulsing Modbus internal bit 48`
4. ✅ **Multímetro medir ~24VDC em S0** ← ESTE É O OBJETIVO!
5. ✅ Após 100ms-2s, tensão cair para 0V
6. ✅ Mesma coisa para RECUAR (S1)
7. ✅ PARADA desligar ambos imediatamente

**Isso significa que a IHM web está 100% funcional!** 🎊

---

**Última atualização**: 2025-11-08 23:45
**Próximo passo**: Modificar ladder seguindo `GUIA_MODIFICACAO_LADDER.md`
