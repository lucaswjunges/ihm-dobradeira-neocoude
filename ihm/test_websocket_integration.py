#!/usr/bin/env python3
"""
Teste de Integração WebSocket
==============================

Testa comunicação end-to-end:
- Cliente WebSocket → Servidor → Modbus → CLP
- CLP → Modbus → Servidor → WebSocket → Cliente

Como engenheiro sênior, vou validar:
1. Conexão WebSocket
2. Recebimento de estado inicial (full_state)
3. Envio de comandos (write_angle, change_speed)
4. Recebimento de atualizações (state_update)
"""

import asyncio
import websockets
import json
import sys

class WebSocketTester:
    """Testa integração WebSocket"""

    def __init__(self):
        self.uri = "ws://localhost:8765"
        self.results = {
            'connection': False,
            'full_state_received': False,
            'state_has_angles': False,
            'state_has_encoder': False,
            'write_angle_accepted': False,
            'state_update_received': False
        }

    async def test_connection(self):
        """Testa conexão e recebimento de estado"""
        print("=" * 70)
        print("TESTE DE INTEGRAÇÃO WEBSOCKET")
        print("=" * 70)

        try:
            print("\n[1] Conectando ao servidor WebSocket...")
            async with websockets.connect(self.uri) as websocket:
                print("    ✅ Conectado!")
                self.results['connection'] = True

                # Aguardar estado inicial
                print("\n[2] Aguardando estado inicial (full_state)...")
                try:
                    message = await asyncio.wait_for(websocket.recv(), timeout=3.0)
                    data = json.loads(message)

                    if data.get('type') == 'full_state':
                        print("    ✅ Estado inicial recebido!")
                        self.results['full_state_received'] = True

                        # Validar conteúdo do estado
                        state = data.get('data', {})
                        print(f"\n[3] Validando conteúdo do estado ({len(state)} chaves)...")

                        # Verificar ângulos
                        if 'bend_1_left' in state:
                            angle = state['bend_1_left']
                            print(f"    ✅ Ângulo Dobra 1: {angle}°")
                            self.results['state_has_angles'] = True
                        else:
                            print(f"    ⚠️ Ângulos não encontrados no estado")

                        # Verificar encoder
                        if 'encoder_angle' in state:
                            encoder = state['encoder_angle']
                            print(f"    ✅ Encoder: {encoder}°")
                            self.results['state_has_encoder'] = True
                        else:
                            print(f"    ⚠️ Encoder não encontrado no estado")

                        # Verificar outras chaves importantes
                        important_keys = ['speed_class', 'modbus_connected', 'leds']
                        for key in important_keys:
                            if key in state:
                                print(f"    ✅ {key}: {state[key]}")
                            else:
                                print(f"    ⚠️ {key}: não encontrado")

                    else:
                        print(f"    ❌ Tipo inesperado: {data.get('type')}")

                except asyncio.TimeoutError:
                    print("    ❌ Timeout aguardando estado inicial")
                    return False

                # Enviar comando de escrita de ângulo
                print("\n[4] Enviando comando: escrever ângulo 90° na Dobra 1...")
                command = {
                    'action': 'write_angle',
                    'bend': 1,
                    'angle': 90.0
                }
                await websocket.send(json.dumps(command))
                print("    ✅ Comando enviado!")

                # Aguardar resposta
                print("\n[5] Aguardando resposta...")
                try:
                    message = await asyncio.wait_for(websocket.recv(), timeout=2.0)
                    data = json.loads(message)

                    if data.get('type') == 'angle_response':
                        success = data.get('success')
                        if success:
                            print(f"    ✅ CLP aceitou o comando!")
                            self.results['write_angle_accepted'] = True
                        else:
                            print(f"    ❌ CLP rejeitou o comando")
                    else:
                        print(f"    ⚠️ Resposta inesperada: {data}")

                except asyncio.TimeoutError:
                    print("    ❌ Timeout aguardando resposta")

                # Aguardar state_update
                print("\n[6] Aguardando atualizações de estado (state_update)...")
                try:
                    for _ in range(3):  # Aguarda até 3 mensagens
                        message = await asyncio.wait_for(websocket.recv(), timeout=1.0)
                        data = json.loads(message)

                        if data.get('type') == 'state_update':
                            print(f"    ✅ State update recebido: {list(data.get('data', {}).keys())}")
                            self.results['state_update_received'] = True
                            break
                        else:
                            print(f"    ℹ️ Mensagem: {data.get('type')}")

                except asyncio.TimeoutError:
                    print("    ⚠️ Nenhum state_update recebido (polling pode estar lento)")

                print("\n[7] Encerrando conexão...")

        except ConnectionRefusedError:
            print("    ❌ Servidor não está rodando!")
            print("\n    Execute primeiro: python3 main_server.py --port /dev/ttyUSB0")
            return False
        except Exception as e:
            print(f"    ❌ Erro: {e}")
            import traceback
            traceback.print_exc()
            return False

        return True

    def print_report(self):
        """Imprime relatório final"""
        print("\n" + "=" * 70)
        print("RELATÓRIO DE INTEGRAÇÃO")
        print("=" * 70)

        tests = [
            ('Conexão WebSocket', self.results['connection']),
            ('Recebimento de full_state', self.results['full_state_received']),
            ('Estado contém ângulos', self.results['state_has_angles']),
            ('Estado contém encoder', self.results['state_has_encoder']),
            ('Comando write_angle aceito', self.results['write_angle_accepted']),
            ('Recebimento de state_update', self.results['state_update_received'])
        ]

        passed = sum(1 for _, result in tests if result)
        total = len(tests)

        for test_name, result in tests:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"  {status}  {test_name}")

        print(f"\n  Total: {passed}/{total} ({passed/total*100:.0f}%)")

        if passed == total:
            print("\n  🎉 INTEGRAÇÃO 100% FUNCIONAL!")
            print("  ✅ Sistema pronto para uso no tablet!")
        elif passed >= total * 0.75:
            print("\n  ⚠️ INTEGRAÇÃO PARCIAL (≥75%)")
            print("  ✅ Funcional, mas há problemas menores")
        else:
            print("\n  ❌ INTEGRAÇÃO FALHOU (<75%)")
            print("  🔧 Revisar servidor e conexões")

        print("=" * 70)

        return passed == total


async def main():
    """Executa teste"""
    tester = WebSocketTester()

    success = await tester.test_connection()
    result = tester.print_report()

    return 0 if result else 1


if __name__ == '__main__':
    try:
        exit(asyncio.run(main()))
    except KeyboardInterrupt:
        print("\n\n⚠️ Teste interrompido pelo usuário")
        sys.exit(1)
