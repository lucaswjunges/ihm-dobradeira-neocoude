"""
boot.py - Configuração WiFi ESP32 (Modo Bridge AP+STA)
Executado automaticamente no boot
"""
import network
import time
import machine

# ========== CONFIGURAÇÕES WIFI ==========
# Rede que o ESP32 cria (para tablet conectar) - SEMPRE ATIVA
AP_SSID = 'IHM_NEOCOUDE'
AP_PASSWORD = 'dobradeira123'  # Min 8 caracteres

# Rede externa para internet (WiFi da casa/fábrica) - OPCIONAL
# Deixe vazio ('') para operar SEM internet externa
STA_SSID = 'NET_2G5F245C'  # Trocar para '' para desabilitar
STA_PASSWORD = 'natureza'
# =========================================

# LED interno (GPIO2)
led = machine.Pin(2, machine.Pin.OUT)

def setup_wifi():
    """Configura WiFi: STA prioritário, AP apenas se falhar"""
    print("\n" + "="*50)
    print("IHM WEB - DOBRADEIRA NEOCOUDE-HD-15 (ESP32)")
    print("="*50)

    sta_connected = False
    sta_ip = None

    # ====== ETAPA 1: Tentar conectar na rede externa (se configurada) ======
    if STA_SSID and STA_SSID.strip() != '':
        print(f"\n[1/2] Tentando conectar em '{STA_SSID}'...")
        sta = network.WLAN(network.STA_IF)
        sta.active(True)

        try:
            sta.connect(STA_SSID, STA_PASSWORD)

            # Aguarda conexão (max 10s)
            timeout = 10
            while not sta.isconnected() and timeout > 0:
                led.value(not led.value())  # Pisca
                time.sleep(0.5)
                timeout -= 0.5

            if sta.isconnected():
                sta_config = sta.ifconfig()
                sta_ip = sta_config[0]
                sta_connected = True
                print(f"✓ Conectado em '{STA_SSID}'")
                print(f"  IP: {sta_ip}")
                print(f"  Gateway: {sta_config[2]}")
                print(f"  DNS: {sta_config[3]}")
                led.value(1)  # LED aceso = conectado
            else:
                print(f"✗ Não conectou em '{STA_SSID}' (timeout)")
                print(f"  → Criando AP próprio...")
                sta.active(False)  # Desliga STA se não conectou
        except Exception as e:
            print(f"✗ Erro ao conectar: {e}")
            print(f"  → Criando AP próprio...")
            sta.active(False)
    else:
        print("\n[1/2] Rede externa não configurada")
        print("  → Criando AP próprio...")

    # ====== ETAPA 2: Decidir modo de operação ======
    if sta_connected:
        # Modo STA: Desliga AP, usa apenas rede externa
        print(f"\n[2/2] Desabilitando Access Point...")
        ap = network.WLAN(network.AP_IF)
        ap.active(False)
        print(f"✓ AP desabilitado (modo STA puro)")

        print("\n" + "="*50)
        print("SISTEMA PRONTO - MODO STA")
        print("="*50)
        print(f"Acesse: http://{sta_ip}")
        print(f"Rede: {STA_SSID}")
        print("Internet: ✓ Disponível")
        print("="*50)

    else:
        # Modo AP: Cria rede própria (fallback)
        print(f"\n[2/2] Criando Access Point...")
        ap = network.WLAN(network.AP_IF)
        ap.active(True)

        ap.ifconfig((
            '192.168.4.1',      # IP do ESP32
            '255.255.255.0',    # Netmask
            '192.168.4.1',      # Gateway
            '8.8.8.8'           # DNS
        ))

        ap.config(
            essid=AP_SSID,
            password=AP_PASSWORD,
            authmode=network.AUTH_WPA_WPA2_PSK,
            channel=6,
            hidden=False
        )

        time.sleep(2)

        if ap.active():
            print(f"✓ WiFi AP ativo")
            print(f"  SSID: {AP_SSID}")
            print(f"  Senha: {AP_PASSWORD}")
            print(f"  IP: 192.168.4.1")
            led.value(1)  # LED aceso = sistema pronto
        else:
            print("✗ ERRO: Falha ao criar AP!")
            led.value(0)
            return False

        print("\n" + "="*50)
        print("SISTEMA PRONTO - MODO AP")
        print("="*50)
        print(f"Acesse: http://192.168.4.1")
        print(f"SSID: {AP_SSID}")
        print("Internet: ✗ Não disponível")
        print("="*50)

    return True

# Executa configuração WiFi
setup_wifi()

# Coleta de lixo
import gc
gc.collect()
print(f"\nRAM livre: {gc.mem_free()} bytes")
print("")
