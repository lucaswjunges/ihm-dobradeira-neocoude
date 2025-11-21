#!/bin/bash
# setup_advanced_features.sh - Recursos avançados opcionais
# ================================================================
# Autor: Lucas William Junges
# Data: 21/Nov/2025
# Descrição: Adiciona recursos profissionais ao sistema IHM

set -e

echo "═══════════════════════════════════════════════════════════"
echo "RECURSOS AVANÇADOS PARA IHM WEB"
echo "═══════════════════════════════════════════════════════════"
echo

# Menu de opções
PS3="Escolha uma opção (0 para sair): "
options=(
    "LED de status no painel (GPIO)"
    "Buzzer de alerta (GPIO)"
    "Monitoramento de temperatura do RPi"
    "Alertas via Telegram"
    "Logs remotos (rsyslog)"
    "Dashboard Grafana (métricas)"
    "Backup automático (cron)"
    "UPS/Bateria backup (detecção queda energia)"
    "SAIR"
)

select opt in "${options[@]}"
do
    case $opt in
        "LED de status no painel (GPIO)")
            echo
            echo "🔴🟢🔵 Instalando suporte a LEDs de status..."

            # Instalar biblioteca GPIO
            pip3 install gpiozero

            # Criar script de LEDs
            cat > /home/pi/ihm_neocoude/ihm_rpi/gpio_leds.py <<'EOF'
"""
gpio_leds.py - LEDs de status físicos no painel
================================================

Pinos GPIO usados:
  GPIO17 (pino 11) → LED VERDE   = WiFi conectado
  GPIO27 (pino 13) → LED AMARELO = Modbus OK
  GPIO22 (pino 15) → LED AZUL    = Cliente WebSocket conectado
  GPIO10 (pino 19) → LED VERMELHO = Erro/Emergência
"""

from gpiozero import LED
import time

class StatusLEDs:
    def __init__(self):
        self.led_wifi = LED(17)      # Verde
        self.led_modbus = LED(27)    # Amarelo
        self.led_client = LED(22)    # Azul
        self.led_error = LED(10)     # Vermelho

    def set_wifi(self, state: bool):
        """Liga/desliga LED WiFi"""
        if state:
            self.led_wifi.on()
        else:
            self.led_wifi.off()

    def set_modbus(self, state: bool):
        """Liga/desliga LED Modbus"""
        if state:
            self.led_modbus.on()
        else:
            self.led_modbus.off()

    def set_client(self, state: bool):
        """Liga/desliga LED Cliente"""
        if state:
            self.led_client.on()
        else:
            self.led_client.off()

    def set_error(self, state: bool):
        """Liga/desliga LED Erro"""
        if state:
            self.led_error.on()
        else:
            self.led_error.off()

    def blink_error(self, times=3):
        """Pisca LED de erro"""
        for _ in range(times):
            self.led_error.on()
            time.sleep(0.2)
            self.led_error.off()
            time.sleep(0.2)

    def test_all(self):
        """Testa todos os LEDs"""
        print("Testando LEDs...")
        for led in [self.led_wifi, self.led_modbus, self.led_client, self.led_error]:
            led.on()
            time.sleep(0.5)
            led.off()
        print("Teste concluído!")

    def cleanup(self):
        """Desliga todos os LEDs"""
        self.led_wifi.off()
        self.led_modbus.off()
        self.led_client.off()
        self.led_error.off()

# Uso no main_server.py:
# from gpio_leds import StatusLEDs
# leds = StatusLEDs()
# leds.set_wifi(True)  # WiFi conectado
# leds.set_modbus(modbus_client.connected)
# leds.set_client(len(self.clients) > 0)
EOF

            echo "   ✅ LEDs configurados!"
            echo "   📋 Pinos GPIO:"
            echo "      GPIO17 (pino 11) → LED VERDE (WiFi)"
            echo "      GPIO27 (pino 13) → LED AMARELO (Modbus)"
            echo "      GPIO22 (pino 15) → LED AZUL (Cliente)"
            echo "      GPIO10 (pino 19) → LED VERMELHO (Erro)"
            echo
            echo "   🔧 Adicione ao main_server.py:"
            echo "      from gpio_leds import StatusLEDs"
            echo "      leds = StatusLEDs()"
            echo "      leds.set_wifi(True)"
            ;;

        "Buzzer de alerta (GPIO)")
            echo
            echo "🔊 Instalando suporte a buzzer..."

            cat > /home/pi/ihm_neocoude/ihm_rpi/gpio_buzzer.py <<'EOF'
