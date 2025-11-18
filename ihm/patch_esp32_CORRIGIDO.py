"""
PATCH CORRIGIDO - Área 0x0A00 (Modbus Input Buffer)

Este patch corrige o erro da Solução A original que tentava gravar
em 0x0840 (READ-ONLY). Agora grava em 0x0A00 e aciona trigger para
ROT5 copiar automaticamente.

Data: 18/Nov/2025
Status: TESTADO EM TEORIA - Aguarda aplicação
"""

import time

def write_bend_angle_CORRECTED(self, bend_number, degrees):
    """
    Grava ângulo na área Modbus Input (0x0A00+) e aciona trigger.
    ROT5 copia automaticamente para shadow (0x0840+).
    """
    if bend_number not in [1, 2, 3]:
        return False

    # Mapeamento: Modbus Input + Trigger
    mapping = {
        1: {'msw': 0x0A00, 'lsw': 0x0A02, 'trigger': 0x0390},
        2: {'msw': 0x0A04, 'lsw': 0x0A06, 'trigger': 0x0391},
        3: {'msw': 0x0A08, 'lsw': 0x0A0A, 'trigger': 0x0392},
    }

    addr = mapping[bend_number]
    value_32bit = int(degrees * 10)
    msw = (value_32bit >> 16) & 0xFFFF
    lsw = value_32bit & 0xFFFF

    # Grava MSW e LSW
    ok_msw = self.write_register(addr['msw'], msw)
    ok_lsw = self.write_register(addr['lsw'], lsw)

    if not (ok_msw and ok_lsw):
        return False

    # Aciona trigger
    self.write_coil(addr['trigger'], True)
    time.sleep(0.05)  # 50ms
    self.write_coil(addr['trigger'], False)

    return True


def read_bend_angle_CORRECTED(self, bend_number):
    """
    Lê ângulo da área shadow (0x0840+) para confirmar sincronização.
    """
    if bend_number not in [1, 2, 3]:
        return None

    # Ler da shadow (o que ladder usa)
    mapping = {
        1: {'msw': 0x0842, 'lsw': 0x0840},
        2: {'msw': 0x0848, 'lsw': 0x0846},
        3: {'msw': 0x0852, 'lsw': 0x0850},
    }

    addr = mapping[bend_number]
    msw = self.read_register(addr['msw'])
    lsw = self.read_register(addr['lsw'])

    if msw is None or lsw is None:
        return None

    value_32bit = (msw << 16) | lsw
    return value_32bit / 10.0


# ========== APLICAR PATCH ==========
print("Aplicando patch CORRIGIDO (0x0A00)...")

try:
    import modbus_client_esp32

    # Substituir métodos
    modbus_client_esp32.ModbusClientWrapper.write_bend_angle = write_bend_angle_CORRECTED
    modbus_client_esp32.ModbusClientWrapper.read_bend_angle = read_bend_angle_CORRECTED

    print("✅ Patch 0x0A00 aplicado com sucesso!")
    print("   - write_bend_angle: Grava em 0x0A00 + trigger")
    print("   - read_bend_angle: Lê de 0x0840 (shadow)")

except Exception as e:
    print(f"❌ Erro ao aplicar patch: {e}")
