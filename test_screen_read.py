#!/usr/bin/env python3
"""
Teste CORRIGIDO - Leitura dos Registros de Tela
================================================

Testa se registros 0FEE e 0FEC podem ser lidos via Modbus RTU.
Usa sintaxe correta do pymodbus 3.x (device_id ao invés de slave).
"""

from pymodbus.client import ModbusSerialClient
import time

# Configuração
PORT = '/dev/ttyUSB0'
BAUDRATE = 57600
SLAVE_ID = 1

# Registros a testar
REG_TELA_ATUAL = 0x0FEE  # 4078 decimal - tela atual
REG_TELA_ALVO = 0x0FEC   # 4076 decimal - tela alvo
STATE_TRIGGER = 0x00DA   # 218 decimal - trigger carrega tela

print("=" * 60)
print("TESTE DE REGISTROS DE TELA (0FEE e 0FEC)")
print("=" * 60)
print(f"Porta: {PORT}")
print(f"Baudrate: {BAUDRATE}")
print(f"Slave ID: {SLAVE_ID}\n")

# Conecta ao CLP
client = ModbusSerialClient(
    port=PORT,
    baudrate=BAUDRATE,
    parity='N',
    stopbits=1,
    bytesize=8,
    timeout=1.0
)

if not client.connect():
    print("✗ ERRO: Não foi possível abrir a porta serial")
    print(f"  Verifique se {PORT} está conectado")
    exit(1)

print(f"✓ Conexão Modbus estabelecida em {PORT}\n")

# Teste 1: Ler registro 0FEE (tela atual)
print("[Teste 1] Registro 0FEE (4078 decimal) - TELA ATUAL")
print("-" * 60)

try:
    # Sintaxe correta pymodbus 3.x: device_id ao invés de slave
    result = client.read_holding_registers(
        address=REG_TELA_ATUAL,
        count=1,
        device_id=SLAVE_ID
    )

    if result.isError():
        print(f"  ✗ ERRO: {result}")
        print("  Possível que este registro não esteja implementado no firmware")
    else:
        tela_atual = result.registers[0]
        print(f"  ✓ Registro 0FEE lido com sucesso!")
        print(f"  Valor: 0x{tela_atual:04X} ({tela_atual} decimal)")

        # Interpreta valor
        telas = {
            1: "Tela principal/inicial",
            2: "Tela de configuração",
            3: "Tela de status",
            4: "Tela Dobra 1 (K1)",
            5: "Tela Dobra 2 (K2)",
            6: "Tela Dobra 3 (K3)",
            7: "Tela de diagnóstico",
            8: "Tela auxiliar",
        }

        if tela_atual in telas:
            print(f"  Interpretação: {telas[tela_atual]}")
        else:
            print(f"  Interpretação: Tela #{tela_atual}")

except Exception as e:
    print(f"  ✗ EXCEÇÃO ao ler 0FEE: {e}")

# Teste 2: Ler registro 0FEC (tela alvo)
print("\n[Teste 2] Registro 0FEC (4076 decimal) - TELA ALVO")
print("-" * 60)

try:
    result = client.read_holding_registers(
        address=REG_TELA_ALVO,
        count=1,
        device_id=SLAVE_ID
    )

    if result.isError():
        print(f"  ✗ ERRO: {result}")
        print("  Possível que este registro não esteja implementado no firmware")
    else:
        tela_alvo = result.registers[0]
        print(f"  ✓ Registro 0FEC lido com sucesso!")
        print(f"  Valor: 0x{tela_alvo:04X} ({tela_alvo} decimal)")
        print(f"  Nota: Este registro é usado para ESCREVER (mudar de tela)")

except Exception as e:
    print(f"  ✗ EXCEÇÃO ao ler 0FEC: {e}")

# Teste 3: Ler estado 00DA (trigger de carregamento)
print("\n[Teste 3] Estado 00DA (218 decimal) - TRIGGER CARREGA TELA")
print("-" * 60)

try:
    result = client.read_coils(
        address=STATE_TRIGGER,
        count=1,
        device_id=SLAVE_ID
    )

    if result.isError():
        print(f"  ✗ ERRO: {result}")
    else:
        trigger = result.bits[0]
        print(f"  ✓ Estado 00DA lido com sucesso!")
        print(f"  Valor: {'ON' if trigger else 'OFF'}")
        print(f"  Nota: Transição OFF→ON carrega tela definida em 0FEC")

except Exception as e:
    print(f"  ✗ EXCEÇÃO ao ler 00DA: {e}")

# Teste 4: Monitoramento por 5 segundos
print("\n[Teste 4] Monitoramento por 5 segundos")
print("-" * 60)
print("  Pressione botões K1, K2 ou K3 no CLP físico se possível...")
print("  Verificando se registro 0FEE muda:\n")

last_screen = None
for i in range(10):
    try:
        result = client.read_holding_registers(
            address=REG_TELA_ATUAL,
            count=1,
            device_id=SLAVE_ID
        )

        if not result.isError():
            screen = result.registers[0]
            if screen != last_screen:
                print(f"  [{i*0.5:.1f}s] ✓ Tela mudou para: {screen}")
                last_screen = screen
            else:
                print(f"  [{i*0.5:.1f}s] Tela: {screen} (sem mudança)")
        else:
            print(f"  [{i*0.5:.1f}s] ✗ Erro na leitura")
    except Exception as e:
        print(f"  [{i*0.5:.1f}s] ✗ Exceção: {e}")

    time.sleep(0.5)

# Fecha conexão
client.close()

print("\n" + "=" * 60)
print("TESTE CONCLUÍDO")
print("=" * 60)

print("\n[Resumo]")
print("  Se 0FEE e 0FEC foram lidos com sucesso:")
print("    → ✓ Podemos implementar sincronização de telas!")
print("    → IHM web pode detectar qual tela está ativa no CLP")
print("    → IHM web pode mudar tela escrevendo em 0FEC + trigger 00DA")
print("\n  Se retornaram erro:")
print("    → ✗ Registros não disponíveis neste firmware")
print("    → Precisaremos criar via ROT5 no ladder")
print("    → Solução alternativa: usar registros 0880-0885")
