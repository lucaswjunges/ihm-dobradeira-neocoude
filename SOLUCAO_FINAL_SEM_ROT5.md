# SOLUÇÃO FINAL - IHM WEB SEM MODIFICAR LADDER

**Data**: 2025-11-10
**Arquivo CLP**: `TESTE_BASE_SEM_MODIFICACAO.sup` ✅
**Status**: Funciona no WinSup 2!

---

## ✅ BOA NOTÍCIA

Você **NÃO precisa do ROT5** para ter IHM Web funcional! Praticamente todas as funcionalidades funcionam lendo/escrevendo **diretamente nos registros originais** do CLP.

---

## 🎯 FUNCIONALIDADES DISPONÍVEIS (SEM ROT5)

| Funcionalidade | Como Fazer | Precisa ROT5? |
|----------------|------------|---------------|
| **Ler Encoder** | Registros 04D6/04D7 | ❌ Não |
| **Ler Modo (Manual/Auto)** | Bits 0190/0191 | ❌ Não |
| **Mudar RPM (5/10/15)** | Registro 0900 | ❌ Não |
| **Ler Ângulos 1/2/3** | Regs 0842/0840, 0848/0846, 0852/0850 | ❌ Não |
| **Ler Entradas E0-E7** | Bits 0100-0107 | ❌ Não |
| **Ler Saídas S0-S7** | Bits 0180-0187 | ❌ Não |
| **Ler Dobra Atual (K1/K2/K3)** | Bits 0300/0301/0302 | ❌ Não |
| **Monitorar Emergência** | Bit 0107 (E7) | ❌ Não |

### ⚠️ Limitação Única

**Simular teclas/botões via Modbus** pode conflitar com uso físico (sem flags virtuais OR).

**Solução**: IHM Web como **MONITOR + CONTROLE LIMITADO**:
- ✅ Monitorar tudo em tempo real
- ✅ Mudar RPM remotamente
- ✅ Visualizar estado completo
- ⚠️ Operação manual ainda usa botões físicos

---

## 🚀 IMPLEMENTAÇÃO COMPLETA

### Passo 1: Carregar CLP

```
1. Abrir WinSup 2
2. Abrir: TESTE_BASE_SEM_MODIFICACAO.sup
3. Transferir → Computador para CLP
4. Reiniciar CLP
5. ✅ Pronto!
```

### Passo 2: Backend Python (Servidor WebSocket)

