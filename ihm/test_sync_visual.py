#!/usr/bin/env python3
"""
TESTE VISUAL DE SINCRONIZAÇÃO IHM WEB
Usa apenas WebSocket para monitorar estado em tempo real
Instruções manuais para validação

Data: 15/Nov/2025 04:05 BRT
"""

import asyncio
import websockets
import json
from datetime import datetime

class IHMWebMonitor:
    def __init__(self):
        self.ws_uri = "ws://localhost:8765"
        self.websocket = None
        self.state = {}

    async def connect(self):
        """Conecta ao WebSocket"""
        print("🔌 Conectando ao WebSocket da IHM Web...")
        self.websocket = await websockets.connect(self.ws_uri)
        initial = await self.websocket.recv()
        self.state = json.loads(initial)
        print(f"✅ Conectado! Estado inicial recebido ({len(self.state)} campos)")
        return True

    async def monitor_updates(self):
        """Monitora atualizações em tempo real"""
        print("\n🔄 Monitorando atualizações...")
        print("=" * 70)

        while True:
            try:
                message = await self.websocket.recv()
                update = json.loads(message)
                self.state.update(update)

                # Mostra atualizações relevantes
                if any(k in update for k in ['mode_bit_02ff', 'mode_text', 'leds']):
                    self.print_status()

            except websockets.exceptions.ConnectionClosed:
                print("\n❌ Conexão fechada")
                break
            except KeyboardInterrupt:
                print("\n⚠️  Interrompido pelo usuário")
                break

    def print_status(self):
        """Imprime status atual"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        mode = self.state.get('mode_text', 'DESCONHECIDO')
        mode_bit = self.state.get('mode_bit_02ff', None)

        leds = self.state.get('leds', {})
        led1 = '🟢' if leds.get('LED1') else '⚫'
        led2 = '🟢' if leds.get('LED2') else '⚫'
        led3 = '🟢' if leds.get('LED3') else '⚫'

        angles = self.state.get('angles', {})
        ang1 = angles.get('bend_1_left', 0.0)
        ang2 = angles.get('bend_2_left', 0.0)
        ang3 = angles.get('bend_3_left', 0.0)

        print(f"\n[{timestamp}] 📊 ESTADO ATUALIZADO:")
        print(f"   Modo: {mode} (bit 0x02FF = {mode_bit})")
        print(f"   LEDs: K1={led1} K2={led2} K3={led3}")
        print(f"   Ângulos: {ang1:.1f}° | {ang2:.1f}° | {ang3:.1f}°")
        print("-" * 70)

async def main():
    print("╔" + "="*68 + "╗")
    print("║" + " "*15 + "MONITOR IHM WEB EM TEMPO REAL" + " "*23 + "║")
    print("╚" + "="*68 + "╝")
    print(f"\n📅 Data: {datetime.now().strftime('%d/%b/%Y %H:%M:%S')}")
    print(f"🌐 WebSocket: ws://localhost:8765")
    print("\n⚠️  INSTRUÇÕES PARA VALIDAÇÃO:")
    print("   1. Abra a IHM Web no navegador (http://localhost:8080)")
    print("   2. Use mbpoll para alterar valores no CLP")
    print("   3. Observe se as mudanças aparecem aqui E na IHM Web")
    print("\n📝 TESTES MANUAIS:")
    print("   • Mudar modo:    mbpoll -a 1 -b 57600 -P none -s 2 -t 0 -r 767 /dev/ttyUSB0 <0|1>")
    print("   • Ligar LED K1:  mbpoll -a 1 -b 57600 -P none -s 2 -t 0 -r 192 /dev/ttyUSB0 1")
    print("   • Desligar LED:  mbpoll -a 1 -b 57600 -P none -s 2 -t 0 -r 192 /dev/ttyUSB0 0")
    print("\n" + "="*70)

    monitor = IHMWebMonitor()

    try:
        await monitor.connect()
        monitor.print_status()
        print("\n✅ Monitoramento ativo. Pressione Ctrl+C para sair.")
        await monitor.monitor_updates()
    except KeyboardInterrupt:
        print("\n\n⚠️  Monitor encerrado pelo usuário")
    except Exception as e:
        print(f"\n\n❌ Erro: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if monitor.websocket:
            await monitor.websocket.close()
        print("\n🔌 Desconectado")

if __name__ == '__main__':
    asyncio.run(main())
