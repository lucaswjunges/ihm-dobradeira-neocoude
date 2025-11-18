"""
State Manager ESP32 - IHM Web Dobradeira
Gerenciador de estado com polling assíncrono
"""
import uasyncio as asyncio
import gc
import modbus_map as mm


class StateManager:
    """Gerencia estado da máquina via polling Modbus"""

    def __init__(self, modbus_client):
        self.modbus = modbus_client
        self.state = {
            'encoder_angle': 0.0,
            'bend_1_angle': 0.0,
            'bend_2_angle': 0.0,
            'bend_3_angle': 0.0,
            'speed_class': 1,
            'emergency_stop': False,
            'cycle_active': False,
            'connected': False
        }
        self.running = False

    async def start_polling(self):
        """Loop de polling (500ms)"""
        self.running = True
        print(" Polling iniciado (500ms)")

        while self.running:
            try:
                await self._poll_data()
                await asyncio.sleep_ms(500)
                gc.collect()  # Libera memória
            except Exception as e:
                print(f"  Erro polling: {e}")
                await asyncio.sleep_ms(1000)

    async def _poll_data(self):
        """Lê dados vitais do CLP"""
        # Encoder (32-bit)
        encoder_raw = self.modbus.read_register_32bit(mm.ENCODER['ANGLE_MSW'])
        if encoder_raw is not None:
            self.state['encoder_angle'] = encoder_raw / 10.0
            self.state['connected'] = True
        else:
            self.state['connected'] = False

        # Ângulos setpoint
        bend1 = self.modbus.read_register(mm.BEND_ANGLES['BEND_1_SETPOINT'])
        if bend1 is not None:
            self.state['bend_1_angle'] = bend1 / 10.0

        bend2 = self.modbus.read_register(mm.BEND_ANGLES['BEND_2_SETPOINT'])
        if bend2 is not None:
            self.state['bend_2_angle'] = bend2 / 10.0

        bend3 = self.modbus.read_register(mm.BEND_ANGLES['BEND_3_SETPOINT'])
        if bend3 is not None:
            self.state['bend_3_angle'] = bend3 / 10.0

        # Velocidade (RPM)
        speed_reg = self.modbus.read_register(mm.SPEED_CONTROL['SPEED_SETPOINT'])
        if speed_reg is not None:
            # Conversão: 2000=5rpm, 4000=10rpm, 6000=15rpm
            if speed_reg < 3000:
                self.state['speed_class'] = 1
            elif speed_reg < 5000:
                self.state['speed_class'] = 2
            else:
                self.state['speed_class'] = 3

    def get_state(self):
        """Retorna estado atual"""
        return self.state.copy()

    def stop(self):
        """Para polling"""
        self.running = False
