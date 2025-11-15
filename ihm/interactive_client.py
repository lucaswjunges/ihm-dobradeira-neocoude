#!/usr/bin/env python3
"""
CLIENTE INTERATIVO PARA IHM WEB
================================

Ferramenta de linha de comando para:
- Conectar ao servidor IHM via WebSocket
- Enviar comandos (teclas, toggle modo, escrever ângulos)
- Monitorar estado em tempo real
- Emular operador humano
- Validar sincronização IHM ↔ CLP

Uso:
    python3 interactive_client.py
    >>> connect
    >>> monitor
    >>> toggle_mode
    >>> press K1
    >>> set_angle 1 90.5
"""

import asyncio
import websockets
import json
import sys
from datetime import datetime
from typing import Optional, Dict, Any
import readline  # Para histórico de comandos


class IHMInteractiveClient:
    """Cliente interativo para IHM Web com comandos em tempo real."""

    def __init__(self, ws_uri: str = "ws://localhost:8765"):
        self.ws_uri = ws_uri
        self.websocket: Optional[websockets.WebSocketClientProtocol] = None
        self.state: Dict[str, Any] = {}
        self.connected = False
        self.monitoring = False
        self.monitor_task = None

    async def connect(self):
        """Conecta ao servidor WebSocket."""
        try:
            print(f"🔌 Conectando a {self.ws_uri}...")
            self.websocket = await websockets.connect(self.ws_uri)

            # Receber estado inicial
            initial_msg = await self.websocket.recv()
            initial_data = json.loads(initial_msg)

            if 'data' in initial_data:
                self.state = initial_data['data']
            else:
                self.state = initial_data

            self.connected = True
            print("✅ Conectado ao servidor IHM!")
            print(f"📊 Estado inicial recebido: {len(self.state)} campos")
            self._print_critical_state()

        except Exception as e:
            print(f"❌ Erro na conexão: {e}")
            self.connected = False

    async def disconnect(self):
        """Desconecta do servidor."""
        if self.websocket:
            await self.websocket.close()
            self.connected = False
            print("🔌 Desconectado")

    def _print_critical_state(self):
        """Imprime estado crítico atual."""
        print("\n" + "="*70)
        print("ESTADO CRÍTICO ATUAL")
        print("="*70)

        # Modo
        mode_bit = self.state.get('mode_bit_02ff')
        mode_text = self.state.get('mode_text', 'DESCONHECIDO')
        print(f"🔧 MODO: {mode_text} (bit 0x02FF = {mode_bit})")

        # LEDs
        leds = self.state.get('leds', {})
        led_status = []
        for led_name in ['LED1', 'LED2', 'LED3', 'LED4', 'LED5']:
            status = '🟢' if leds.get(led_name, False) else '⚫'
            led_status.append(f"{led_name}:{status}")
        print(f"💡 LEDs: {' '.join(led_status)}")

        # Encoder
        encoder = self.state.get('encoder_degrees', 0.0)
        print(f"📐 ENCODER: {encoder:.1f}°")

        # Ângulos
        angles = self.state.get('angles', {})
        print(f"📏 ÂNGULOS PROGRAMADOS:")
        if angles:
            # Mostrar apenas ângulos "razoáveis" (0-180°) ou lixo de memória com aviso
            for name, value in angles.items():
                if 0 <= value <= 180:
                    print(f"   {name}: {value:.1f}°")
                elif value > 1000:
                    print(f"   {name}: (não programado - {value:.0f}°)")
        else:
            print(f"   (nenhum ângulo disponível)")

        # Conexão
        modbus_conn = self.state.get('modbus_connected', False)
        conn_symbol = '🟢' if modbus_conn else '🔴'
        print(f"{conn_symbol} MODBUS: {'Conectado' if modbus_conn else 'Desconectado'}")

        # Última atualização
        last_update = self.state.get('last_update', 'N/A')
        print(f"⏱️  ÚLTIMA ATUALIZAÇÃO: {last_update}")
        print("="*70 + "\n")

    async def _receive_updates(self):
        """Loop de recebimento de atualizações (para modo monitor)."""
        try:
            while self.monitoring and self.connected:
                msg = await asyncio.wait_for(self.websocket.recv(), timeout=5.0)
                msg_data = json.loads(msg)

                # Extrair dados
                if 'data' in msg_data:
                    changes = msg_data['data']
                    self.state.update(changes)
                else:
                    changes = msg_data
                    self.state.update(changes)

                # Imprimir mudanças
                timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
                print(f"\n[{timestamp}] 📡 ATUALIZAÇÃO RECEBIDA:")
                for key, value in changes.items():
                    if key not in ['last_update', 'poll_count']:
                        print(f"   {key}: {value}")

        except asyncio.TimeoutError:
            pass  # Timeout normal, continua monitorando
        except Exception as e:
            print(f"\n❌ Erro recebendo atualizações: {e}")

    async def start_monitoring(self):
        """Inicia monitoramento contínuo de atualizações."""
        if not self.connected:
            print("❌ Não conectado! Use 'connect' primeiro")
            return

        print("📡 Iniciando monitoramento em tempo real...")
        print("   (Pressione Ctrl+C para parar)\n")
        self.monitoring = True
        self.monitor_task = asyncio.create_task(self._receive_updates())

    def stop_monitoring(self):
        """Para monitoramento."""
        self.monitoring = False
        if self.monitor_task:
            self.monitor_task.cancel()
        print("⏹️  Monitoramento parado")

    async def send_command(self, action: str, **kwargs):
        """Envia comando ao servidor."""
        if not self.connected:
            print("❌ Não conectado! Use 'connect' primeiro")
            return False

        try:
            command = {'action': action, **kwargs}
            print(f"📤 Enviando: {json.dumps(command)}")
            await self.websocket.send(json.dumps(command))

            # Aguardar resposta ou broadcast (aumentado para 3s)
            try:
                response = await asyncio.wait_for(self.websocket.recv(), timeout=3.0)
                response_data = json.loads(response)

                # Atualizar estado
                if 'data' in response_data:
                    self.state.update(response_data['data'])

                print(f"✅ Resposta: {response_data.get('type', 'N/A')}")
            except asyncio.TimeoutError:
                # Não é erro crítico - servidor pode ter feito broadcast assíncrono
                print(f"✅ Comando enviado (sem resposta imediata)")

            return True

        except Exception as e:
            print(f"❌ Erro enviando comando: {e}")
            return False

    async def toggle_mode(self):
        """Alterna modo MANUAL ↔ AUTO."""
        mode_antes = self.state.get('mode_text', 'DESCONHECIDO')
        print(f"\n🔄 Alternando modo (atual: {mode_antes})...")

        success = await self.send_command('toggle_mode')

        if success:
            await asyncio.sleep(0.5)  # Aguardar sincronização
            mode_depois = self.state.get('mode_text', 'DESCONHECIDO')
            print(f"✅ Modo alterado: {mode_antes} → {mode_depois}")
        else:
            print("❌ Falha ao alternar modo")

    async def press_key(self, key_name: str):
        """Pressiona tecla virtual (K0-K9, S1, S2, ENTER, etc)."""
        print(f"\n⌨️  Pressionando tecla: {key_name}")
        success = await self.send_command('press_key', key=key_name)

        if success:
            print(f"✅ Tecla {key_name} pressionada")
        else:
            print(f"❌ Falha ao pressionar {key_name}")

    async def set_angle(self, bend_num: int, angle: float):
        """Define ângulo de dobra (1, 2 ou 3)."""
        print(f"\n📐 Definindo ângulo da dobra {bend_num}: {angle}°")
        success = await self.send_command('write_angle', bend=bend_num, angle=angle)

        if success:
            print(f"✅ Ângulo definido")
            await asyncio.sleep(1.0)  # Aguardar leitura do CLP
            self._print_critical_state()
        else:
            print(f"❌ Falha ao definir ângulo")

    async def wait_and_check(self, seconds: float = 2.0):
        """Aguarda tempo especificado e verifica mudanças."""
        print(f"\n⏳ Aguardando {seconds}s e checando mudanças...")
        state_before = self.state.copy()

        await asyncio.sleep(seconds)

        # Verificar mudanças
        changes = {}
        for key, value in self.state.items():
            if key not in state_before or state_before[key] != value:
                changes[key] = {'antes': state_before.get(key), 'depois': value}

        if changes:
            print("📊 MUDANÇAS DETECTADAS:")
            for key, vals in changes.items():
                print(f"   {key}: {vals['antes']} → {vals['depois']}")
        else:
            print("✅ Nenhuma mudança detectada")

    def show_state(self):
        """Mostra estado completo atual."""
        self._print_critical_state()

    def show_help(self):
        """Mostra ajuda de comandos."""
        print("""
╔══════════════════════════════════════════════════════════════════╗
║                    COMANDOS DISPONÍVEIS                          ║
╚══════════════════════════════════════════════════════════════════╝

CONEXÃO:
  connect             - Conecta ao servidor IHM
  disconnect          - Desconecta do servidor

MONITORAMENTO:
  monitor             - Inicia monitoramento contínuo (Ctrl+C para parar)
  state               - Mostra estado atual completo
  wait <segundos>     - Aguarda e verifica mudanças

COMANDOS IHM:
  toggle              - Alterna modo MANUAL ↔ AUTO
  press <tecla>       - Pressiona tecla (K0-K9, S1, S2, ENTER, ESC, EDIT)
  angle <n> <graus>   - Define ângulo (n=1,2,3, graus=0-180)

EXEMPLOS:
  >>> connect
  >>> state
  >>> toggle
  >>> press K1
  >>> angle 1 90.5
  >>> wait 3
  >>> monitor

SISTEMA:
  help                - Mostra esta ajuda
  exit / quit         - Encerra cliente
        """)


