# CONTROLE DE RPM VIA MODBUS - Adendo ROT5
## Mudança de Velocidade pela IHM Web

**Data**: 2025-11-10
**Adendo para**: `clp_FINAL_COM_ROT5.sup`

---

## 📋 RESUMO

Adiciona controle remoto de velocidade (RPM) da máquina via IHM Web, permitindo alternar entre as 3 classes de velocidade (5/10/15 rpm) sem precisar pressionar fisicamente K1+K7.

---

## 🎯 COMO FUNCIONA ATUALMENTE (IHM Física)

### Mudança de Velocidade Manual

Segundo o manual da máquina (NEOCOUDE-HD-15):

1. **Pré-requisito**: Sistema deve estar em **modo MANUAL**
2. **Comando**: Pressionar **K1 + K7 simultaneamente**
3. **Efeito**: Cicla entre as classes de velocidade
4. **Registro afetado**: **0900** (classe de velocidade)
5. **Valores possíveis**:
   - `1` = Classe 1 → 5 RPM
   - `2` = Classe 2 → 10 RPM
   - `3` = Classe 3 → 15 RPM

### Limitações

- ⚠️ Mudança de velocidade **APENAS em modo MANUAL**
- ⚠️ Requer pressionamento físico simultâneo de 2 teclas
- ⚠️ Cicla sequencialmente (não permite selecionar diretamente)

---

## 💡 SOLUÇÃO VIA MODBUS (2 Opções)

### OPÇÃO 1: Escrita Direta no Registro 0900 (RECOMENDADA)

#### Vantagens
- ✅ Mais simples e direto
- ✅ Permite selecionar velocidade específica sem ciclar
- ✅ Não requer modificação adicional no ladder
- ✅ Usa Modbus Function Code 0x06 (Preset Single Register) já suportado

#### Desvantagens
- ⚠️ Bypassa lógica de validação do ladder original
- ⚠️ Responsabilidade de verificar modo MANUAL fica no IHM Web

#### Implementação

**1. Verificar que está em modo MANUAL**:
```python
# Ler modo atual (shadow register 0A01)
modo = client.read_holding_registers(0x0A01, 1, slave=1).registers[0]

if modo != 0:  # 0 = MANUAL, 1 = AUTO
    print("❌ Erro: Mudança de velocidade só é permitida em modo MANUAL")
    return False
```

**2. Escrever novo valor no registro 0900**:
```python
from pymodbus.client import ModbusSerialClient

client = ModbusSerialClient(
    port='/dev/ttyUSB0',
    baudrate=57600,
    stopbits=2,
    parity='N',
    timeout=1
)

# Função para mudar velocidade
def mudar_velocidade(nova_classe):
    """
    Muda classe de velocidade da máquina

    Args:
        nova_classe (int): 1, 2 ou 3
            1 = 5 RPM
            2 = 10 RPM
            3 = 15 RPM

    Returns:
        bool: True se sucesso, False se falha
    """
    # Validar entrada
    if nova_classe not in [1, 2, 3]:
        print(f"❌ Classe inválida: {nova_classe}. Use 1, 2 ou 3")
        return False

    # Verificar modo MANUAL
    result = client.read_holding_registers(0x0A01, 1, slave=1)
    if result.isError():
        print("❌ Erro ao ler modo do sistema")
        return False

    modo = result.registers[0]
    if modo != 0:  # 0 = MANUAL
        print("❌ Mudança de velocidade só permitida em modo MANUAL")
        return False

    # Escrever novo valor no registro 0900
    result = client.write_register(0x0900, nova_classe, slave=1)

    if result.isError():
        print(f"❌ Erro ao escrever registro 0900: {result}")
        return False

    # Verificar se mudança foi aplicada
    time.sleep(0.2)
    result = client.read_holding_registers(0x0900, 1, slave=1)
    if not result.isError():
        velocidade_atual = result.registers[0]
        rpm_map = {1: 5, 2: 10, 3: 15}
        print(f"✅ Velocidade alterada para Classe {velocidade_atual} ({rpm_map[velocidade_atual]} RPM)")
        return True

    return False

# Exemplos de uso
mudar_velocidade(1)  # 5 RPM
mudar_velocidade(2)  # 10 RPM
mudar_velocidade(3)  # 15 RPM
```