"""
gpio_buzzer.py - Buzzer de alertas sonoros
===========================================

Pino GPIO usado:
  GPIO18 (pino 12) → BUZZER (PWM)
"""

from gpiozero import TonalBuzzer
from gpiozero.tones import Tone
import time

class AlertBuzzer:
    def __init__(self):
        self.buzzer = TonalBuzzer(18)

    def beep_short(self):
        """Beep curto (confirmação)"""
        self.buzzer.play(Tone("A4"))
        time.sleep(0.1)
        self.buzzer.stop()

    def beep_long(self):
        """Beep longo (alerta)"""
        self.buzzer.play(Tone("C4"))
        time.sleep(0.5)
        self.buzzer.stop()

    def beep_error(self):
        """Som de erro (3 beeps rápidos)"""
        for _ in range(3):
            self.buzzer.play(Tone("E5"))
            time.sleep(0.15)
            self.buzzer.stop()
            time.sleep(0.1)

    def beep_emergency(self):
        """Som de emergência (sirene)"""
        for freq in range(400, 800, 50):
            self.buzzer.play(Tone(freq))
            time.sleep(0.05)
        self.buzzer.stop()

    def cleanup(self):
        """Para buzzer"""
        self.buzzer.stop()

# Uso:
# from gpio_buzzer import AlertBuzzer
# buzzer = AlertBuzzer()
# buzzer.beep_short()  # Ao receber comando
# buzzer.beep_error()  # Ao detectar erro Modbus
# buzzer.beep_emergency()  # Ao acionar emergência
EOF

            echo "   ✅ Buzzer configurado!"
            echo "   📋 Pino GPIO:"
            echo "      GPIO18 (pino 12) → BUZZER (ativo em 5V)"
            ;;

        "Monitoramento de temperatura do RPi")
            echo
            echo "🌡️  Instalando monitoramento de temperatura..."

            cat > /home/pi/ihm_neocoude/ihm_rpi/monitor_temp.py <<'EOF'
"""
monitor_temp.py - Monitora temperatura do Raspberry Pi
=======================================================
Alerta se CPU > 70°C (risco de throttling)
"""

import subprocess
import time

def get_cpu_temp():
    """Retorna temperatura da CPU em Celsius"""
    result = subprocess.run(['vcgencmd', 'measure_temp'], capture_output=True, text=True)
    temp_str = result.stdout.strip()
    # Formato: temp=52.1'C
    temp = float(temp_str.split('=')[1].split("'")[0])
    return temp

def check_temperature():
    """Verifica temperatura e retorna status"""
    temp = get_cpu_temp()

    if temp > 80:
        return {'status': 'CRITICAL', 'temp': temp, 'message': 'CPU MUITO QUENTE! Risco de desligamento!'}
    elif temp > 70:
        return {'status': 'WARNING', 'temp': temp, 'message': 'CPU quente, verifique ventilação'}
    else:
        return {'status': 'OK', 'temp': temp, 'message': 'Temperatura normal'}

# Adicionar ao state_manager.py:
# from monitor_temp import check_temperature
# temp_status = check_temperature()
# self.state['cpu_temp'] = temp_status['temp']
# self.state['cpu_temp_status'] = temp_status['status']
EOF

            echo "   ✅ Monitoramento de temperatura configurado!"
            echo "   🔧 Adicione ao state_manager.py"
            ;;

        "Alertas via Telegram")
            echo
            echo "📱 Instalando alertas via Telegram..."

            pip3 install python-telegram-bot

            cat > /home/pi/ihm_neocoude/ihm_rpi/telegram_alerts.py <<'EOF'
