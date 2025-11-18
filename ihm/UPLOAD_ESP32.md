# INSTRUÇÕES: Upload para ESP32

O ESP32 não tem SSH habilitado. Use um dos métodos abaixo:

---

## Método 1: Via Cabo Serial (Recomendado)

### Se ESP32 está conectado via USB nesta máquina:

```bash
# 1. Verificar porta USB
ls -la /dev/ttyACM* /dev/ttyUSB*

# 2. Conectar via terminal serial (screen, minicom, ou Python)
screen /dev/ttyACM0 115200

# 3. No terminal do ESP32, navegar e editar
cd /diretorio/do/projeto
# Copiar conteúdo do arquivo modificado
```

---

## Método 2: Via Interface Web (Upload de Arquivo)

Se o ESP32 tem interface web para upload:

```bash
# 1. Preparar arquivo para upload
cd /home/lucas-junges/Documents/clientes/w&co/ihm

# 2. Acessar interface web do ESP32
# http://192.168.0.106/upload (se disponível)

# 3. Fazer upload de:
#    - modbus_client.py
#    - test_solucao_a.py
```

---

## Método 3: Via MicroPython REPL (se ESP32 usa MicroPython)

```bash
# 1. Instalar ampy
pip3 install adafruit-ampy

# 2. Upload via ampy
ampy --port /dev/ttyACM0 put modbus_client.py
ampy --port /dev/ttyACM0 put test_solucao_a.py

# 3. Verificar
ampy --port /dev/ttyACM0 ls
```

---

## Método 4: Copiar Manualmente o Código

Se nenhum método acima funcionar, copie o código manualmente:

### 1. Conecte no ESP32 via cabo USB/Serial

### 2. Abra o editor de arquivos do ESP32

### 3. Modifique `modbus_client.py`:

**Encontre a função `write_bend_angle` (aprox. linha 636) e substitua por:**

```python
def write_bend_angle(self, bend_number: int, degrees: float) -> bool:
    """
    Grava ângulo de dobra na área SHADOW (0x0840+) - lida pelo ladder
    MODIFICADO 18/Nov/2025
    """
    if bend_number not in [1, 2, 3]:
        print(f"✗ Número de dobra inválido: {bend_number}")
        return False

    # Mapeamento: 0x0840-0x0852 (área SHADOW lida pelo ladder)
    addresses = {
        1: {'msw': 0x0842, 'lsw': 0x0840},
        2: {'msw': 0x0848, 'lsw': 0x0846},
        3: {'msw': 0x0852, 'lsw': 0x0850},
    }

    addr = addresses[bend_number]

    # Converter graus para valor CLP 32-bit
    value_32bit = int(degrees * 10)

    # Dividir em MSW e LSW
    msw = (value_32bit >> 16) & 0xFFFF
    lsw = value_32bit & 0xFFFF

    print(f"✎ Gravando Dobra {bend_number}: {degrees}° → MSW={msw}, LSW={lsw}")

    # Escrever MSW primeiro, depois LSW
    success_msw = self.write_register(addr['msw'], msw)
    success_lsw = self.write_register(addr['lsw'], lsw)

    return success_msw and success_lsw
```

**Encontre a função `read_bend_angle` (aprox. linha 696) e substitua por:**

```python
def read_bend_angle(self, bend_number: int):
    """
    Lê ângulo de dobra da área SHADOW (0x0840+)
    MODIFICADO 18/Nov/2025
    """
    addresses = {
        1: {'msw': 0x0842, 'lsw': 0x0840},
        2: {'msw': 0x0848, 'lsw': 0x0846},
        3: {'msw': 0x0852, 'lsw': 0x0850},
    }

    if bend_number not in addresses:
        return None

    addr = addresses[bend_number]

    # Ler MSW e LSW
    msw = self.read_register(addr['msw'])
    lsw = self.read_register(addr['lsw'])

    if msw is None or lsw is None:
        return None

    # Combinar em 32-bit
    value_32bit = (msw << 16) | lsw

    # Converter para graus
    return value_32bit / 10.0
```

### 4. Salvar e reiniciar o servidor

---

## Método 5: Usar Pendrive/Cartão SD

Se ESP32 tem slot para cartão SD:

```bash
# 1. Copiar para pendrive
cp modbus_client.py /media/pendrive/
cp test_solucao_a.py /media/pendrive/

# 2. Inserir no ESP32

# 3. No ESP32, copiar do pendrive
cp /sd/modbus_client.py /projeto/
cp /sd/test_solucao_a.py /projeto/
```

---

## ✅ Após Upload

### 1. Testar a modificação:

```bash
python3 test_solucao_a.py
```

### 2. Se OK, reiniciar servidor:

```bash
# Método depende de como servidor está configurado:
systemctl restart ihm_server
# OU
killall python3 && python3 main_server.py &
# OU
reboot
```

---

## 🆘 Se Não Conseguir Upload

### Alternativa: Aplicar patch via código inline

Crie um arquivo `patch_modbus.py` no ESP32:

```python
#!/usr/bin/env python3
"""
Patch temporário para modbus_client
"""
import modbus_client

# Salvar função original
original_write = modbus_client.ModbusClientWrapper.write_bend_angle

def patched_write_bend_angle(self, bend_number, degrees):
    """Versão patcheada que grava em 0x0840"""
    addresses = {
        1: {'msw': 0x0842, 'lsw': 0x0840},
        2: {'msw': 0x0848, 'lsw': 0x0846},
        3: {'msw': 0x0852, 'lsw': 0x0850},
    }

    addr = addresses[bend_number]
    value_32bit = int(degrees * 10)
    msw = (value_32bit >> 16) & 0xFFFF
    lsw = value_32bit & 0xFFFF

    success_msw = self.write_register(addr['msw'], msw)
    success_lsw = self.write_register(addr['lsw'], lsw)

    return success_msw and success_lsw

# Aplicar patch
modbus_client.ModbusClientWrapper.write_bend_angle = patched_write_bend_angle

print("✅ Patch aplicado! Reinicie o servidor.")
```

Execute: `python3 patch_modbus.py`

---

## 📞 Precisa de Ajuda?

Me informe qual método você consegue usar e posso adaptar as instruções.
