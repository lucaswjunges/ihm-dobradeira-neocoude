import time
import modbus_client_esp32 as mc

def write_bend_angle_NEW(self, bend_number, degrees):
    if bend_number not in [1, 2, 3]:
        return False
    addrs = {1: (0x0A00, 0x0A02, 0x0390), 2: (0x0A04, 0x0A06, 0x0391), 3: (0x0A08, 0x0A0A, 0x0392)}
    msw_addr, lsw_addr, trigger = addrs[bend_number]
    value = int(degrees * 10)
    msw = (value >> 16) & 0xFFFF
    lsw = value & 0xFFFF
    if not (self.write_register(msw_addr, msw) and self.write_register(lsw_addr, lsw)):
        return False
    self.write_coil(trigger, True)
    time.sleep(0.05)
    self.write_coil(trigger, False)
    return True

def read_bend_angle_NEW(self, bend_number):
    if bend_number not in [1, 2, 3]:
        return None
    addrs = {1: (0x0842, 0x0840), 2: (0x0848, 0x0846), 3: (0x0852, 0x0850)}
    msw_addr, lsw_addr = addrs[bend_number]
    msw = self.read_register(msw_addr)
    lsw = self.read_register(lsw_addr)
    if msw is None or lsw is None:
        return None
    return ((msw << 16) | lsw) / 10.0

mc.ModbusClientWrapper.write_bend_angle = write_bend_angle_NEW
mc.ModbusClientWrapper.read_bend_angle = read_bend_angle_NEW
print("Patch 0x0A00 OK")