"""
telegram_alerts.py - Envia alertas via Telegram
================================================

Configuração:
1. Crie um bot com @BotFather no Telegram
2. Copie o TOKEN
3. Inicie conversa com o bot
4. Execute /start
5. Use get_chat_id() para descobrir seu CHAT_ID
"""

import asyncio
from telegram import Bot

class TelegramAlerts:
    def __init__(self, token: str, chat_id: str):
        self.bot = Bot(token=token)
        self.chat_id = chat_id

    async def send_alert(self, message: str):
        """Envia mensagem de alerta"""
        try:
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=f"🚨 IHM DOBRADEIRA ALERTA:\n\n{message}"
            )
            return True
        except Exception as e:
            print(f"Erro ao enviar Telegram: {e}")
            return False

    async def send_emergency(self):
        """Envia alerta de emergência"""
        await self.send_alert("⛔ PARADA DE EMERGÊNCIA ACIONADA!")

    async def send_modbus_error(self):
        """Envia alerta de falha Modbus"""
        await self.send_alert("⚠️ COMUNICAÇÃO MODBUS FALHOU!\nVerifique cabo RS485.")

    async def send_startup(self):
        """Envia mensagem de inicialização"""
        await self.send_alert("✅ Sistema IHM iniciado com sucesso")

# Configuração (SUBSTITUA COM SEUS DADOS):
# TOKEN = "123456789:ABCdefGHIjklMNOpqrsTUVwxyz"  # Do @BotFather
# CHAT_ID = "987654321"  # Seu chat ID

# Uso:
# telegram = TelegramAlerts(TOKEN, CHAT_ID)
# await telegram.send_startup()
EOF

            echo "   ✅ Telegram configurado!"
            echo "   📋 PRÓXIMOS PASSOS:"
            echo "      1. Abra Telegram e busque @BotFather"
            echo "      2. Digite /newbot e siga instruções"
            echo "      3. Copie o TOKEN"
            echo "      4. Edite telegram_alerts.py com TOKEN e CHAT_ID"
            ;;

        "Logs remotos (rsyslog)")
            echo
            echo "📡 Configurando logs remotos..."

            read -p "   IP do servidor de logs (ex: 192.168.0.10): " LOG_SERVER

            sudo tee -a /etc/rsyslog.conf > /dev/null <<EOF

# Enviar logs para servidor remoto
*.* @${LOG_SERVER}:514
EOF

            sudo systemctl restart rsyslog

            echo "   ✅ Logs sendo enviados para $LOG_SERVER:514"
            echo "   (Configure servidor com: sudo apt install rsyslog)"
            ;;

        "Dashboard Grafana (métricas)")
            echo
            echo "📊 Instalando Prometheus + Grafana..."

            # Prometheus exporter
            pip3 install prometheus-client

            cat > /home/pi/ihm_neocoude/ihm_rpi/metrics_exporter.py <<'EOF'
"""
metrics_exporter.py - Exporta métricas para Prometheus
=======================================================
Acesse http://<IP_RPI>:9090/metrics
"""

from prometheus_client import start_http_server, Gauge
import time

# Métricas
encoder_position = Gauge('dobradeira_encoder_degrees', 'Posição do encoder em graus')
motor_speed = Gauge('dobradeira_motor_rpm', 'Velocidade do motor em RPM')
modbus_connected = Gauge('dobradeira_modbus_connected', 'Status conexão Modbus')
websocket_clients = Gauge('dobradeira_websocket_clients', 'Clientes WebSocket conectados')
cpu_temp = Gauge('rpi_cpu_temp_celsius', 'Temperatura CPU Raspberry Pi')

def update_metrics(state):
    """Atualiza métricas com estado da máquina"""
    encoder_position.set(state.get('encoder_degrees', 0))
    motor_speed.set(state.get('motor_rpm', 0))
    modbus_connected.set(1 if state.get('modbus_connected') else 0)
    # websocket_clients atualizado manualmente
    # cpu_temp atualizado pelo monitor_temp.py

