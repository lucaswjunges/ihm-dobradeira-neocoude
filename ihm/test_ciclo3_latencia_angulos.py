#!/usr/bin/env python3
"""
TESTE CICLO 3: LATÊNCIA DE ÂNGULOS
===================================

Valida otimização de leitura imediata após write_angle.

ANTES (CICLO 2): Ângulos levavam ~5s para refletir (polling a cada 20 ciclos)
DEPOIS (CICLO 3): Ângulos devem refletir em < 1s (leitura forçada imediatamente)

Teste:
1. Conecta ao servidor IHM
2. Escreve ângulo 90° na dobra 1
3. Aguarda 1 segundo
4. Verifica se ângulo já aparece no estado
5. Mede latência real
"""

import asyncio
import websockets
import json
import time
from datetime import datetime


class TestadorLatenciaAngulos:
    """Testa latência de atualização de ângulos após escrita."""

    def __init__(self, ws_uri: str = "ws://localhost:8765"):
        self.ws_uri = ws_uri
        self.websocket = None
        self.state = {}
        self.connected = False

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
            print(f"✅ Conectado! Estado inicial: {len(self.state)} campos\n")

        except Exception as e:
            print(f"❌ Erro na conexão: {e}")
            self.connected = False
            return False

        return True

    async def disconnect(self):
        """Desconecta do servidor."""
        if self.websocket:
            await self.websocket.close()
            self.connected = False
            print("🔌 Desconectado")

    async def write_angle_and_measure(self, bend_num: int, angle: float):
        """
        Escreve ângulo e mede latência até aparecer no estado.

        Returns:
            float: Latência em segundos, ou None se falhou
        """
        if not self.connected:
            print("❌ Não conectado!")
            return None

        print(f"📐 Escrevendo ângulo: Dobra {bend_num} = {angle}°")

        # Timestamp ANTES da escrita
        t0 = time.time()

        # Enviar comando
        command = {'action': 'write_angle', 'bend': bend_num, 'angle': angle}
        await self.websocket.send(json.dumps(command))

        # Receber resposta (angle_response)
        try:
            response = await asyncio.wait_for(self.websocket.recv(), timeout=2.0)
            response_data = json.loads(response)
            print(f"✅ Resposta servidor: {response_data.get('type')}")
        except asyncio.TimeoutError:
            print(f"⚠️  Timeout esperando resposta (mas isso é OK)")

        # Aguardar broadcasts e medir quando ângulo aparece
        angle_found = False
        latency = None
        max_wait = 6.0  # Máximo 6 segundos (maior que os 5s antigos)
        deadline = t0 + max_wait

        angle_keys = {
            1: 'bend_1_left',
            2: 'bend_2_left',
            3: 'bend_3_left'
        }
        key_to_check = angle_keys.get(bend_num)

        print(f"⏱️  Aguardando ângulo aparecer em '{key_to_check}'...\n")

        while time.time() < deadline and not angle_found:
            try:
                # Receber broadcasts
                msg = await asyncio.wait_for(
                    self.websocket.recv(),
                    timeout=max(0.1, deadline - time.time())
                )
                msg_data = json.loads(msg)

                # Atualizar estado local
                if 'data' in msg_data:
                    changes = msg_data['data']
                    self.state.update(changes)

                    # Verificar se ângulo apareceu
                    if 'angles' in changes:
                        angles_dict = changes['angles']
                        if key_to_check in angles_dict:
                            angle_valor = angles_dict[key_to_check]

                            # Validar se é o ângulo esperado (±1° tolerância)
                            if abs(angle_valor - angle) < 1.0:
                                latency = time.time() - t0
                                angle_found = True
                                print(f"🎯 ÂNGULO ENCONTRADO!")
                                print(f"   Valor: {angle_valor}°")
                                print(f"   Latência: {latency:.3f}s")
                                break

            except asyncio.TimeoutError:
                # Timeout no recv - continua aguardando
                pass

        if not angle_found:
            elapsed = time.time() - t0
            print(f"❌ TIMEOUT! Ângulo NÃO apareceu em {elapsed:.1f}s")
            return None

        return latency

    async def run_test(self):
        """Executa teste completo de latência."""
        print("╔" + "═"*68 + "╗")
        print("║" + " "*68 + "║")
        print("║" + "  CICLO 3: TESTE DE LATÊNCIA DE ÂNGULOS".center(68) + "║")
        print("║" + " "*68 + "║")
        print("╚" + "═"*68 + "╝\n")

        # Conectar
        if not await self.connect():
            return False

        # Mostrar estado inicial de ângulos
        print("📊 Estado inicial dos ângulos:")
        angles_inicial = self.state.get('angles', {})
        for nome, valor in angles_inicial.items():
            if 0 <= valor <= 180:
                print(f"   {nome}: {valor:.1f}°")
            elif valor > 1000:
                print(f"   {nome}: (não programado - {valor:.0f}°)")
        print()

        # TESTE 1: Dobra 1 = 90°
        print("━"*70)
        print("TESTE 1: Dobra 1 = 90°")
        print("━"*70)
        latencia1 = await self.write_angle_and_measure(1, 90.0)

        await asyncio.sleep(1.0)

        # TESTE 2: Dobra 2 = 120°
        print("\n" + "━"*70)
        print("TESTE 2: Dobra 2 = 120°")
        print("━"*70)
        latencia2 = await self.write_angle_and_measure(2, 120.0)

        await asyncio.sleep(1.0)

        # TESTE 3: Dobra 3 = 45°
        print("\n" + "━"*70)
        print("TESTE 3: Dobra 3 = 45°")
        print("━"*70)
        latencia3 = await self.write_angle_and_measure(3, 45.0)

        # Desconectar
        await self.disconnect()

        # RELATÓRIO FINAL
        print("\n" + "╔" + "═"*68 + "╗")
        print("║" + " "*68 + "║")
        print("║" + "  RELATÓRIO DE LATÊNCIA".center(68) + "║")
        print("║" + " "*68 + "║")
        print("╚" + "═"*68 + "╝\n")

        latencias = []

        if latencia1:
            print(f"✅ Dobra 1: {latencia1:.3f}s")
            latencias.append(latencia1)
        else:
            print(f"❌ Dobra 1: FALHOU")

        if latencia2:
            print(f"✅ Dobra 2: {latencia2:.3f}s")
            latencias.append(latencia2)
        else:
            print(f"❌ Dobra 2: FALHOU")

        if latencia3:
            print(f"✅ Dobra 3: {latencia3:.3f}s")
            latencias.append(latencia3)
        else:
            print(f"❌ Dobra 3: FALHOU")

        # Calcular média
        if latencias:
            media = sum(latencias) / len(latencias)
            print(f"\n📊 Latência Média: {media:.3f}s")

            # Validar sucesso
            print("\n" + "─"*70)
            if media < 1.0:
                print("🎉 CICLO 3 APROVADO!")
                print(f"   Objetivo: < 1.0s")
                print(f"   Alcançado: {media:.3f}s")
                print(f"   Melhoria vs CICLO 2: ~{((5.0 - media) / 5.0 * 100):.0f}% mais rápido")
                print("\n✅ Otimização de leitura imediata FUNCIONANDO!")
            elif media < 2.0:
                print("⚠️  CICLO 3 PARCIALMENTE APROVADO")
                print(f"   Objetivo: < 1.0s")
                print(f"   Alcançado: {media:.3f}s")
                print(f"   Ainda melhor que CICLO 2 (5s), mas pode melhorar")
            else:
                print("❌ CICLO 3 FALHOU")
                print(f"   Objetivo: < 1.0s")
                print(f"   Alcançado: {media:.3f}s")
                print("\n⚠️  Possível problema na otimização - investigar!")
        else:
            print("\n❌ TODOS OS TESTES FALHARAM - sistema com problema!")

        return True


async def main():
    """Função principal."""
    testador = TestadorLatenciaAngulos()
    await testador.run_test()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Teste interrompido pelo usuário")