**3. Espelhar velocidade atual no shadow register 0A03**:

O espelhamento JÁ ESTÁ IMPLEMENTADO na Line 24 do ROT5:
```ladder
Line 24: Copiar Classe de Velocidade (0900 → 0A03)
```

Portanto, após mudar a velocidade, você pode ler:
```python
# Ler velocidade atual (shadow register 0A03)
velocidade = client.read_holding_registers(0x0A03, 1, slave=1).registers[0]
print(f"Velocidade: Classe {velocidade}")  # 1, 2 ou 3
```

---

### OPÇÃO 2: Comando Modbus que Simula K1+K7

#### Vantagens
- ✅ Segue fluxo normal do ladder (mais seguro)
- ✅ Validações automáticas pelo programa original

#### Desvantagens
- ❌ Requer adicionar nova linha no ladder (Line 56 ou modificar existente)
- ❌ Cicla sequencialmente em vez de permitir seleção direta
- ❌ Mais complexo de implementar

#### Implementação (Requer Modificação do Ladder)

**Adicionar nova linha ao ROT5** (Line 56):
```ladder
[Line00056]
  [Features]
    Branchs:01
    Type:0
    Label:0
    Comment:SIMULAR K1+K7 MUDANCA VELOCIDADE
    Out:SETR    T:0043 Size:001 E:00A0  ; K1 HMI
    Height:01
  [Branch01]
    X1position:00
    X2position:13
    Yposition:00
    Height:01
    B1:00
    B2:00
    BInputnumber:00
    {0;00;03F9;-1;-1;-1;-1;00}  ; Novo bit: MB_MUDAR_VELOCIDADE (03F9 / 1017)
    Out:SETR    T:0043 Size:001 E:00A0  ; Ativa K1 HMI
    Out:SETR    T:0043 Size:001 E:00A6  ; Ativa K7 HMI
    Out:RESET   T:0042 Size:001 E:03F9  ; Auto-reset comando
    ###
```

**Código Python para usar**:
```python
def mudar_velocidade_via_k1k7():
    """Simula pressionamento simultâneo de K1+K7"""

    # Verificar modo MANUAL
    result = client.read_holding_registers(0x0A01, 1, slave=1)
    if result.registers[0] != 0:
        print("❌ Deve estar em modo MANUAL")
        return False

    # Enviar comando Modbus
    client.write_coil(1017, True, slave=1)  # MB_MUDAR_VELOCIDADE (03F9) = ON
    time.sleep(0.1)
    client.write_coil(1017, False, slave=1)  # MB_MUDAR_VELOCIDADE = OFF

    # Aguardar processamento
    time.sleep(0.3)

    # Ler velocidade nova
    velocidade = client.read_holding_registers(0x0A03, 1, slave=1).registers[0]
    rpm_map = {1: 5, 2: 10, 3: 15}
    print(f"✅ Nova velocidade: Classe {velocidade} ({rpm_map[velocidade]} RPM)")

    return True
```

⚠️ **NOTA**: Esta opção requer reabrir o .sup, adicionar Line 56 ao ROT4, e transferir novamente para o CLP.

---

## 🎯 RECOMENDAÇÃO: OPÇÃO 1

**Use a OPÇÃO 1** (escrita direta no registro 0900) porque:

1. ✅ **Não requer modificação adicional do ladder** - funciona imediatamente com `clp_FINAL_COM_ROT5.sup` atual
2. ✅ **Mais flexível** - permite ir diretamente para velocidade desejada sem ciclar
3. ✅ **Mais simples** - apenas 1 escrita de registro Modbus
4. ✅ **Shadow register já implementado** - 0A03 já espelha 0900 (Line 24)
5. ✅ **Modbus Function Code 0x06 já suportado** pelo MPC4004

---

## 📝 EXEMPLO COMPLETO: IHM WEB COM CONTROLE DE VELOCIDADE

### Backend (Python WebSocket Server)

