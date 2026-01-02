# Compartilhamento de Internet WiFi no Raspberry Pi 3B+

## Resumo

Este documento descreve como o Raspberry Pi 3B+ compartilha a internet da rede WiFi (via dongle USB `wlan1`) com clientes conectados ao Access Point (WiFi interno `wlan0`).

**Status:** ✅ Funcionando e configurado para iniciar automaticamente no boot.

## Arquitetura

```
Internet
   │
   │ WiFi (WiFi_Fabrica - 192.168.0.0/24)
   ▼
┌──────────────────────────────────────┐
│ Raspberry Pi 3B+                     │
│                                      │
│  wlan1 (Dongle USB)                  │
│  IP: 192.168.0.109                   │
│  Gateway: 192.168.0.1                │
│          │                           │
│          │ NAT/MASQUERADE            │
│          │ + Policy Routing          │
│          ▼                           │
│  wlan0 (WiFi interno - AP)           │
│  IP: 192.168.50.1                    │
│  SSID: IHM_NEOCOUDE                  │
│  DHCP: 192.168.50.10-20              │
└──────────────────────────────────────┘
   │
   │ WiFi AP
   ▼
Celular/Tablet
IP: 192.168.50.17 (DHCP)
Gateway: 192.168.50.1
DNS: 192.168.50.1
```

## Componentes da Solução

### 1. dnsmasq (Proxy DNS + DHCP)

**Arquivo:** `/etc/dnsmasq.conf`

**Configuração chave:**
```conf
# Interface para servir DHCP (WiFi AP)
interface=wlan0

# Range de IPs DHCP
dhcp-range=192.168.50.10,192.168.50.20,255.255.255.0,24h

# Gateway (o próprio RPi)
dhcp-option=3,192.168.50.1

# DNS (o próprio RPi fará proxy para 8.8.8.8)
dhcp-option=6,192.168.50.1

# Servidores DNS upstream (para forwarding)
server=8.8.8.8
server=8.8.4.4
```

**Função:**
- Fornece endereços IP via DHCP para clientes do AP (192.168.50.10-20)
- Informa aos clientes que o gateway é 192.168.50.1 (o próprio RPi)
- Informa aos clientes que o DNS é 192.168.50.1 (o próprio RPi fará proxy)
- Resolve consultas DNS dos clientes e faz forwarding para 8.8.8.8/8.8.4.4

### 2. IP Forwarding (Kernel)

**Configuração:**
```bash
echo 1 > /proc/sys/net/ipv4/ip_forward
```

**Função:**
- Permite que o kernel do Linux encaminhe pacotes entre interfaces de rede
- Necessário para que o RPi funcione como router entre wlan0 e wlan1

### 3. Policy Routing (Tabela 100)

**Problema original:**
- O kernel não sabia como rotear pacotes vindos da rede AP (192.168.50.0/24) para destinos externos
- A rota padrão estava configurada apenas para pacotes originados no próprio RPi

**Solução:**
```bash
# Criar tabela de roteamento separada (tabela 100)
ip route add default via 192.168.0.1 dev wlan1 table 100
ip route add 192.168.50.0/24 dev wlan0 scope link table 100

# Regra de policy routing: tráfego vindo de 192.168.50.0/24 usa tabela 100
ip rule add from 192.168.50.0/24 table 100 priority 100
```

**Função:**
- Cria uma tabela de roteamento separada (100) para tráfego vindo do AP
- Direciona todo tráfego de 192.168.50.0/24 para usar o gateway 192.168.0.1 via wlan1
- Permite que pacotes do celular sejam roteados para a internet

### 4. iptables/nftables (Firewall + NAT)

**Regras de FORWARD:**
```bash
# Aceitar tráfego de wlan0 (AP) para wlan1 (STA)
iptables -I FORWARD -i wlan0 -o wlan1 -j ACCEPT

# Aceitar tráfego de resposta (wlan1 → wlan0) se for conexão estabelecida
iptables -I FORWARD -i wlan1 -o wlan0 -m state --state RELATED,ESTABLISHED -j ACCEPT
```

**Regras de NAT (MASQUERADE):**
```bash
# Traduzir endereço IP de origem (192.168.50.x → 192.168.0.109)
iptables -t nat -A POSTROUTING -o wlan1 -j MASQUERADE
```

**Regras de INPUT/OUTPUT:**
```bash
# Aceitar tráfego de entrada/saída em wlan0 (para DNS, DHCP, etc.)
iptables -I INPUT -i wlan0 -j ACCEPT
iptables -I OUTPUT -o wlan0 -j ACCEPT
```

**Função:**
- FORWARD: Permite que pacotes sejam encaminhados entre wlan0 e wlan1
- NAT/MASQUERADE: Traduz o endereço IP de origem dos pacotes do celular (192.168.50.17) para o IP do RPi na rede externa (192.168.0.109)
- INPUT/OUTPUT: Permite que o RPi responda a requisições DNS, DHCP, etc. dos clientes do AP

