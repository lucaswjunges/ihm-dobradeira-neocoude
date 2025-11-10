# Guia: WinSUP 2 no Ubuntu 25.04 via Wine

## ✅ Configuração Confirmada

**Comunicação com CLP funcionando:**
- Porta: `/dev/ttyUSB0`
- Baudrate: 57600
- Paridade: None (N)
- Stop bits: 2
- Slave ID: 1
- Status: ✓ TESTADO E FUNCIONANDO

---

## 🎯 Método 1: Wine Padrão (RÁPIDO)

### Configuração das Portas COM

No Wine padrão (`~/.wine`), o mapeamento é:
- `COM33` → `/dev/ttyUSB0`

### Como usar no WinSUP

1. **Abra o WinSUP 2 normalmente**
2. **Configure a porta:**
   - Porta: **COM33** (digite manualmente, não busque)
   - Baudrate: **57600**
   - Paridade: **Nenhuma**
   - Stop bits: **2**
   - Slave ID: **1**

3. **Se a porta não aparecer:**
   - Feche o WinSUP
   - Dê permissão: `sudo chmod 666 /dev/ttyUSB0`
   - Abra o WinSUP novamente

---

## 🎯 Método 2: Wine Dedicado (MELHOR COMPATIBILIDADE)

### Usando o Wine Prefix Dedicado

Um Wine prefix dedicado está sendo configurado em `~/.wine-winsup` com:
- Arquitetura: 32-bit (melhor compatibilidade)
- COM1 → `/dev/ttyUSB0` (mais intuitivo)
- Bibliotecas Windows instaladas (VC++, .NET)

### Instalando WinSUP no Prefix Dedicado

```bash
# 1. Baixe o instalador do WinSUP (se ainda não tiver)
# 2. Instale com:
WINEPREFIX="$HOME/.wine-winsup" WINEARCH=win32 wine /caminho/para/setup_winsup.exe

# 3. Execute com:
./run_winsup.sh
```

### No WinSUP (prefix dedicado):
- Porta: **COM1** (mais simples!)
- Baudrate: **57600**
- Paridade: **Nenhuma**
- Stop bits: **2**
- Slave ID: **1**

---

## 🎯 Método 3: Via TCP/IP (ALTERNATIVA)

### Usar a Ponte ser2net

```bash
# Iniciar ponte (se não estiver rodando):
ser2net -c ser2net_clp.yaml -d > ser2net.log 2>&1 &

# Verificar se está ativa:
lsof -i :5000
```

### No WinSUP:
- Tipo: **TCP/IP ou Ethernet**
- Host: **127.0.0.1**
- Porta: **5000**
- Slave ID: **1**

---

## 🔧 Solução de Problemas

### "Porta não disponível" ou "Device not found"

```bash
# Verificar se porta existe:
ls -la /dev/ttyUSB*

# Dar permissão (temporária):
sudo chmod 666 /dev/ttyUSB0

# Dar permissão permanente (adicionar ao grupo dialout):
sudo usermod -a -G dialout $USER
# IMPORTANTE: Reinicie o sistema após este comando
```

### "Erro ao abrir canal" no WinSUP

1. **Verifique se outra aplicação está usando a porta:**
   ```bash
   lsof /dev/ttyUSB0
   ```

2. **Se aparecer `ser2net` ou outro programa, mate o processo:**
   ```bash
   sudo pkill ser2net
   # ou
   sudo fuser -k /dev/ttyUSB0
   ```

3. **Tente novamente no WinSUP**

### WinSUP não encontra o CLP

1. **Teste a comunicação fora do Wine:**
   ```bash
   python3 test_clp_working.py
   ```

2. **Se funcionar no Python mas não no Wine:**
   - O problema é mapeamento de portas COM
   - Tente o Método 3 (TCP/IP) como alternativa

---

## 📝 Verificação Rápida

### Checklist antes de conectar:

- [ ] CLP está ligado e energizado
- [ ] Cabo USB-RS485 conectado
- [ ] `/dev/ttyUSB0` existe: `ls -la /dev/ttyUSB*`
- [ ] Permissões OK: `ls -la /dev/ttyUSB0` (deve mostrar `rw-rw-rw-`)
- [ ] Nenhum programa usando a porta: `lsof /dev/ttyUSB0` (deve estar vazio)
- [ ] Comunicação Python OK: `python3 test_clp_working.py`

Se todos os itens acima estiverem OK, o WinSUP deve funcionar!

---

## 🚀 Dica de Ouro

**Se o WinSUP insistir em não funcionar via COM**, use o **Método 3 (TCP/IP)** que é mais confiável no Wine:

1. Inicie o ser2net: `ser2net -c ser2net_clp.yaml -d &`
2. No WinSUP: TCP/IP → 127.0.0.1:5000
3. Pronto! O ser2net faz a ponte transparente.

Essa é a **solução mais confiável** para aplicações Windows industriais no Wine.