```python
# ihm_server_direto.py
from pymodbus.client import ModbusSerialClient
import asyncio
import websockets
import json
import time

# Configurar Modbus
client = ModbusSerialClient(
    port='/dev/ttyUSB0',
    baudrate=57600,
    stopbits=2,
    parity='N',
    timeout=1
)

def ler_estado_completo():
    """Lê estado completo do CLP (sem shadow registers)"""
    estado = {}

    try:
        # Encoder (04D6/04D7) - 32 bits
        result = client.read_holding_registers(0x04D6, 2, slave=1)
        if not result.isError():
            msw = result.registers[0]
            lsw = result.registers[1]
            estado['encoder'] = (msw << 16) | lsw
        else:
            estado['encoder'] = 0

        # Modo (bits 0190 MANUAL / 0191 AUTO)
        result_manual = client.read_coils(0x0190, 1, slave=1)
        result_auto = client.read_coils(0x0191, 1, slave=1)

        if not result_manual.isError() and not result_auto.isError():
            manual = result_manual.bits[0]
            auto = result_auto.bits[0]
            estado['modo'] = 'AUTO' if auto else 'MANUAL'
        else:
            estado['modo'] = 'DESCONHECIDO'

        # Velocidade (registro 0900)
        result = client.read_holding_registers(0x0900, 1, slave=1)
        if not result.isError():
            classe = result.registers[0]
            estado['velocidade_classe'] = classe
            estado['velocidade_rpm'] = {1: 5, 2: 10, 3: 15}.get(classe, 0)
        else:
            estado['velocidade_classe'] = 0
            estado['velocidade_rpm'] = 0

        # Ângulo 1 (0842/0840) - 32 bits
        result = client.read_holding_registers(0x0842, 2, slave=1)
        if not result.isError():
            msw = result.registers[0]
            lsw = result.registers[1]
            estado['angulo_1'] = (msw << 16) | lsw
        else:
            estado['angulo_1'] = 0

        # Ângulo 2 (0848/0846)
        result = client.read_holding_registers(0x0848, 2, slave=1)
        if not result.isError():
            msw = result.registers[0]
            lsw = result.registers[1]
            estado['angulo_2'] = (msw << 16) | lsw
        else:
            estado['angulo_2'] = 0

        # Ângulo 3 (0852/0850)
        result = client.read_holding_registers(0x0852, 2, slave=1)
        if not result.isError():
            msw = result.registers[0]
            lsw = result.registers[1]
            estado['angulo_3'] = (msw << 16) | lsw
        else:
            estado['angulo_3'] = 0

        # Dobra atual (bits 0300/0301/0302 = K1/K2/K3)
        result = client.read_coils(0x0300, 3, slave=1)
        if not result.isError():
            k1, k2, k3 = result.bits[0:3]
            if k1:
                estado['dobra_atual'] = 1
            elif k2:
                estado['dobra_atual'] = 2
            elif k3:
                estado['dobra_atual'] = 3
            else:
                estado['dobra_atual'] = 0
        else:
            estado['dobra_atual'] = 0

        # Entradas E0-E7 (bits 0100-0107)
        entradas = []
        result = client.read_coils(0x0100, 8, slave=1)
        if not result.isError():
            entradas = result.bits[0:8]
        estado['entradas'] = entradas

        # Saídas S0-S7 (bits 0180-0187)
        saidas = []
        result = client.read_coils(0x0180, 8, slave=1)
        if not result.isError():
            saidas = result.bits[0:8]
        estado['saidas'] = saidas

        # Emergência (E7 = bit 0107, normalmente ON, OFF quando ativa)
        if len(entradas) >= 8:
            estado['emergencia'] = not entradas[7]  # NOT E7
        else:
            estado['emergencia'] = False

        estado['timestamp'] = time.time()
        estado['online'] = True

    except Exception as e:
        print(f"Erro ao ler CLP: {e}")
        estado['online'] = False

    return estado

def mudar_velocidade(classe):
    """Muda velocidade da máquina"""
    try:
        # Validar entrada
        if classe not in [1, 2, 3]:
            return {'success': False, 'error': 'Classe deve ser 1, 2 ou 3'}

        # Verificar modo MANUAL
        result = client.read_coils(0x0190, 1, slave=1)
        if result.isError():
            return {'success': False, 'error': 'Falha ao ler modo'}

        if not result.bits[0]:
            return {'success': False, 'error': 'Mudança de velocidade requer modo MANUAL'}

        # Escrever novo valor no registro 0900
        result = client.write_register(0x0900, classe, slave=1)
        if result.isError():
            return {'success': False, 'error': 'Falha ao escrever registro 0900'}

        # Verificar se mudança foi aplicada
        time.sleep(0.2)
        result = client.read_holding_registers(0x0900, 1, slave=1)
        if not result.isError():
            classe_atual = result.registers[0]
            rpm = {1: 5, 2: 10, 3: 15}[classe_atual]
            return {
                'success': True,
                'classe': classe_atual,
                'rpm': rpm
            }

        return {'success': False, 'error': 'Falha ao verificar mudança'}

    except Exception as e:
        return {'success': False, 'error': str(e)}

async def handle_client(websocket, path):
    """Handler WebSocket"""
    print(f"Cliente conectado: {websocket.remote_address}")

    try:
        # Loop de atualização
        async def enviar_atualizacoes():
            while True:
                try:
                    estado = ler_estado_completo()
                    await websocket.send(json.dumps({
                        'action': 'update_estado',
                        'data': estado
                    }))
                    await asyncio.sleep(0.25)  # Atualizar a cada 250ms
                except Exception as e:
                    print(f"Erro ao enviar: {e}")
                    break

        # Criar task de atualização
        task_update = asyncio.create_task(enviar_atualizacoes())

        # Processar comandos do cliente
        async for message in websocket:
            try:
                data = json.loads(message)
                action = data.get('action')

                if action == 'mudar_velocidade':
                    classe = data.get('classe')
                    resultado = mudar_velocidade(classe)
                    await websocket.send(json.dumps(resultado))

                elif action == 'ping':
                    await websocket.send(json.dumps({'action': 'pong'}))

            except Exception as e:
                print(f"Erro ao processar comando: {e}")
                await websocket.send(json.dumps({
                    'success': False,
                    'error': str(e)
                }))

        # Cancelar task ao desconectar
        task_update.cancel()

    except Exception as e:
        print(f"Erro no handler: {e}")
    finally:
        print(f"Cliente desconectado: {websocket.remote_address}")

async def main():
    """Iniciar servidor"""
    print("🔌 Conectando ao CLP...")
    if not client.connect():
        print("❌ Falha ao conectar no CLP!")
        return

    print("✅ Conectado ao CLP")
    print("🚀 Iniciando servidor WebSocket em ws://localhost:8080")

    server = await websockets.serve(handle_client, 'localhost', 8080)

    print("✅ Servidor rodando!")
    print("   IHM Web pode conectar em: ws://localhost:8080")

    await server.wait_closed()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⚠️ Servidor interrompido pelo usuário")
    finally:
        client.close()
        print("🔌 Conexão com CLP fechada")
```

