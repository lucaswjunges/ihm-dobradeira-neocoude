#!/usr/bin/env python3
"""
Máquina de Estados da Operação - IHM Virtual NEOCOUDE-HD-15
Controla a lógica de operação da máquina (modo, dobra, velocidade, direção)
"""

import logging

logger = logging.getLogger(__name__)


class OperationStateMachine:
    """
    Gerencia estados operacionais da dobradeira
    - Modo: MANUAL ou AUTOMÁTICO
    - Dobra atual: 1, 2 ou 3
    - Direção: ESQ ou DIR
    - Velocidade: Classe 1, 2 ou 3 (5, 10, 15 RPM)
    """

    def __init__(self):
        # Estados principais
        self.modo = "MANUAL"  # MANUAL ou AUTO
        self.dobra_atual = 1  # 1, 2 ou 3
        self.direcao = None  # "ESQ" ou "DIR" (None = não selecionado)
        self.velocidade_classe = 1  # 1=5rpm, 2=10rpm, 3=15rpm

        # Estados derivados
        self.ciclo_ativo = False
        self.emergencia = False
        self.posicao_zero = True
        self.motor_ligado = False

        # Ângulos programados (6 ângulos: 3 esquerda + 3 direita)
        self.angulos = {
            "D1E": 90.0,  # Dobra 1 Esquerda
            "D2E": 90.0,  # Dobra 2 Esquerda
            "D3E": 90.0,  # Dobra 3 Esquerda
            "D1D": 90.0,  # Dobra 1 Direita
            "D2D": 90.0,  # Dobra 2 Direita
            "D3D": 90.0,  # Dobra 3 Direita
        }

        # Encoder
        self.encoder_angle = 0.0
        self.pv_value = 0.0  # Position Value (auto-calculado pelo CLP)

        logger.info("OperationStateMachine initialized")

    def update_from_clp(self, machine_state):
        """
        Atualiza estados com base nos dados lidos do CLP

        Args:
            machine_state: Dicionário com estados do CLP
        """
        # Atualizar encoder
        if 'encoder_value' in machine_state:
            # Converter valor bruto do encoder para graus (depende da configuração)
            # Por enquanto, usar valor direto
            self.encoder_angle = machine_state.get('encoder_angle', 0.0)
            self.pv_value = machine_state.get('pv_value', self.encoder_angle)

        # Atualizar estados de I/O
        self.ciclo_ativo = machine_state.get('ciclo_ativo', False)
        self.emergencia = machine_state.get('emergencia', False)
        self.posicao_zero = machine_state.get('posicao_zero', True)
        self.motor_ligado = machine_state.get('motor_ligado', False)

        # Atualizar estados do ladder (quando mapeados)
        if 'modo_auto' in machine_state:
            self.modo = "AUTO" if machine_state['modo_auto'] else "MANUAL"

        if 'dobra_atual' in machine_state:
            self.dobra_atual = machine_state['dobra_atual']

        if 'direcao_esq' in machine_state and 'direcao_dir' in machine_state:
            if machine_state['direcao_esq']:
                self.direcao = "ESQ"
            elif machine_state['direcao_dir']:
                self.direcao = "DIR"
            else:
                self.direcao = None

        if 'velocidade_classe' in machine_state:
            self.velocidade_classe = machine_state['velocidade_classe']

    def can_change_mode(self):
        """
        Verifica se pode trocar de modo (MANUAL ↔ AUTO)
        Regra: Só pode trocar se máquina parada E em dobra 1
        """
        can_change = (not self.ciclo_ativo and
                     self.dobra_atual == 1 and
                     not self.emergencia)

        if not can_change:
            if self.ciclo_ativo:
                logger.warning("Não pode trocar modo: ciclo ativo")
            elif self.dobra_atual != 1:
                logger.warning(f"Não pode trocar modo: dobra atual é {self.dobra_atual} (precisa estar em D1)")
            elif self.emergencia:
                logger.warning("Não pode trocar modo: emergência ativa")

        return can_change

    def toggle_mode(self):
        """
        Alterna entre MANUAL e AUTO (se permitido)
        Returns: True se alterou, False se não pode
        """
        if not self.can_change_mode():
            return False

        old_mode = self.modo
        self.modo = "AUTO" if self.modo == "MANUAL" else "MANUAL"

        # Se mudou para MANUAL, resetar velocidade para classe 1
        if self.modo == "MANUAL":
            self.velocidade_classe = 1

        logger.info(f"Modo alterado: {old_mode} → {self.modo}")
        return True

    def can_change_velocity(self):
        """
        Verifica se pode trocar velocidade
        Regra: Só em modo MANUAL (K1+K7 simultâneo)
        """
        can_change = self.modo == "MANUAL" and not self.ciclo_ativo

        if not can_change:
            if self.modo != "MANUAL":
                logger.warning("Não pode trocar velocidade: modo automático")
            elif self.ciclo_ativo:
                logger.warning("Não pode trocar velocidade: ciclo ativo")

        return can_change

    def set_velocity_class(self, classe):
        """
        Define classe de velocidade (1, 2 ou 3)
        Args:
            classe: 1 (5rpm), 2 (10rpm) ou 3 (15rpm)
        Returns: True se alterou, False se não pode
        """
        if not self.can_change_velocity():
            return False

        if classe not in [1, 2, 3]:
            logger.error(f"Classe de velocidade inválida: {classe}")
            return False

        old_classe = self.velocidade_classe
        self.velocidade_classe = classe
        logger.info(f"Velocidade alterada: Classe {old_classe} → {classe}")
        return True

    def get_velocity_rpm(self):
        """Retorna RPM correspondente à classe atual"""
        return {1: 5, 2: 10, 3: 15}.get(self.velocidade_classe, 5)

    def can_select_direction(self):
        """
        Verifica se pode selecionar direção
        Regra: Máquina deve estar parada
        """
        return not self.ciclo_ativo and not self.emergencia

    def set_direction(self, direction):
        """
        Define direção (ESQ ou DIR)
        Args:
            direction: "ESQ" ou "DIR"
        Returns: True se alterou, False se não pode
        """
        if not self.can_select_direction():
            logger.warning("Não pode selecionar direção: máquina não está parada")
            return False

        if direction not in ["ESQ", "DIR"]:
            logger.error(f"Direção inválida: {direction}")
            return False

        old_dir = self.direcao
        self.direcao = direction
        logger.info(f"Direção alterada: {old_dir} → {direction}")
        return True

    def can_advance_dobra(self):
        """
        Verifica se pode avançar para próxima dobra
        Regra: Só em modo AUTO, após completar dobra atual
        """
        can_advance = (self.modo == "AUTO" and
                      not self.ciclo_ativo and
                      self.dobra_atual < 3 and
                      self.posicao_zero)

        if not can_advance:
            if self.modo != "AUTO":
                logger.warning("Não pode avançar dobra: modo manual")
            elif self.ciclo_ativo:
                logger.warning("Não pode avançar dobra: ciclo ativo")
            elif self.dobra_atual >= 3:
                logger.warning("Não pode avançar dobra: já está na última (D3)")
            elif not self.posicao_zero:
                logger.warning("Não pode avançar dobra: não está em posição zero")

        return can_advance

    def advance_dobra(self):
        """
        Avança para próxima dobra (D1 → D2 → D3)
        IMPORTANTE: Não permite voltar! Só avança.
        Returns: True se avançou, False se não pode
        """
        if not self.can_advance_dobra():
            return False

        old_dobra = self.dobra_atual
        self.dobra_atual += 1
        logger.info(f"Dobra avançada: D{old_dobra} → D{self.dobra_atual}")
        return True

    def can_select_dobra(self, dobra):
        """
        Verifica se pode selecionar uma dobra específica
        Regra: Só em modo MANUAL
        """
        can_select = (self.modo == "MANUAL" and
                     not self.ciclo_ativo and
                     1 <= dobra <= 3)

        if not can_select:
            if self.modo != "MANUAL":
                logger.warning("Não pode selecionar dobra: modo automático")
            elif self.ciclo_ativo:
                logger.warning("Não pode selecionar dobra: ciclo ativo")
            elif not (1 <= dobra <= 3):
                logger.error(f"Dobra inválida: {dobra}")

        return can_select

    def set_dobra(self, dobra):
        """
        Define dobra atual (1, 2 ou 3) - só MANUAL
        Args:
            dobra: 1, 2 ou 3
        Returns: True se alterou, False se não pode
        """
        if not self.can_select_dobra(dobra):
            return False

        old_dobra = self.dobra_atual
        self.dobra_atual = dobra
        logger.info(f"Dobra selecionada: D{old_dobra} → D{dobra}")
        return True

    def get_current_angle_setpoint(self):
        """
        Retorna o ângulo programado para dobra e direção atuais
        Returns: Ângulo em graus (float)
        """
        if self.direcao is None:
            return 0.0

        key = f"D{self.dobra_atual}{self.direcao[0]}"  # D1E, D2D, etc
        return self.angulos.get(key, 0.0)

    def set_angle(self, dobra, direction, angle):
        """
        Define ângulo para uma dobra e direção específicas
        Args:
            dobra: 1, 2 ou 3
            direction: "ESQ" ou "DIR"
            angle: Ângulo em graus (0.0 - 360.0)
        Returns: True se alterou, False se inválido
        """
        if not (1 <= dobra <= 3):
            logger.error(f"Dobra inválida: {dobra}")
            return False

        if direction not in ["ESQ", "DIR"]:
            logger.error(f"Direção inválida: {direction}")
            return False

        if not (0.0 <= angle <= 360.0):
            logger.error(f"Ângulo inválido: {angle}")
            return False

        key = f"D{dobra}{direction[0]}"
        old_angle = self.angulos.get(key, 0.0)
        self.angulos[key] = angle
        logger.info(f"Ângulo {key} alterado: {old_angle:.1f}° → {angle:.1f}°")
        return True

    def can_start_cycle(self):
        """
        Verifica se pode iniciar ciclo de dobra
        Regras:
        - Máquina parada
        - Direção selecionada
        - Sem emergência
        - Em posição zero
        """
        can_start = (not self.ciclo_ativo and
                    self.direcao is not None and
                    not self.emergencia and
                    self.posicao_zero)

        if not can_start:
            if self.ciclo_ativo:
                logger.warning("Não pode iniciar: ciclo já ativo")
            elif self.direcao is None:
                logger.warning("Não pode iniciar: direção não selecionada")
            elif self.emergencia:
                logger.warning("Não pode iniciar: emergência ativa")
            elif not self.posicao_zero:
                logger.warning("Não pode iniciar: não está em posição zero")

        return can_start

    def reset_to_initial_state(self):
        """
        Reseta para estado inicial (simulação de desligar/ligar)
        """
        logger.info("Resetando máquina de estados para estado inicial")
        self.modo = "MANUAL"
        self.dobra_atual = 1
        self.direcao = None
        self.velocidade_classe = 1
        self.ciclo_ativo = False
        self.emergencia = False
        self.posicao_zero = True
        self.motor_ligado = False

    def get_state_dict(self):
        """
        Retorna dicionário com todos os estados atuais
        Útil para enviar via WebSocket
        """
        return {
            "modo": self.modo,
            "dobra_atual": self.dobra_atual,
            "direcao": self.direcao,
            "velocidade_classe": self.velocidade_classe,
            "velocidade_rpm": self.get_velocity_rpm(),
            "ciclo_ativo": self.ciclo_ativo,
            "emergencia": self.emergencia,
            "posicao_zero": self.posicao_zero,
            "motor_ligado": self.motor_ligado,
            "encoder_angle": self.encoder_angle,
            "pv_value": self.pv_value,
            "angulos": self.angulos.copy(),
            "current_setpoint": self.get_current_angle_setpoint(),
            # Flags de LEDs
            "led_k1": self.dobra_atual == 1,
            "led_k2": self.dobra_atual == 2,
            "led_k3": self.dobra_atual == 3,
            "led_k4": self.direcao == "ESQ",
            "led_k5": self.direcao == "DIR",
            "led_s1": self.modo == "AUTO",
        }

    def __repr__(self):
        return (f"<OperationStateMachine modo={self.modo} "
                f"dobra={self.dobra_atual} dir={self.direcao} "
                f"vel={self.velocidade_classe} ciclo={self.ciclo_ativo}>")
