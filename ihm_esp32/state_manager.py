#!/usr/bin/env python3
"""
State Manager - IHM Web Dobradeira (Novo Ladder)
================================================

Gerenciador de estado da maquina baseado no novo programa ladder
com maquina de 8 estados distintos.

Referencia: PROJETO_LADDER_NOVO.md
"""

import asyncio
import copy
import time
from typing import Optional, Dict, Any
from datetime import datetime
from modbus_client import ModbusClientWrapper
import modbus_map as mm
from bend_logger import get_bend_logger


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

        # MELHORADO 08/Fev/2026: Flag para forçar leitura imediata de ângulos
        # Usado após escrita de ângulo para confirmação rápida
        self.force_angle_read = False

        # NOVO 08/Fev/2026: Sistema de auditoria de dobras
        # Detecta quando uma dobra é completada e registra automaticamente
        self._previous_state = None
        self._bend_start_time = None
        self._bend_start_angle = None
        self._bend_target_angle = None
        self._bend_logger = get_bend_logger(tolerance=2.0)

        # Callback para notificar quando uma dobra é registrada
        self.on_bend_logged = None  # Será setado pelo main_server

        # REMOVIDO: Filtro digital (CLP já fornece valor preciso 0-399)

        # Estado completo da maquina
        self.machine_state: Dict[str, Any] = {
            # Encoder / Posicao
            'encoder_raw': 0,
            'encoder_degrees': 0.0,

            # Angulos programados (0 até leitura do CLP)
            'angles': {
                'bend_1': 0.0,
                'bend_2': 0.0,
                'bend_3': 0.0,
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
        """
        Le encoder (16-bit) DIRETO do CLP em 04D6.

        CORRIGIDO 06/Jan/2026: Conversão encoder → IHM!
        - Encoder está em 0x04D6 (1238) - APENAS 1 REGISTRO de 16-bit
        - NÃO é 32-bit! NÃO precisa ler 04D7!
        - Valor 0-399 pulsos (ou mais se sem sensor zero)
        - Encoder mede DISCO que gira 2x mais que IHM
        - Conversão: pulsos → graus DISCO → graus IHM

        Exemplo:
        - Encoder: 376 pulsos
        - Disco: (376/400) × 360° = 338.4°
        - IHM: 338.4° / 2 = 169.2° ✅
        """
        try:
            # Ler contador de pulsos DIRETO (16-bit, apenas 04D6!)
            pulsos = await asyncio.to_thread(
                self.client.read_register,
                mm.ENCODER['ANGLE_MSW']  # Apenas 04D6, não lê 04D7!
            )

            if pulsos is not None:
                # Valor RAW do registro (pode ser > 399 sem sensor zero)
                self.machine_state['encoder_raw'] = pulsos

                # NORMALIZA para 0-399 com MOD 400
                # Necessário quando sensor zero está ausente (bancada de teste)
                # Com sensor: CLP zera automaticamente
                # Sem sensor: Acumula indefinidamente, precisamos MOD
                pulsos_normalizados = pulsos % 400

                # PASSO 1: Conversão pulsos → graus DISCO (0-360°)
                # 400 pulsos = 360° disco
                graus_disco = (pulsos_normalizados / 400.0) * 360.0

                # PASSO 2: Conversão disco → IHM (relação 2:1)
                # Disco gira o dobro do ângulo IHM devido à transmissão
                graus_ihm = graus_disco / 2.0

                # Atualiza estado (encoder_degrees agora é IHM!)
                self.machine_state['encoder_degrees'] = graus_ihm
                self.machine_state['encoder_degrees_disco'] = graus_disco  # Debug
                self.machine_state['encoder_pulses'] = pulsos_normalizados

                # Detecta movimento
                if hasattr(self, '_last_encoder_pulsos'):
                    delta = abs(pulsos - self._last_encoder_pulsos)
                    self.machine_state['encoder_moving'] = delta > 0
                else:
                    self.machine_state['encoder_moving'] = False

                self._last_encoder_pulsos = pulsos
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
        Le todos os angulos programados e converte para ângulos REAIS.

        CORRIGIDO 08/Fev/2026: Lê dos endereços de ESCRITA (0x0A00+)
        Os endereços antigos (0x0842+) dependiam do ladder copiar e retornavam 0.

        Endereços de leitura (DECIMAL): 2560, 2562, 2564
        Conversão: ângulo_real = valor_clp / 2
        """
        try:
            # Angulo 1 (endereço 2114 decimal)
            ang1 = await asyncio.to_thread(
                self.client.read_register,
                mm.BEND_ANGLES['ANGULO_1_READ']  # 2114
            )
            if ang1 is not None:
                self.machine_state['angles']['bend_1'] = mm.clp_to_real_angle(ang1)

            # Angulo 2 (endereço 2116 decimal)
            ang2 = await asyncio.to_thread(
                self.client.read_register,
                mm.BEND_ANGLES['ANGULO_2_READ']  # 2116
            )
            if ang2 is not None:
                self.machine_state['angles']['bend_2'] = mm.clp_to_real_angle(ang2)

            # Angulo 3 (endereço 2118 decimal)
            ang3 = await asyncio.to_thread(
                self.client.read_register,
                mm.BEND_ANGLES['ANGULO_3_READ']  # 2118
            )
            if ang3 is not None:
                self.machine_state['angles']['bend_3'] = mm.clp_to_real_angle(ang3)

            # Angulo alvo = angulo REAL da dobra atual
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

    def _detect_bend_completion(self):
        """
        Detecta quando uma dobra é completada e registra automaticamente.

        NOVO 08/Fev/2026: Sistema de auditoria de dobras.

        Detecta transição:
        - ST_DOBRANDO (0x0302) → qualquer outro estado = dobra completada
        - Registra ângulo programado vs ângulo executado
        - Emite alerta se erro exceder tolerância
        """
        current_state = self.machine_state.get('machine_state_address', 0x0300)

        # Detecta início de dobra (entrada em ST_DOBRANDO)
        if current_state == 0x0302 and self._previous_state != 0x0302:
            # Iniciou uma dobra
            self._bend_start_time = time.time()
            self._bend_start_angle = self.machine_state.get('encoder_degrees', 0.0)
            dobra_atual = self.machine_state.get('dobra_atual', 1)
            self._bend_target_angle = self.machine_state['angles'].get(f'bend_{dobra_atual}', 90.0)
            print(f"🔄 Dobra {dobra_atual} INICIADA (alvo: {self._bend_target_angle}°)")

        # Detecta fim de dobra (saída de ST_DOBRANDO)
        elif self._previous_state == 0x0302 and current_state != 0x0302:
            # Dobra completada - registrar
            if self._bend_start_time is not None:
                duration_ms = int((time.time() - self._bend_start_time) * 1000)
                angle_executed = self.machine_state.get('encoder_degrees', 0.0)
                angle_programmed = self._bend_target_angle or 90.0
                dobra_atual = self.machine_state.get('dobra_atual', 1)
                speed_rpm = self.machine_state.get('velocidade_rpm', 5.0)

                # Determina direção
                dir_avanco = self.machine_state.get('control_bits', {}).get('DIR_AVANCO', False)
                direction = 'CCW' if dir_avanco else 'CW'

                # Registra a dobra
                result = self._bend_logger.log_bend(
                    bend_number=dobra_atual,
                    angle_programmed=angle_programmed,
                    angle_executed=angle_executed,
                    speed_rpm=speed_rpm,
                    direction=direction,
                    duration_ms=duration_ms
                )

                # Armazena resultado para broadcast
                self.machine_state['last_bend_result'] = result

                # Notifica via callback se configurado
                if self.on_bend_logged and callable(self.on_bend_logged):
                    try:
                        self.on_bend_logged(result)
                    except Exception as e:
                        print(f"⚠️ Erro no callback on_bend_logged: {e}")

                # Limpa estado temporário
                self._bend_start_time = None
                self._bend_start_angle = None
                self._bend_target_angle = None

        # Atualiza estado anterior
        self._previous_state = current_state

    async def poll_once(self) -> bool:
        """
        Executa um ciclo completo de polling.

        CORRIGIDO 02/Jan/2026: Polling otimizado para encoder
        - Encoder SEMPRE lido (crítico para visualização em tempo real)
        - I/O e estados a cada ciclo durante movimento
        - Registros estáticos lidos menos frequentemente

        MELHORADO 08/Fev/2026: Detecção de conclusão de dobra para auditoria
        """
        try:
            self.machine_state['poll_count'] += 1
            self.machine_state['last_update'] = datetime.now().isoformat()
            self.machine_state['connected'] = self.client.connected
            self.machine_state['modbus_connected'] = self.client.connected

            # ==========================================
            # LEITURAS CRÍTICAS (TODO CICLO)
            # ==========================================
            # Encoder: SEMPRE lido para tracking em tempo real
            await self.read_encoder()

            # Estados da máquina: necessário para detectar movimento
            await self.read_machine_states()

            # NOVO 08/Fev/2026: Detecta conclusão de dobra para auditoria
            self._detect_bend_completion()

            # Bits de controle: direção, pedal, etc
            await self.read_control_bits()

            # ==========================================
            # LEITURAS FREQUENTES (A CADA 2 CICLOS)
            # ==========================================
            # Durante movimento, precisamos ler I/O com frequência
            if self.machine_state['poll_count'] % 2 == 0:
                await self.read_inputs()
                await self.read_outputs()
                await self.read_work_registers()  # Movido para cá (dobra atual, contador)

            # ==========================================
            # LEITURAS DE ÂNGULOS - MELHORADO 08/Fev/2026
            # ==========================================
            # Ângulos lidos a cada 5 ciclos (~1.5s) ou IMEDIATAMENTE se force_angle_read
            should_read_angles = (
                self.force_angle_read or  # Leitura forçada após escrita
                self.machine_state['poll_count'] % 5 == 0  # A cada 5 ciclos (era 20)
            )

            if should_read_angles:
                await self.read_angles()
                if self.force_angle_read:
                    print("✅ [StateManager] Leitura forçada de ângulos concluída")
                    self.force_angle_read = False  # Reset flag

            return True
        except Exception as e:
            print(f"✗ Erro critico em poll_once: {e}")
            import traceback
            traceback.print_exc()
            self.machine_state['modbus_connected'] = False
            return False

    async def start_polling(self):
        """
        Inicia loop de polling com taxa OTIMIZADA para Modbus RTU.

        OTIMIZADO 02/Jan/2026: Máximo desempenho respeitando limites do Modbus
        - MOVIMENTO: 50ms (20 Hz) - máximo sustentável em Modbus RTU 57600bps
        - PARADO: 150ms (6.7 Hz) - economia de CPU
        - SEM FILTRO: CLP já fornece dados precisos
        - Leitura direta com timeout otimizado
        """
        self.running = True
        idle_interval = 0.3     # OTIMIZADO 06/Jan/2026: 300ms quando parado (3.3 Hz)
        fast_interval = 0.1     # OTIMIZADO 06/Jan/2026: 100ms durante movimento (10 Hz)

        print(f"🚀 State Manager OTIMIZADO para Modbus RTU iniciado!")
        print(f"   📊 Parado: {idle_interval*1000:.0f}ms ({1/idle_interval:.1f} Hz)")
        print(f"   ⚡ Movimento: {fast_interval*1000:.0f}ms ({1/fast_interval:.0f} Hz)")
        print(f"   🎯 Polling balanceado para estabilidade máxima")

        while self.running:
            start_time = time.time()
            await self.poll_once()
            elapsed = time.time() - start_time

            # Polling adaptativo: rápido durante movimento
            current_state = self.machine_state.get('machine_state_address', 0x0300)
            is_moving = current_state in [0x0302, 0x0303]  # ST_DOBRANDO ou ST_RETORNANDO

            # Também considera encoder_moving (detecta movimento fino)
            encoder_moving = self.machine_state.get('encoder_moving', False)

            # Usa intervalo rápido se em movimento
            target_interval = fast_interval if (is_moving or encoder_moving) else idle_interval

            sleep_time = max(0, target_interval - elapsed)
            await asyncio.sleep(sleep_time)
            await asyncio.sleep(0)  # Yield control

    def stop_polling(self):
        """Para loop de polling."""
        self.running = False
        print("✓ State Manager parado")

    def get_state(self) -> Dict[str, Any]:
        """
        Retorna estado completo com campos achatados para compatibilidade.

        CORRIGIDO 08/Fev/2026: Deep copy para evitar referências compartilhadas
        que impediam get_changes() de detectar mudanças em dicts aninhados.
        """
        state = copy.deepcopy(self.machine_state)

        # Achatar angulos para compatibilidade
        if 'angles' in state:
            state['bend_1_left'] = state['angles'].get('bend_1', 0.0)
            state['bend_2_left'] = state['angles'].get('bend_2', 0.0)
            state['bend_3_left'] = state['angles'].get('bend_3', 0.0)

        # Alias para compatibilidade
        state['encoder_angle'] = state.get('encoder_degrees', 0.0)
        state['speed_class'] = int(state.get('velocidade_rpm', 5))

        # DESABILITADO 08/Fev/2026: PEDAL_SEGURA sempre False por solicitação do operador
        # O operador achou incômodo ter que segurar o pedal durante toda a dobra
        state['pedal_segura'] = False  # SEMPRE False - ignorar valor do CLP

        # Modo (para compatibilidade)
        state['mode_manual'] = state['states'].get('ST_MANUAL', False)

        # Encoder: Informações adicionais para visualização profissional
        state['encoder_pulses'] = state.get('encoder_pulses', 0)  # Pulsos 0-399
        state['encoder_moving'] = state.get('encoder_moving', False)  # Flag movimento

        # Sentido de rotação (inferido dos bits de controle)
        dir_avanco = state.get('control_bits', {}).get('DIR_AVANCO', False)  # CCW
        dir_recuo = state.get('control_bits', {}).get('DIR_RECUO', False)    # CW

        if dir_avanco:
            state['encoder_direction'] = 'CCW'  # Anti-horário
            state['encoder_direction_symbol'] = '⟲'
        elif dir_recuo:
            state['encoder_direction'] = 'CW'   # Horário
            state['encoder_direction_symbol'] = '⟳'
        else:
            state['encoder_direction'] = 'STOP'
            state['encoder_direction_symbol'] = '—'

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
