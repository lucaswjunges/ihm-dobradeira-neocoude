# APIs de Teste Modbus - ESP32

## 🎯 Objetivo

Criei novas APIs REST para testar comunicação Modbus diretamente via navegador/curl, sem precisar da interface web.

---

## 📤 Upload Necessário

**Arquivos para atualizar via Thonny:**

1. **`main.py`** - Contém as novas APIs de teste
2. **`static/index.html`** - Corrigido (data.connected, data.encoder_angle, etc.)

### Como fazer upload via Thonny:

```bash
thonny &
```

1. Tools → Options → Interpreter → MicroPython (ESP32) em `/dev/ttyACM0`
2. Abrir `/home/lucas-junges/Documents/clientes/w&co/ihm_esp32/main.py`
3. File → Save As → MicroPython device → `main.py` (substituir)
4. Abrir `/home/lucas-junges/Documents/clientes/w&co/ihm_esp32/static/index.html`
5. File → Save As → MicroPython device → `static/index.html` (substituir)
6. No console: CTRL+D (resetar)

---

## 🧪 APIs de Teste Disponíveis

### 1. **GET /api/test_modbus** - Teste Completo

Testa leitura do encoder e bend 1.

**Exemplo:**
```bash
curl http://192.168.0.106/api/test_modbus | python3 -m json.tool
```

**Resposta esperada:**
```json
{
    "connected": true,
    "encoder_test": {
        "success": false,        // Timeout normal se encoder não conectado
        "value": null,
        "degrees": 0
    },
    "bend1_test": {
        "success": true,
        "value": 450,            // Valor bruto (45.0 * 10)
        "degrees": 45.0          // ✅ Leitura OK!
    }
}
```

**Exemplo real (testado em 17/Nov/2025 22:50):**
- Bend 1 leu 45.0° com sucesso ✓
- Encoder timeout (CLP pode não estar enviando)

---

### 2. **GET /api/read_test?address=XXXX** - Ler Registro

Lê um registro Modbus específico.

**Exemplos:**

```bash
# Ler encoder MSW (1238 decimal)
curl "http://192.168.0.106/api/read_test?address=1238" | python3 -m json.tool

# Ler encoder LSW (1239 decimal)
curl "http://192.168.0.106/api/read_test?address=1239" | python3 -m json.tool

# Ler ângulo dobra 1 (1280 decimal)
curl "http://192.168.0.106/api/read_test?address=1280" | python3 -m json.tool

# Ler entrada digital E0 (256 decimal)
curl "http://192.168.0.106/api/read_test?address=256" | python3 -m json.tool
```

**Resposta esperada:**
```json
{
    "success": true,
    "address": 1280,
    "value": 450,
    "hex": "0x01C2"
}
```

**Exemplo real (Bend 1 = 45°):**
```json
{
    "success": true,
    "address": 1280,
    "value": 450,        // 45.0° (valor * 10)
    "hex": "0x01C2"      // 450 decimal = 0x01C2
}
```

---

### 3. **GET /api/write_test?address=XXXX&value=YYYY** - Escrever Registro

Escreve um valor em um registro Modbus.

**Exemplos:**

```bash
# Escrever 90° (900) na dobra 1
curl "http://192.168.0.106/api/write_test?address=1280&value=900" | python3 -m json.tool

# Escrever 120° (1200) na dobra 2
curl "http://192.168.0.106/api/write_test?address=1282&value=1200" | python3 -m json.tool

# Escrever 45° (450) na dobra 3
curl "http://192.168.0.106/api/write_test?address=1284&value=450" | python3 -m json.tool
```

**Resposta esperada:**
```json
{
    "success": true,
    "address": 1280,
    "value": 900,
    "message": "OK"
}
```

---

## 📋 Endereços Modbus Importantes

### Leitura (Holding Registers):

| Descrição | Endereço Decimal | Endereço Hex | Tipo |
|-----------|------------------|--------------|------|
| **Encoder MSW** | 1238 | 0x04D6 | 16-bit |
| **Encoder LSW** | 1239 | 0x04D7 | 16-bit |
| **Ângulo Dobra 1** | 1280 | 0x0500 | 16-bit |
| **Ângulo Dobra 2** | 1282 | 0x0502 | 16-bit |
| **Ângulo Dobra 3** | 1284 | 0x0504 | 16-bit |
| **Entrada E0** | 256 | 0x0100 | 16-bit (bit 0) |
| **Entrada E1** | 257 | 0x0101 | 16-bit (bit 0) |
| **Saída S0** | 384 | 0x0180 | 16-bit (bit 0) |
| **Saída S1** | 385 | 0x0181 | 16-bit (bit 0) |

