"""
Main Server - Servidor WebSocket IHM Web
=========================================

Servidor principal que coordena:
- Modbus client (comunicação com CLP)
- State manager (estado da máquina)
- WebSocket server (comunicação com tablet)
- HTTP server (serve index.html)
"""

import asyncio
import websockets
import json
import argparse
import time
from pathlib import Path
from typing import Set
from aiohttp import web

from modbus_client import ModbusClientWrapper
from state_manager import MachineStateManager
import modbus_map as mm


class IHMServer:
    """
    Servidor principal da IHM Web
    """
    
    def __init__(self, stub_mode: bool = False, port: str = '/dev/ttyUSB0'):
        """
        Inicializa servidor
        
        Args:
            stub_mode: True para modo simulado
            port: Porta serial para modo live
        """
        self.stub_mode = stub_mode
        self.port = port
        
        # Clientes WebSocket conectados
        self.clients: Set[websockets.WebSocketServerProtocol] = set()
        
        # Componentes principais
        self.modbus_client = None
        self.state_manager = None
        
        # Tasks asyncio
        self.tasks = []
        
    async def start(self):
        """Inicializa todos os componentes"""
        print("=" * 60)
        print("IHM WEB - DOBRADEIRA NEOCOUDE-HD-15")
        print("=" * 60)
        
        # 1. Inicializa Modbus client
        print(f"\nModo: {'STUB (simulação)' if self.stub_mode else 'LIVE (CLP real)'}")
        self.modbus_client = ModbusClientWrapper(
            stub_mode=self.stub_mode,
            port=self.port
        )
        
        if not self.modbus_client.connected:
            print("✗ AVISO: Modbus não conectado!")
            if not self.stub_mode:
                print("  Verifique:")
                print(f"  - Cabo RS485 conectado em {self.port}")
                print("  - CLP ligado e em RUN")
                print("  - Estado 00BE (190) ativo no ladder")
                return False
        
        # 2. Inicializa State Manager
        self.state_manager = MachineStateManager(self.modbus_client)
        
        # 3. Inicia loop de polling
        poll_task = asyncio.create_task(self.state_manager.start_polling())
        self.tasks.append(poll_task)
        
        # 4. Inicia loop de broadcast
        broadcast_task = asyncio.create_task(self.broadcast_loop())
        self.tasks.append(broadcast_task)
        
        print("\n✓ Servidor iniciado com sucesso")
        print(f"  WebSocket: ws://localhost:8765")
        print(f"  HTTP: http://localhost:8080")
        print("\nAbra http://localhost:8080 no navegador do tablet")
        print("Pressione Ctrl+C para encerrar\n")
        
        return True
        
    async def handle_websocket(self, websocket):
        """
        Gerencia conexão WebSocket de um cliente

        Args:
            websocket: Conexão WebSocket
        """
        # Registra cliente
        self.clients.add(websocket)
        client_addr = websocket.remote_address
        print(f"✓ Cliente conectado: {client_addr}")
        
        try:
            # Envia estado completo inicial
            initial_state = self.state_manager.get_state()
            print(f"🔍 [DEBUG] Estado completo antes de enviar: {len(initial_state)} chaves")
            print(f"🔍 [DEBUG] modbus_connected no estado: {initial_state.get('modbus_connected')}")
            print(f"🔍 [DEBUG] connected no estado: {initial_state.get('connected')}")
            print(f"🔍 [DEBUG] encoder_raw no estado: {initial_state.get('encoder_raw')}")
            print(f"🔍 [DEBUG] encoder_degrees no estado: {initial_state.get('encoder_degrees')}")

            await websocket.send(json.dumps({
                'type': 'full_state',
                'data': initial_state
            }))
            print("✅ [DEBUG] Estado completo enviado com sucesso!")
            
            # Loop de recebimento de comandos
            async for message in websocket:
                await self.handle_client_message(websocket, message)
                
        except websockets.exceptions.ConnectionClosed:
            print(f"✗ Cliente desconectado: {client_addr}")
        finally:
            # Remove cliente
            self.clients.discard(websocket)
            
    async def handle_client_message(self, websocket, message: str):
        """
        Processa mensagem recebida do cliente

        Args:
            websocket: Conexão WebSocket
            message: Mensagem JSON
        """
        try:
            data = json.loads(message)
            action = data.get('action')
            print(f"📨 Comando recebido: {action} - {data}")  # LOG ADICIONAL

            if action == 'press_key':
                # Pressionar botão
                key_name = data.get('key')  # Ex: 'K1', 'S1', 'ENTER'
                
                # Mapeia nome para endereço
                addr = None
                if key_name in mm.KEYBOARD_NUMERIC:
                    addr = mm.KEYBOARD_NUMERIC[key_name]
                elif key_name in mm.KEYBOARD_FUNCTION:
                    addr = mm.KEYBOARD_FUNCTION[key_name]
                    
                if addr:
                    success = self.modbus_client.press_key(addr)
                    await websocket.send(json.dumps({
                        'type': 'key_response',
                        'key': key_name,
                        'success': success
                    }))
                    
            elif action == 'change_speed':
                # Alterar velocidade (K1+K7)
                success = self.modbus_client.change_speed_class()
                await websocket.send(json.dumps({
                    'type': 'speed_response',
                    'success': success
                }))
                
            elif action == 'toggle_mode':
                # Toggle direto do modo (bypass S1+E6)
                await self.handle_toggle_mode(websocket, data)

            elif action == 'write_angle':
                # Escrever ângulo de dobra
                bend_num = data.get('bend')  # 1, 2 ou 3
                angle_value = int(data.get('angle') * 10)  # Converte graus para unidades CLP

                # Usa novo formato de dicionário do modbus_map
                addr_map = {
                    1: (mm.BEND_ANGLES['BEND_1_LEFT_MSW'], mm.BEND_ANGLES['BEND_1_LEFT_LSW']),
                    2: (mm.BEND_ANGLES['BEND_2_LEFT_MSW'], mm.BEND_ANGLES['BEND_2_LEFT_LSW']),
                    3: (mm.BEND_ANGLES['BEND_3_LEFT_MSW'], mm.BEND_ANGLES['BEND_3_LEFT_LSW'])
                }

                if bend_num in addr_map:
                    msw_addr, lsw_addr = addr_map[bend_num]
                    success = self.modbus_client.write_32bit(msw_addr, lsw_addr, angle_value)
                    await websocket.send(json.dumps({
                        'type': 'angle_response',
                        'bend': bend_num,
                        'success': success
                    }))

            elif action == 'write_output':
                # Controlar saída digital (motor)
                output_name = data.get('output')  # 'S0' ou 'S1'
                value = data.get('value')  # True/False

                if output_name in mm.DIGITAL_OUTPUTS:
                    # M-002: INTERTRAVAMENTO S0/S1 (Safety)
                    if value and output_name in ['S0', 'S1']:
                        # Verificar se a outra saída está ativa
                        other_output = 'S1' if output_name == 'S0' else 'S0'
                        other_addr = mm.DIGITAL_OUTPUTS[other_output]
                        other_state = self.modbus_client.read_coil(other_addr)

                        if other_state:
                            # BLOQUEIO DE SEGURANÇA
                            print(f"⚠️ BLOQUEIO: {output_name} não pode ligar enquanto {other_output} está ativo!")
                            await websocket.send(json.dumps({
                                'type': 'error',
                                'message': f'ERRO DE SEGURANÇA: {other_output} ainda está ativo. Pare o motor antes de inverter direção.'
                            }))
                            return

                    addr = mm.DIGITAL_OUTPUTS[output_name]
                    success = self.modbus_client.write_coil(addr, value)
                    print(f"{'✓' if success else '✗'} Motor {output_name}: {'ON' if value else 'OFF'}")
                    await websocket.send(json.dumps({
                        'type': 'output_response',
                        'output': output_name,
                        'value': value,
                        'success': success
                    }))

            elif action == 'write_speed':
                # Alterar velocidade do motor
                speed = data.get('speed')  # 5, 10 ou 15 RPM

                if speed in [5, 10, 15]:
                    addr = mm.SUPERVISION_AREA['SPEED_CLASS']
                    success = self.modbus_client.write_register(addr, speed)
                    print(f"{'✓' if success else '✗'} Velocidade: {speed} RPM")
                    await websocket.send(json.dumps({
                        'type': 'speed_response',
                        'speed': speed,
                        'success': success
                    }))
                else:
                    print(f"✗ Velocidade inválida: {speed}")
                    await websocket.send(json.dumps({
                        'type': 'error',
                        'message': f'Velocidade inválida: {speed}. Use 5, 10 ou 15 RPM.'
                    }))

            elif action == 'emergency_stop':
                # M-001: PARADA DE EMERGÊNCIA (NR-12)
                print("🚨 EMERGÊNCIA ACIONADA! Desligando tudo...")

                # Desliga S0 e S1 imediatamente (sem verificação)
                s0_success = self.modbus_client.write_coil(mm.DIGITAL_OUTPUTS['S0'], False)
                s1_success = self.modbus_client.write_coil(mm.DIGITAL_OUTPUTS['S1'], False)

                # Opcional: Zera velocidade (ou coloca em classe mais baixa)
                # speed_success = self.modbus_client.write_register(mm.SUPERVISION_AREA['SPEED_CLASS'], 5)

                print(f"{'✓' if s0_success and s1_success else '✗'} Motor desligado (S0={s0_success}, S1={s1_success})")

                await websocket.send(json.dumps({
                    'type': 'emergency_response',
                    'success': s0_success and s1_success,
                    'message': 'Parada de emergência executada'
                }))
                    
        except json.JSONDecodeError:
            print(f"✗ JSON inválido recebido: {message}")
        except Exception as e:
            print(f"✗ Erro processando mensagem: {e}")
            
    async def broadcast_loop(self):
        """
        Loop que envia atualizações para todos os clientes conectados
        """
        previous_state = {}

        while True:
            await asyncio.sleep(0.5)  # Broadcast a cada 500ms

            if not self.clients:
                # Atualiza previous_state mesmo sem clientes
                previous_state = self.state_manager.get_state()
                continue

            # Pega apenas mudanças (deltas)
            changes = self.state_manager.get_changes(previous_state)

            if changes:
                message = json.dumps({
                    'type': 'state_update',
                    'data': changes
                })

                # Envia para todos os clientes
                disconnected = set()
                for client in self.clients:
                    try:
                        await client.send(message)
                    except:
                        disconnected.add(client)

                # Remove clientes desconectados
                self.clients -= disconnected

            # Atualiza estado anterior
            previous_state = self.state_manager.get_state()
                
    async def handle_toggle_mode(self, websocket, data):
        """
        Handler para toggle de modo (direto em 02FF - bypass S1+E6)
        """
        print("🔄 Toggle de modo (direto em 02FF)...")

        # Ler modo atual
        mode_antes_bit = self.modbus_client.read_real_mode()
        mode_antes = "AUTO" if mode_antes_bit else "MANUAL" if mode_antes_bit is not None else "UNKNOWN"

        # Toggle usando método direto (NÃO simula S1 que está bloqueado)
        new_mode_bit = not mode_antes_bit if mode_antes_bit is not None else None
        if new_mode_bit is not None:
            success = self.modbus_client.change_mode_direct(to_auto=new_mode_bit)
            if not success:
                new_mode_bit = None

        if new_mode_bit is not None:
            mode_depois = "AUTO" if new_mode_bit else "MANUAL"

            # Aguardar sincronização
            await asyncio.sleep(0.3)

            # Broadcast para TODOS os clientes (formato compatível com state_update)
            update = {
                'type': 'state_update',
                'data': {
                    'mode_bit_02ff': new_mode_bit,
                    'mode_text': mode_depois,
                    'mode_manual': not new_mode_bit
                }
            }

            for client in self.clients:
                try:
                    await client.send(json.dumps(update))
                except:
                    pass

            print(f"✅ Modo alterado: {mode_antes} → {mode_depois}")
        else:
            await websocket.send(json.dumps({
                'type': 'error',
                'message': 'Falha ao alternar modo - verifique conexão Modbus'
            }))
            print("❌ Falha ao alternar modo")

    async def http_handler(self, request):
        """
        Serve arquivo index.html
        
        Args:
            request: Request HTTP
            
        Returns:
            Response com HTML
        """
        html_path = Path(__file__).parent / 'static' / 'index.html'
        
        if html_path.exists():
            return web.FileResponse(html_path)
        else:
            return web.Response(text="index.html não encontrado", status=404)
            
    async def run(self):
        """Executa servidor (WebSocket + HTTP)"""
        # Inicializa componentes
        if not await self.start():
            return
            
        # Servidor HTTP (para servir index.html)
        app = web.Application()
        app.router.add_get('/', self.http_handler)
        app.router.add_static('/static', Path(__file__).parent / 'static')
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, 'localhost', 8080)
        await site.start()
        
        # Servidor WebSocket
        async with websockets.serve(self.handle_websocket, 'localhost', 8765):
            # Mantém rodando até Ctrl+C
            await asyncio.Future()  # Run forever
            
    def stop(self):
        """Encerra servidor"""
        print("\nEncerrando servidor...")
        
        if self.state_manager:
            self.state_manager.stop_polling()
            
        if self.modbus_client:
            self.modbus_client.close()
            
        for task in self.tasks:
            task.cancel()
            
        print("✓ Servidor encerrado")


async def main():
    """Função principal"""
    parser = argparse.ArgumentParser(description='IHM Web - Dobradeira NEOCOUDE-HD-15')
    parser.add_argument('--stub', action='store_true', help='Modo stub (simulação sem CLP)')
    parser.add_argument('--port', default='/dev/ttyUSB0', help='Porta serial (padrão: /dev/ttyUSB0)')
    
    args = parser.parse_args()
    
    server = IHMServer(stub_mode=args.stub, port=args.port)
    
    try:
        await server.run()
    except KeyboardInterrupt:
        print("\n\n✓ Interrompido pelo usuário")
    finally:
        server.stop()


if __name__ == "__main__":
    asyncio.run(main())
