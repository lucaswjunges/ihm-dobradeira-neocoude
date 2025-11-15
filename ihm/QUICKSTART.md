# 🚀 Início Rápido - IHM Web

## Instalação (1 minuto)

```bash
cd /home/lucas-junges/Documents/clientes/w\&co/ihm

# Instalar dependências
pip3 install -r requirements.txt
```

## Teste IMEDIATO (sem CLP)

```bash
# Inicia servidor em modo STUB (simulação)
python3 main_server.py --stub

# Abra no navegador:
# http://localhost:8080
```

✅ **Deve funcionar**: Encoder simulado, teclado virtual, ângulos pré-carregados

---

## Teste com CLP Real

### 1. Verificar Hardware

```bash
# Listar portas seriais
ls -l /dev/ttyUSB*

# Deve aparecer: /dev/ttyUSB0 ou /dev/ttyUSB1
```

### 2. Testar Comunicação

```bash
cd tests

# Teste completo
python3 test_modbus.py

# Esperado:
# ✓ Estado 00BE: ON
# ✓ Encoder: XX.X°
# ✓ Dobra 1/2/3: valores
```

### 3. Iniciar IHM Web

```bash
# Voltar para pasta ihm/
cd ..

# Iniciar servidor (modo LIVE)
python3 main_server.py --port /dev/ttyUSB0

# Abrir no navegador:
# http://localhost:8080
```

---

## Problemas Comuns

### ❌ "Permission denied: /dev/ttyUSB0"

```bash
# Adicionar usuário ao grupo dialout
sudo usermod -a -G dialout $USER

# IMPORTANTE: Fazer logout e login novamente
```

### ❌ "FALHA CLP" na interface

```bash
# Verificar estado 00BE
python3 -c "
from modbus_client import ModbusClientWrapper
c = ModbusClientWrapper()
print('Estado 00BE:', c.read_coil(0x00BE))
"

# Deve retornar: True
# Se False → ativar estado 0190 no ladder
```

### ❌ WebSocket não conecta

```bash
# Verificar se servidor está rodando
ps aux | grep main_server

# Verificar portas
lsof -i :8765
lsof -i :8080
```

---

## Próximos Passos

1. ✅ Testar teclado virtual (clicar nos botões)
2. ✅ Verificar encoder atualizando em tempo real
3. ✅ Editar ângulo (duplo clique + ENTER)
4. ✅ Testar K1+K7 para mudar velocidade

---

## 📖 Documentação Completa

- **README.md** - Instruções detalhadas
- **CLAUDE.md** - Documentação técnica para desenvolvimento
- **tests/** - Scripts de validação

---

**Dúvidas?** Consulte `README.md` ou `CLAUDE.md`
