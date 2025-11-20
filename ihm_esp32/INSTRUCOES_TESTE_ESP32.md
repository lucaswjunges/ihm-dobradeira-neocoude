# INSTRUÇÕES - TESTAR ÂNGULOS NO ESP32

**Data:** 18 de Novembro de 2025
**Status:** ✅ Código corrigido e carregado no ESP32

---

## ✅ Arquivos Atualizados no ESP32

Os seguintes arquivos foram carregados com as correções:

1. **modbus_map.py** - Área 0x0A00 para escrita, triggers como COILS
2. **modbus_client_esp32.py** - write_bend_angle() e read_bend_angle() corrigidos
3. **test_esp32_quick.py** - Teste rápido para validar

---

## 🔌 Pré-requisitos

Antes de testar, verifique:

- [ ] CLP ligado
- [ ] RS485 conectado:
  - ESP32 GPIO17 (TX) → MAX485 DI
  - ESP32 GPIO16 (RX) → MAX485 RO
  - ESP32 GPIO4 (DE/RE) → MAX485 DE + RE
  - MAX485 A/B → CLP RS485 A/B
- [ ] Estado `0x00BE` (190) = ON no ladder (habilita Modbus slave)
- [ ] Baudrate 57600, 8N2

---

## 🧪 OPÇÃO 1: Teste Rápido no ESP32 (RECOMENDADO)

### Via Thonny IDE:

1. Abra Thonny
2. Configure porta: `/dev/ttyACM0` (ou `/dev/ttyUSB0`)
3. Abra o console Python (Shell)
4. Execute:

```python
import test_esp32_quick
test_esp32_quick.test_angles()
```

### Via ampy + screen:

```bash
# Terminal 1: Monitor serial
screen /dev/ttyACM0 115200

# Terminal 2: Executa teste
ampy --port /dev/ttyACM0 run test_esp32_quick.py
```

### Saída Esperada:

```
==================================================
TESTE RÁPIDO - ÂNGULOS ESP32
==================================================

Conectando CLP...
OK: CLP conectado

==================================================
TESTE 1: ESCRITA
==================================================
Gravando Dobra 1: 90.5°
Gravando Dobra 1: 90.5° -> 0x0A00/0x0A02 (MSW=0, LSW=905)
  Acionando trigger 0x0390 (via coil)...
OK: Dobra 1 = 90.5°
  OK: Gravado 90.5°

==================================================
TESTE 2: LEITURA
==================================================
Lendo Dobra 1 (área SCADA 0x0B00)...
  OK: Lido 90.5°

Validação:
  Esperado: 90.5°
  Lido:     90.5°
  Diferença: 0.0°

  SUCESSO!

==================================================
TESTE CONCLUÍDO
==================================================
```

---

## 🧪 OPÇÃO 2: Teste Completo no Ubuntu

Se preferir testar via Ubuntu (não ESP32):

```bash
cd /home/lucas-junges/Documents/clientes/w&co/ihm_esp32
python3 test_angles_complete.py
```

**IMPORTANTE:** Edite o arquivo antes se precisar trocar a porta serial:

```python
# Linha ~220 em test_angles_complete.py
client = ModbusClientWrapper(stub_mode=False, slave_id=1)
```

---

## 🐛 Troubleshooting

### Erro: "CLP não conectado"

**Causa:** UART2 não está comunicando
**Solução:**
1. Verificar pinos GPIO17/16 no ESP32
2. Verificar MAX485 ligado corretamente
3. Medir tensão: GPIO4 deve estar em 3.3V (DE/RE high)
4. Verificar baudrate 57600 no CLP

### Erro: "Timeout ao escrever registro"

**Causa:** CLP não está respondendo Modbus
**Solução:**
1. Verificar estado `0x00BE` = ON no ladder
2. Verificar slave_id correto (padrão: 1)
3. Usar mbpoll no Ubuntu para testar:

```bash
mbpoll -a 1 -b 57600 -P none -t 3 -r 2560 -c 1 /dev/ttyACM0
```

### Erro: "Falha ao ler" após escrever

**Causa:** ROT5 ainda não copiou para área SCADA
**Solução:**
1. Aumentar sleep após escrita (linha ~195 do modbus_client_esp32.py):
   - De: `time.sleep_ms(100)`
   - Para: `time.sleep_ms(200)`

### Erro: "Diferença muito grande"

**Causa:** Trigger não foi acionado corretamente
**Solução:**
1. Verificar que triggers são COILS (0x0390/0x0391/0x0392)
2. **NÃO** usar `write_register()` nos triggers
3. Usar `write_coil()` conforme código corrigido

---

## 📊 Debug Avançado

### Ver logs do ESP32 em tempo real:

```bash
screen /dev/ttyACM0 115200
```

Pressione `Ctrl+C` no ESP32 para abrir REPL, depois:

```python
import modbus_client_esp32 as mc

# Teste manual
client = mc.ModbusClientWrapper(stub_mode=False, slave_id=1)
client.write_bend_angle(1, 135.0)  # Escreve 135°
angle = client.read_bend_angle(1)   # Lê de volta
print(f"Ângulo: {angle}°")
```

### Ler registros diretamente:

```python
# Área MODBUS INPUT (0x0A00)
msw = client.read_register(0x0A00)
lsw = client.read_register(0x0A02)
print(f"0x0A00: MSW={msw}, LSW={lsw}")

# Área SCADA (0x0B00)
lsw = client.read_register(0x0B00)
msw = client.read_register(0x0B02)
value = (msw << 16) | lsw
degrees = value / 10.0
print(f"0x0B00: {degrees}°")
```

---

## ✅ Checklist de Validação

- [ ] Teste rápido ESP32 PASSOU (diferença < 0.2°)
- [ ] Escrever 3 ângulos diferentes (90°, 120°, 45°)
- [ ] Ler de volta os 3 ângulos
- [ ] Verificar área SCADA sincronizada
- [ ] Reiniciar ESP32 e verificar que CLP mantém valores

---

## 📝 Próximos Passos

Após validar ângulos:

1. Testar IHM Web completa (http://192.168.4.1)
2. Validar botões K0-K9, S1, S2
3. Validar leitura encoder
4. Validar LEDs de status
5. Teste de stress 24h

---

## 🆘 Suporte

Se encontrar problemas:

1. Capture logs do ESP32:
   ```bash
   screen -L /dev/ttyACM0 115200
   ```
   (salva em `screenlog.0`)

2. Execute teste completo:
   ```bash
   python3 test_angles_complete.py > teste_resultado.txt 2>&1
   ```

3. Compartilhe:
   - `screenlog.0` (logs ESP32)
   - `teste_resultado.txt` (resultado teste)
   - Foto da conexão RS485

---

**IMPORTANTE:** O código agora usa a arquitetura correta validada no ladder:

```
IHM → 0x0A00 (escrita) → trigger 0x0390 (coil) →
ROT5 copia → 0x0840 (oficial) → 0x0B00 (SCADA) → IHM lê
```

**Boa sorte com os testes!** 🚀