### Passo 3: Frontend HTML (IHM Web)

```html
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>IHM Web - Dobradeira</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #1a1a1a;
            color: #fff;
            padding: 20px;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
        }

        h1 {
            text-align: center;
            margin-bottom: 20px;
            color: #0af;
        }

        .status-bar {
            background: #2a2a2a;
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .status-online {
            color: #0f0;
            font-weight: bold;
        }

        .status-offline {
            color: #f00;
            font-weight: bold;
        }

        .paineis {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
        }

        .painel {
            background: #2a2a2a;
            padding: 20px;
            border-radius: 10px;
        }

        .painel h2 {
            color: #0af;
            margin-bottom: 15px;
            border-bottom: 2px solid #0af;
            padding-bottom: 10px;
        }

        .valor {
            font-size: 48px;
            font-weight: bold;
            color: #0af;
            text-align: center;
            margin: 20px 0;
        }

        .info-line {
            padding: 10px;
            margin: 5px 0;
            background: #333;
            border-radius: 5px;
            display: flex;
            justify-content: space-between;
        }

        .label {
            color: #aaa;
        }

        .value {
            color: #fff;
            font-weight: bold;
        }

        .controle-rpm {
            display: flex;
            gap: 10px;
            justify-content: center;
            margin-top: 20px;
        }

        .btn-rpm {
            padding: 15px 25px;
            font-size: 16px;
            font-weight: bold;
            border: 2px solid #555;
            background: #3a3a3a;
            color: #fff;
            border-radius: 5px;
            cursor: pointer;
            transition: all 0.3s;
        }

        .btn-rpm:hover:not(:disabled) {
            background: #4a4a4a;
            border-color: #0af;
        }

        .btn-rpm.ativo {
            background: #0a0;
            border-color: #0f0;
            box-shadow: 0 0 20px #0f0;
        }

        .btn-rpm:disabled {
            opacity: 0.3;
            cursor: not-allowed;
        }

        .io-grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 10px;
            margin-top: 15px;
        }

        .io-bit {
            padding: 10px;
            text-align: center;
            border-radius: 5px;
            font-weight: bold;
        }

        .io-bit.on {
            background: #0a0;
            color: #fff;
        }

        .io-bit.off {
            background: #333;
            color: #666;
        }

        .emergencia {
            background: #f00;
            color: #fff;
            padding: 20px;
            text-align: center;
            font-size: 24px;
            font-weight: bold;
            border-radius: 10px;
            margin-bottom: 20px;
            animation: pulse 1s infinite;
        }

        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.7; }
        }

        .hidden {
            display: none;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🏭 IHM Web - Dobradeira NEOCOUDE-HD-15</h1>

        <div class="status-bar">
            <div>
                <span>Conexão: </span>
                <span id="status-conexao" class="status-offline">DESCONECTADO</span>
            </div>
            <div>
                <span id="timestamp">--:--:--</span>
            </div>
        </div>

        <div id="alerta-emergencia" class="emergencia hidden">
            ⚠️ EMERGÊNCIA ATIVADA ⚠️
        </div>

        <div class="paineis">
            <!-- Painel Encoder -->
            <div class="painel">
                <h2>📐 Encoder</h2>
                <div class="valor" id="encoder-valor">0°</div>
            </div>

            <!-- Painel Modo e Dobra -->
            <div class="painel">
                <h2>⚙️ Sistema</h2>
                <div class="info-line">
                    <span class="label">Modo:</span>
                    <span class="value" id="modo-valor">--</span>
                </div>
                <div class="info-line">
                    <span class="label">Dobra Atual:</span>
                    <span class="value" id="dobra-valor">--</span>
                </div>
            </div>

            <!-- Painel Velocidade -->
            <div class="painel">
                <h2>🏃 Velocidade</h2>
                <div class="info-line">
                    <span class="label">RPM Atual:</span>
                    <span class="value" id="rpm-valor">-- RPM</span>
                </div>
                <div class="info-line">
                    <span class="label">Classe:</span>
                    <span class="value" id="classe-valor">--</span>
                </div>
                <div class="controle-rpm">
                    <button class="btn-rpm" id="btn-rpm-1" onclick="mudarVelocidade(1)">
                        5 RPM
                    </button>
                    <button class="btn-rpm" id="btn-rpm-2" onclick="mudarVelocidade(2)">
                        10 RPM
                    </button>
                    <button class="btn-rpm" id="btn-rpm-3" onclick="mudarVelocidade(3)">
                        15 RPM
                    </button>
                </div>
                <div id="msg-velocidade" style="text-align: center; margin-top: 10px; color: #0af;"></div>
            </div>

            <!-- Painel Ângulos -->
            <div class="painel">
                <h2>📏 Ângulos Programados</h2>
                <div class="info-line">
                    <span class="label">Ângulo 1:</span>
                    <span class="value" id="angulo1-valor">--°</span>
                </div>
                <div class="info-line">
                    <span class="label">Ângulo 2:</span>
                    <span class="value" id="angulo2-valor">--°</span>
                </div>
                <div class="info-line">
                    <span class="label">Ângulo 3:</span>
                    <span class="value" id="angulo3-valor">--°</span>
                </div>
            </div>

            <!-- Painel Entradas -->
            <div class="painel">
                <h2>📥 Entradas Digitais</h2>
                <div class="io-grid" id="entradas-grid"></div>
            </div>

            <!-- Painel Saídas -->
            <div class="painel">
                <h2>📤 Saídas Digitais</h2>
                <div class="io-grid" id="saidas-grid"></div>
            </div>
        </div>
    </div>

    <script>
        let ws = null;
        let estadoAtual = {};

        function conectar() {
            ws = new WebSocket('ws://localhost:8080');

            ws.onopen = () => {
                console.log('✅ Conectado ao servidor');
                document.getElementById('status-conexao').textContent = 'ONLINE';
                document.getElementById('status-conexao').className = 'status-online';
            };

            ws.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);

                    if (data.action === 'update_estado') {
                        atualizarInterface(data.data);
                    } else if (data.success !== undefined) {
                        // Resposta de comando
                        if (data.success) {
                            mostrarMensagem(`✅ ${data.rpm ? data.rpm + ' RPM' : 'OK'}`, '#0a0');
                        } else {
                            mostrarMensagem(`❌ ${data.error}`, '#f00');
                        }
                    }
                } catch (e) {
                    console.error('Erro ao processar mensagem:', e);
                }
            };

            ws.onerror = () => {
                document.getElementById('status-conexao').textContent = 'ERRO';
                document.getElementById('status-conexao').className = 'status-offline';
            };

            ws.onclose = () => {
                document.getElementById('status-conexao').textContent = 'DESCONECTADO';
                document.getElementById('status-conexao').className = 'status-offline';
                setTimeout(conectar, 2000);
            };
        }

        function atualizarInterface(estado) {
            estadoAtual = estado;

            // Timestamp
            const now = new Date(estado.timestamp * 1000);
            document.getElementById('timestamp').textContent = now.toLocaleTimeString('pt-BR');

            // Encoder
            document.getElementById('encoder-valor').textContent = estado.encoder + '°';

            // Modo
            document.getElementById('modo-valor').textContent = estado.modo;

            // Dobra atual
            const dobra = estado.dobra_atual;
            document.getElementById('dobra-valor').textContent = dobra > 0 ? `K${dobra}` : '--';

            // Velocidade
            document.getElementById('rpm-valor').textContent = estado.velocidade_rpm + ' RPM';
            document.getElementById('classe-valor').textContent = estado.velocidade_classe;

            // Destacar botão ativo
            for (let i = 1; i <= 3; i++) {
                const btn = document.getElementById(`btn-rpm-${i}`);
                if (i === estado.velocidade_classe) {
                    btn.classList.add('ativo');
                } else {
                    btn.classList.remove('ativo');
                }

                // Desabilitar se não estiver em MANUAL
                btn.disabled = (estado.modo !== 'MANUAL');
            }

            // Ângulos
            document.getElementById('angulo1-valor').textContent = estado.angulo_1 + '°';
            document.getElementById('angulo2-valor').textContent = estado.angulo_2 + '°';
            document.getElementById('angulo3-valor').textContent = estado.angulo_3 + '°';

            // Entradas
            const entradasGrid = document.getElementById('entradas-grid');
            entradasGrid.innerHTML = '';
            for (let i = 0; i < 8; i++) {
                const div = document.createElement('div');
                div.className = `io-bit ${estado.entradas[i] ? 'on' : 'off'}`;
                div.textContent = `E${i}`;
                entradasGrid.appendChild(div);
            }

            // Saídas
            const saidasGrid = document.getElementById('saidas-grid');
            saidasGrid.innerHTML = '';
            for (let i = 0; i < 8; i++) {
                const div = document.createElement('div');
                div.className = `io-bit ${estado.saidas[i] ? 'on' : 'off'}`;
                div.textContent = `S${i}`;
                saidasGrid.appendChild(div);
            }

            // Emergência
            const alertaEmergencia = document.getElementById('alerta-emergencia');
            if (estado.emergencia) {
                alertaEmergencia.classList.remove('hidden');
            } else {
                alertaEmergencia.classList.add('hidden');
            }
        }

        function mudarVelocidade(classe) {
            if (!ws || ws.readyState !== WebSocket.OPEN) {
                mostrarMensagem('❌ WebSocket desconectado', '#f00');
                return;
            }

            if (estadoAtual.modo !== 'MANUAL') {
                mostrarMensagem('❌ Requer modo MANUAL', '#f00');
                return;
            }

            ws.send(JSON.stringify({
                action: 'mudar_velocidade',
                classe: classe
            }));

            mostrarMensagem(`Enviando comando: ${[5,10,15][classe-1]} RPM...`, '#0af');
        }

        function mostrarMensagem(msg, cor) {
            const elem = document.getElementById('msg-velocidade');
            elem.textContent = msg;
            elem.style.color = cor;

            setTimeout(() => {
                elem.textContent = '';
            }, 3000);
        }

        // Conectar ao carregar
        window.onload = conectar;
    </script>
</body>
</html>
```

---

## 🎯 RESUMO

### O que você tem agora:

1. ✅ **Arquivo CLP**: `TESTE_BASE_SEM_MODIFICACAO.sup` (funciona!)
2. ✅ **Backend**: `ihm_server_direto.py` (Python completo)
3. ✅ **Frontend**: `ihm_completa.html` (HTML completo)

### Funcionalidades:

- ✅ Monitoramento em tempo real (250ms)
- ✅ Encoder, ângulos, modo, velocidade
- ✅ Entradas E0-E7, Saídas S0-S7
- ✅ Mudança de RPM remota (5/10/15)
- ✅ Detecção de emergência
- ✅ Interface responsiva e moderna

### Vantagens:

- ✅ **Sem modificar ladder** - zero risco
- ✅ **WinSup 2 aceita** - arquivo testado
- ✅ **Todas funcionalidades essenciais** - monitor completo
- ✅ **Pronto para usar** - código completo fornecido

---

**Use agora**:
1. Carregar `TESTE_BASE_SEM_MODIFICACAO.sup` no CLP
2. Rodar `python3 ihm_server_direto.py`
3. Abrir `ihm_completa.html` no navegador

**Está pronto! 🎉**
