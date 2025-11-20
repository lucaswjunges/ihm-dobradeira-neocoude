#!/usr/bin/env python3
"""
Test script para verificar comunicação RS485-B com CLP Atos MPC4004
Testa a porta dos fundos após upload do clp_pronto_CORRIGIDO.sup
"""

import serial
import time
from pymodbus.client import ModbusSerialClient
from pymodbus.exceptions import ModbusException

# Configuração RS485 conforme manual
BAUDRATE = 57600
PARITY = 'N'  # None
STOPBITS = 2
BYTESIZE = 8
TIMEOUT = 1.0

# Endereços críticos (decimal)
REG_SLAVE_ADDRESS = 6536  # 1988H - endereço slave do CLP
STATE_MODBUS_ENABLE = 190  # 00BE - habilita modo Modbus slave
REG_ENCODER_MSW = 1238    # 04D6 - encoder high word
REG_ENCODER_LSW = 1239    # 04D7 - encoder low word

def find_serial_port():
    """Tenta encontrar o conversor USB-RS485-FTDI"""
    possible_ports = ['/dev/ttyUSB0', '/dev/ttyUSB1', '/dev/ttyUSB2']
    
    print("Procurando porta serial...")
    for port in possible_ports:
        try:
            ser = serial.Serial(port, timeout=0.1)
            ser.close()
            print(f"✓ Porta encontrada: {port}")
            return port
        except (OSError, serial.SerialException):
            continue
    
    print("✗ Nenhuma porta USB-RS485 encontrada")
    print("  Verifique se o conversor está conectado")
    return None

def test_modbus_connection(port, slave_address):
    """Testa conexão Modbus com o CLP"""
    print(f"\nTestando Modbus no endereço slave {slave_address}...")
    
    client = None
    try:
        client = ModbusSerialClient(
            port=port,
            baudrate=BAUDRATE,
            parity=PARITY,
            stopbits=STOPBITS,
            bytesize=BYTESIZE,
            timeout=TIMEOUT
        )
        
        if not client.connect():
            print("✗ Falha ao abrir porta serial")
            return False
        
        print(f"✓ Porta serial aberta: {port}")
        
        # Teste 1: Ler registrador do encoder (32-bit)
        print("\n[Teste 1] Lendo contador do encoder (04D6/04D7)...")
        try:
            # pymodbus 3.x usa 'device_id' ao invés de 'slave' ou 'unit'
            result = client.read_holding_registers(
                address=REG_ENCODER_MSW,
                count=2,
                device_id=slave_address
            )
            
            if result.isError():
                print(f"✗ Erro Modbus: {result}")
                return False
            
            msw = result.registers[0]
            lsw = result.registers[1]
            encoder_value = (msw << 16) | lsw
            
            print(f"✓ Encoder lido com sucesso!")
            print(f"  MSW (04D6): 0x{msw:04X} ({msw})")
            print(f"  LSW (04D7): 0x{lsw:04X} ({lsw})")
            print(f"  Valor 32-bit: {encoder_value}")
            
        except ModbusException as e:
            print(f"✗ Exceção Modbus: {e}")
            return False
        except Exception as e:
            print(f"✗ Erro: {e}")
            return False
        
        # Teste 2: Ler estado 00BE (Modbus enable)
        print("\n[Teste 2] Verificando estado 00BE (Modbus slave enable)...")
        try:
            result = client.read_coils(
                address=STATE_MODBUS_ENABLE,
                count=1,
                device_id=slave_address
            )
            
            if result.isError():
                print(f"✗ Erro ao ler estado 00BE: {result}")
            else:
                state = result.bits[0]
                if state:
                    print(f"✓ Estado 00BE = ON (Modbus habilitado)")
                else:
                    print(f"⚠ Estado 00BE = OFF (Modbus NÃO habilitado!)")
                    print("  O CLP não está em modo Modbus slave!")
                    
        except Exception as e:
            print(f"✗ Exceção ao ler coil: {e}")
        
        # Teste 3: Ler entradas digitais E0-E7
        print("\n[Teste 3] Lendo status entradas digitais E0-E7...")
        try:
            result = client.read_holding_registers(
                address=256,  # 0100H
                count=8,
                device_id=slave_address
            )
            
            if result.isError():
                print(f"✗ Erro ao ler entradas: {result}")
            else:
                print("✓ Entradas digitais:")
                for i, reg in enumerate(result.registers):
                    status = "ON" if (reg & 0x0001) else "OFF"
                    print(f"  E{i}: {status} (reg=0x{reg:04X})")
                    
        except Exception as e:
            print(f"✗ Exceção ao ler entradas: {e}")
        
        # Teste 4: Ler saídas digitais S0-S7
        print("\n[Teste 4] Lendo status saídas digitais S0-S7...")
        try:
            result = client.read_holding_registers(
                address=384,  # 0180H
                count=8,
                device_id=slave_address
            )
            
            if result.isError():
                print(f"✗ Erro ao ler saídas: {result}")
            else:
                print("✓ Saídas digitais:")
                for i, reg in enumerate(result.registers):
                    status = "ON" if (reg & 0x0001) else "OFF"
                    print(f"  S{i}: {status} (reg=0x{reg:04X})")
                    
        except Exception as e:
            print(f"✗ Exceção ao ler saídas: {e}")
        
        print("\n" + "=" * 60)
        print("✓✓✓ TESTES CONCLUÍDOS COM SUCESSO ✓✓✓")
        print("=" * 60)
        print("  A porta RS485-B está FUNCIONAL")
        print(f"  Endereço slave confirmado: {slave_address}")
        return True
        
    except Exception as e:
        print(f"\n✗ Erro inesperado: {e}")
        return False
    finally:
        if client:
            client.close()
            time.sleep(0.2)  # Aguarda para liberar porta