if __name__ == '__main__':
    # Inicia servidor HTTP na porta 9090
    start_http_server(9090)
    print("Prometheus exporter rodando em :9090/metrics")

    # Loop infinito
    while True:
        time.sleep(1)
EOF

            echo "   ✅ Prometheus exporter criado!"
            echo "   📋 Acesse métricas em: http://<IP_RPI>:9090/metrics"
            echo "   🔧 Instale Grafana em outro PC para dashboards"
            ;;

        "Backup automático (cron)")
            echo
            echo "💾 Configurando backup automático..."

            cat > /home/pi/backup_ihm.sh <<'EOF'
#!/bin/bash
# Backup automático da IHM

BACKUP_DIR="/home/pi/backups"
BACKUP_FILE="ihm_backup_$(date +%Y%m%d_%H%M%S).tar.gz"

mkdir -p $BACKUP_DIR

tar -czf "$BACKUP_DIR/$BACKUP_FILE" \
    /home/pi/ihm_neocoude \
    /etc/systemd/system/ihm.service \
    /etc/hostapd \
    /etc/dnsmasq.conf \
    2>/dev/null

# Manter apenas últimos 7 backups
cd $BACKUP_DIR
ls -t | tail -n +8 | xargs rm -f 2>/dev/null

echo "Backup salvo: $BACKUP_FILE"
EOF

            chmod +x /home/pi/backup_ihm.sh

            # Adicionar ao crontab (backup diário às 3h)
            (crontab -l 2>/dev/null; echo "0 3 * * * /home/pi/backup_ihm.sh >> /home/pi/backup.log 2>&1") | crontab -

            echo "   ✅ Backup automático configurado!"
            echo "   📅 Executa diariamente às 03:00"
            echo "   💾 Backups salvos em: /home/pi/backups/"
            ;;

        "UPS/Bateria backup (detecção queda energia)")
            echo
            echo "🔋 Configurando detecção de queda de energia..."

            pip3 install gpiozero

            cat > /home/pi/ihm_neocoude/ihm_rpi/ups_monitor.py <<'EOF'
"""
ups_monitor.py - Monitora UPS/bateria via GPIO
===============================================

Pino GPIO usado:
  GPIO23 (pino 16) → Entrada digital do UPS (LOW = energia OK, HIGH = bateria)

Hardware necessário:
  - UPS com saída digital (ex: StromPi 3)
  - Ou circuito detector de queda de tensão
"""

from gpiozero import Button
import subprocess

class UPSMonitor:
    def __init__(self, callback_power_lost=None):
        # Pino 23 com pull-down (LOW = AC OK, HIGH = bateria)
        self.ups_pin = Button(23, pull_up=False)

        # Callback quando energia cai
        if callback_power_lost:
            self.ups_pin.when_pressed = callback_power_lost

    def is_on_battery(self):
        """Retorna True se estiver em bateria"""
        return self.ups_pin.is_pressed

    def shutdown_safe(self):
        """Desliga sistema com segurança"""
        print("⚠️  QUEDA DE ENERGIA! Desligando sistema...")
        subprocess.run(['sudo', 'shutdown', '-h', 'now'])

# Uso no main_server.py:
# from ups_monitor import UPSMonitor
#
# def on_power_lost():
#     print("🔋 Energia caiu! Rodando em bateria...")
#     # Enviar alerta Telegram
#     # Fechar conexão Modbus
#     # Desligar após 2 minutos se não voltar
#
# ups = UPSMonitor(callback_power_lost=on_power_lost)
EOF

            echo "   ✅ Monitor UPS configurado!"
            echo "   📋 Pino GPIO:"
            echo "      GPIO23 (pino 16) → Entrada digital UPS"
            echo "   🔌 Conecte saída do UPS neste pino"
            ;;

        "SAIR")
            break
            ;;

        *) echo "Opção inválida: $REPLY";;
    esac
done

echo
echo "═══════════════════════════════════════════════════════════"
echo "✅ RECURSOS AVANÇADOS CONFIGURADOS"
echo "═══════════════════════════════════════════════════════════"
