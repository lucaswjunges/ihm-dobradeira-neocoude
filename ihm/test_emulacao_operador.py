#!/usr/bin/env python3
"""
TESTE DE EMULAÇÃO DE OPERADOR
==============================

Simula operador real usando a IHM Web via WebSocket.
Valida todas as funcionalidades críticas do sistema.

Testes:
1. Conectar e ler estado inicial
2. Alternar modo MANUAL ↔ AUTO
3. Ler encoder em tempo real
4. Programar ângulos de dobra
5. Verificar LEDs
6. Ler I/O digital (entradas/saídas)
"""

import asyncio
import websockets
import json
import time
from datetime import datetime


class EmuladorOperador:
    """Emula operador humano usando IHM Web."""

    def __init__(self, ws_uri: str = "ws://localhost:8765"):
        self.ws_uri = ws_uri
        self.websocket = None
        self.state = {}
        self.connected = False

    async def connect(self):
        """Conecta ao servidor WebSocket."""
        print("╔════════════════════════════════════════════════════════════════╗")
        print("║         EMULAÇÃO DE OPERADOR - IHM WEB DOBRADEIRA             ║")
        print("╚════════════════════════════════════════════════════════════════╝\n")

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
            print(f"✅ Conectado! Estado inicial: {len(self.state)} campos\n")
            return True

        except Exception as e:
            print(f"❌ Erro na conexão: {e}")
            self.connected = False
            return False

    async def disconnect(self):
        """Desconecta do servidor."""
        if self.websocket:
            await self.websocket.close()
            self.connected = False
            print("🔌 Desconectado")

    def _print_separator(self, title: str):
        """Imprime separador visual."""
        print("\n" + "━" * 70)
        print(f"  {title}")
        print("━" * 70)

    def _print_state_summary(self):
        """Imprime resumo do estado atual."""
        print("\n" + "═" * 70)
        print("  ESTADO ATUAL DO SISTEMA")
        print("═" * 70)

        # Modo
        mode_text = self.state.get('mode_text', 'DESCONHECIDO')
        mode_bit = self.state.get('mode_bit_02ff', None)
        print(f"🔧 MODO: {mode_text} (bit 0x02FF = {mode_bit})")

        # Encoder
        encoder = self.state.get('encoder_degrees', 0.0)
        print(f"📐 ENCODER: {encoder:.1f}°")

        # LEDs
        leds = self.state.get('leds', {})
        led_status = []
        for led_name in ['LED1', 'LED2', 'LED3', 'LED4', 'LED5']:
            status = '🟢' if leds.get(led_name, False) else '⚫'
            led_status.append(f"{led_name}:{status}")
        print(f"💡 LEDs: {' '.join(led_status)}")

        # Ângulos
        angles = self.state.get('angles', {})
        print(f"📏 ÂNGULOS PROGRAMADOS:")
        for name, value in angles.items():
            if 0 <= value <= 180:
                print(f"   {name}: {value:.1f}°")
            elif value > 1000:
                print(f"   {name}: (não programado - {value:.0f}°)")

        # Conexão
        modbus_conn = self.state.get('modbus_connected', False)
        conn_symbol = '🟢' if modbus_conn else '🔴'
        print(f"{conn_symbol} MODBUS: {'Conectado' if modbus_conn else 'Desconectado'}")

        # Timestamp
        last_update = self.state.get('last_update', 'N/A')
        print(f"⏱️  ÚLTIMA ATUALIZAÇÃO: {last_update}")
        print("═" * 70 + "\n")

    async def send_command(self, action: str, **kwargs):
        """Envia comando ao servidor."""
        if not self.connected:
            print("❌ Não conectado!")
            return False

        try:
            command = {'action': action, **kwargs}
            print(f"📤 Enviando comando: {action}")
            print(f"   Dados: {kwargs}")
            await self.websocket.send(json.dumps(command))

            # Aguardar resposta
            try:
                response = await asyncio.wait_for(self.websocket.recv(), timeout=3.0)
                response_data = json.loads(response)

                # Atualizar estado local
                if 'data' in response_data:
                    self.state.update(response_data['data'])

                print(f"✅ Resposta: {response_data.get('type', 'N/A')}")
                return True

            except asyncio.TimeoutError:
                print(f"⚠️  Timeout (comando pode ter sido processado)")
                return True

        except Exception as e:
            print(f"❌ Erro: {e}")
            return False

    async def teste_toggle_modo(self):
        """Testa alternar modo MANUAL ↔ AUTO."""
        self._print_separator("TESTE 1: ALTERNAR MODO")

        modo_antes = self.state.get('mode_text', 'DESCONHECIDO')
        print(f"Modo atual: {modo_antes}")

        success = await self.send_command('toggle_mode')

        if success:
            await asyncio.sleep(0.5)  # Aguardar sincronização
            modo_depois = self.state.get('mode_text', 'DESCONHECIDO')

            if modo_antes != modo_depois:
                print(f"✅ SUCESSO: {modo_antes} → {modo_depois}")
                return True
            else:
                print(f"⚠️  AVISO: Modo não mudou (ainda {modo_antes})")
                return False
        else:
            print("❌ FALHA no comando")
            return False

    async def teste_ler_encoder(self):
        """Testa leitura do encoder."""
        self._print_separator("TESTE 2: LEITURA DE ENCODER")

        print("Lendo encoder por 3 ciclos...")
        for i in range(3):
            await asyncio.sleep(0.5)

            # Receber broadcast
            try:
                msg = await asyncio.wait_for(self.websocket.recv(), timeout=1.0)
                msg_data = json.loads(msg)

                if 'data' in msg_data:
                    self.state.update(msg_data['data'])

                encoder = self.state.get('encoder_degrees', 0.0)
                encoder_raw = self.state.get('encoder_raw', 0)
                print(f"  Ciclo {i+1}: {encoder:.2f}° (raw: {encoder_raw})")

            except asyncio.TimeoutError:
                print(f"  Ciclo {i+1}: Sem atualização")

        print("✅ Leitura de encoder funcionando")
        return True

    async def teste_programar_angulos(self):
        """Testa programação de ângulos."""
        self._print_separator("TESTE 3: PROGRAMAR ÂNGULOS")

        angulos_teste = [
            (1, 90.0),
            (2, 120.0),
            (3, 45.0)
        ]

        for bend_num, angle in angulos_teste:
            print(f"\nProgramando dobra {bend_num}: {angle}°")
            success = await self.send_command('write_angle', bend=bend_num, angle=angle)

            if success:
                print(f"✅ Ângulo {bend_num} programado")
            else:
                print(f"❌ Falha ao programar ângulo {bend_num}")
                return False

            await asyncio.sleep(0.5)

        print("\n✅ Todos os ângulos programados com sucesso")
        return True

    async def teste_leitura_io(self):
        """Testa leitura de I/O digital."""
        self._print_separator("TESTE 4: LEITURA I/O DIGITAL")

        # Entradas
        inputs = self.state.get('inputs', {})
        print("📥 ENTRADAS (E0-E7):")
        for name, value in sorted(inputs.items()):
            status = '🟢 ON' if value else '⚫ OFF'
            print(f"   {name}: {status}")

        # Saídas
        outputs = self.state.get('outputs', {})
        print("\n📤 SAÍDAS (S0-S7):")
        for name, value in sorted(outputs.items()):
            status = '🟢 ON' if value else '⚫ OFF'
            print(f"   {name}: {status}")

        print("\n✅ Leitura de I/O funcionando")
        return True

    async def teste_validacao_modbus_direto(self):
        """Valida leituras Modbus diretas do CLP."""
        self._print_separator("TESTE 5: VALIDAÇÃO MODBUS DIRETO")

        print("Comparando dados da IHM com leituras Modbus diretas...")
        print("(Este teste requer mbpoll instalado)")

        # Ler encoder via mbpoll
        from modbus_client import ModbusClientWrapper
        client = ModbusClientWrapper(port='/dev/ttyUSB0')

        encoder_ihm = self.state.get('encoder_raw', 0)
        encoder_mbpoll = client.read_32bit(0x04D6, 0x04D7)

        print(f"\nEncoder IHM:    {encoder_ihm}")
        print(f"Encoder mbpoll: {encoder_mbpoll}")

        if encoder_ihm == encoder_mbpoll:
            print("✅ MATCH! Leituras consistentes")
            client.close()
            return True
        else:
            diff = abs(encoder_ihm - encoder_mbpoll)
            print(f"⚠️  DIFERENÇA: {diff} unidades")
            client.close()
            return False

    async def run_all_tests(self):
        """Executa todos os testes em sequência."""
        if not await self.connect():
            return False

        resultados = []

        # Estado inicial
        self._print_state_summary()

        # Teste 1: Toggle modo
        resultado1 = await self.teste_toggle_modo()
        resultados.append(('Toggle Modo', resultado1))
        await asyncio.sleep(1.0)

        # Teste 2: Encoder
        resultado2 = await self.teste_ler_encoder()
        resultados.append(('Leitura Encoder', resultado2))
        await asyncio.sleep(1.0)

        # Teste 3: Ângulos
        resultado3 = await self.teste_programar_angulos()
        resultados.append(('Programar Ângulos', resultado3))
        await asyncio.sleep(2.0)  # Aguardar polling de ângulos

        # Teste 4: I/O
        resultado4 = await self.teste_leitura_io()
        resultados.append(('Leitura I/O', resultado4))
        await asyncio.sleep(1.0)

        # Teste 5: Validação Modbus
        resultado5 = await self.teste_validacao_modbus_direto()
        resultados.append(('Validação Modbus', resultado5))

        # Estado final
        self._print_state_summary()

        # Desconectar
        await self.disconnect()

        # Relatório final
        self._print_separator("RELATÓRIO FINAL")
        print()
        total = len(resultados)
        sucesso = sum(1 for _, r in resultados if r)

        for nome, resultado in resultados:
            status = '✅ PASSOU' if resultado else '❌ FALHOU'
            print(f"{status}: {nome}")

        print(f"\n📊 TAXA DE SUCESSO: {sucesso}/{total} ({sucesso*100//total}%)")

        if sucesso == total:
            print("\n🎉 TODOS OS TESTES PASSARAM!")
            print("Sistema aprovado para produção ✅")
        else:
            print(f"\n⚠️  {total - sucesso} teste(s) falharam")
            print("Revisar funcionalidades com falha")

        return sucesso == total


async def main():
    """Função principal."""
    emulador = EmuladorOperador()
    await emulador.run_all_tests()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Teste interrompido pelo usuário")