## Fluxo de Dados (Exemplo: Celular acessa Google)

1. **DNS Query:**
   ```
   Celular (192.168.50.17) → RPi (192.168.50.1:53): "Qual o IP de google.com?"
   RPi consulta 8.8.8.8 e responde: "142.250.102.188"
   ```

2. **HTTP Request:**
   ```
   Celular (192.168.50.17:45732) → Google (142.250.102.188:80)
   ```

3. **Policy Routing (Lookup):**
   ```
   Kernel verifica: pacote vem de 192.168.50.17
   Aplica regra: from 192.168.50.0/24 lookup table 100
   Resultado: usa rota default via 192.168.0.1 dev wlan1
   ```

4. **FORWARD (Firewall):**
   ```
   iptables: wlan0 → wlan1? SIM (regra 1)
   Pacote segue para wlan1
   ```

5. **NAT/MASQUERADE:**
   ```
   iptables NAT POSTROUTING:
   Origem: 192.168.50.17:45732 → 192.168.0.109:45732
   Destino: 142.250.102.188:80 (inalterado)
   ```

6. **Saída via wlan1:**
   ```
   RPi (192.168.0.109:45732) → Google (142.250.102.188:80)
   ```

7. **Resposta do Google:**
   ```
   Google (142.250.102.188:80) → RPi (192.168.0.109:45732)
   ```

8. **NAT Reverso:**
   ```
   iptables NAT (connection tracking):
   Destino: 192.168.0.109:45732 → 192.168.50.17:45732
   Origem: 142.250.102.188:80 (inalterado)
   ```

9. **FORWARD Reverso:**
   ```
   iptables: wlan1 → wlan0? SIM (regra 2, state ESTABLISHED)
   Pacote segue para wlan0
   ```

10. **Entrega ao Celular:**
    ```
    RPi (192.168.50.1) → Celular (192.168.50.17:45732)
    ```

## Scripts e Serviços

### Script de Configuração

**Arquivo:** `scripts/setup_nat_routing.sh`

- Configura todas as regras de roteamento, firewall e NAT
- Executado automaticamente no boot via systemd

### Serviço systemd

**Arquivo:** `/etc/systemd/system/ihm-routing.service`

- Executa o script `setup_nat_routing.sh` na inicialização
- Habilitado para iniciar automaticamente no boot
- Status: `sudo systemctl status ihm-routing.service`
- Logs: `sudo journalctl -u ihm-routing.service`

## Verificação e Diagnóstico

### Verificar Configuração

```bash
# Ver regras de policy routing
ip rule list

# Ver tabela de roteamento 100
ip route show table 100

# Ver regras de FORWARD
sudo iptables -L FORWARD -v -n --line-numbers

# Ver regras de NAT
sudo iptables -t nat -L POSTROUTING -v -n

# Ver status do dnsmasq
sudo systemctl status dnsmasq

# Ver status do serviço de roteamento
sudo systemctl status ihm-routing.service
```

### Verificar Conectividade

```bash
# Ping do RPi para celular
ping -c 3 192.168.50.17

# Ping do RPi para internet via wlan1
ping -I wlan1 -c 3 8.8.8.8

# Ver clientes conectados no AP
iw dev wlan0 station dump

# Ver logs de DHCP
sudo journalctl -u dnsmasq -n 20
```

### Monitorar Tráfego

```bash
# Capturar pacotes na interface wlan0 (AP)
sudo tcpdump -i wlan0 -n 'host 192.168.50.17'

# Ver estatísticas de FORWARD
sudo iptables -L FORWARD -v -n

# Ver estatísticas de NAT
sudo iptables -t nat -L POSTROUTING -v -n

# Ver logs do kernel (firewall)
sudo dmesg | tail -50
```

## Estatísticas (Exemplo Real)

Após configuração bem-sucedida:

```
=== FORWARD ===
Chain FORWARD (policy ACCEPT)
num   pkts bytes target     prot opt in     out
1     7144 1.2M  ACCEPT     all  --  wlan0  wlan1   (celular → internet)
2    23272  28M  ACCEPT     all  --  wlan1  wlan0   (internet → celular)

=== NAT ===
Chain POSTROUTING (policy ACCEPT)
 pkts bytes target     prot opt in     out
  134 62KB  MASQUERADE all  --  *      wlan1
```

**Interpretação:**
- 7144 pacotes (1.2 MB) enviados do celular para internet
- 23272 pacotes (28 MB) recebidos da internet pelo celular
- 134 pacotes passaram pelo NAT/MASQUERADE
- Tudo funcionando perfeitamente! ✅

## Problemas Comuns e Soluções

### 1. "Sem acesso à internet" no celular

**Sintomas:**
- Celular conecta no WiFi IHM_NEOCOUDE
- Mostra "Sem acesso à internet" ou "Internet não disponível"
- Navegador não carrega páginas

