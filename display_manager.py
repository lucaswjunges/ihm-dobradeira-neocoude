#!/usr/bin/env python3
"""
Display Manager - Gerenciador de Telas da IHM Virtual
Simula o display LCD de 2 linhas do CLP, com navegação entre telas
"""

import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class DisplayManager:
    """
    Gerencia o conteúdo e navegação do display LCD virtual

    Telas disponíveis:
    - TELA_PRINCIPAL: Operação normal (ângulo, dobra, modo)
    - TELA_EDICAO: Edição de ângulos (tela 1HM)
    - TELA_MODO: Seleção de modo (Manual/Auto)
    - TELA_VELOCIDADE: Seleção de velocidade (5/10/15 RPM)
    - TELA_ERRO: Mensagens de erro/emergência
    """

    # Constantes de telas
    TELA_PRINCIPAL = "TELA_PRINCIPAL"
    TELA_EDICAO = "TELA_EDICAO"
    TELA_MODO = "TELA_MODO"
    TELA_VELOCIDADE = "TELA_VELOCIDADE"
    TELA_ERRO = "TELA_ERRO"

    # Dimensões do display (ajustar conforme IHM física)
    DISPLAY_WIDTH = 20  # Assumindo 20 caracteres (pode ser 16)
    DISPLAY_LINES = 2

    def __init__(self, state_machine):
        """
        Args:
            state_machine: Instância de OperationStateMachine
        """
        self.state_machine = state_machine
        self.current_screen = self.TELA_PRINCIPAL

        # Estado de edição
        self.edit_mode = False
        self.edit_field = "D1E"  # D1E, D2E, D3E, D1D, D2D, D3D
        self.edit_buffer = ""
        self.cursor_position = 0

        # Estado de seleção
        self.selection_index = 0

        # Conteúdo do display
        self.line1 = ""
        self.line2 = ""

        # Controle de cursor piscante
        self.cursor_visible = True
        self.last_cursor_toggle = datetime.now()

        logger.info("DisplayManager initialized")

    def update_display(self):
        """
        Atualiza conteúdo do display baseado na tela atual
        """
        if self.current_screen == self.TELA_PRINCIPAL:
            self._render_main_screen()
        elif self.current_screen == self.TELA_EDICAO:
            self._render_edit_screen()
        elif self.current_screen == self.TELA_MODO:
            self._render_mode_screen()
        elif self.current_screen == self.TELA_VELOCIDADE:
            self._render_velocity_screen()
        elif self.current_screen == self.TELA_ERRO:
            self._render_error_screen()

    def _render_main_screen(self):
        """
        Renderiza tela principal
        Formato:
        ┌────────────────────┐
        │ ANG: 000.0° D1 ESQ │
        │ PV:  000.0° [AUTO] │
        └────────────────────┘
        """
        sm = self.state_machine

        # Linha 1: Ângulo atual, dobra, direção
        angle = sm.encoder_angle
        dobra = sm.dobra_atual
        direction = sm.direcao if sm.direcao else "---"

        self.line1 = f"ANG:{angle:6.1f}\u00b0 D{dobra} {direction:3s}"

        # Linha 2: PV, modo
        pv = sm.pv_value
        mode = "AUTO" if sm.modo == "AUTO" else "MANUAL"

        # Indicador de ciclo
        if sm.ciclo_ativo:
            status = "DOBRANDO"
        elif not sm.posicao_zero:
            status = "RETORN.."
        else:
            status = f"[{mode:>6s}]"

        self.line2 = f"PV: {pv:6.1f}\u00b0 {status}"

        # Ajustar para largura do display
        self.line1 = self._pad_line(self.line1)
        self.line2 = self._pad_line(self.line2)

    def _render_edit_screen(self):
        """
        Renderiza tela de edição de ângulos (tela 1HM)
        Formato:
        ┌────────────────────┐
        │ EDITAR ANGULOS     │
        │ D1E: 090.0°  █     │  █ = cursor
        └────────────────────┘
        """
        # Linha 1: Título
        self.line1 = "EDITAR ANGULOS"

        # Linha 2: Campo sendo editado
        current_angle = self.state_machine.angulos.get(self.edit_field, 0.0)

        if self.edit_mode:
            # Mostra buffer de edição com cursor
            display_value = self.edit_buffer if self.edit_buffer else "___._"
            cursor = "\u2588" if self.cursor_visible else " "  # Bloco sólido
            self.line2 = f"{self.edit_field}: {display_value:>5s}\u00b0 {cursor}"
        else:
            # Mostra valor atual (navegando entre campos)
            self.line2 = f"{self.edit_field}: {current_angle:5.1f}\u00b0"

        # Ajustar para largura
        self.line1 = self._pad_line(self.line1)
        self.line2 = self._pad_line(self.line2)

    def _render_mode_screen(self):
        """
        Renderiza tela de seleção de modo
        Formato:
        ┌────────────────────┐
        │ SELECIONAR MODO    │
        │ > MANUAL           │
        └────────────────────┘
        """
        self.line1 = "SELECIONAR MODO"

        # Opções: 0=MANUAL, 1=AUTO
        options = ["MANUAL", "AUTOMATICO"]
        selected = options[self.selection_index]

        self.line2 = f"> {selected}"

        # Ajustar para largura
        self.line1 = self._pad_line(self.line1)
        self.line2 = self._pad_line(self.line2)

    def _render_velocity_screen(self):
        """
        Renderiza tela de seleção de velocidade
        Formato:
        ┌────────────────────┐
        │ VELOCIDADE         │
        │ CLASSE: 2 (10 RPM) │
        └────────────────────┘
        """
        self.line1 = "VELOCIDADE"

        # Classes: 1=5rpm, 2=10rpm, 3=15rpm
        classe = self.state_machine.velocidade_classe
        rpm = self.state_machine.get_velocity_rpm()

        self.line2 = f"CLASSE: {classe} ({rpm} RPM)"

        # Ajustar para largura
        self.line1 = self._pad_line(self.line1)
        self.line2 = self._pad_line(self.line2)

    def _render_error_screen(self):
        """
        Renderiza tela de erro/emergência
        Formato:
        ┌────────────────────┐
        │ ** EMERGENCIA **   │
        │ Pressione S2       │
        └────────────────────┘
        """
        if self.state_machine.emergencia:
            self.line1 = "** EMERGENCIA **"
            self.line2 = "Pressione S2"
        else:
            self.line1 = "** ERRO **"
            self.line2 = "Pressione ESC"

        # Ajustar para largura
        self.line1 = self._pad_line(self.line1)
        self.line2 = self._pad_line(self.line2)

    def _pad_line(self, line):
        """
        Ajusta linha para largura do display (preenche com espaços ou trunca)
        """
        if len(line) > self.DISPLAY_WIDTH:
            return line[:self.DISPLAY_WIDTH]
        return line.ljust(self.DISPLAY_WIDTH)

    def handle_keypress(self, key):
        """
        Processa tecla pressionada e atualiza tela/estado

        Args:
            key: Código da tecla (K0-K9, S1, S2, UP, DOWN, ESC, ENTER, EDIT, etc)

        Returns:
            dict: {
                "screen_changed": bool,
                "need_clp_write": bool,
                "clp_command": dict ou None,
                "message": str
            }
        """
        logger.info(f"Keypress: {key} (tela atual: {self.current_screen})")

        result = {
            "screen_changed": False,
            "need_clp_write": False,
            "clp_command": None,
            "message": ""
        }

        # Processar conforme tela atual
        if self.current_screen == self.TELA_PRINCIPAL:
            result = self._handle_main_screen_key(key)

        elif self.current_screen == self.TELA_EDICAO:
            result = self._handle_edit_screen_key(key)

        elif self.current_screen == self.TELA_MODO:
            result = self._handle_mode_screen_key(key)

        elif self.current_screen == self.TELA_VELOCIDADE:
            result = self._handle_velocity_screen_key(key)

        elif self.current_screen == self.TELA_ERRO:
            result = self._handle_error_screen_key(key)

        # Atualizar display após processar tecla
        self.update_display()

        return result

    def _handle_main_screen_key(self, key):
        """Processa teclas na tela principal"""
        result = {"screen_changed": False, "need_clp_write": False,
                 "clp_command": None, "message": ""}

        # EDIT: Ir para tela de edição
        if key == "EDIT":
            self.current_screen = self.TELA_EDICAO
            self.edit_mode = False
            self.edit_field = "D1E"
            result["screen_changed"] = True
            result["message"] = "Entrando em modo de edição de ângulos"

        # S1: Trocar modo (se permitido)
        elif key == "S1":
            if self.state_machine.can_change_mode():
                self.current_screen = self.TELA_MODO
                self.selection_index = 0 if self.state_machine.modo == "MANUAL" else 1
                result["screen_changed"] = True
                result["message"] = "Seleção de modo"
            else:
                result["message"] = "Não pode trocar modo agora (deve estar parado e em D1)"

        # S2: Reset/Zerar display
        elif key == "S2":
            result["need_clp_write"] = True
            result["clp_command"] = {"action": "reset_display"}
            result["message"] = "Display zerado"

        # K1, K2, K3: Selecionar dobra (só manual)
        elif key in ["K1", "K2", "K3"]:
            dobra = int(key[1])  # K1 -> 1, K2 -> 2, K3 -> 3
            if self.state_machine.set_dobra(dobra):
                result["need_clp_write"] = True
                result["clp_command"] = {"action": "select_dobra", "dobra": dobra}
                result["message"] = f"Dobra D{dobra} selecionada"
            else:
                result["message"] = "Não pode selecionar dobra (modo automático?)"

        # K4, K5: Selecionar direção
        elif key in ["K4", "K5"]:
            direction = "ESQ" if key == "K4" else "DIR"
            if self.state_machine.set_direction(direction):
                result["need_clp_write"] = True
                result["clp_command"] = {"action": "select_direction", "direction": direction}
                result["message"] = f"Direção {direction} selecionada"
            else:
                result["message"] = "Não pode selecionar direção (ciclo ativo?)"

        # K1+K7: Trocar velocidade (só manual)
        # Nota: Combo keys tratado em camada superior

        # Qualquer outra tecla: enviar para CLP (comando físico)
        else:
            result["need_clp_write"] = True
            result["clp_command"] = {"action": "press_key", "key": key}
            result["message"] = f"Tecla {key} enviada ao CLP"

        return result

    def _handle_edit_screen_key(self, key):
        """Processa teclas na tela de edição"""
        result = {"screen_changed": False, "need_clp_write": False,
                 "clp_command": None, "message": ""}

        # ESC: Cancelar e voltar
        if key == "ESC":
            self.current_screen = self.TELA_PRINCIPAL
            self.edit_mode = False
            self.edit_buffer = ""
            result["screen_changed"] = True
            result["message"] = "Edição cancelada"

        # UP/DOWN: Navegar entre campos (se não estiver editando)
        elif key in ["UP", "DOWN"] and not self.edit_mode:
            fields = ["D1E", "D2E", "D3E", "D1D", "D2D", "D3D"]
            current_idx = fields.index(self.edit_field)

            if key == "UP":
                current_idx = (current_idx - 1) % len(fields)
            else:  # DOWN
                current_idx = (current_idx + 1) % len(fields)

            self.edit_field = fields[current_idx]
            result["message"] = f"Campo {self.edit_field} selecionado"

        # ENTER: Entrar/sair modo edição ou confirmar valor
        elif key == "ENTER":
            if not self.edit_mode:
                # Entrar em modo edição
                self.edit_mode = True
                self.edit_buffer = ""
                result["message"] = f"Editando {self.edit_field}"
            else:
                # Confirmar valor editado
                try:
                    new_angle = float(self.edit_buffer)
                    dobra = int(self.edit_field[1])
                    direction = "ESQ" if self.edit_field[2] == "E" else "DIR"

                    if self.state_machine.set_angle(dobra, direction, new_angle):
                        result["need_clp_write"] = True
                        result["clp_command"] = {
                            "action": "write_angle",
                            "field": self.edit_field,
                            "value": new_angle
                        }
                        result["message"] = f"{self.edit_field} = {new_angle:.1f}°"

                        # Sair do modo edição
                        self.edit_mode = False
                        self.edit_buffer = ""
                    else:
                        result["message"] = "Valor inválido"
                except ValueError:
                    result["message"] = "Valor inválido"

        # K0-K9: Digitar valor (se em modo edição)
        elif key in ["K0", "K1", "K2", "K3", "K4", "K5", "K6", "K7", "K8", "K9"]:
            if self.edit_mode:
                digit = key[1]  # K0 -> 0, K1 -> 1, etc

                # Limitar buffer (formato: XXX.X -> 5 chars)
                if len(self.edit_buffer) < 5:
                    # Se ainda não tem ponto, adicionar após 3 dígitos
                    if "." not in self.edit_buffer and len(self.edit_buffer) == 3:
                        self.edit_buffer += "."

                    self.edit_buffer += digit
                    result["message"] = f"Digitando: {self.edit_buffer}"
            else:
                result["message"] = "Pressione ENTER para editar"

        return result

    def _handle_mode_screen_key(self, key):
        """Processa teclas na tela de seleção de modo"""
        result = {"screen_changed": False, "need_clp_write": False,
                 "clp_command": None, "message": ""}

        # ESC: Cancelar
        if key == "ESC":
            self.current_screen = self.TELA_PRINCIPAL
            result["screen_changed"] = True
            result["message"] = "Seleção cancelada"

        # UP/DOWN: Alternar opção
        elif key in ["UP", "DOWN"]:
            self.selection_index = 1 - self.selection_index  # Alterna 0<->1
            result["message"] = "MANUAL" if self.selection_index == 0 else "AUTOMATICO"

        # ENTER: Confirmar seleção
        elif key == "ENTER":
            new_mode = "MANUAL" if self.selection_index == 0 else "AUTO"

            if self.state_machine.toggle_mode():
                result["need_clp_write"] = True
                result["clp_command"] = {"action": "set_mode", "mode": new_mode}
                result["message"] = f"Modo alterado para {new_mode}"

                self.current_screen = self.TELA_PRINCIPAL
                result["screen_changed"] = True
            else:
                result["message"] = "Não pode trocar modo agora"

        return result

    def _handle_velocity_screen_key(self, key):
        """Processa teclas na tela de seleção de velocidade"""
        result = {"screen_changed": False, "need_clp_write": False,
                 "clp_command": None, "message": ""}

        # ESC: Cancelar
        if key == "ESC":
            self.current_screen = self.TELA_PRINCIPAL
            result["screen_changed"] = True
            result["message"] = "Seleção cancelada"

        # UP/DOWN: Trocar classe
        elif key in ["UP", "DOWN"]:
            current = self.state_machine.velocidade_classe

            if key == "UP":
                new_class = (current % 3) + 1  # 1->2, 2->3, 3->1
            else:
                new_class = ((current - 2) % 3) + 1  # 1->3, 2->1, 3->2

            self.state_machine.set_velocity_class(new_class)
            result["message"] = f"Classe {new_class} ({self.state_machine.get_velocity_rpm()} RPM)"

        # ENTER: Confirmar
        elif key == "ENTER":
            result["need_clp_write"] = True
            result["clp_command"] = {
                "action": "set_velocity",
                "class": self.state_machine.velocidade_classe
            }
            result["message"] = f"Velocidade: {self.state_machine.get_velocity_rpm()} RPM"

            self.current_screen = self.TELA_PRINCIPAL
            result["screen_changed"] = True

        return result

    def _handle_error_screen_key(self, key):
        """Processa teclas na tela de erro"""
        result = {"screen_changed": False, "need_clp_write": False,
                 "clp_command": None, "message": ""}

        # S2 ou ESC: Sair da tela de erro
        if key in ["S2", "ESC"]:
            self.current_screen = self.TELA_PRINCIPAL
            result["screen_changed"] = True
            result["need_clp_write"] = True
            result["clp_command"] = {"action": "clear_error"}
            result["message"] = "Erro limpo"

        return result

    def show_error(self):
        """Força exibição da tela de erro"""
        self.current_screen = self.TELA_ERRO
        self.update_display()

    def show_velocity_screen(self):
        """Mostra tela de velocidade (chamado quando K1+K7 simultâneo)"""
        if self.state_machine.can_change_velocity():
            self.current_screen = self.TELA_VELOCIDADE
            self.update_display()
            return True
        return False

    def toggle_cursor(self):
        """Alterna visibilidade do cursor (chamado periodicamente)"""
        now = datetime.now()
        if (now - self.last_cursor_toggle).total_seconds() > 0.5:
            self.cursor_visible = not self.cursor_visible
            self.last_cursor_toggle = now
            # Atualizar display se estiver em modo edição
            if self.edit_mode:
                self.update_display()

    def get_display_content(self):
        """
        Retorna conteúdo atual do display para envio via WebSocket

        Returns:
            dict: {
                "line1": str,
                "line2": str,
                "screen": str,
                "cursor_pos": int,
                "cursor_visible": bool
            }
        """
        return {
            "line1": self.line1,
            "line2": self.line2,
            "screen": self.current_screen,
            "cursor_pos": self.cursor_position,
            "cursor_visible": self.cursor_visible and self.edit_mode
        }

    def __repr__(self):
        return f"<DisplayManager screen={self.current_screen} edit={self.edit_mode}>"
