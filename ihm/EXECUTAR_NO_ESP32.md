# EXECUTAR TESTE NO ESP32 (192.168.0.106)

O CLP está conectado no **ESP32** (192.168.0.106), não nesta máquina.

## Opção 1: Executar via SSH (se ESP32 tem SSH)

```bash
# Conectar no ESP32
ssh usuario@192.168.0.106

# Ir para diretório do projeto
cd /caminho/do/projeto

# Executar teste
python3 test_write_official_angles.py
```

## Opção 2: Copiar script para ESP32 e executar

```bash
# Copiar script para ESP32
scp test_write_official_angles.py usuario@192.168.0.106:/tmp/

# Conectar e executar
ssh usuario@192.168.0.106
cd /tmp
python3 test_write_official_angles.py
```

## Opção 3: Testar manualmente via Python no ESP32

Conecte no ESP32 e execute:

```python
from pymodbus.client import ModbusSerialClient
import time

# Conectar ao CLP
client = ModbusSerialClient(
    port='/dev/ttyUSB0',  # ou a porta que o ESP32 usa
    baudrate=57600,
    parity='N',
    stopbits=2,
    bytesize=8,
    timeout=1.0
)

if client.connect():
    print("✅ Conectado ao CLP")

    # Teste 1: Ler área 0x0500
    print("\n📖 Lendo valor atual...")
    result = client.read_holding_registers(address=1279, count=1, slave=1)
    if not result.isError():
        original = result.registers[0]
        print(f"  Valor original: {original} ({original/10.0:.1f}°)")

        # Teste 2: Escrever valor de teste
        print("\n✏️  Escrevendo valor de teste (90.0°)...")
        test_value = 900
        client.write_register(address=1279, value=test_value, slave=1)

        time.sleep(0.5)

        # Teste 3: Ler de volta
        print("\n🔍 Verificando escrita...")
        result = client.read_holding_registers(address=1279, count=1, slave=1)
        if not result.isError():
            new_value = result.registers[0]
            print(f"  Valor lido: {new_value} ({new_value/10.0:.1f}°)")

            if new_value == test_value:
                print("\n✅ SUCESSO! Área 0x0500 é GRAVÁVEL")
            else:
                print(f"\n❌ FALHA! Esperado {test_value}, obtido {new_value}")
                print("   → Área pode estar protegida pelo ladder")

        # Teste 4: Restaurar valor original
        print("\n♻️  Restaurando valor original...")
        client.write_register(address=1279, value=original, slave=1)
        print("  ✅ Restaurado")

    client.close()
else:
    print("❌ Não conectou no CLP")
```

## Opção 4: Verificar via logs do servidor rodando

O servidor já está rodando desde ontem. Vamos verificar os logs:

```bash
tail -100 /home/lucas-junges/Documents/clientes/w&co/ihm/server_producao_new.log | grep -E "write_register|write.*0x050"
```

Isso mostrará se a IHM já está escrevendo com sucesso.
