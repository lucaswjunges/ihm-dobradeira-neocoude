# Teste Simples - Verificar Comunicação Modbus

## 🎯 Objetivo

Verificar se o ESP32 está conseguindo comunicar com o CLP após inverter A/B de volta.

## 📱 Método Mais Simples: Usar a Interface Web

### Passo 1: Descobrir IP do ESP32

O IP pode ter mudado. Verificar nos logs:

```bash
screen /dev/ttyACM0 115200
```

Procurar por:
- `Acesse: http://192.168.0.XXX` (modo STA)
- ou `Acesse: http://192.168.4.1` (modo AP)

**Para sair do screen:** CTRL+A depois K

### Passo 2: Acessar Interface

Abrir navegador em:
- `http://192.168.0.106` (IP antigo)
- ou `http://192.168.0.132` (IP novo detectado)
- ou `http://192.168.4.1` (modo AP)

### Passo 3: Verificar Indicador CLP

Olhar canto superior direito:

- **"CLP ✓"** em VERDE = ✅ MODBUS FUNCIONANDO!
- **"CLP ✗"** em VERMELHO = ❌ Sem comunicação

### Passo 4: Verificar Valores

Se CLP estiver verde:
- Encoder deve mostrar valor real (ex: 36.5°)
- Ângulos devem mostrar valores configurados

Se CLP estiver vermelho:
- Encoder mostra 0.0°
- Todos valores em 0.0

---

## 🔧 Alternativa: Testar via Curl

```bash
# Testar IP antigo
curl -s http://192.168.0.106/api/state | python3 -m json.tool

# Testar IP novo
curl -s http://192.168.0.132/api/state | python3 -m json.tool

# Testar modo AP
curl -s http://192.168.4.1/api/state | python3 -m json.tool
```

**Resultado esperado se funcionando:**
```json
{
    "connected": true,  // ✅ CLP respondendo!
    "encoder_angle": 36.5,
    "bend_1_angle": 90.0,
    "bend_2_angle": 120.0,
    "bend_3_angle": 56.0
}
```

**Resultado se NÃO funcionando:**
```json
{
    "connected": false,  // ❌ CLP não responde
    "encoder_angle": 0.0,
    "bend_1_angle": 0.0,
    "bend_2_angle": 0.0
}
```

---

## 📊 Resumo de Testes Feitos

### Tentativa 1: A/B Original
- Resultado: `connected: false`
- Valores estranhos (lixo de memória)

### Tentativa 2: A/B Invertidos
- Resultado: `connected: false`
- Valores em 0.0 (melhor, mas ainda sem comunicação)

### Tentativa 3: A/B Voltou Original
- **EM TESTE AGORA**
- Aguardando verificação

---

## 🎯 O Que Fazer Baseado no Resultado

### Se `connected: true` ✅
**SUCESSO! Modbus funcionando!**

- A/B está correto na posição ORIGINAL
- CLP está respondendo
- Sistema pronto para uso

### Se `connected: false` ❌
**Ainda não funciona.**

Possíveis causas:
1. **State 00BE = OFF no CLP** ⭐ MAIS PROVÁVEL
2. Slave ID errado (não é 1)
3. Baudrate errado (não é 57600)
4. MAX485 sem alimentação ou defeituoso
5. Cabo RS485 com problema

---

## 🆘 Se Continuar Falhando

### Teste com mbpoll (via PC):

```bash
# Conectar USB-RS485 no PC
# Testar diretamente do PC para o CLP

mbpoll -a 1 -r 1238 -c 2 -t 4 -b 57600 /dev/ttyUSB0
```

**Se funcionar do PC mas não do ESP32:**
- Problema no MAX485 ou conexão ESP32↔MAX485

**Se não funcionar do PC:**
- Problema no CLP (state 00BE) ou cabo RS485

---

**Por favor, verifique a interface web e me informe:**
- Qual o IP do ESP32?
- O indicador "CLP" está verde ou vermelho?
- Quais valores aparecem?