def main():
    print("=" * 60)
    print("TESTE DE COMUNICAÇÃO RS485-B - CLP ATOS MPC4004")
    print("Arquivo carregado: clp_pronto_CORRIGIDO.sup")
    print("=" * 60)
    
    # Encontrar porta serial
    port = find_serial_port()
    if not port:
        print("\n⚠ AÇÃO NECESSÁRIA:")
        print("  1. Conecte o conversor USB-RS485-FTDI")
        print("  2. Execute: ls -l /dev/ttyUSB*")
        return
    
    # Tentar endereços slave comuns (1-10)
    print("\nTestando endereços slave comuns...")
    
    for slave_id in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]:
        print(f"\n{'─' * 60}")
        print(f"Testando slave ID {slave_id}")
        print(f"{'─' * 60}")
        
        if test_modbus_connection(port, slave_id):
            print(f"\n{'=' * 60}")
            print(f"✓✓✓ SUCESSO! CLP responde no endereço slave {slave_id} ✓✓✓")
            print(f"{'=' * 60}")
            print("\nPróximos passos:")
            print(f"  1. Use slave_id={slave_id} no seu código Python")
            print("  2. A porta RS485-B está funcional e pronta para uso")
            print("  3. Pode prosseguir com desenvolvimento da IHM web")
            return
        
        time.sleep(0.3)  # Aguarda entre tentativas
    
    print("\n" + "=" * 60)
    print("⚠ NENHUM DISPOSITIVO RESPONDEU")
    print("=" * 60)
    print("\nPossíveis causas:")
    print("  1. Fiação RS485 invertida (trocar A e B)")
    print("  2. Estado 00BE (190 dec) não está ativo no ladder")
    print("  3. Baudrate incorreto no CLP (verificar reg 1987H)")
    print("  4. Endereço slave > 10 (verificar reg 1988H)")
    print("  5. CLP não está alimentado ou em RUN")
    print("\nDiagnóstico adicional:")
    print("  - Verificar LEDs do CLP (PWR, RUN, ERR)")
    print("  - Testar com cabo RS485 invertido (A↔B)")
    print("  - Verificar se estado 00BE está ON no ladder")
    print("  - Ler manual do CLP para configuração RS485-B")

if __name__ == "__main__":
    main()