async def interactive_loop():
    """Loop interativo principal."""
    client = IHMInteractiveClient()

    print("╔══════════════════════════════════════════════════════════════════╗")
    print("║         CLIENTE INTERATIVO IHM WEB - NEOCOUDE-HD-15             ║")
    print("╚══════════════════════════════════════════════════════════════════╝")
    print("\nDigite 'help' para ver comandos disponíveis")
    print("Digite 'connect' para conectar ao servidor\n")

    while True:
        try:
            # Prompt
            connected_symbol = "🟢" if client.connected else "🔴"
            cmd_input = input(f"{connected_symbol} >>> ").strip()

            if not cmd_input:
                continue

            # Parse comando
            parts = cmd_input.split()
            cmd = parts[0].lower()
            args = parts[1:]

            # Executar comando
            if cmd in ['exit', 'quit']:
                if client.connected:
                    await client.disconnect()
                print("👋 Até logo!")
                break

            elif cmd == 'help':
                client.show_help()

            elif cmd == 'connect':
                await client.connect()

            elif cmd == 'disconnect':
                await client.disconnect()

            elif cmd == 'state':
                client.show_state()

            elif cmd == 'monitor':
                await client.start_monitoring()
                try:
                    while client.monitoring:
                        await asyncio.sleep(0.1)
                except KeyboardInterrupt:
                    client.stop_monitoring()
                    print("\n⏹️  Monitoramento parado")

            elif cmd == 'toggle':
                await client.toggle_mode()

            elif cmd == 'press':
                if not args:
                    print("❌ Uso: press <tecla>  (ex: press K1)")
                else:
                    await client.press_key(args[0].upper())

            elif cmd == 'angle':
                if len(args) < 2:
                    print("❌ Uso: angle <dobra> <graus>  (ex: angle 1 90.5)")
                else:
                    try:
                        bend_num = int(args[0])
                        angle_val = float(args[1])
                        await client.set_angle(bend_num, angle_val)
                    except ValueError:
                        print("❌ Argumentos inválidos")

            elif cmd == 'wait':
                if not args:
                    await client.wait_and_check(2.0)
                else:
                    try:
                        seconds = float(args[0])
                        await client.wait_and_check(seconds)
                    except ValueError:
                        print("❌ Tempo inválido")

            else:
                print(f"❌ Comando desconhecido: {cmd}")
                print("   Digite 'help' para ver comandos disponíveis")

        except KeyboardInterrupt:
            print("\n⚠️  Interrompido (use 'exit' para sair)")
        except Exception as e:
            print(f"❌ Erro: {e}")
            import traceback
            traceback.print_exc()


if __name__ == '__main__':
    try:
        asyncio.run(interactive_loop())
    except KeyboardInterrupt:
        print("\n\n👋 Encerrado pelo usuário")
