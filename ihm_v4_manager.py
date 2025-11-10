"""
IHM v4 - Screen Manager
Emulador da IHM Expert Series 4004.95C com backend centralizado

Arquitetura:
- Backend: Lê Modbus, formata telas, gerencia navegação
- Frontend: LCD "burro" (2×20) + Teclado virtual
- Comunicação: WebSocket (envia texto pronto)
"""

import asyncio
import logging
from typing import Tuple, Dict, Any

logger = logging.getLogger(__name__)


class IHMv4Manager:
    """Gerenciador de telas da IHM Expert Series (backend)"""

    def __init__(self, modbus_client):
        self.modbus = modbus_client
        self.current_screen = 0
        self.total_screens = 11
        self.edit_mode = False
        self.edit_value = ""
        self.edit_field = None

        # Cache de dados do CLP (atualizados por polling)
        self.machine_data = {
            'encoder': 0,
            'encoder_degrees': 0,
            'angles': {
                'aj1_esq': 0, 'aj1_dir': 0,
                'aj2_esq': 0, 'aj2_dir': 0,
                'aj3_esq': 0, 'aj3_dir': 0
            },
            'speed_class': 1,
            'active_bend': 1,
            'direction': None,  # 'CCW' ou 'CW'
            'cycle_active': False,
            'auto_mode': False,
            'carenagem_ok': True,
            'runtime_hours': 0,
            'runtime_minutes': 0,
            'machine_state': 3,  # 0=Parada, 1=Operando, 2=Erro, 3=Standby
        }

        # LEDs ativos (para enviar ao frontend)
        self.leds = {
            'K1': False,  # Dobra 1
            'K2': False,  # Dobra 2
            'K3': False,  # Dobra 3
            'K4': False,  # Sentido anti-horário
            'K5': False,  # Sentido horário
            'S1': False,  # Modo AUTO
        }

    # ==================== MÉTODOS PÚBLICOS ====================

    async def get_display_state(self) -> Dict[str, Any]:
        """
        Retorna estado completo do display para envio via WebSocket

        Returns:
            {
                'line1': str,
                'line2': str,
                'screen': int,
                'leds': dict,
                'edit_mode': bool
            }
        """
        line1, line2 = self.get_current_screen_text()

        # Atualizar LEDs
        self._update_leds()

        return {
            'line1': line1,
            'line2': line2,
            'screen': self.current_screen,
            'leds': self.leds.copy(),
            'edit_mode': self.edit_mode
        }

    async def handle_key_press(self, key_code: int) -> Dict[str, Any]:
        """
        Processa tecla pressionada

        Args:
            key_code: Código Modbus da tecla (160-241)

        Returns:
            Estado atualizado do display
        """
        logger.info(f"IHM v4: Tecla pressionada: {key_code}")

        # Mapear código para nome da tecla
        key_name = self._get_key_name(key_code)

        # Processar no contexto atual
        if self.edit_mode:
            await self._handle_key_edit_mode(key_code, key_name)
        else:
            await self._handle_key_navigation_mode(key_code, key_name)

        # Também enviar tecla para o CLP (simulação física)
        await self._send_key_to_plc(key_code)

        # Retornar novo estado
        return await self.get_display_state()

    async def update_machine_data(self, data: Dict[str, Any]):
        """
        Atualiza dados da máquina (chamado pelo polling)

        Args:
            data: Dicionário com dados lidos do CLP via Modbus
        """
        self.machine_data.update(data)

        # Recalcular graus se encoder mudou
        if 'encoder' in data:
            self.machine_data['encoder_degrees'] = self._encoder_to_degrees(
                data['encoder']
            )

    def get_current_screen_text(self) -> Tuple[str, str]:
        """
        Retorna texto das 2 linhas da tela atual

        Returns:
            (linha1, linha2) - cada uma com exatamente 20 caracteres
        """
        screen_method = getattr(self, f'_screen_{self.current_screen}', None)

        if screen_method is None:
            return ('ERRO: Tela inválida', f'Tela {self.current_screen}')

        line1, line2 = screen_method()

        # Garantir exatamente 20 caracteres por linha
        return (self._format_line(line1), self._format_line(line2))

    # ==================== TELAS (11 TELAS) ====================

    def _screen_0(self) -> Tuple[str, str]:
        """Tela 0: Splash Screen"""
        return (
            '**TRILLOR MAQUINAS**',
            '**DOBRADEIRA HD    **'
        )

    def _screen_1(self) -> Tuple[str, str]:
        """Tela 1: Cliente"""
        return (
            'CAMARGO CORREIA CONS',
            'AQUISICAO AGOSTO-06 '
        )

    def _screen_2(self) -> Tuple[str, str]:
        """Tela 2: Modo AUTO/MAN"""
        mode = 'AUTO  ' if self.machine_data['auto_mode'] else 'MANUAL'
        return (
            'SELECAO DE AUTO/MAN ',
            f'        [{mode}]      '
        )

    def _screen_3(self) -> Tuple[str, str]:
        """Tela 3: Encoder (posição angular)"""
        degrees = self.machine_data['encoder_degrees']
        count = self.machine_data['encoder']

        return (
            'DESLOCAMENTO ANGULAR',
            f'PV={degrees:3d}° ({count:5d})   '
        )

    def _screen_4(self) -> Tuple[str, str]:
        """Tela 4: Ângulo Dobra 1"""
        # Selecionar ângulo baseado na direção
        if self.machine_data['direction'] == 'CW':
            aj = self.machine_data['angles']['aj1_dir']
        else:
            aj = self.machine_data['angles']['aj1_esq']

        pv = self.machine_data['encoder_degrees']

        return (
            'AJUSTE DO ANGULO 01 ',
            f'AJ={aj:3d}° PV={pv:3d}°     '
        )

    def _screen_5(self) -> Tuple[str, str]:
        """Tela 5: Ângulo Dobra 2"""
        if self.machine_data['direction'] == 'CW':
            aj = self.machine_data['angles']['aj2_dir']
        else:
            aj = self.machine_data['angles']['aj2_esq']

        pv = self.machine_data['encoder_degrees']

        return (
            'AJUSTE DO ANGULO 02 ',
            f'AJ={aj:3d}° PV={pv:3d}°     '
        )

    def _screen_6(self) -> Tuple[str, str]:
        """Tela 6: Ângulo Dobra 3"""
        if self.machine_data['direction'] == 'CW':
            aj = self.machine_data['angles']['aj3_dir']
        else:
            aj = self.machine_data['angles']['aj3_esq']

        pv = self.machine_data['encoder_degrees']

        return (
            'AJUSTE DO ANGULO 03 ',
            f'AJ={aj:3d}° PV={pv:3d}°     '
        )

    def _screen_7(self) -> Tuple[str, str]:
        """Tela 7: Seleção de velocidade"""
        k = self.machine_data['speed_class']

        return (
            '*SELECAO DA ROTACAO*',
            f'        [{k}]         '
        )

    def _screen_8(self) -> Tuple[str, str]:
        """Tela 8: Carenagem"""
        status = '3' if self.machine_data['carenagem_ok'] else '5'

        return (
            'CARENAGEM DOBRADEIRA',
            f'        [{status}]         '
        )

    def _screen_9(self) -> Tuple[str, str]:
        """Tela 9: Totalizador de tempo"""
        h = self.machine_data['runtime_hours']
        m = self.machine_data['runtime_minutes']

        return (
            'TOTALIZADOR DE TEMPO',
            f'*****{h:3d}:{m:02d}h *****  '
        )

    def _screen_10(self) -> Tuple[str, str]:
        """Tela 10: Estado da dobradeira"""
        state = self.machine_data['machine_state']

        return (
            'ESTADO DA DOBRADEIRA',
            f'        [{state}]         '
        )

    # ==================== NAVEGAÇÃO ====================

    async def _handle_key_navigation_mode(self, key_code: int, key_name: str):
        """Processa tecla em modo navegação"""

        # Setas (navegação sequencial)
        if key_code == 172:  # ↑ (UP)
            self._previous_screen()

        elif key_code == 173:  # ↓ (DOWN)
            self._next_screen()

        # Atalhos diretos
        elif key_code == 160:  # K1 → Tela 4 (Ângulo 1)
            self.current_screen = 4

        elif key_code == 161:  # K2 → Tela 5 (Ângulo 2)
            self.current_screen = 5

        elif key_code == 162:  # K3 → Tela 6 (Ângulo 3)
            self.current_screen = 6

        # ESC → Volta para tela inicial
        elif key_code == 188:  # ESC
            self.current_screen = 0

        # EDIT → Entra em modo edição (se aplicável)
        elif key_code == 38:  # EDIT
            if self.current_screen in [4, 5, 6]:  # Telas de ângulo
                self.edit_mode = True
                self.edit_value = ""
                self.edit_field = f'angle_{self.current_screen - 3}'
                logger.info(f"Modo EDIT ativado para tela {self.current_screen}")

        # S1 → Alterna modo AUTO/MAN (apenas na tela 2)
        elif key_code == 220:  # S1
            if self.current_screen == 2:
                # Alternar modo (via Modbus - CLP decide)
                pass

        # K1 + K7 simultâneo → Mudar velocidade (tela 7)
        # TODO: Implementar detecção de teclas simultâneas

    async def _handle_key_edit_mode(self, key_code: int, key_name: str):
        """Processa tecla em modo edição"""

        # ESC → Cancela edição
        if key_code == 188:  # ESC
            self.edit_mode = False
            self.edit_value = ""
            self.edit_field = None
            logger.info("Modo EDIT cancelado")

        # ENTER → Confirma e escreve no CLP
        elif key_code == 37:  # ENTER
            if self.edit_value:
                try:
                    value = int(self.edit_value)
                    await self._write_angle_to_plc(self.edit_field, value)
                    logger.info(f"Ângulo {self.edit_field} escrito: {value}°")
                except ValueError:
                    logger.error(f"Valor inválido: {self.edit_value}")

            self.edit_mode = False
            self.edit_value = ""
            self.edit_field = None

        # K0-K9 → Digita número
        elif 160 <= key_code <= 169:  # K0-K9
            digit = (key_code - 160) if key_code != 169 else 0  # K0 = 169
            self.edit_value += str(digit)
            logger.info(f"Dígito digitado: {digit}, valor atual: {self.edit_value}")

    def _next_screen(self):
        """Avança para próxima tela"""
        self.current_screen = (self.current_screen + 1) % self.total_screens
        logger.info(f"Navegação: Tela {self.current_screen}")

    def _previous_screen(self):
        """Volta para tela anterior"""
        self.current_screen = (self.current_screen - 1) % self.total_screens
        logger.info(f"Navegação: Tela {self.current_screen}")

    # ==================== COMUNICAÇÃO MODBUS ====================

    async def _send_key_to_plc(self, key_code: int):
        """Envia tecla para CLP (simulação física)"""
        try:
            await asyncio.to_thread(self.modbus.press_key, key_code)
        except Exception as e:
            logger.error(f"Erro ao enviar tecla {key_code} para CLP: {e}")

    async def _write_angle_to_plc(self, field: str, value: int):
        """Escreve ângulo no CLP via Modbus"""
        # Mapear field para endereço Modbus
        angle_map = {
            'angle_1': 2112,  # 0840 hex - Dobra 1 esquerda
            'angle_2': 2118,  # 0846 hex - Dobra 2 esquerda
            'angle_3': 2128,  # 0850 hex - Dobra 3 esquerda
        }

        address = angle_map.get(field)
        if address is None:
            logger.error(f"Campo desconhecido: {field}")
            return

        try:
            await asyncio.to_thread(
                self.modbus.client.write_register,
                address=address,
                value=value,
                device_id=1
            )
            logger.info(f"Ângulo escrito: endereço {address} = {value}°")

            # Atualizar cache local
            if field == 'angle_1':
                self.machine_data['angles']['aj1_esq'] = value
            elif field == 'angle_2':
                self.machine_data['angles']['aj2_esq'] = value
            elif field == 'angle_3':
                self.machine_data['angles']['aj3_esq'] = value

        except Exception as e:
            logger.error(f"Erro ao escrever ângulo {field}={value}: {e}")

    # ==================== UTILITÁRIOS ====================

    def _update_leds(self):
        """Atualiza estado dos LEDs baseado nos dados da máquina"""
        self.leds['K1'] = (self.machine_data['active_bend'] == 1)
        self.leds['K2'] = (self.machine_data['active_bend'] == 2)
        self.leds['K3'] = (self.machine_data['active_bend'] == 3)
        self.leds['K4'] = (self.machine_data['direction'] == 'CCW')
        self.leds['K5'] = (self.machine_data['direction'] == 'CW')
        self.leds['S1'] = self.machine_data['auto_mode']

    def _format_line(self, text: str) -> str:
        """
        Formata linha para exatamente 20 caracteres

        Args:
            text: Texto a formatar

        Returns:
            String com exatamente 20 caracteres (trunca ou preenche com espaços)
        """
        return (text + ' ' * 20)[:20]

    def _encoder_to_degrees(self, encoder_value: int) -> int:
        """
        Converte valor do encoder para graus

        Args:
            encoder_value: Valor do contador encoder (32-bit)

        Returns:
            Ângulo em graus (0-360)
        """
        # TODO: Calibrar com valores reais da máquina
        # Fator de conversão provisório (ajustar após testes)
        # Redução total: 58.5:1 × 3.44:1 = 201.24:1
        # Encoder 360 ppr → 72446.4 pulsos por revolução do prato

        PULSES_PER_REVOLUTION = 72446  # PLACEHOLDER - calibrar!

        degrees = int((encoder_value % PULSES_PER_REVOLUTION) * 360 / PULSES_PER_REVOLUTION)
        return degrees % 360

    def _get_key_name(self, key_code: int) -> str:
        """Retorna nome da tecla baseado no código"""
        key_map = {
            160: 'K1', 161: 'K2', 162: 'K3', 163: 'K4', 164: 'K5',
            165: 'K6', 166: 'K7', 167: 'K8', 168: 'K9', 169: 'K0',
            220: 'S1', 221: 'S2',
            172: 'UP', 173: 'DOWN',
            188: 'ESC', 37: 'ENTER', 38: 'EDIT', 241: 'LOCK'
        }
        return key_map.get(key_code, f'KEY_{key_code}')