```python
import asyncio
import websockets
import json
from pymodbus.client import ModbusSerialClient
import time

# Configurar cliente Modbus
modbus_client = ModbusSerialClient(
    port='/dev/ttyUSB0',
    baudrate=57600,
    stopbits=2,
    parity='N',
    timeout=1
)

def mudar_velocidade(nova_classe):
    """Muda velocidade da máquina (1=5rpm, 2=10rpm, 3=15rpm)"""
    try:
        # Verificar modo MANUAL
        result = modbus_client.read_holding_registers(0x0A01, 1, slave=1)
        if result.isError() or result.registers[0] != 0:
            return {'success': False, 'error': 'Modo MANUAL necessário'}

        # Escrever no registro 0900
        result = modbus_client.write_register(0x0900, nova_classe, slave=1)
        if result.isError():
            return {'success': False, 'error': 'Falha ao escrever registro'}

        # Confirmar mudança
        time.sleep(0.2)
        result = modbus_client.read_holding_registers(0x0A03, 1, slave=1)
        if not result.isError():
            velocidade_atual = result.registers[0]
            rpm = {1: 5, 2: 10, 3: 15}[velocidade_atual]
            return {
                'success': True,
                'classe': velocidade_atual,
                'rpm': rpm
            }

        return {'success': False, 'error': 'Falha ao verificar mudança'}

    except Exception as e:
        return {'success': False, 'error': str(e)}

async def handle_client(websocket, path):
    """Handler WebSocket"""
    async for message in websocket:
        try:
            data = json.loads(message)
            action = data.get('action')

            if action == 'mudar_velocidade':
                classe = data.get('classe')  # 1, 2 ou 3
                resultado = mudar_velocidade(classe)
                await websocket.send(json.dumps(resultado))

            elif action == 'ler_estado':
                # Ler estado completo incluindo velocidade
                result = modbus_client.read_holding_registers(0x0A01, 13, slave=1)
                if not result.isError():
                    shadow = result.registers
                    estado = {
                        'modo': 'AUTO' if shadow[0] == 1 else 'MANUAL',
                        'velocidade_classe': shadow[2],  # 0A03
                        'velocidade_rpm': {1: 5, 2: 10, 3: 15}[shadow[2]],
                        'dobra_atual': shadow[3],
                        'encoder': (shadow[11] << 16) | shadow[12]
                    }
                    await websocket.send(json.dumps({
                        'action': 'update_estado',
                        'data': estado
                    }))

        except Exception as e:
            await websocket.send(json.dumps({
                'success': False,
                'error': str(e)
            }))

# Iniciar servidor WebSocket
async def main():
    modbus_client.connect()
    server = await websockets.serve(handle_client, 'localhost', 8080)
    print("🚀 Servidor WebSocket rodando em ws://localhost:8080")
    await server.wait_closed()

if __name__ == '__main__':
    asyncio.run(main())
```

### Frontend (HTML/JavaScript)