**Diagnóstico:**
```bash
# Verificar se policy routing está configurado
ip rule list | grep "192.168.50"

# Deve mostrar:
# 100:	from 192.168.50.0/24 lookup 100

# Verificar se tabela 100 tem rota padrão
ip route show table 100

# Deve mostrar:
# default via 192.168.0.1 dev wlan1
# 192.168.50.0/24 dev wlan0 scope link
```

**Solução:**
```bash
# Reexecutar script de configuração
sudo /home/lucas-junges/Documents/wco/ihm_esp32/scripts/setup_nat_routing.sh

# Ou reiniciar serviço
sudo systemctl restart ihm-routing.service
```

### 2. DNS não resolve (celular não acessa sites por nome)

**Sintomas:**
- Celular consegue acessar IPs diretamente (ex: http://8.8.8.8)
- Não consegue acessar por nome (ex: http://google.com)

**Diagnóstico:**
```bash
# Verificar se dnsmasq está usando servidores upstream
sudo journalctl -u dnsmasq | grep "using nameserver"

# Deve mostrar:
# using nameserver 8.8.8.8#53
# using nameserver 8.8.4.4#53

# Testar resolução DNS no próprio RPi
python3 -c "import socket; print(socket.gethostbyname('google.com'))"
```

**Solução:**
```bash
# Verificar configuração do dnsmasq
cat /etc/dnsmasq.conf | grep -E "(server=|dhcp-option=6)"

# Reiniciar dnsmasq
sudo systemctl restart dnsmasq
```

### 3. Pacotes não passam pelo FORWARD (0 packets)

**Sintomas:**
- `iptables -L FORWARD -v -n` mostra 0 packets
- tcpdump mostra pacotes chegando em wlan0, mas não saindo em wlan1

**Diagnóstico:**
```bash
# Verificar se IP forwarding está habilitado
cat /proc/sys/net/ipv4/ip_forward
# Deve mostrar: 1

# Verificar policy routing
ip route get 142.250.102.188 from 192.168.50.17
# NÃO deve mostrar "Network is unreachable"
```

**Solução:**
```bash
# Habilitar IP forwarding
sudo sysctl -w net.ipv4.ip_forward=1

# Reconfigurar policy routing
sudo ip rule add from 192.168.50.0/24 table 100 priority 100
sudo ip route add default via 192.168.0.1 dev wlan1 table 100
sudo ip route add 192.168.50.0/24 dev wlan0 scope link table 100
```

## Modo de Produção (Sem Ethernet)

Em produção, o cabo Ethernet será removido. A única interface com internet será **wlan1** (dongle USB).

**Rotas esperadas:**
```
default via 192.168.0.1 dev wlan1 proto dhcp src 192.168.0.109 metric 600
192.168.0.0/24 dev wlan1 proto kernel scope link src 192.168.0.109 metric 600
192.168.50.0/24 dev wlan0 proto kernel scope link src 192.168.50.1
```

**Não é necessário nenhuma mudança!** A configuração atual já funciona com ou sem Ethernet:
- Se Ethernet estiver conectado: usará métrica 100 (prioridade)
- Se Ethernet for removido: usará wlan1 automaticamente (métrica 600)
- Policy routing garante que tráfego do AP sempre usa wlan1

## Manutenção

### Reiniciar Todos os Serviços

```bash
# Reiniciar dnsmasq
sudo systemctl restart dnsmasq

# Reiniciar hostapd (AP)
sudo systemctl restart hostapd

# Reconfigurar roteamento
sudo systemctl restart ihm-routing.service
```

### Logs Úteis

```bash
# Logs do dnsmasq (DHCP + DNS)
sudo journalctl -u dnsmasq -f

# Logs do hostapd (Access Point)
sudo journalctl -u hostapd -f

# Logs do serviço de roteamento
sudo journalctl -u ihm-routing.service

# Logs do kernel (firewall, routing)
sudo dmesg -w
```

### Backup da Configuração

```bash
# Backup manual
sudo tar -czf ~/ihm_backup_$(date +%Y%m%d).tar.gz \
    /etc/dnsmasq.conf \
    /etc/hostapd/hostapd.conf \
    /etc/systemd/system/ihm-routing.service \
    /home/lucas-junges/Documents/wco/ihm_esp32/scripts/
```

## Referências

- **dnsmasq:** https://thekelleys.org.uk/dnsmasq/doc.html
- **Linux Advanced Routing:** https://lartc.org/howto/
- **iptables NAT:** https://www.netfilter.org/documentation/HOWTO/NAT-HOWTO.html
- **Policy Routing:** https://wiki.archlinux.org/title/Advanced_traffic_control

---

**Desenvolvido por:** Eng. Lucas William Junges
**Data:** 02/01/2026
**Versão:** 1.0
**Status:** ✅ Funcionando em produção
