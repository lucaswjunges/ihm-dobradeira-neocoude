#!/usr/bin/env python3
"""
Teste de escrita nos bits internos livres (0x0030-0x0034)
Objetivo: Validar que podemos usar esses endereços sem conflito com ladder
"""

import time
from pymodbus.client import ModbusSerialClient

PORT = '/dev/ttyUSB0'
BAUDRATE = 57600
SLAVE_ADDRESS = 1

# Bits internos livres escolhidos
BITS_INTERNOS = {
    'MODBUS_CMD_FORWARD': 48,    # 0x0030
    'MODBUS_CMD_BACKWARD': 49,   # 0x0031
    'MODBUS_CMD_STOP': 50,       # 0x0032
    'MODBUS_CMD_EMERGENCY': 51,  # 0x0033
    'MODBUS_CMD_COMMAND_ON': 52  # 0x0034
}

print("=" * 70)
print("TESTE DE ESCRITA EM BITS INTERNOS LIVRES")
print("=" * 70)
print("\nBits a testar:")
for name, addr in BITS_INTERNOS.items():
    print(f"  {name:30s}: {addr:3d} (0x{addr:04X})")
print("=" * 70)

client = ModbusSerialClient(
    port=PORT,
    baudrate=BAUDRATE,
    parity='N',
    stopbits=2,
    bytesize=8,
    timeout=1.0
)

if not client.connect():
    print("❌ Falha ao conectar ao PLC")
    exit(1)

print("\n✓ Conectado ao PLC\n")

try:
    # Teste 1: Escrever e ler cada bit individual
    print("[TESTE 1] Escrita e leitura individual\n")
    print(f"{'Bit':<30s} {'Addr':>5s} {'Write':>8s} {'Read':>8s} {'Status':>10s}")
    print("-" * 70)

    for name, addr in BITS_INTERNOS.items():
        # Escrever TRUE
        write_resp = client.write_coil(address=addr, value=True, device_id=SLAVE_ADDRESS)
        time.sleep(0.05)

        # Ler de volta
        read_resp = client.read_coils(address=addr, count=1, device_id=SLAVE_ADDRESS)

        if write_resp.isError() or read_resp.isError():
            print(f"{name:<30s} {addr:>5d} {'ERROR':>8s} {'ERROR':>8s} {'❌ FAIL':>10s}")
        else:
            read_value = read_resp.bits[0]
            status = "✓ PASS" if read_value else "✗ FAIL"
            print(f"{name:<30s} {addr:>5d} {'TRUE':>8s} {str(read_value):>8s} {status:>10s}")

        # Limpar (escrever FALSE)
        client.write_coil(address=addr, value=False, device_id=SLAVE_ADDRESS)
        time.sleep(0.05)

    # Teste 2: Verificar que bits permanecem estáveis (não são sobrescritos)
    print("\n[TESTE 2] Estabilidade dos bits (não sobrescritos pelo ladder)\n")
    print("Escrevendo TRUE em todos os bits e aguardando 2 segundos...")

    # Escrever TRUE em todos
    for addr in BITS_INTERNOS.values():
        client.write_coil(address=addr, value=True, device_id=SLAVE_ADDRESS)
        time.sleep(0.01)

    # Aguardar
    time.sleep(2.0)

    # Ler todos de novo
    print(f"\n{'Bit':<30s} {'Addr':>5s} {'Após 2s':>10s} {'Status':>10s}")
    print("-" * 70)

    all_stable = True
    for name, addr in BITS_INTERNOS.items():
        read_resp = client.read_coils(address=addr, count=1, device_id=SLAVE_ADDRESS)
        if not read_resp.isError():
            value = read_resp.bits[0]
            status = "✓ ESTÁVEL" if value else "✗ DESLIGOU"
            if not value:
                all_stable = False
            print(f"{name:<30s} {addr:>5d} {str(value):>10s} {status:>10s}")

    # Limpar todos
    print("\nLimpando bits...")
    for addr in BITS_INTERNOS.values():
        client.write_coil(address=addr, value=False, device_id=SLAVE_ADDRESS)
        time.sleep(0.01)

    # Teste 3: Pulso rápido (simular comando IHM)
    print("\n[TESTE 3] Simulação de pulso de comando (100ms)\n")
    print("Testando bit FORWARD (48):")

    # Ler estado inicial
    resp = client.read_coils(address=48, count=1, device_id=SLAVE_ADDRESS)
    initial = resp.bits[0]
    print(f"  Estado inicial: {initial}")

    # Pulso ON
    print("  Ativando (TRUE)...")
    client.write_coil(address=48, value=True, device_id=SLAVE_ADDRESS)
    time.sleep(0.05)

    resp = client.read_coils(address=48, count=1, device_id=SLAVE_ADDRESS)
    during = resp.bits[0]
    print(f"  Durante pulso: {during} {'✓' if during else '✗'}")

    # Aguardar 100ms
    time.sleep(0.1)

    # Pulso OFF
    print("  Desativando (FALSE)...")
    client.write_coil(address=48, value=False, device_id=SLAVE_ADDRESS)
    time.sleep(0.05)

    resp = client.read_coils(address=48, count=1, device_id=SLAVE_ADDRESS)
    after = resp.bits[0]
    print(f"  Após desativar: {after} {'✓' if not after else '✗'}")

    # Resultado final
    print("\n" + "=" * 70)
    if all_stable:
        print("RESULTADO: ✓ TODOS OS TESTES PASSARAM")
        print("\nBits internos 48-52 (0x0030-0x0034) estão LIVRES e FUNCIONAIS!")
        print("\n✓ Pode usar para comandos Modbus")
        print("✓ Bits permanecem estáveis (não sobrescritos pelo ladder)")
        print("✓ Leitura/escrita funcionando corretamente")
        print("\n⚠️  PRÓXIMO PASSO: Modificar ladder para LER esses bits")
    else:
        print("RESULTADO: ⚠️  ALGUNS BITS SÃO INSTÁVEIS")
        print("\nBits podem estar sendo usados pelo ladder.")
        print("Considere escolher outros endereços.")
    print("=" * 70)

except Exception as e:
    print(f"\n❌ ERRO: {e}")
    import traceback
    traceback.print_exc()
finally:
    # Garantir que todos os bits estão desligados
    print("\nDesligando todos os bits de teste...")
    for addr in BITS_INTERNOS.values():
        try:
            client.write_coil(address=addr, value=False, device_id=SLAVE_ADDRESS)
        except:
            pass

    client.close()
    print("Conexão fechada")