```html
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>IHM Web - Dobradeira</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            padding: 20px;
            background: #1a1a1a;
            color: #fff;
        }
        .painel-velocidade {
            background: #2a2a2a;
            padding: 20px;
            border-radius: 10px;
            margin: 20px 0;
        }
        .botao-velocidade {
            width: 100px;
            height: 100px;
            margin: 10px;
            font-size: 18px;
            font-weight: bold;
            border-radius: 50%;
            border: 3px solid #555;
            background: #3a3a3a;
            color: #fff;
            cursor: pointer;
            transition: all 0.2s;
        }
        .botao-velocidade:hover {
            background: #4a4a4a;
            border-color: #0af;
        }
        .botao-velocidade.ativo {
            background: #0a0;
            border-color: #0f0;
            box-shadow: 0 0 20px #0f0;
        }
        .display-rpm {
            font-size: 48px;
            font-weight: bold;
            color: #0af;
            text-align: center;
            margin: 20px 0;
        }
        .status {
            padding: 10px;
            background: #333;
            border-radius: 5px;
            margin: 10px 0;
        }
    </style>
</head>
<body>
    <h1>🏭 IHM Web - Controle de Velocidade</h1>

    <div class="painel-velocidade">
        <h2>Velocidade do Motor</h2>

        <div class="display-rpm" id="displayRPM">-- RPM</div>

        <div class="status">
            <strong>Modo:</strong> <span id="modoAtual">--</span><br>
            <strong>Classe:</strong> <span id="classeAtual">--</span><br>
            <strong>Dobra:</strong> K<span id="dobraAtual">-</span>
        </div>

        <div style="text-align: center;">
            <button class="botao-velocidade" id="btn-vel-1" onclick="mudarVelocidade(1)">
                CLASSE 1<br>5 RPM
            </button>
            <button class="botao-velocidade" id="btn-vel-2" onclick="mudarVelocidade(2)">
                CLASSE 2<br>10 RPM
            </button>
            <button class="botao-velocidade" id="btn-vel-3" onclick="mudarVelocidade(3)">
                CLASSE 3<br>15 RPM
            </button>
        </div>

        <div id="mensagem" style="color: #0af; margin-top: 20px; text-align: center;"></div>
    </div>

    <script>
        let ws = null;

        // Conectar WebSocket
        function conectar() {
            ws = new WebSocket('ws://localhost:8080');

            ws.onopen = () => {
                console.log('✅ Conectado ao servidor');
                setInterval(atualizarEstado, 250);  // Atualizar a cada 250ms
            };

            ws.onmessage = (event) => {
                const data = JSON.parse(event.data);

                if (data.action === 'update_estado') {
                    atualizarInterface(data.data);
                } else if (data.success) {
                    mostrarMensagem(`✅ Velocidade alterada: ${data.rpm} RPM`, '#0a0');
                } else {
                    mostrarMensagem(`❌ Erro: ${data.error}`, '#f00');
                }
            };

            ws.onerror = () => {
                mostrarMensagem('❌ Erro de conexão', '#f00');
            };

            ws.onclose = () => {
                mostrarMensagem('⚠️ Desconectado - Tentando reconectar...', '#fa0');
                setTimeout(conectar, 2000);
            };
        }

        // Mudar velocidade
        function mudarVelocidade(classe) {
            if (!ws || ws.readyState !== WebSocket.OPEN) {
                mostrarMensagem('❌ WebSocket desconectado', '#f00');
                return;
            }

            ws.send(JSON.stringify({
                action: 'mudar_velocidade',
                classe: classe
            }));

            mostrarMensagem(`Enviando comando: Classe ${classe}...`, '#0af');
        }

        // Atualizar estado
        function atualizarEstado() {
            if (ws && ws.readyState === WebSocket.OPEN) {
                ws.send(JSON.stringify({ action: 'ler_estado' }));
            }
        }

        // Atualizar interface
        function atualizarInterface(estado) {
            document.getElementById('modoAtual').textContent = estado.modo;
            document.getElementById('classeAtual').textContent = estado.velocidade_classe;
            document.getElementById('dobraAtual').textContent = estado.dobra_atual;
            document.getElementById('displayRPM').textContent = estado.velocidade_rpm + ' RPM';

            // Destacar botão ativo
            for (let i = 1; i <= 3; i++) {
                const btn = document.getElementById(`btn-vel-${i}`);
                if (i === estado.velocidade_classe) {
                    btn.classList.add('ativo');
                } else {
                    btn.classList.remove('ativo');
                }
            }

            // Desabilitar botões se não estiver em modo MANUAL
            const desabilitar = estado.modo !== 'MANUAL';
            for (let i = 1; i <= 3; i++) {
                document.getElementById(`btn-vel-${i}`).disabled = desabilitar;
            }
        }

        // Mostrar mensagem
        function mostrarMensagem(msg, cor) {
            const elem = document.getElementById('mensagem');
            elem.textContent = msg;
            elem.style.color = cor;

            // Limpar após 3 segundos
            setTimeout(() => {
                elem.textContent = '';
            }, 3000);
        }

        // Conectar ao carregar página
        window.onload = conectar;
    </script>
</body>
</html>
```

---

## ⚠️ CONSIDERAÇÕES DE SEGURANÇA

### Validações Obrigatórias

