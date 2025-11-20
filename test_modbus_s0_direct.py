#!/usr/bin/env python3
"""
Teste DIRETO de escrita Modbus na saída S0 (coil 384)
Objetivo: Isolar se o problema está no Modbus ou no WebSocket/async
"""

import time
import sys
from pymodbus.client import ModbusSerialClient
from pymodbus.exceptions import ModbusException

# Configuração serial (mesma do modbus_client.py)
PORT = '/dev/ttyUSB0'
BAUDRATE = 57600
PARITY = 'N'
STOPBITS = 2
BYTESIZE = 8
TIMEOUT = 1.0
SLAVE_ADDRESS = 1

# Endereço da saída S0
S0_ADDRESS = 384  # 0x0180 em hex

def test_modbus_s0():
    """Testa escrita direta em S0 com logs verbosos"""

    print("=" * 60)
    print("TESTE DIRETO MODBUS - SAÍDA S0")
    print("=" * 60)
    print(f"Porta: {PORT}")
    print(f"Baudrate: {BAUDRATE}")
    print(f"Configuração: {BYTESIZE}{PARITY}{STOPBITS}")
    print(f"Slave Address: {SLAVE_ADDRESS}")
    print(f"Coil S0: {S0_ADDRESS} (0x{S0_ADDRESS:04X})")
    print("=" * 60)

    # Conectar
    print(f"\n[1] Conectando ao PLC...")
    client = ModbusSerialClient(
        port=PORT,
        baudrate=BAUDRATE,
        parity=PARITY,
        stopbits=STOPBITS,
        bytesize=BYTESIZE,
        timeout=TIMEOUT
    )

    if not client.connect():
        print("❌ FALHA: Não conseguiu conectar ao PLC")
        print("   Verifique:")
        print("   - Cabo RS485 conectado")
        print("   - Porta correta (/dev/ttyUSB0 ou /dev/ttyUSB1)")
        print("   - CLP ligado")
        return False

    print("✓ Conectado com sucesso")

    try:
        # Ler estado atual de S0
        print(f"\n[2] Lendo estado atual de S0 (coil {S0_ADDRESS})...")
        response = client.read_coils(
            address=S0_ADDRESS,
            count=1,
            device_id=SLAVE_ADDRESS
        )

        if response.isError():
            print(f"❌ ERRO ao ler coil: {response}")
        else:
            current_state = response.bits[0]
            print(f"✓ Estado atual de S0: {current_state} ({'ON' if current_state else 'OFF'})")

        # FASE 1: Ativar S0 (TRUE)
        print(f"\n[3] ATIVANDO S0 (escrevendo TRUE no coil {S0_ADDRESS})...")
        response_on = client.write_coil(
            address=S0_ADDRESS,
            value=True,
            device_id=SLAVE_ADDRESS
        )

        if response_on.isError():
            print(f"❌ ERRO ao escrever TRUE: {response_on}")
            return False
        else:
            print("✓ Comando write_coil(TRUE) enviado com sucesso")
            print(f"  Resposta do PLC: {response_on}")

        # Verificar se escrita funcionou
        print(f"\n[4] Verificando se S0 foi ativado...")
        time.sleep(0.05)  # 50ms para estabilizar
        response_check = client.read_coils(
            address=S0_ADDRESS,
            count=1,
            device_id=SLAVE_ADDRESS
        )

        if response_check.isError():
            print(f"❌ ERRO ao verificar: {response_check}")
        else:
            state_after_on = response_check.bits[0]
            print(f"✓ Estado de S0 após write: {state_after_on} ({'ON' if state_after_on else 'OFF'})")

            if state_after_on:
                print("\n🎯 SUCESSO! S0 está ATIVADO!")
                print("   >> MEÇA AGORA: Deve ter ~24VDC em S0 <<")
            else:
                print("\n⚠️ PROBLEMA! S0 continua DESATIVADO mesmo após write_coil(TRUE)")
                print("   Possíveis causas:")
                print("   - CLP não está aceitando escritas (modo protegido?)")
                print("   - Saída S0 desabilitada na configuração do CLP")
                print("   - Estado 00BE (Modbus slave) não está ON")

        # Aguardar para medição
        print(f"\n[5] Aguardando 3 segundos para medição...")
        for i in range(3, 0, -1):
            print(f"   {i}...")
            time.sleep(1)

        # FASE 2: Desativar S0 (FALSE)
        print(f"\n[6] DESATIVANDO S0 (escrevendo FALSE no coil {S0_ADDRESS})...")
        response_off = client.write_coil(
            address=S0_ADDRESS,
            value=False,
            device_id=SLAVE_ADDRESS
        )

        if response_off.isError():
            print(f"❌ ERRO ao escrever FALSE: {response_off}")
        else:
            print("✓ Comando write_coil(FALSE) enviado com sucesso")
            print(f"  Resposta do PLC: {response_off}")

        # Verificar desativação
        print(f"\n[7] Verificando se S0 foi desativado...")
        time.sleep(0.05)
        response_final = client.read_coils(
            address=S0_ADDRESS,
            count=1,
            device_id=SLAVE_ADDRESS
        )

        if response_final.isError():
            print(f"❌ ERRO ao verificar: {response_final}")
        else:
            state_after_off = response_final.bits[0]
            print(f"✓ Estado final de S0: {state_after_off} ({'ON' if state_after_off else 'OFF'})")

            if not state_after_off:
                print("\n✓ S0 desativado com sucesso")
            else:
                print("\n⚠️ PROBLEMA! S0 continua ATIVADO mesmo após write_coil(FALSE)")

        print("\n" + "=" * 60)
        print("TESTE CONCLUÍDO")
        print("=" * 60)
        return True

    except ModbusException as e:
        print(f"\n❌ EXCEÇÃO MODBUS: {e}")
        return False
    except Exception as e:
        print(f"\n❌ ERRO INESPERADO: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        client.close()
        print("\nConexão fechada")


if __name__ == "__main__":
    print("\n⚠️  ATENÇÃO: Este script irá ativar fisicamente a saída S0!")
    print("   Certifique-se de que é seguro fazer isso.\n")

    input("Pressione ENTER para continuar ou Ctrl+C para cancelar...")

    success = test_modbus_s0()

    if success:
        print("\n✓ Teste executado com sucesso")
        sys.exit(0)
    else:
        print("\n❌ Teste falhou - verifique os erros acima")
        sys.exit(1)
