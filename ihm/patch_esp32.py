# Patch para ESP32 - Modifica write_bend_angle e read_bend_angle
# Para gravar em 0x0840 ao invés de 0x0500

def write_bend_angle_patched(self, bend_number, degrees):
    """Grava em 0x0840 (área lida pelo ladder) - PATCHED 18/Nov/2025"""
    if bend_number not in [1, 2, 3]:
        return False

    # Área 0x0840-0x0852 (SHADOW lida pelo ladder)
    addrs = {
        1: {'msw': 0x0842, 'lsw': 0x0840},
        2: {'msw': 0x0848, 'lsw': 0x0846},
        3: {'msw': 0x0852, 'lsw': 0x0850},
    }

    addr = addrs[bend_number]
    value_32bit = int(degrees * 10)
    msw = (value_32bit >> 16) & 0xFFFF
    lsw = value_32bit & 0xFFFF

    print(f"Gravando Dobra {bend_number}: {degrees}° → MSW={msw}, LSW={lsw}")

    ok_msw = self.write_register(addr['msw'], msw)
    ok_lsw = self.write_register(addr['lsw'], lsw)

    return ok_msw and ok_lsw


def read_bend_angle_patched(self, bend_number):
    """Lê de 0x0840 (área lida pelo ladder) - PATCHED 18/Nov/2025"""
    addrs = {
        1: {'msw': 0x0842, 'lsw': 0x0840},
        2: {'msw': 0x0848, 'lsw': 0x0846},
        3: {'msw': 0x0852, 'lsw': 0x0850},
    }

    if bend_number not in addrs:
        return None

    addr = addrs[bend_number]
    msw = self.read_register(addr['msw'])
    lsw = self.read_register(addr['lsw'])

    if msw is None or lsw is None:
        return None

    value_32bit = (msw << 16) | lsw
    return value_32bit / 10.0


# Aplicar patch
import modbus_client_esp32
modbus_client_esp32.ModbusClientWrapper.write_bend_angle = write_bend_angle_patched
modbus_client_esp32.ModbusClientWrapper.read_bend_angle = read_bend_angle_patched

print("✅ Patch aplicado com sucesso!")
print("   write_bend_angle → grava em 0x0840")
print("   read_bend_angle → lê de 0x0840")
print()
print("⚠️  Reinicie o servidor para aplicar:")
print("   import machine")
print("   machine.reset()")