1. **Verificar modo MANUAL**: SEMPRE verificar que bit 0A01 = 0 antes de permitir mudança
2. **Verificar sistema parado**: Ideal verificar que motor não está em movimento (S0 e S1 = OFF)
3. **Confirmar mudança**: Sempre ler 0A03 após escrever 0900 para confirmar
4. **Timeout**: Definir timeout de 500ms para operação
5. **Feedback visual**: IHM Web deve mostrar claramente modo atual e desabilitar botões se não estiver em MANUAL

### Fluxo Seguro Recomendado

```python
def mudar_velocidade_seguro(nova_classe):
    """Versão com todas as verificações de segurança"""

    # 1. Validar entrada
    if nova_classe not in [1, 2, 3]:
        return {'error': 'Classe inválida. Use 1, 2 ou 3'}

    # 2. Ler estado atual completo
    result = modbus_client.read_holding_registers(0x0A01, 20, slave=1)
    if result.isError():
        return {'error': 'Falha ao ler estado do CLP'}

    shadow = result.registers
    modo = shadow[0]          # 0A01: Modo
    velocidade_atual = shadow[2]  # 0A03: Velocidade

    # 3. Verificar modo MANUAL
    if modo != 0:
        return {'error': 'Mudança de velocidade só permitida em modo MANUAL'}

    # 4. Verificar se já está na velocidade desejada
    if velocidade_atual == nova_classe:
        return {
            'success': True,
            'message': f'Já está na classe {nova_classe}',
            'classe': nova_classe,
            'rpm': {1: 5, 2: 10, 3: 15}[nova_classe]
        }

    # 5. Escrever novo valor
    result = modbus_client.write_register(0x0900, nova_classe, slave=1)
    if result.isError():
        return {'error': 'Falha ao escrever registro 0900'}

    # 6. Aguardar e verificar
    time.sleep(0.3)
    result = modbus_client.read_holding_registers(0x0A03, 1, slave=1)
    if result.isError():
        return {'error': 'Falha ao verificar mudança'}

    velocidade_nova = result.registers[0]

    # 7. Confirmar sucesso
    if velocidade_nova == nova_classe:
        rpm = {1: 5, 2: 10, 3: 15}[nova_classe]
        return {
            'success': True,
            'message': f'Velocidade alterada com sucesso',
            'classe': nova_classe,
            'rpm': rpm
        }
    else:
        return {
            'error': f'Mudança falhou. Esperava classe {nova_classe}, obteve {velocidade_nova}'
        }
```

---

## 📊 RESUMO

| Aspecto | Detalhes |
|---------|----------|
| **Registro Modbus** | 0900 (2304 dec) - Classe de velocidade |
| **Shadow Register** | 0A03 (2563 dec) - Já implementado (Line 24) |
| **Valores válidos** | 1 = 5 RPM, 2 = 10 RPM, 3 = 15 RPM |
| **Function Code** | 0x06 (Preset Single Register) |
| **Pré-requisito** | Modo MANUAL (bit 0A01 = 0) |
| **Método recomendado** | OPÇÃO 1 (escrita direta) |
| **Modificação ladder** | Não necessária (usa .sup atual) |

---

## ✅ CHECKLIST DE IMPLEMENTAÇÃO

- [ ] Backend implementa função `mudar_velocidade(classe)`
- [ ] Frontend mostra botões para Classe 1, 2 e 3
- [ ] Botões desabilitados quando não estiver em modo MANUAL
- [ ] Display mostra RPM atual em tempo real
- [ ] Validação de modo MANUAL antes de enviar comando
- [ ] Confirmação de mudança via leitura de 0A03
- [ ] Feedback visual para usuário (mensagem de sucesso/erro)
- [ ] Timeout de 500ms para operação
- [ ] Log de mudanças de velocidade (opcional)
- [ ] Teste em bancada antes de instalar na máquina

---

**Status**: ✅ **PRONTO PARA IMPLEMENTAÇÃO**
**Método Recomendado**: OPÇÃO 1 (Escrita Direta)
**Arquivo Ladder**: `clp_FINAL_COM_ROT5.sup` (já inclui espelhamento 0A03)

---

**Autor**: Claude Code
**Data**: 2025-11-10
**Versão**: 1.0 - Controle de RPM via Modbus
