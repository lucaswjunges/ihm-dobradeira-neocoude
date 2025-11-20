#!/usr/bin/env python3
"""
TESTE DE EMULAÇÃO E VALIDAÇÃO IHM WEB
Compara valores lidos diretamente do CLP vs valores mostrados na IHM Web via WebSocket

Data: 15/Nov/2025 04:00 BRT
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import asyncio
import websockets
import json
import time
from datetime import datetime
from modbus_client import ModbusClientWrapper
import modbus_map as mm

class IHMWebValidator:
    def __init__(self):
        # Cliente Modbus para ler diretamente do CLP
        self.modbus = ModbusClientWrapper(port='/dev/ttyUSB0', stub_mode=False)

        # WebSocket para ler dados da IHM Web
        self.ws_uri = "ws://localhost:8765"
        self.websocket = None
        self.ihm_web_state = {}

        # Resultados dos testes
        self.test_results = []

    async def connect_websocket(self):
        """Conecta ao WebSocket da IHM Web"""
        print("🔌 Conectando ao WebSocket da IHM Web...")
        try:
            self.websocket = await websockets.connect(self.ws_uri)
            print("✅ WebSocket conectado!")

            # Receber estado inicial
            initial_state = await self.websocket.recv()
            self.ihm_web_state = json.loads(initial_state)
            print(f"📦 Estado inicial recebido: {len(self.ihm_web_state)} campos")
            return True
        except Exception as e:
            print(f"❌ Erro ao conectar WebSocket: {e}")
            return False

    async def update_ihm_web_state(self, timeout=2.0):
        """Aguarda e processa atualizações do WebSocket"""
        try:
            message = await asyncio.wait_for(self.websocket.recv(), timeout=timeout)
            update = json.loads(message)
            self.ihm_web_state.update(update)
            return True
        except asyncio.TimeoutError:
            print("⏱️  Timeout aguardando atualização do WebSocket")
            return False
        except Exception as e:
            print(f"❌ Erro ao receber atualização: {e}")
            return False

    def read_clp_mode(self):
        """Lê modo diretamente do CLP (bit 0x02FF)"""
        return self.modbus.read_coil(mm.CRITICAL_STATES['MODE_BIT_REAL'])  # 0x02FF

    def read_ihm_web_mode(self):
        """Lê modo da IHM Web"""
        return self.ihm_web_state.get('mode_bit_02ff')

    def read_clp_leds(self):
        """Lê LEDs K1, K2, K3 diretamente do CLP"""
        led1 = self.modbus.read_coil(mm.LEDS['LED1'])  # 0x00C0
        led2 = self.modbus.read_coil(mm.LEDS['LED2'])  # 0x00C1
        led3 = self.modbus.read_coil(mm.LEDS['LED3'])  # 0x00C2
        return {'LED1': led1, 'LED2': led2, 'LED3': led3}

    def read_ihm_web_leds(self):
        """Lê LEDs da IHM Web"""
        leds = self.ihm_web_state.get('leds', {})
        return {
            'LED1': leds.get('LED1'),
            'LED2': leds.get('LED2'),
            'LED3': leds.get('LED3')
        }

    def read_clp_angle(self, bend_name):
        """Lê ângulo diretamente do CLP (32-bit)"""
        addrs = mm.BEND_ANGLES.get(bend_name)
        if not addrs:
            return None
        msw_addr, lsw_addr = addrs
        value_32bit = self.modbus.read_32bit(msw_addr, lsw_addr)
        if value_32bit is not None:
            return value_32bit / 10.0
        return None

    def read_ihm_web_angle(self, bend_name):
        """Lê ângulo da IHM Web"""
        angles = self.ihm_web_state.get('angles', {})
        return angles.get(bend_name)

    def print_separator(self, title):
        """Imprime separador visual"""
        print("\n" + "="*70)
        print(f"  {title}")
        print("="*70)

    def print_result(self, test_name, clp_value, ihm_value, match):
        """Registra resultado de teste"""
        symbol = "✅" if match else "❌"
        status = "SINCRONIZADO" if match else "DESSINCRONIZADO"

        result = {
            'test': test_name,
            'clp_value': clp_value,
            'ihm_value': ihm_value,
            'match': match,
            'status': status,
            'timestamp': datetime.now().isoformat()
        }
        self.test_results.append(result)

        print(f"\n{symbol} {test_name}: {status}")
        print(f"   CLP:     {clp_value}")
        print(f"   IHM Web: {ihm_value}")

        return match

    async def test_scenario_1_mode_change(self):
        """
        CENÁRIO 1: Mudança de Modo (MANUAL ↔ AUTO)
        """
        self.print_separator("CENÁRIO 1: Mudança de Modo (MANUAL ↔ AUTO)")

        # Passo 1: Estado inicial
        print("\n📖 Lendo estado inicial...")
        clp_mode_initial = self.read_clp_mode()
        ihm_mode_initial = self.read_ihm_web_mode()

        print(f"   CLP (0x02FF):  {clp_mode_initial} ({'AUTO' if clp_mode_initial else 'MANUAL'})")
        print(f"   IHM Web:       {ihm_mode_initial} ({'AUTO' if ihm_mode_initial else 'MANUAL'})")

        match_initial = (clp_mode_initial == ihm_mode_initial)
        self.print_result("Estado Inicial", clp_mode_initial, ihm_mode_initial, match_initial)

        # Passo 2: Trocar modo
        print("\n🔄 Alternando modo...")
        new_mode = not clp_mode_initial if clp_mode_initial is not None else True
        success = self.modbus.change_mode_direct(to_auto=new_mode)

        if not success:
            print("❌ Falha ao alterar modo via Modbus")
            return False

        time.sleep(0.5)  # Aguardar propagação

        # Aguardar atualização do WebSocket
        print("⏳ Aguardando atualização da IHM Web...")
        await self.update_ihm_web_state(timeout=3.0)

        # Passo 3: Verificar sincronização
        print("\n📖 Lendo estado após mudança...")
        clp_mode_after = self.read_clp_mode()
        ihm_mode_after = self.read_ihm_web_mode()

        print(f"   CLP (0x02FF):  {clp_mode_after} ({'AUTO' if clp_mode_after else 'MANUAL'})")
        print(f"   IHM Web:       {ihm_mode_after} ({'AUTO' if ihm_mode_after else 'MANUAL'})")

        match_after = (clp_mode_after == ihm_mode_after) and (clp_mode_after == new_mode)
        self.print_result("Estado Após Mudança", clp_mode_after, ihm_mode_after, match_after)

        # Voltar ao estado original
        print("\n↩️  Revertendo para estado original...")
        self.modbus.change_mode_direct(to_auto=clp_mode_initial)
        time.sleep(0.5)
        await self.update_ihm_web_state(timeout=3.0)

        return match_initial and match_after

    async def test_scenario_2_led_activation(self):
        """
        CENÁRIO 2: Ativação de LEDs (K1, K2, K3)
        """
        self.print_separator("CENÁRIO 2: Ativação de LEDs (K1, K2, K3)")

        # Passo 1: Estado inicial
        print("\n📖 Lendo LEDs iniciais...")
        clp_leds_initial = self.read_clp_leds()
        ihm_leds_initial = self.read_ihm_web_leds()

        print(f"   CLP:     {clp_leds_initial}")
        print(f"   IHM Web: {ihm_leds_initial}")

        match_initial = (clp_leds_initial == ihm_leds_initial)
        self.print_result("LEDs Iniciais", clp_leds_initial, ihm_leds_initial, match_initial)

        # Passo 2: Forçar LED1 ON (K1)
        print("\n💡 Forçando LED1 (K1) ON...")
        success = self.modbus.write_coil(mm.LEDS['LED1'], True)

        if not success:
            print("❌ Falha ao forçar LED1")
            return False

        time.sleep(0.5)
        await self.update_ihm_web_state(timeout=3.0)

        # Passo 3: Verificar sincronização
        print("\n📖 Lendo LEDs após ativação...")
        clp_leds_after = self.read_clp_leds()
        ihm_leds_after = self.read_ihm_web_leds()

        print(f"   CLP:     {clp_leds_after}")
        print(f"   IHM Web: {ihm_leds_after}")

        match_after = (clp_leds_after == ihm_leds_after) and clp_leds_after['LED1'] == True
        self.print_result("LEDs Após Ativação", clp_leds_after, ihm_leds_after, match_after)

        # Reverter
        print("\n↩️  Desligando LED1...")
        self.modbus.write_coil(mm.LEDS['LED1'], False)
        time.sleep(0.5)
        await self.update_ihm_web_state(timeout=3.0)

        return match_initial and match_after

    async def test_scenario_3_angle_write(self):
        """
        CENÁRIO 3: Escrita de Ângulo (90.5°)
        """
        self.print_separator("CENÁRIO 3: Escrita de Ângulo (90.5°)")

        bend_name = "BEND_1_LEFT"
        target_angle = 90.5

        # Passo 1: Estado inicial
        print(f"\n📖 Lendo ângulo inicial de {bend_name}...")
        clp_angle_initial = self.read_clp_angle(bend_name)
        ihm_angle_initial = self.read_ihm_web_angle(bend_name)

        print(f"   CLP:     {clp_angle_initial}°")
        print(f"   IHM Web: {ihm_angle_initial}°")

        match_initial = (clp_angle_initial == ihm_angle_initial)
        self.print_result(f"{bend_name} Inicial", clp_angle_initial, ihm_angle_initial, match_initial)

        # Passo 2: Escrever novo ângulo
        print(f"\n✏️  Escrevendo {target_angle}° em {bend_name}...")
        addrs = mm.BEND_ANGLES[bend_name]
        msw_addr, lsw_addr = addrs
        success = self.modbus.write_32bit(msw_addr, lsw_addr, int(target_angle * 10))

        if not success:
            print(f"❌ Falha ao escrever ângulo")
            return False

        time.sleep(0.5)

        # Aguardar polling da IHM Web (ciclo de leitura de ângulos a cada 20 polls)
        print("⏳ Aguardando próximo ciclo de leitura de ângulos (pode levar até 5s)...")
        for _ in range(3):
            await self.update_ihm_web_state(timeout=3.0)
            await asyncio.sleep(1)

        # Passo 3: Verificar sincronização
        print(f"\n📖 Lendo ângulo após escrita...")
        clp_angle_after = self.read_clp_angle(bend_name)
        ihm_angle_after = self.read_ihm_web_angle(bend_name)

        print(f"   CLP:     {clp_angle_after}°")
        print(f"   IHM Web: {ihm_angle_after}°")

        match_after = (clp_angle_after == ihm_angle_after) and (clp_angle_after == target_angle)
        self.print_result(f"{bend_name} Após Escrita", clp_angle_after, ihm_angle_after, match_after)

        # Reverter
        if clp_angle_initial is not None:
            print(f"\n↩️  Revertendo para {clp_angle_initial}°...")
            self.modbus.write_32bit(msw_addr, lsw_addr, int(clp_angle_initial * 10))
            time.sleep(0.5)

        return match_initial and match_after

    async def run_all_tests(self):
        """Executa todos os testes de validação"""
        print("╔" + "="*68 + "╗")
        print("║" + " "*10 + "VALIDAÇÃO SINCRONIZAÇÃO IHM WEB ↔ CLP" + " "*20 + "║")
        print("╚" + "="*68 + "╝")
        print(f"\n📅 Data: {datetime.now().strftime('%d/%b/%Y %H:%M:%S')}")
        print(f"🔧 Porta Modbus: /dev/ttyUSB0 @ 57600 bps")
        print(f"🌐 WebSocket: {self.ws_uri}")

        # Conectar WebSocket
        if not await self.connect_websocket():
            print("\n❌ Falha ao conectar WebSocket. Servidor rodando?")
            return False

        # Executar cenários
        results = []

        try:
            result_1 = await self.test_scenario_1_mode_change()
            results.append(("CENÁRIO 1 (Modo)", result_1))

            result_2 = await self.test_scenario_2_led_activation()
            results.append(("CENÁRIO 2 (LEDs)", result_2))

            result_3 = await self.test_scenario_3_angle_write()
            results.append(("CENÁRIO 3 (Ângulo)", result_3))

        finally:
            # Fechar WebSocket
            if self.websocket:
                await self.websocket.close()
                print("\n🔌 WebSocket desconectado")

            # Fechar Modbus
            self.modbus.close()
            print("🔌 Modbus desconectado")

        # Relatório final
        self.print_separator("RELATÓRIO FINAL")

        print("\n📊 RESUMO DOS TESTES:")
        passed = 0
        total = len(results)

        for test_name, result in results:
            symbol = "✅" if result else "❌"
            status = "PASSOU" if result else "FALHOU"
            print(f"   {symbol} {test_name}: {status}")
            if result:
                passed += 1

        print(f"\n📈 Taxa de Sucesso: {passed}/{total} ({100*passed/total:.0f}%)")

        if passed == total:
            print("\n🎉 SUCESSO COMPLETO!")
            print("✅ IHM Web está 100% sincronizada com o CLP")
            print("✅ Todas as leituras coincidem")
            print("✅ Todas as escritas são refletidas corretamente")
        else:
            print("\n⚠️  VERIFICAR FALHAS")
            print(f"❌ {total - passed} teste(s) falharam")

        # Detalhes dos testes
        print("\n📋 DETALHES DOS TESTES:")
        for i, result in enumerate(self.test_results, 1):
            symbol = "✅" if result['match'] else "❌"
            print(f"\n{i}. {result['test']}: {symbol} {result['status']}")
            print(f"   CLP:     {result['clp_value']}")
            print(f"   IHM Web: {result['ihm_value']}")

        print("\n" + "="*70)

        return passed == total

async def main():
    """Função principal"""
    validator = IHMWebValidator()

    try:
        success = await validator.run_all_tests()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Teste interrompido pelo usuário")
        sys.exit(130)
    except Exception as e:
        print(f"\n\n❌ Erro fatal: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    asyncio.run(main())
