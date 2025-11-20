"""
boot.py - Configuração WiFi ESP32 (Modo AP - Access Point)
IHM Web acessível diretamente pelo tablet SEM depender da rede da fábrica

IMPORTANTE: Substitua o boot.py atual por este arquivo se quiser usar modo AP
"""
import network
import time
import machine

# ========== CONFIGURAÇÕES WIFI (MODO AP) ==========
AP_SSID = 'IHM_NEOCOUDE'
AP_PASSWORD = 'dobradeira123'  # Min 8 caracteres
AP_CHANNEL = 6  # Canal WiFi (1-13)
# ==================================================

# LED interno (GPIO2)
led = machine.Pin(2, machine.Pin.OUT)

def setup_wifi_ap():
    """Configura WiFi em modo AP (Access Point)"""
    print("\n" + "="*50)
    print("IHM WEB - DOBRADEIRA NEOCOUDE-HD-15 (ESP32)")
    print("="*50)

    # Desativa modo STA (station/cliente)
    sta = network.WLAN(network.STA_IF)
    sta.active(False)

    # Ativa modo AP
    print(f"\nCriando rede WiFi: '{AP_SSID}'...")
    ap = network.WLAN(network.AP_IF)
    ap.active(True)
    ap.config(essid=AP_SSID, password=AP_PASSWORD, channel=AP_CHANNEL)

    # Aguarda AP ficar ativo
    timeout = 5
    while not ap.active() and timeout > 0:
        led.value(not led.value())  # Pisca
        time.sleep(0.2)
        timeout -= 0.2

    if ap.active():
        ap_config = ap.ifconfig()
        print(f"✓ WiFi AP ativo!")
        print(f"  SSID: {AP_SSID}")
        print(f"  Senha: {AP_PASSWORD}")
        print(f"  IP: {ap_config[0]} (fixo)")
        print(f"  Gateway: {ap_config[2]}")
        print(f"  Canal: {AP_CHANNEL}")
        print("\n" + "-"*50)
        print("ACESSE A IHM WEB:")
        print(f"  1. Conecte o tablet na rede '{AP_SSID}'")
        print(f"  2. Abra navegador: http://{ap_config[0]}")
        print("-"*50)

        led.value(1)  # LED aceso = WiFi OK
        return ap_config[0]
    else:
        print("✗ ERRO: Falha ao criar rede WiFi AP")
        led.value(0)
        return None

# ========== EXECUÇÃO ==========
ip = setup_wifi_ap()

if not ip:
    print("\n✗ ERRO FATAL: WiFi não inicializado")
    print("  Verifique configurações e reinicie ESP32")

    # Pisca LED rapidamente = erro
    while True:
        led.value(not led.value())
        time.sleep(0.1)
else:
    print("\n✓ Boot concluído - main.py será executado")
    print("="*50 + "\n")
