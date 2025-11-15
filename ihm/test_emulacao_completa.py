#!/usr/bin/env python3
"""
Emulação Completa de Operador
==============================

Simula um operador real utilizando a IHM Web através de WebSocket.
Testa todas as funcionalidades principais do sistema.
"""

import asyncio
import websockets
import json
import time
from datetime import datetime


class OperadorVirtual:
    """Emula comportamento de operador usando a IHM"""

    def __init__(self, uri='ws://localhost:8765'):
        self.uri = uri
        self.ws = None
        self.state = {}
        self.logs = []

    def log(self, msg):
        """Adiciona log com timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        log_msg = f"[{timestamp}] {msg}"
        self.logs.append(log_msg)
        print(log_msg)

    async def conectar(self):
        """Conecta ao servidor WebSocket"""
        self.log("🔌 Conectando ao servidor IHM...")
        try:
            self.ws = await websockets.connect(self.uri)
            self.log("✅ Conectado ao servidor!")
            return True
        except Exception as e:
            self.log(f"❌ Erro ao conectar: {e}")
            return False

    async def receber_estado(self):
        """Recebe e processa mensagens do servidor"""
        try:
            message = await asyncio.wait_for(self.ws.recv(), timeout=2.0)
            data = json.loads(message)

            if data['type'] == 'full_state':
                self.state = data['data']
                self.log(f"📥 Estado completo recebido ({len(self.state)} campos)")
                self.log(f"   Modo: {self.state.get('mode_text', 'N/A')}")
                self.log(f"   Ângulo atual: {self.state.get('encoder_angle', 'N/A')}°")
                self.log(f"   Dobra 1: {self.state.get('bend_1_left', 'N/A')}°")

            elif data['type'] == 'state_update':
                # Atualiza apenas campos modificados
                changes = data['data']
                self.state.update(changes)

                # Log apenas mudanças relevantes
                if 'mode_text' in changes:
                    self.log(f"🔄 Modo alterado para: {changes['mode_text']}")
                if 'encoder_angle' in changes:
                    self.log(f"🔄 Ângulo: {changes['encoder_angle']}°")
                if any(k.startswith('led') for k in changes):
                    leds_ativos = [k for k, v in changes.items() if k.startswith('led') and v]
                    if leds_ativos:
                        self.log(f"💡 LEDs ativos: {', '.join(leds_ativos)}")

            return data

        except asyncio.TimeoutError:
            return None
        except Exception as e:
            self.log(f"❌ Erro ao receber: {e}")
            return None

    async def pressionar_tecla(self, key_name):
        """Pressiona uma tecla da IHM"""
        self.log(f"⌨️  Pressionando {key_name}...")

        await self.ws.send(json.dumps({
            'action': 'press_key',
            'key': key_name
        }))

        # Aguarda resposta
        try:
            response = await asyncio.wait_for(self.ws.recv(), timeout=1.0)
            data = json.loads(response)

            if data.get('type') == 'key_response':
                if data.get('success'):
                    self.log(f"✅ {key_name} pressionado com sucesso")
                else:
                    self.log(f"❌ Falha ao pressionar {key_name}")

        except asyncio.TimeoutError:
            self.log(f"⏱️  Timeout aguardando resposta de {key_name}")

    async def alterar_modo(self):
        """Alterna entre MANUAL e AUTO"""
        modo_atual = self.state.get('mode_text', 'UNKNOWN')
        self.log(f"🔄 Alternando modo (atual: {modo_atual})...")

        await self.ws.send(json.dumps({
            'action': 'toggle_mode'
        }))

        # Aguarda atualização do estado
        await asyncio.sleep(0.5)
        await self.receber_estado()

    async def mudar_velocidade(self):
        """Muda classe de velocidade (K1+K7)"""
        self.log("⚡ Mudando velocidade (K1+K7)...")

        await self.ws.send(json.dumps({
            'action': 'change_speed'
        }))

        try:
            response = await asyncio.wait_for(self.ws.recv(), timeout=1.0)
            data = json.loads(response)

            if data.get('success'):
                self.log("✅ Velocidade alterada")
            else:
                self.log("❌ Falha ao mudar velocidade")

        except asyncio.TimeoutError:
            self.log("⏱️  Timeout mudando velocidade")

    async def escrever_angulo(self, bend, angle):
        """Escreve ângulo de dobra"""
        self.log(f"📝 Escrevendo ângulo dobra {bend}: {angle}°...")

        await self.ws.send(json.dumps({
            'action': 'write_angle',
            'bend': bend,
            'angle': angle
        }))

        try:
            response = await asyncio.wait_for(self.ws.recv(), timeout=1.0)
            data = json.loads(response)

            if data.get('success'):
                self.log(f"✅ Ângulo {angle}° gravado na dobra {bend}")
            else:
                self.log(f"❌ Falha ao gravar ângulo")

        except asyncio.TimeoutError:
            self.log("⏱️  Timeout gravando ângulo")

    async def executar_teste_completo(self):
        """Executa sequência completa de testes"""

        self.log("\n" + "="*60)
        self.log("INICIANDO TESTE COMPLETO DE EMULAÇÃO")
        self.log("="*60 + "\n")

        # 1. Conectar
        if not await self.conectar():
            return False

        # 2. Receber estado inicial
        self.log("\n--- FASE 1: Recebimento de Estado Inicial ---")
        await self.receber_estado()
        await asyncio.sleep(1)

        # 3. Testar mudança de modo
        self.log("\n--- FASE 2: Teste de Mudança de Modo ---")
        await self.alterar_modo()
        await asyncio.sleep(1)

        # Voltar ao modo original
        await self.alterar_modo()
        await asyncio.sleep(1)

        # 4. Testar mudança de velocidade
        self.log("\n--- FASE 3: Teste de Mudança de Velocidade ---")
        await self.mudar_velocidade()
        await asyncio.sleep(1)

        # 5. Programar ângulos
        self.log("\n--- FASE 4: Programação de Ângulos ---")

        # CRÍTICO: Delay inicial de 2s antes da primeira gravação
        self.log("⏱️  Aguardando inicialização do CLP (2s)...")
        await asyncio.sleep(2.0)

        angulos = [90, 135, 45]

        for i, angulo in enumerate(angulos, start=1):
            await self.escrever_angulo(i, angulo)

            # IMPORTANTE: Delay de 1.5s entre gravações
            if i < 3:
                await asyncio.sleep(1.5)

            await self.receber_estado()  # Recebe atualização

        # 6. Simular operação manual
        self.log("\n--- FASE 5: Simulação de Operação Manual ---")
        sequencia_teclas = ['K1', 'K2', 'K3', 'ENTER', 'ESC']

        for tecla in sequencia_teclas:
            await self.pressionar_tecla(tecla)
            await asyncio.sleep(0.3)

        # 7. Testar S1 e S2
        self.log("\n--- FASE 6: Teste de Botões Funcionais ---")
        await self.pressionar_tecla('S1')
        await asyncio.sleep(0.5)

        await self.pressionar_tecla('S2')
        await asyncio.sleep(0.5)

        # 8. Monitorar estado por alguns segundos
        self.log("\n--- FASE 7: Monitoramento Contínuo (5s) ---")
        for i in range(10):
            await asyncio.sleep(0.5)
            update = await self.receber_estado()
            if update and update.get('type') == 'state_update':
                self.log(f"   [Monitor] {len(update.get('data', {}))} campos atualizados")

        # 9. Relatório final
        self.log("\n" + "="*60)
        self.log("TESTE COMPLETO FINALIZADO")
        self.log("="*60)
        self.log(f"\nTotal de logs: {len(self.logs)}")
        self.log(f"Estado final possui {len(self.state)} campos")

        # Exibir alguns campos importantes
        self.log("\n--- Estado Final da Máquina ---")
        campos_importantes = [
            'mode_text', 'encoder_angle', 'modbus_connected',
            'bend_1_left', 'bend_2_left', 'bend_3_left',
            'led1', 'led2', 'led3'
        ]

        for campo in campos_importantes:
            valor = self.state.get(campo, 'N/A')
            self.log(f"  {campo}: {valor}")

        await self.ws.close()
        return True


async def main():
    """Função principal"""
    operador = OperadorVirtual()

    try:
        await operador.executar_teste_completo()
    except KeyboardInterrupt:
        print("\n\n⚠️  Teste interrompido pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro durante teste: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
