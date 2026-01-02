"""
WiFi Manager - Gerenciamento de WiFi Dongle USB
================================================

Gerencia conexão WiFi STA (Station) via dongle USB para:
- Detectar dongle WiFi USB conectado (wlan1)
- Conectar em redes WiFi externas
- Configurar NAT para rotear internet para rede AP
- Persistir configurações em arquivo JSON

Arquitetura:
- wlan0: Interface WiFi interna do RPi (modo AP - IHM_NEOCOUDE)
- wlan1: Dongle WiFi USB (modo STA - conecta em rede externa)
"""

import subprocess
import json
import os
import time
import asyncio
from pathlib import Path
from typing import Optional, Dict, List, Tuple


class WiFiManager:
    """Gerenciador de WiFi Dongle USB para Raspberry Pi"""

    # Arquivo de configuração persistente
    CONFIG_FILE = Path(__file__).parent / 'wifi_config.json'

    # Interface do dongle USB (segunda interface WiFi)
    DONGLE_INTERFACE = 'wlan1'

    # Interface AP interna
    AP_INTERFACE = 'wlan0'

    # Configuração padrão
    DEFAULT_CONFIG = {
        'ssid': 'Optimos Construtora',
        'password': '992234556',
        'auto_connect': True
    }

    def __init__(self):
        """Inicializa o gerenciador WiFi"""
        self.config = self._load_config()
        self._nat_enabled = False
        # Habilita NAT por padrão na inicialização
        self.enable_nat()

    def _load_config(self) -> Dict:
        """Carrega configuração do arquivo JSON"""
        if self.CONFIG_FILE.exists():
            try:
                with open(self.CONFIG_FILE, 'r') as f:
                    config = json.load(f)
                    # Garante campos obrigatórios
                    for key, value in self.DEFAULT_CONFIG.items():
                        if key not in config:
                            config[key] = value
                    return config
            except Exception as e:
                print(f"[WiFi] Erro ao carregar config: {e}")
        return self.DEFAULT_CONFIG.copy()

    def _save_config(self):
        """Salva configuração no arquivo JSON"""
        try:
            with open(self.CONFIG_FILE, 'w') as f:
                json.dump(self.config, f, indent=2)
            print(f"[WiFi] Config salva em {self.CONFIG_FILE}")
        except Exception as e:
            print(f"[WiFi] Erro ao salvar config: {e}")

    def is_dongle_connected(self) -> bool:
        """Verifica se o dongle WiFi USB está fisicamente conectado"""
        try:
            # Verifica se interface wlan1 existe
            result = subprocess.run(
                ['ip', 'link', 'show', self.DONGLE_INTERFACE],
                capture_output=True, text=True, timeout=5
            )
            return result.returncode == 0
        except Exception:
            return False

    def get_dongle_info(self) -> Optional[Dict]:
        """Retorna informações do dongle WiFi USB via lsusb"""
        try:
            result = subprocess.run(
                ['lsusb'],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                # Procura por adaptadores WiFi comuns
                wifi_keywords = ['Wireless', 'WiFi', 'WLAN', '802.11', 'Ralink', 'RTL', 'Realtek']
                for line in result.stdout.split('\n'):
                    if any(kw.lower() in line.lower() for kw in wifi_keywords):
                        return {'usb_info': line.strip()}
            return None
        except Exception:
            return None

    def get_interface_ip(self, interface: str) -> Optional[str]:
        """Retorna o IP de uma interface de rede"""
        try:
            result = subprocess.run(
                ['ip', '-4', 'addr', 'show', interface],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                # Extrai IP da saída (formato: inet 192.168.50.1/24)
                for line in result.stdout.split('\n'):
                    if 'inet ' in line:
                        parts = line.strip().split()
                        for i, part in enumerate(parts):
                            if part == 'inet' and i + 1 < len(parts):
                                ip = parts[i + 1].split('/')[0]
                                return ip
            return None
        except Exception:
            return None

    def get_ap_ip(self) -> Optional[str]:
        """Retorna IP da interface AP (wlan0)"""
        return self.get_interface_ip(self.AP_INTERFACE)

    def get_dongle_ip(self) -> Optional[str]:
        """Retorna IP do dongle WiFi (wlan1)"""
        return self.get_interface_ip(self.DONGLE_INTERFACE)

    def get_tailscale_ip(self) -> Optional[str]:
        """Retorna IP do Tailscale (interface tailscale0)"""
        return self.get_interface_ip('tailscale0')

    def is_dongle_connected_to_wifi(self) -> bool:
        """Verifica se o dongle está conectado a uma rede WiFi"""
        try:
            result = subprocess.run(
                ['iw', 'dev', self.DONGLE_INTERFACE, 'link'],
                capture_output=True, text=True, timeout=5
            )
            return 'Connected to' in result.stdout or 'SSID:' in result.stdout
        except Exception:
            return False

    def get_dongle_ssid(self) -> Optional[str]:
        """Retorna SSID da rede WiFi conectada no dongle"""
        try:
            result = subprocess.run(
                ['iw', 'dev', self.DONGLE_INTERFACE, 'link'],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if 'SSID:' in line:
                        return line.split('SSID:')[1].strip()
            return None
        except Exception:
            return None

    def scan_networks(self) -> List[Dict]:
        """Escaneia redes WiFi disponíveis pelo dongle"""
        networks = []
        try:
            # Primeiro, ativa a interface se necessário
            subprocess.run(
                ['sudo', 'ip', 'link', 'set', self.DONGLE_INTERFACE, 'up'],
                capture_output=True, timeout=5
            )
            time.sleep(1)

            # Escaneia redes
            result = subprocess.run(
                ['sudo', 'iw', 'dev', self.DONGLE_INTERFACE, 'scan'],
                capture_output=True, text=True, timeout=30
            )

            if result.returncode == 0:
                current_network = {}
                for line in result.stdout.split('\n'):
                    line = line.strip()
                    if line.startswith('BSS '):
                        if current_network and 'ssid' in current_network:
                            networks.append(current_network)
                        current_network = {'bssid': line.split()[1].replace('(', '').replace(')', '')}
                    elif line.startswith('SSID:'):
                        ssid = line.split(':', 1)[1].strip()
                        if ssid:  # Ignora SSIDs vazios
                            current_network['ssid'] = ssid
                    elif 'signal:' in line:
                        try:
                            signal = line.split(':')[1].strip().split()[0]
                            current_network['signal'] = int(float(signal))
                        except:
                            pass

                if current_network and 'ssid' in current_network:
                    networks.append(current_network)

        except subprocess.TimeoutExpired:
            print("[WiFi] Timeout ao escanear redes")
        except Exception as e:
            print(f"[WiFi] Erro ao escanear: {e}")

        # Remove duplicatas e ordena por sinal
        seen = set()
        unique_networks = []
        for net in networks:
            if net.get('ssid') and net['ssid'] not in seen:
                seen.add(net['ssid'])
                unique_networks.append(net)

        return sorted(unique_networks, key=lambda x: x.get('signal', -100), reverse=True)

    def connect_to_wifi(self, ssid: str, password: str, save: bool = True) -> Tuple[bool, str]:
        """
        Conecta o dongle WiFi a uma rede

        Args:
            ssid: Nome da rede WiFi
            password: Senha da rede
            save: Se True, salva as credenciais na configuração

        Returns:
            Tupla (sucesso, mensagem)
        """
        if not self.is_dongle_connected():
            return False, "Dongle WiFi USB não detectado"

        try:
            # Cria arquivo de configuração wpa_supplicant temporário
            wpa_conf = f'''
ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1
country=BR

network={{
    ssid="{ssid}"
    psk="{password}"
    key_mgmt=WPA-PSK
}}
'''
            # Salva configuração temporária
            conf_file = Path('/tmp/wpa_supplicant_dongle.conf')
            with open(conf_file, 'w') as f:
                f.write(wpa_conf)

            # Para wpa_supplicant existente no dongle
            subprocess.run(
                ['sudo', 'killall', '-9', 'wpa_supplicant'],
                capture_output=True, timeout=5
            )
            time.sleep(1)

            # Ativa interface
            subprocess.run(
                ['sudo', 'ip', 'link', 'set', self.DONGLE_INTERFACE, 'up'],
                capture_output=True, timeout=5
            )

            # Inicia wpa_supplicant no dongle
            result = subprocess.run(
                ['sudo', 'wpa_supplicant', '-B', '-i', self.DONGLE_INTERFACE,
                 '-c', str(conf_file), '-D', 'nl80211,wext'],
                capture_output=True, text=True, timeout=10
            )

            if result.returncode != 0:
                return False, f"Erro ao iniciar wpa_supplicant: {result.stderr}"

            # Aguarda conexão
            time.sleep(3)

            # Solicita IP via DHCP
            subprocess.run(
                ['sudo', 'dhclient', '-v', self.DONGLE_INTERFACE],
                capture_output=True, timeout=30
            )

            # Aguarda IP
            time.sleep(3)

            # Verifica se conectou
            if self.is_dongle_connected_to_wifi():
                ip = self.get_dongle_ip()

                # Salva configuração se solicitado
                if save:
                    self.config['ssid'] = ssid
                    self.config['password'] = password
                    self._save_config()

                # Habilita NAT automaticamente
                self.enable_nat()

                return True, f"Conectado! IP: {ip}"
            else:
                return False, "Falha ao conectar. Verifique SSID e senha."

        except subprocess.TimeoutExpired:
            return False, "Timeout ao conectar"
        except Exception as e:
            return False, f"Erro: {str(e)}"

    def disconnect_wifi(self) -> Tuple[bool, str]:
        """Desconecta o dongle da rede WiFi"""
        try:
            # Para wpa_supplicant
            subprocess.run(
                ['sudo', 'wpa_cli', '-i', self.DONGLE_INTERFACE, 'disconnect'],
                capture_output=True, timeout=5
            )

            # Libera IP
            subprocess.run(
                ['sudo', 'dhclient', '-r', self.DONGLE_INTERFACE],
                capture_output=True, timeout=5
            )

            # Desabilita NAT
            self.disable_nat()

            return True, "Desconectado"
        except Exception as e:
            return False, f"Erro: {str(e)}"

    def enable_nat(self) -> bool:
        """
        Habilita NAT para rotear internet do dongle (wlan1) para AP (wlan0)

        Dispositivos conectados na rede IHM_NEOCOUDE terão acesso à internet
        através do dongle WiFi USB.
        """
        try:
            # Habilita IP forwarding
            subprocess.run(
                ['sudo', 'sysctl', '-w', 'net.ipv4.ip_forward=1'],
                capture_output=True, timeout=5
            )

            # Limpa regras antigas de NAT
            subprocess.run(
                ['sudo', 'iptables', '-t', 'nat', '-F'],
                capture_output=True, timeout=5
            )

            # Configura MASQUERADE (NAT) no dongle
            subprocess.run(
                ['sudo', 'iptables', '-t', 'nat', '-A', 'POSTROUTING',
                 '-o', self.DONGLE_INTERFACE, '-j', 'MASQUERADE'],
                capture_output=True, timeout=5
            )

            # Permite forwarding da AP para dongle
            subprocess.run(
                ['sudo', 'iptables', '-A', 'FORWARD',
                 '-i', self.AP_INTERFACE, '-o', self.DONGLE_INTERFACE,
                 '-j', 'ACCEPT'],
                capture_output=True, timeout=5
            )

            # Permite forwarding de retorno (established connections)
            subprocess.run(
                ['sudo', 'iptables', '-A', 'FORWARD',
                 '-i', self.DONGLE_INTERFACE, '-o', self.AP_INTERFACE,
                 '-m', 'state', '--state', 'RELATED,ESTABLISHED',
                 '-j', 'ACCEPT'],
                capture_output=True, timeout=5
            )

            self._nat_enabled = True
            print("[WiFi] NAT habilitado - Internet disponível na rede AP")
            return True

        except Exception as e:
            print(f"[WiFi] Erro ao habilitar NAT: {e}")
            return False

    def disable_nat(self) -> bool:
        """Desabilita NAT"""
        try:
            # Limpa regras de NAT
            subprocess.run(
                ['sudo', 'iptables', '-t', 'nat', '-F'],
                capture_output=True, timeout=5
            )
            subprocess.run(
                ['sudo', 'iptables', '-F', 'FORWARD'],
                capture_output=True, timeout=5
            )

            self._nat_enabled = False
            print("[WiFi] NAT desabilitado")
            return True

        except Exception as e:
            print(f"[WiFi] Erro ao desabilitar NAT: {e}")
            return False

    def is_nat_enabled(self) -> bool:
        """Verifica se NAT está habilitado"""
        return self._nat_enabled

    def get_status(self) -> Dict:
        """Retorna status completo do WiFi"""
        dongle_connected = self.is_dongle_connected()
        wifi_connected = self.is_dongle_connected_to_wifi() if dongle_connected else False

        status = {
            'dongle_detected': dongle_connected,
            'dongle_info': self.get_dongle_info() if dongle_connected else None,
            'dongle_interface': self.DONGLE_INTERFACE,
            'wifi_connected': wifi_connected,
            'connected_ssid': self.get_dongle_ssid() if wifi_connected else None,
            'dongle_ip': self.get_dongle_ip() if wifi_connected else None,
            'ap_interface': self.AP_INTERFACE,
            'ap_ip': self.get_ap_ip(),
            'ap_ssid': 'IHM_NEOCOUDE',
            'tailscale_ip': self.get_tailscale_ip(),
            'nat_enabled': self._nat_enabled,
            'config': {
                'ssid': self.config.get('ssid', ''),
                'auto_connect': self.config.get('auto_connect', True)
                # Não expõe a senha por segurança
            }
        }
        return status

    def set_config(self, ssid: str, password: str, auto_connect: bool = True):
        """Atualiza configuração de WiFi"""
        self.config['ssid'] = ssid
        self.config['password'] = password
        self.config['auto_connect'] = auto_connect
        self._save_config()

    async def auto_connect_loop(self):
        """
        Loop assíncrono que tenta conectar automaticamente quando:
        - Dongle é detectado
        - Não está conectado a uma rede
        - Auto-connect está habilitado
        """
        print("[WiFi] Auto-connect loop iniciado")
        while True:
            try:
                if self.config.get('auto_connect', True):
                    if self.is_dongle_connected() and not self.is_dongle_connected_to_wifi():
                        ssid = self.config.get('ssid')
                        password = self.config.get('password')

                        if ssid and password:
                            print(f"[WiFi] Tentando conectar automaticamente em '{ssid}'...")
                            success, msg = self.connect_to_wifi(ssid, password, save=False)
                            print(f"[WiFi] Auto-connect: {msg}")

            except Exception as e:
                print(f"[WiFi] Erro no auto-connect: {e}")

            await asyncio.sleep(30)  # Verifica a cada 30 segundos


# Singleton para uso global
_wifi_manager: Optional[WiFiManager] = None

def get_wifi_manager() -> WiFiManager:
    """Retorna instância singleton do WiFiManager"""
    global _wifi_manager
    if _wifi_manager is None:
        _wifi_manager = WiFiManager()
    return _wifi_manager


# Teste standalone
if __name__ == '__main__':
    wm = WiFiManager()
    print("=== Status WiFi ===")
    status = wm.get_status()
    for key, value in status.items():
        print(f"  {key}: {value}")

    if wm.is_dongle_connected():
        print("\n=== Redes Disponíveis ===")
        networks = wm.scan_networks()
        for net in networks[:10]:  # Mostra top 10
            print(f"  {net.get('ssid', '???')} ({net.get('signal', '?')} dBm)")
