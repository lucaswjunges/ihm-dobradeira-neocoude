#!/usr/bin/env python3
"""
State Manager - IHM Web Dobradeira (Novo Ladder)
================================================

Gerenciador de estado da maquina baseado no novo programa ladder
com maquina de 8 estados distintos.

Referencia: PROJETO_LADDER_NOVO.md
"""

import asyncio
import time
from typing import Optional, Dict, Any
from datetime import datetime
from modbus_client import ModbusClientWrapper
import modbus_map as mm


class MachineStateManager:
    """
    Gerenciador de estado da maquina com suporte a maquina de estados.
    """

    def __init__(self, modbus_client: ModbusClientWrapper, poll_interval: float = 0.25):
        """
        Inicializa gerenciador de estado.

        Args:
            modbus_client: Cliente Modbus (stub ou real)
            poll_interval: Intervalo de polling em segundos (padrao 250ms)
        """
        self.client = modbus_client
        self.poll_interval = poll_interval
        self.running = False

        # Estado completo da maquina
        self.machine_state: Dict[str, Any] = {
            # Encoder / Posicao
            'encoder_raw': 0,
            'encoder_degrees': 0.0,

            # Angulos programados
            'angles': {
                'bend_1': 90.0,
                'bend_2': 90.0,
                'bend_3': 90.0,
            },

            # Angulo alvo atual
            'target_angle': 0.0,

            # Estado da maquina (novo ladder)
            'machine_state_address': 0x0300,  # Endereco do estado ativo
            'machine_state_name': 'PARADA',
            'machine_state_description': 'Maquina parada. Pressione o pedal para iniciar.',
            'machine_state_color': 'gray',
            'machine_state_icon': '⏸️',

            # Estados individuais (M000-M008)
            'states': {
                'ST_IDLE': False,
                'ST_AGUARDA_DIRECAO': False,
                'ST_DOBRANDO': False,
                'ST_RETORNANDO': False,
                'ST_AGUARDA_PROXIMA': False,
                'ST_COMPLETO': False,
                'ST_EMERGENCIA': False,
                'ST_MANUAL': False,
                'ST_CALIBRACAO': False,
            },

            # Bits de controle (B000-B007)
            'control_bits': {
                'DIR_AVANCO': False,
                'DIR_RECUO': False,
                'MODO_AUTO': False,
                'MODO_MANUAL': False,
                'PEDAL_SEGURA': False,
                'NA_POSICAO_ZERO': False,
                'ATINGIU_ANGULO': False,
                'HABILITADO': False,
            },

            # Entradas digitais (E0-E7)
            'inputs': {
                'E0': False,  # Sensor Zero
                'E2': False,  # Pedal Avanco
                'E3': False,  # Pedal Parada
                'E4': False,  # Pedal Recuo
                'E5': False,  # Sensor Seguranca
                'E6': False,  # Botao Emergencia
            },

            # Saidas digitais (S0-S7)
            'outputs': {
                'S0': False,  # Motor Avanco
                'S1': False,  # Motor Recuo
                'S2': False,  # Inversor
                'S4': False,  # LED Dobra 1
                'S5': False,  # LED Dobra 2
                'S6': False,  # LED Dobra 3
            },

            # Registros de trabalho
            'dobra_atual': 1,
            'contador_pecas': 0,
            'velocidade_rpm': 5.0,

            # LEDs (para compatibilidade)
            'leds': {
                'LED1': False,
                'LED2': False,
                'LED3': False,
                'LED4': False,
                'LED5': False,
            },

            # Calibracao (Estado 8) - DESATIVADO 02/Jan/2026
            # 'calibration': {
            #     'active': False,
            #     'step_code': 0,
            #     'step_name': 'Inativo',
            #     'step_description': '',
            #     'progress': 0,
            #     'resultado_zero': 0,
            #     'resultado_inercia': 0,
            #     'resultado_offset': 0,
            # },

            # Metadados
            'connected': False,
            'modbus_connected': False,
            'last_update': None,
            'poll_count': 0,
        }

    async def read_encoder(self) -> bool:
        """Le encoder (32-bit) e atualiza estado."""
        try:
            raw = await asyncio.to_thread(
                self.client.read_32bit,
                mm.ENCODER['ANGLE_MSW'],
                mm.ENCODER['ANGLE_LSW']
            )
            if raw is not None:
                self.machine_state['encoder_raw'] = raw
                self.machine_state['encoder_degrees'] = mm.clp_to_degrees(raw)
                return True
            return False
        except Exception as e:
            print(f"✗ Erro lendo encoder: {e}")
            return False

    async def read_machine_states(self) -> bool:
        """
        Le os 8 estados da maquina (M000-M007) e determina qual esta ativo.
        """
        try:
            state_values = {}

            for name, addr in mm.MACHINE_STATES.items():
                value = await asyncio.to_thread(self.client.read_coil, addr)
                state_values[addr] = value if value is not None else False
                self.machine_state['states'][name] = state_values[addr]

            # Determina qual estado esta ativo
            active_addr = None
            for addr, value in state_values.items():
                if value:
                    active_addr = addr
                    break

            if active_addr is None:
                active_addr = mm.MACHINE_STATES['ST_IDLE']

            # Atualiza informacoes do estado ativo
            state_info = mm.get_state_info(active_addr)
            self.machine_state['machine_state_address'] = active_addr
            self.machine_state['machine_state_name'] = state_info['name']
            self.machine_state['machine_state_description'] = state_info['description']
            self.machine_state['machine_state_color'] = state_info['color']
            self.machine_state['machine_state_icon'] = state_info['icon']

            return True
        except Exception as e:
            print(f"✗ Erro lendo estados da maquina: {e}")
            return False

    async def read_control_bits(self) -> bool:
        """
        Le os bits de controle (B000-B007).
        """
        try:
            for name, addr in mm.CONTROL_BITS.items():
                value = await asyncio.to_thread(self.client.read_coil, addr)
                self.machine_state['control_bits'][name] = value if value is not None else False

            return True
        except Exception as e:
            print(f"✗ Erro lendo bits de controle: {e}")
            return False

    async def read_inputs(self) -> bool:
        """
        Le as entradas digitais (E0-E7).
        """
        try:
            for name, addr in mm.DIGITAL_INPUTS.items():
                value = await asyncio.to_thread(self.client.read_coil, addr)
                if name in self.machine_state['inputs']:
                    self.machine_state['inputs'][name] = value if value is not None else False

            return True
        except Exception as e:
            print(f"✗ Erro lendo entradas: {e}")
            return False

    async def read_outputs(self) -> bool:
        """
        Le as saidas digitais (S0-S7).
        """
        try:
            for name, addr in mm.DIGITAL_OUTPUTS.items():
                value = await asyncio.to_thread(self.client.read_coil, addr)
                if name in self.machine_state['outputs']:
                    self.machine_state['outputs'][name] = value if value is not None else False

            # Atualiza LEDs baseado nas saidas (para compatibilidade)
            self.machine_state['leds']['LED1'] = self.machine_state['outputs'].get('S4', False)
            self.machine_state['leds']['LED2'] = self.machine_state['outputs'].get('S5', False)
            self.machine_state['leds']['LED3'] = self.machine_state['outputs'].get('S6', False)

            return True
        except Exception as e:
            print(f"✗ Erro lendo saidas: {e}")
            return False

    async def read_work_registers(self) -> bool:
        """
        Le os registros de trabalho (dobra atual, contador, velocidade).
        """
        try:
            # Dobra atual (0x0918)
            dobra = await asyncio.to_thread(
                self.client.read_register,
                mm.WORK_REGISTERS['DOBRA_ATUAL']
            )
            if dobra is not None:
                self.machine_state['dobra_atual'] = dobra

            # Contador de pecas (0x0920)
            pecas = await asyncio.to_thread(
                self.client.read_register,
                mm.WORK_REGISTERS['CONTADOR_PECAS']
            )
            if pecas is not None:
                self.machine_state['contador_pecas'] = pecas

            # Velocidade do inversor (0x06E0)
            vel_raw = await asyncio.to_thread(
                self.client.read_register,
                mm.INVERTER['VELOCIDADE_INVERSOR']
            )
            if vel_raw is not None:
                self.machine_state['velocidade_rpm'] = mm.register_to_rpm(vel_raw)

            return True
        except Exception as e:
            print(f"✗ Erro lendo registros de trabalho: {e}")
            return False

    # DESATIVADO 02/Jan/2026: Auto-calibração removida (ajuste manual via ângulos)
    # async def read_calibration(self) -> bool:
    #     """
    #     Le os dados de calibracao (Estado 8).
    #     """
    #     try:
    #         # Verifica se esta em modo calibracao
    #         calib_active = await asyncio.to_thread(
    #             self.client.read_coil,
    #             mm.CALIBRATION['ST_CALIBRACAO']
    #         )
    #         self.machine_state['calibration']['active'] = calib_active if calib_active is not None else False
    #
    #         # Le etapa atual do sequenciador
    #         etapa = await asyncio.to_thread(
    #             self.client.read_register,
    #             mm.CALIBRATION['ETAPA_CALIB']
    #         )
    #         if etapa is not None:
    #             self.machine_state['calibration']['step_code'] = etapa
    #             step_info = mm.get_calibration_step_info(etapa)
    #             self.machine_state['calibration']['step_name'] = step_info['name']
    #             self.machine_state['calibration']['step_description'] = step_info['description']
    #             self.machine_state['calibration']['progress'] = step_info['progress']
    #
    #         # Le resultados (quando calibracao finalizada)
    #         if self.machine_state['calibration']['step_code'] >= 70:
    #             resultado_zero = await asyncio.to_thread(
    #                 self.client.read_register,
    #                 mm.CALIBRATION['RESULTADO_ZERO']
    #             )
    #             if resultado_zero is not None:
    #                 self.machine_state['calibration']['resultado_zero'] = resultado_zero
    #
    #             resultado_inercia = await asyncio.to_thread(
    #                 self.client.read_register,
    #                 mm.CALIBRATION['RESULTADO_INERCIA']
    #             )
    #             if resultado_inercia is not None:
    #                 self.machine_state['calibration']['resultado_inercia'] = resultado_inercia
    #
    #             resultado_offset = await asyncio.to_thread(
    #                 self.client.read_register,
    #                 mm.CALIBRATION['RESULTADO_OFFSET']
    #             )
    #             if resultado_offset is not None:
    #                 self.machine_state['calibration']['resultado_offset'] = resultado_offset
    #
    #         return True
    #     except Exception as e:
    #         print(f"✗ Erro lendo calibracao: {e}")
    #         return False

    async def read_angles(self) -> bool:
        """
        Le todos os angulos programados.
        CORRIGIDO 27/Nov/2025: Le de 0x0842+ (onde o ladder copia os valores)
        """
        try:
            # Angulo 1 (0x0842)
            ang1 = await asyncio.to_thread(
                self.client.read_register,
                mm.BEND_ANGLES['ANGULO_1_READ']
            )
            if ang1 is not None:
                self.machine_state['angles']['bend_1'] = ang1 / 10.0

            # Angulo 2 (0x0844)
            ang2 = await asyncio.to_thread(
                self.client.read_register,
                mm.BEND_ANGLES['ANGULO_2_READ']
            )
            if ang2 is not None:
                self.machine_state['angles']['bend_2'] = ang2 / 10.0

            # Angulo 3 (0x0846)
            ang3 = await asyncio.to_thread(
                self.client.read_register,
                mm.BEND_ANGLES['ANGULO_3_READ']
            )
            if ang3 is not None:
                self.machine_state['angles']['bend_3'] = ang3 / 10.0

            # Angulo alvo = angulo da dobra atual
            dobra = self.machine_state.get('dobra_atual', 1)
            if dobra == 1:
                self.machine_state['target_angle'] = self.machine_state['angles']['bend_1']
            elif dobra == 2:
                self.machine_state['target_angle'] = self.machine_state['angles']['bend_2']
            else:
                self.machine_state['target_angle'] = self.machine_state['angles']['bend_3']

            return True
        except Exception as e:
            print(f"✗ Erro lendo angulos: {e}")
            return False

    async def poll_once(self) -> bool:
        """
        Executa um ciclo completo de polling.
        """
        try:
            self.machine_state['poll_count'] += 1
            self.machine_state['last_update'] = datetime.now().isoformat()
            self.machine_state['connected'] = self.client.connected
            self.machine_state['modbus_connected'] = self.client.connected

            # Leituras essenciais (a cada ciclo)
            await self.read_encoder()
            await self.read_machine_states()
            await self.read_control_bits()

            # DESATIVADO 02/Jan/2026: Auto-calibração removida
            # if self.machine_state['calibration']['active'] or self.machine_state['poll_count'] % 4 == 0:
            #     await self.read_calibration()

            # Leituras de I/O (a cada 2 ciclos)
            if self.machine_state['poll_count'] % 2 == 0:
                await self.read_inputs()
                await self.read_outputs()

            # Leituras menos frequentes (a cada 4 ciclos)
            if self.machine_state['poll_count'] % 4 == 0:
                await self.read_work_registers()

            # Leitura de angulos (a cada 20 ciclos - sao estaticos)
            if self.machine_state['poll_count'] % 20 == 0:
                await self.read_angles()

            return True
        except Exception as e:
            print(f"✗ Erro critico em poll_once: {e}")
            import traceback
            traceback.print_exc()
            self.machine_state['modbus_connected'] = False
            return False

    async def start_polling(self):
        """Inicia loop de polling continuo."""
        self.running = True
        print(f"✓ State Manager iniciado (polling a cada {self.poll_interval}s)")

        while self.running:
            start_time = time.time()
            await self.poll_once()
            elapsed = time.time() - start_time
            sleep_time = max(0, self.poll_interval - elapsed)
            await asyncio.sleep(sleep_time)
            await asyncio.sleep(0)  # Yield control

    def stop_polling(self):
        """Para loop de polling."""
        self.running = False
        print("✓ State Manager parado")

    def get_state(self) -> Dict[str, Any]:
        """Retorna estado completo com campos achatados para compatibilidade."""
        state = self.machine_state.copy()

        # Achatar angulos para compatibilidade
        if 'angles' in state:
            state['bend_1_left'] = state['angles'].get('bend_1', 0.0)
            state['bend_2_left'] = state['angles'].get('bend_2', 0.0)
            state['bend_3_left'] = state['angles'].get('bend_3', 0.0)

        # Alias para compatibilidade
        state['encoder_angle'] = state.get('encoder_degrees', 0.0)
        state['speed_class'] = int(state.get('velocidade_rpm', 5))

        # Flag PEDAL_SEGURA para interface
        state['pedal_segura'] = state['control_bits'].get('PEDAL_SEGURA', False)

        # Modo (para compatibilidade)
        state['mode_manual'] = state['states'].get('ST_MANUAL', False)

        return state

    def get_changes(self, previous_state: Dict[str, Any]) -> Dict[str, Any]:
        """Retorna apenas mudancas."""
        changes = {}
        current = self.get_state()

        for key, value in current.items():
            if key not in previous_state or previous_state[key] != value:
                changes[key] = value

        return changes


if __name__ == "__main__":
    async def main():
        print("=== TESTE STATE MANAGER (NOVO LADDER) ===\n")
        client = ModbusClientWrapper(stub_mode=True)
        manager = MachineStateManager(client, poll_interval=1.0)

        print("Executando 5 ciclos de polling...\n")

        for i in range(5):
            await manager.poll_once()
            state = manager.get_state()
            print(f"Ciclo {i+1}:")
            print(f"  Encoder: {state['encoder_degrees']:.1f}°")
            print(f"  Estado: {state['machine_state_icon']} {state['machine_state_name']}")
            print(f"  Descricao: {state['machine_state_description']}")
            print(f"  Dobra atual: {state['dobra_atual']}")
            print(f"  Pecas: {state['contador_pecas']}")
            print(f"  Velocidade: {state['velocidade_rpm']:.1f} RPM")
            print(f"  PEDAL_SEGURA: {state['pedal_segura']}")
            print()
            await asyncio.sleep(0.5)

        print("✅ Teste concluido!")
        client.close()

    asyncio.run(main())
