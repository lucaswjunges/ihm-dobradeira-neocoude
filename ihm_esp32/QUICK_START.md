# ⚡ Início Rápido - IHM Web Raspberry Pi 3B+

Guia ultra-resumido para colocar a IHM funcionando em **menos de 10 minutos**.

---

## 📋 Checklist Hardware

- [ ] Raspberry Pi 3B+ com microSD 16GB+ (Raspberry Pi OS Lite instalado)
- [ ] Fonte 5V 3A conectada
- [ ] Conversor USB-RS485 (opcional para teste inicial)
- [ ] Acesso SSH ao Raspberry Pi

---

## 🚀 3 Comandos = Sistema Rodando

### 1️⃣ Clonar Repositório

```bash
cd /home/pi
git clone https://github.com/seu-usuario/ihm_neocoude.git
cd ihm_neocoude/ihm_esp32
```

### 2️⃣ Instalar Tudo (Automático)

```bash
sudo bash scripts/install.sh
```

⏱️ **Aguarde 5-10 minutos** (download + instalação)

### 3️⃣ Reiniciar

```bash
sudo reboot
```

---

## ✅ Verificar Funcionamento

Após ~40 segundos do reboot:

### No Tablet/Notebook:

1. **Procurar WiFi:** `IHM_NEOCOUDE` (senha: `dobradeira123`)
2. **Abrir navegador:** http://192.168.50.1
3. **Pronto!** Interface web deve aparecer

### Via SSH (diagnóstico):

```bash
# Status geral do sistema
bash scripts/check_status.sh

# Ou verificar serviços manualmente:
sudo systemctl status ihm       # Servidor IHM
sudo systemctl status hostapd   # WiFi AP
sudo systemctl status dnsmasq   # DHCP

# Ver logs em tempo real:
sudo journalctl -u ihm -f
```

---

## 🔧 Comandos Úteis

### Controlar Servidor

```bash
# Parar
sudo systemctl stop ihm

# Iniciar
sudo systemctl start ihm

# Reiniciar
sudo systemctl restart ihm

# Ver status
sudo systemctl status ihm

# Ver logs
sudo journalctl -u ihm -f
```

### Trocar Senha WiFi

```bash
sudo nano /etc/hostapd/hostapd.conf
# Alterar: wpa_passphrase=SUA_NOVA_SENHA
sudo systemctl restart hostapd
```

### Testar Manualmente (Modo STUB - sem CLP)

```bash
cd /home/pi/ihm_esp32
bash scripts/start_ihm.sh
# Escolher opção 2 (STUB)
```

### Ver Clientes Conectados no WiFi

```bash
iw dev wlan0 station dump
```

---

## 🐛 Troubleshooting 1-Liner

| Problema | Solução |
|----------|---------|
| WiFi não aparece | `sudo systemctl restart hostapd` |
| Página não abre | `sudo systemctl restart ihm` |
| USB não detectado | `ls /dev/ttyUSB*` (conectar conversor) |
| Permissão negada USB | `sudo usermod -a -G dialout pi && logout` |
| Ver logs de erro | `sudo journalctl -u ihm -n 50` |

---

## 📞 Suporte

- **Documentação completa:** `INSTALL.md`
- **Arquitetura do sistema:** `CLAUDE.md`
- **Status do sistema:** `bash scripts/check_status.sh`

---

**Desenvolvido por:** Eng. Lucas William Junges  
**Versão:** 2.0-RPI3B+  
**Data:** Novembro 2025