### Escrita (Coils):

| Descrição | Endereço Decimal | Endereço Hex |
|-----------|------------------|--------------|
| **Tecla K1** | 160 | 0x00A0 |
| **Tecla K2** | 161 | 0x00A1 |
| **Tecla S1** | 220 | 0x00DC |
| **Tecla S2** | 221 | 0x00DD |
| **ENTER** | 37 | 0x0025 |
| **ESC** | 188 | 0x00BC |

---

## 🧪 Testes de Diagnóstico

### Teste 1: Verificar Comunicação Básica

```bash
curl http://192.168.0.106/api/test_modbus | python3 -m json.tool
```

**Se retornar `"connected": true"`:**
✅ Modbus está funcionando!

**Se retornar `"connected": false"`:**
❌ Problema de comunicação

---

### Teste 2: Ler Encoder Completo (32-bit)

```bash
# Ler MSW
MSW=$(curl -s "http://192.168.0.106/api/read_test?address=1238" | python3 -c "import sys,json; print(json.load(sys.stdin)['value'])")

# Ler LSW
LSW=$(curl -s "http://192.168.0.106/api/read_test?address=1239" | python3 -c "import sys,json; print(json.load(sys.stdin)['value'])")

# Combinar
echo "Encoder: MSW=$MSW, LSW=$LSW"
python3 -c "print(f'Ângulo: {(($MSW << 16) | $LSW) / 10.0}°')"
```

---

### Teste 3: Escrever e Verificar Ângulo

```bash
# Escrever 90°
curl "http://192.168.0.106/api/write_test?address=1280&value=900"

# Aguardar 1 segundo
sleep 1

# Ler de volta
curl "http://192.168.0.106/api/read_test?address=1280"
```

**Resultado esperado:**
- Escrita: `"success": true, "message": "OK"`
- Leitura: `"value": 1200` (confirma que foi escrito)

**Exemplo real (testado):**
```bash
# Escrever 120° (1200)
curl "http://192.168.0.106/api/write_test?address=1280&value=1200"
# Resposta: {"success": true, "value": 1200, "message": "OK"}

# Ler de volta
curl "http://192.168.0.106/api/read_test?address=1280"
# Resposta: {"success": true, "value": 1200, "hex": "0x04B0"}

# Verificar no /api/state
curl http://192.168.0.106/api/state
# Resposta: {"bend_1_angle": 120.0, ...}
```

✅ **ESCRITA MODBUS CONFIRMADA FUNCIONANDO!**

---

## 🐛 Troubleshooting

### Se `/api/test_modbus` retornar erro:

```json
{
    "encoder_test": {
        "success": false,
        "error": "timeout"
    }
}
```

**Causa:** CLP não está respondendo
**Solução:** Verificar fiação, replugue cabos

---

### Se `/api/write_test` retornar `"success": false`:

**Causas possíveis:**
1. Registro é read-only
2. CLP não aceitou a escrita
3. Timeout Modbus

---

## 📝 Correção do index.html

**Mudanças aplicadas:**

```javascript
// ANTES (ERRADO):
if (data.modbus_connected !== undefined) {
    updateStatus('clp', data.modbus_connected);
}
if (data.encoder_degrees !== undefined) {
    ...
}

// DEPOIS (CORRETO):
if (data.connected !== undefined) {
    updateStatus('clp', data.connected);
}
if (data.encoder_angle !== undefined) {
    ...
}
```

**Após upload do index.html corrigido:**
- ✅ "CLP ✓" deve ficar VERDE quando `connected: true`
- ✅ Encoder deve mostrar valor correto
- ✅ Ângulos devem atualizar

---

## 🎯 Checklist de Teste

Após fazer upload via Thonny:

- [ ] Acessar `http://192.168.0.106/api/test_modbus`
- [ ] Verificar `"connected": true"`
- [ ] Testar leitura: `/api/read_test?address=1238`
- [ ] Testar escrita: `/api/write_test?address=1280&value=900`
- [ ] Acessar interface web: `http://192.168.0.106`
- [ ] Verificar se "CLP ✓" está VERDE
- [ ] Verificar se encoder atualiza

---

**Data:** 18/Novembro/2025
**Versão:** 2.0-MODBUS-TEST-API
