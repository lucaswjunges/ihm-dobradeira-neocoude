#!/usr/bin/env python3
"""
Emulação de Cliente IHM Web
===========================

Testa todas as funcionalidades da interface web via WebSocket.
Validado em 16/Nov/2025.
"""

import asyncio
import websockets
import json
import sys

class IHMWebEmulator:
    def __init__(self, uri='ws://localhost:8765'):
        self.uri = uri
        self.ws = None
        self.state = {}

    async def connect(self):
        """Conecta ao servidor WebSocket."""
        print(f"🔌 Conectando em {self.uri}...")
        self.ws = await websockets.connect(self.uri)
        print("✅ Conectado!\n")

    async def receive_state(self):
        """Recebe estado inicial do servidor."""
        print("📥 Aguardando estado inicial...")
        msg = await self.ws.recv()
        data = json.loads(msg)

        # Estado vem dentro de 'data' quando type='full_state'
        if data.get('type') == 'full_state':
            self.state = data.get('data', {})
        else:
            self.state = data

        print(f"✅ Estado recebido: {data.get('type', 'unknown')}")
        print(f"   Encoder: {self.state.get('encoder_degrees', 'N/A')}° (raw: {self.state.get('encoder_raw', 'N/A')})")
        print(f"   Velocidade: {self.state.get('speed_class', 'N/A')} rpm\n")
        return data

    async def send_command(self, action, **params):
        """Envia comando para o servidor."""
        command = {'action': action, **params}
        print(f"📤 Enviando: {action} {params}")
        await self.ws.send(json.dumps(command))

        # Aguarda resposta (pode haver state_updates intermediários)
        max_attempts = 5
        for attempt in range(max_attempts):
            response = await self.ws.recv()
            result = json.loads(response)

            # Ignora state_updates intermediários
            if result.get('type') == 'state_update':
                continue

            # Retorna primeira mensagem que não é state_update
            print(f"📥 Resposta: {result}\n")
            return result

        print(f"⚠️  Timeout: Não recebeu resposta após {max_attempts} tentativas\n")
        return {'success': False, 'error': 'timeout'}

    async def test_read_angles(self):
        """Testa leitura de ângulos."""
        print("=" * 60)
        print("TESTE 1: Leitura de Ângulos de Dobra")
        print("=" * 60)

        # Estado já contém ângulos
        angles = self.state.get('angles', {})
        print(f"Ângulos atuais:")
        print(f"  Dobra 1: {angles.get('bend_1_left', 'N/A')}°")
        print(f"  Dobra 2: {angles.get('bend_2_left', 'N/A')}°")
        print(f"  Dobra 3: {angles.get('bend_3_left', 'N/A')}°")
        print()

    async def test_write_angles(self):
        """Testa gravação de ângulos."""
        print("=" * 60)
        print("TESTE 2: Gravação de Ângulos de Dobra")
        print("=" * 60)

        test_angles = [
            (1, 90.0),
            (2, 120.0),
            (3, 45.5)
        ]

        for bend_num, angle in test_angles:
            result = await self.send_command('write_angle', bend=bend_num, angle=angle)
            if result.get('success'):
                print(f"  ✅ Dobra {bend_num}: {angle}° gravado com sucesso")
            else:
                print(f"  ❌ Dobra {bend_num}: Falha ao gravar")
        print()

    async def test_read_speed(self):
        """Testa leitura de velocidade."""
        print("=" * 60)
        print("TESTE 3: Leitura de Velocidade")
        print("=" * 60)

        speed = self.state.get('speed_class', 'N/A')
        print(f"Velocidade atual: {speed} rpm")
        print()

    async def test_write_speed(self):
        """Testa mudança de velocidade."""
        print("=" * 60)
        print("TESTE 4: Mudança de Velocidade")
        print("=" * 60)

        test_speeds = [5, 10, 15]

        for speed in test_speeds:
            result = await self.send_command('write_speed', speed=speed)
            if result.get('success'):
                print(f"  ✅ Velocidade {speed} rpm gravada com sucesso")
            else:
                print(f"  ❌ Velocidade {speed} rpm: Falha ao gravar")
        print()

    async def test_encoder(self):
        """Testa leitura do encoder."""
        print("=" * 60)
        print("TESTE 5: Leitura de Encoder")
        print("=" * 60)

        encoder_angle = self.state.get('encoder_degrees', 0.0)
        encoder_raw = self.state.get('encoder_raw', 0)
        print(f"Encoder: {encoder_angle}° (raw: {encoder_raw})")
        print()

    async def test_press_key(self):
        """Testa simulação de botões."""
        print("=" * 60)
        print("TESTE 6: Simulação de Botões")
        print("=" * 60)

        test_keys = ['K1', 'S1', 'ENTER']

        for key in test_keys:
            result = await self.send_command('press_key', key=key)
            if result.get('success'):
                print(f"  ✅ Botão {key} pressionado com sucesso")
            else:
                print(f"  ❌ Botão {key}: Falha ao pressionar")
        print()

    async def test_io_digital(self):
        """Testa leitura de I/O digital."""
        print("=" * 60)
        print("TESTE 7: Leitura de I/O Digital")
        print("=" * 60)

        inputs = self.state.get('inputs', {})
        outputs = self.state.get('outputs', {})

        print("Entradas (E0-E7):")
        for i in range(8):
            key = f'E{i}'
            value = '●' if inputs.get(key, False) else '○'
            print(f"  {key}: {value}")

        print("\nSaídas (S0-S7):")
        for i in range(8):
            key = f'S{i}'
            value = '●' if outputs.get(key, False) else '○'
            print(f"  {key}: {value}")
        print()

    async def test_leds(self):
        """Testa leitura de LEDs."""
        print("=" * 60)
        print("TESTE 8: Leitura de LEDs")
        print("=" * 60)

        leds = self.state.get('leds', {})
        for i in range(1, 6):
            key = f'LED{i}'
            value = '●' if leds.get(key, False) else '○'
            print(f"  {key}: {value}")
        print()

    async def run_all_tests(self):
        """Executa todos os testes."""
        try:
            await self.connect()
            await self.receive_state()

            await self.test_encoder()
            await self.test_read_angles()
            await self.test_read_speed()
            await self.test_io_digital()
            await self.test_leds()

            # Testes de escrita
            await self.test_write_angles()
            await self.test_write_speed()
            await self.test_press_key()

            print("=" * 60)
            print("✅ TODOS OS TESTES CONCLUÍDOS")
            print("=" * 60)

        except Exception as e:
            print(f"\n❌ ERRO: {e}")
            import traceback
            traceback.print_exc()
        finally:
            if self.ws:
                await self.ws.close()
                print("\n🔌 Desconectado")

async def main():
    emulator = IHMWebEmulator()
    await emulator.run_all_tests()

if __name__ == '__main__':
    asyncio.run(main())
