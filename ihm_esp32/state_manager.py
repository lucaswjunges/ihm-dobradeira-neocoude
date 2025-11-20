#!/usr/bin/env python3
"""
State Manager - IHM Web Dobradeira
===================================

Gerenciador de estado da máquina com polling automático e inferência de tela.

ESTRATÉGIA HÍBRIDA:
- LÊ coils (botões, LEDs) via Modbus
- INFERE estado da tela baseado em lógica
- ESCREVE em área de supervisão (0x0940-0x0950)
- Mantém machine_state atualizado para IHM Web
"""

import asyncio
import time
from typing import Optional, Dict, Any
from datetime import datetime
from modbus_client import ModbusClientWrapper
import modbus_map as mm


class MachineStateManager:
    """
    Gerenciador de estado da máquina com inferência automática.
    """

    def __init__(self, modbus_client: ModbusClientWrapper, poll_interval: float = 0.25):
        """
        Inicializa gerenciador de estado.

        Args:
            modbus_client: Cliente Modbus (stub ou real)
            poll_interval: Intervalo de polling em segundos (padrão 250ms)
        """
        self.client = modbus_client
        self.poll_interval = poll_interval
        self.running = False

        # Estado completo da máquina
        self.machine_state: Dict[str, Any] = {
            # Encoder / Posição
            'encoder_raw': 0,
            'encoder_degrees': 0.0,

            # Ângulos programados
            'angles': {
                'bend_1_left': 0.0,
                'bend_2_left': 0.0,
                'bend_3_left': 0.0,
                'bend_1_right': 0.0,
                'bend_2_right': 0.0,
                'bend_3_right': 0.0,
            },

            # LEDs (estado dos indicadores)
            'leds': {
                'LED1': False,  # Dobra 1 ativa
                'LED2': False,  # Dobra 2 ativa
                'LED3': False,  # Dobra 3 ativa
                'LED4': False,  # Sentido esquerda
                'LED5': False,  # Sentido direita
            },

            # Botões (estado atual)
            'buttons': {},

            # I/O Digital
            'inputs': {},   # E0-E7
            'outputs': {},  # S0-S7

            # Estados críticos
            'modbus_enabled': False,
            'cycle_active': False,
            'mode_manual': True,

            # Supervisão (inferidos/escritos)
            'screen_num': 0,         # 0-10
            'bend_current': 0,       # 1, 2, 3 (0 = nenhuma)
            'direction': 0,          # 0=Esq, 1=Dir
            'speed_class': 5,        # 5, 10, 15 rpm
            'mode_state': 0,         # 0=Manual, 1=Auto

            # Metadados
            'connected': False,
            'modbus_connected': False,  # Para interface HTML
            'last_update': None,
            'poll_count': 0,
        }

    def infer_screen_number(self) -> int:
        """
        Infere número da tela baseado em LEDs e estados.

        Lógica:
        - Tela 0: Estado inicial (nenhum LED ativo)
        - Tela 2: Modo AUTO ativo
        - Tela 4: LED1 ativo (dobra 1)
        - Tela 5: LED2 ativo (dobra 2)
        - Tela 6: LED3 ativo (dobra 3)

        Returns:
            Número da tela (0-10)
        """
        leds = self.machine_state.get('leds', {})

        # Prioridade: LEDs de dobra (K1, K2, K3)
        if leds.get('LED1', False):
            return 4  # Tela dobra 1
        elif leds.get('LED2', False):
            return 5  # Tela dobra 2
        elif leds.get('LED3', False):
            return 6  # Tela dobra 3

        # Se modo AUTO (não manual), tela 2
        if not self.machine_state.get('mode_manual', True):
            return 2  # Tela modo AUTO

        # Padrão: tela inicial
        return 0

    def infer_bend_current(self) -> int:
        """Infere dobra atual (1, 2, 3) baseado em LEDs."""
        leds = self.machine_state.get('leds', {})
        if leds.get('LED1', False):
            return 1
        elif leds.get('LED2', False):
            return 2
        elif leds.get('LED3', False):
            return 3
        return 0

    def infer_direction(self) -> int:
        """Infere direção (0=Esq, 1=Dir) baseado em LEDs."""
        leds = self.machine_state.get('leds', {})
        return 1 if leds.get('LED5', False) else 0

    async def infer_speed_class(self) -> int:
        """
        Lê classe de velocidade do inversor (0x06E0).

        ✅ VALIDADO 20/Nov/2025 - Lê de 0x06E0 (RPM_READ)
        """
        # Executa em thread separada
        speed = await asyncio.to_thread(self.client.read_speed_class)
        return speed if speed in [5, 10, 15] else 5

    async def read_encoder(self) -> bool:
        """Lê encoder (32-bit) e atualiza estado."""
        try:
            # Executa chamada síncrona em thread separada para não bloquear event loop
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

    async def read_angles(self) -> bool:
        """
        Lê todos os ângulos programados.

        ATUALIZADO 16/Nov/2025: Usa novo método read_all_bend_angles()
        validado com 100% de precisão na área 0x0500-0x0504.
        """
        try:
            # Executa em thread separada
            angles = await asyncio.to_thread(self.client.read_all_bend_angles)

            if angles:
                # Atualiza estado com formato esperado pela interface
                self.machine_state['angles'] = {
                    'bend_1_left': angles.get('bend_1', 0.0),
                    'bend_2_left': angles.get('bend_2', 0.0),
                    'bend_3_left': angles.get('bend_3', 0.0),
                }
                return True
            return False
        except Exception as e:
            print(f"✗ Erro lendo ângulos: {e}")
            return False

    async def read_leds(self) -> bool:
        """Lê todos os LEDs."""
        try:
            # Executa em thread separada
            leds = await asyncio.to_thread(self.client.read_leds)
            if leds:
                self.machine_state['leds'] = leds
                return True
            return False
        except Exception as e:
            print(f"✗ Erro lendo LEDs: {e}")
            return False

    async def read_buttons(self) -> bool:
        """Lê todos os botões."""
        try:
            # Executa em thread separada
            buttons = await asyncio.to_thread(self.client.read_buttons)
            if buttons:
                self.machine_state['buttons'] = buttons
                return True
            return False
        except Exception as e:
            print(f"✗ Erro lendo botões: {e}")
            return False

    async def read_critical_states(self) -> bool:
        """Lê estados críticos."""
        try:
            # Executa todas as leituras em threads separadas
            modbus_enabled = await asyncio.to_thread(
                self.client.read_coil,
                mm.CRITICAL_STATES['MODBUS_SLAVE_ENABLED']
            )
            if modbus_enabled is not None:
                self.machine_state['modbus_enabled'] = modbus_enabled

            cycle_active = await asyncio.to_thread(
                self.client.read_coil,
                mm.CRITICAL_STATES['CYCLE_ACTIVE']
            )
            if cycle_active is not None:
                self.machine_state['cycle_active'] = cycle_active

            # Bit de modo REAL (02FF)
            mode_bit_02ff = await asyncio.to_thread(
                self.client.read_coil,
                mm.CRITICAL_STATES['MODE_BIT_REAL']
            )
            if mode_bit_02ff is not None:
                self.machine_state['mode_bit_02ff'] = mode_bit_02ff
                self.machine_state['mode_text'] = "AUTO" if mode_bit_02ff else "MANUAL"
                # Backward compatibility
                self.machine_state['mode_manual'] = not mode_bit_02ff

            # Entrada E6 (crítica para mudança de modo)
            input_e6 = await asyncio.to_thread(self.client.read_coil, 0x0106)  # E6
            if input_e6 is not None:
                self.machine_state['input_e6'] = input_e6
                self.machine_state['mode_change_allowed'] = input_e6

            return True
        except Exception as e:
            print(f"✗ Erro lendo estados críticos: {e}")
            return False

    async def update_supervision_state(self) -> bool:
        """
        Atualiza estados de supervisão (SOMENTE LEITURA).

        MODIFICADO 18/Nov/2025: Removidas todas as escritas em 0x0940-0x094E
        que causavam timeouts. Agora apenas infere valores localmente.
        """
        try:
            # Infere valores localmente (SEM escrever no CLP)
            screen_num = self.infer_screen_number()
            self.machine_state['screen_num'] = screen_num

            bend = self.infer_bend_current()
            self.machine_state['bend_current'] = bend

            direction = self.infer_direction()
            self.machine_state['direction'] = direction

            # Velocidade inferida localmente (modo manual = 5 rpm)
            # DESABILITADO 18/Nov/2025: Registro 0x094C não é confiável
            speed = await self.infer_speed_class()
            self.machine_state['speed_class'] = speed

            mode = 0 if self.machine_state.get('mode_manual', True) else 1
            self.machine_state['mode_state'] = mode

            # ✅ NENHUMA LEITURA/ESCRITA de registros de supervisão
            return True
        except Exception as e:
            print(f"✗ Erro atualizando estados de supervisão: {e}")
            return False

    async def poll_once(self) -> bool:
        """
        Executa um ciclo completo de polling.

        MODIFICADO 18/Nov/2025: Removidas escritas bloqueantes em registros de supervisão.
        Agora opera 100% em modo leitura + inferência local.
        """
        try:
            self.machine_state['poll_count'] += 1
            self.machine_state['last_update'] = datetime.now().isoformat()
            self.machine_state['connected'] = self.client.connected
            self.machine_state['modbus_connected'] = self.client.connected  # Para interface HTML

            # Leituras essenciais (rápidas, não bloqueantes com timeout=1s)
            await self.read_encoder()
            await self.read_leds()
            await self.read_critical_states()

            # Leituras menos frequentes para economizar largura de banda
            if self.machine_state['poll_count'] % 4 == 0:
                await self.read_buttons()

            if self.machine_state['poll_count'] % 20 == 0:
                await self.read_angles()

            # Atualiza estados de supervisão (SEM escritas no CLP)
            await self.update_supervision_state()
            return True
        except Exception as e:
            print(f"✗ Erro crítico em poll_once: {e}")
            import traceback
            traceback.print_exc()
            self.machine_state['modbus_connected'] = False  # Marca como desconectado em erro
            return False

    async def start_polling(self):
        """Inicia loop de polling contínuo."""
        self.running = True
        print(f"✓ State Manager iniciado (polling a cada {self.poll_interval}s)")

        while self.running:
            start_time = time.time()
            await self.poll_once()
            elapsed = time.time() - start_time
            sleep_time = max(0, self.poll_interval - elapsed)
            await asyncio.sleep(sleep_time)
            # CRÍTICO: Yield control para outros coroutines (HTTP/WebSocket)
            await asyncio.sleep(0)

    def stop_polling(self):
        """Para loop de polling."""
        self.running = False
        print("✓ State Manager parado")

    def get_state(self) -> Dict[str, Any]:
        """Retorna estado completo com campos achatados para compatibilidade."""
        state = self.machine_state.copy()

        # Achatar sub-dicionários para compatibilidade com interface
        if 'angles' in state:
            for key, value in state['angles'].items():
                state[key] = value

        # Garantir que encoder_angle está exposto (alias para encoder_degrees)
        state['encoder_angle'] = state.get('encoder_degrees', 0.0)

        return state

    def get_changes(self, previous_state: Dict[str, Any]) -> Dict[str, Any]:
        """Retorna apenas mudanças."""
        changes = {}
        for key, value in self.machine_state.items():
            if key not in previous_state or previous_state[key] != value:
                changes[key] = value
        return changes


if __name__ == "__main__":
    async def main():
        print("=== TESTE STATE MANAGER ===\n")
        client = ModbusClientWrapper(stub_mode=True)
        manager = MachineStateManager(client, poll_interval=1.0)

        print("Executando 5 ciclos de polling...\n")

        for i in range(5):
            await manager.poll_once()
            state = manager.get_state()
            print(f"Ciclo {i+1}:")
            print(f"  Encoder: {state['encoder_degrees']:.1f}°")
            print(f"  Tela inferida: {state['screen_num']}")
            print(f"  Dobra atual: {state['bend_current']}")
            print(f"  LEDs: LED1={state['leds']['LED1']}, LED2={state['leds']['LED2']}, LED3={state['leds']['LED3']}")
            print(f"  Modo: {'MANUAL' if state['mode_manual'] else 'AUTO'}\n")
            await asyncio.sleep(0.5)

        print("✅ Teste concluído!")
        client.close()

    asyncio.run(main())
