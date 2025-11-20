#!/usr/bin/env python3
"""
Script de Teste: Sincronização de Tela IHM Física ↔ IHM Web
Valida se o registro 0x0860 espelha corretamente a tela atual

Requer: Ladder modificado já gravado no CLP
"""

import sys
import time
from pymodbus.client import ModbusSerialClient
from typing import Optional

# Configuração Modbus
PORT = '/dev/ttyUSB0'
BAUDRATE = 57600
PARITY = 'N'
STOPBITS = 2
BYTESIZE = 8
SLAVE_ID = 1

# Mapeamento de telas
TELAS = {
    0: "Inicial/Boot",
    1: "Standby",
    2: "Seleção AUTO/MANUAL",
    3: "Deslocamento Angular",
    4: "Ajuste Ângulo 01",
    5: "Ajuste Ângulo 02",
    6: "Ajuste Ângulo 03",
    7: "Diagnóstico 1",
    8: "Diagnóstico 2",
    9: "Diagnóstico 3",
    10: "Configuração Velocidade",
}

# Mapeamento de teclas → telas esperadas
TECLA_PARA_TELA = {
    'K1': 4,  # 0x00A0 (160)
    'K2': 5,  # 0x00A1 (161)
    'K3': 6,  # 0x00A2 (162)
    'K7': 7,  # 0x00A6 (166)
    'K8': 8,  # 0x00A7 (167)
    'K9': 9,  # 0x00A8 (168)
}

TECLAS_COILS = {
    'K0': 0x00A9,  # 169
    'K1': 0x00A0,  # 160
    'K2': 0x00A1,  # 161
    'K3': 0x00A2,  # 162
    'K4': 0x00A3,  # 163
    'K5': 0x00A4,  # 164
    'K6': 0x00A5,  # 165
    'K7': 0x00A6,  # 166
    'K8': 0x00A7,  # 167
    'K9': 0x00A8,  # 168
    'S1': 0x00DC,  # 220
    'S2': 0x00DD,  # 221
}


class TestadorSincronizacaoIHM:
    def __init__(self):
        self.client: Optional[ModbusSerialClient] = None
        self.testes_ok = 0
        self.testes_falha = 0

    def conectar(self) -> bool:
        """Conecta ao CLP via RS485"""
        print(f"🔌 Conectando ao CLP em {PORT}...")
        print(f"   Baudrate: {BAUDRATE}, Parity: {PARITY}, Stop bits: {STOPBITS}\n")

        self.client = ModbusSerialClient(
            port=PORT,
            baudrate=BAUDRATE,
            parity=PARITY,
            stopbits=STOPBITS,
            bytesize=BYTESIZE,
            timeout=2
        )

        if self.client.connect():
            print("✅ Conectado ao CLP\n")
            return True
        else:
            print("❌ ERRO: Não foi possível conectar ao CLP\n")
            return False

    def ler_tela_atual(self) -> Optional[int]:
        """Lê o registro 0x0860 (tela atual)"""
        try:
            response = self.client.read_holding_registers(
                address=0x0860,  # 2144 decimal
                count=1,
                device_id=SLAVE_ID
            )

            if not response.isError():
                return response.registers[0]
            else:
                print(f"  ✗ Erro ao ler registro 0860: {response}")
                return None
        except Exception as e:
            print(f"  ✗ Exceção ao ler 0860: {e}")
            return None

    def pressionar_tecla(self, tecla: str) -> bool:
        """Simula pressão de tecla (pulso 100ms)"""
        if tecla not in TECLAS_COILS:
            print(f"  ⚠️  Tecla '{tecla}' não reconhecida")
            return False

        coil_addr = TECLAS_COILS[tecla]

        try:
            # ON
            self.client.write_coil(address=coil_addr, value=True, device_id=SLAVE_ID)
            time.sleep(0.1)
            # OFF
            self.client.write_coil(address=coil_addr, value=False, device_id=SLAVE_ID)
            return True
        except Exception as e:
            print(f"  ✗ Erro ao pressionar {tecla}: {e}")
            return False

    def testar_leitura_inicial(self):
        """Teste 1: Verifica se registro 0860 é legível"""
        print("=" * 70)
        print("TESTE 1: Leitura do Registro 0x0860")
        print("=" * 70)

        tela = self.ler_tela_atual()

        if tela is not None:
            print(f"✅ Registro 0x0860 é LEGÍVEL")
            print(f"   Valor atual: {tela} ({TELAS.get(tela, 'Desconhecida')})")
            self.testes_ok += 1
            return True
        else:
            print(f"❌ FALHA: Registro 0x0860 não pôde ser lido")
            print(f"   → Verifique se a modificação do ladder foi gravada no CLP")
            self.testes_falha += 1
            return False

    def testar_mudanca_por_tecla(self, tecla: str, tela_esperada: int):
        """Teste 2: Verifica se pressionar tecla atualiza 0860"""
        print("\n" + "=" * 70)
        print(f"TESTE: Pressionar {tecla} → Tela {tela_esperada}")
        print("=" * 70)

        # Ler estado inicial
        print(f"\n📖 Estado ANTES de pressionar {tecla}:")
        tela_antes = self.ler_tela_atual()
        if tela_antes is not None:
            print(f"   Tela atual: {tela_antes} ({TELAS.get(tela_antes, 'Desconhecida')})")

        # Simular tecla
        print(f"\n⌨️  Pressionando {tecla} (pulso 100ms)...")
        if not self.pressionar_tecla(tecla):
            print(f"❌ FALHA ao simular tecla {tecla}")
            self.testes_falha += 1
            return False

        # Aguardar processamento do ladder
        time.sleep(0.5)

        # Ler estado final
        print(f"\n📖 Estado DEPOIS de pressionar {tecla}:")
        tela_depois = self.ler_tela_atual()

        if tela_depois is None:
            print(f"❌ FALHA: Não foi possível ler tela após tecla")
            self.testes_falha += 1
            return False

        print(f"   Tela atual: {tela_depois} ({TELAS.get(tela_depois, 'Desconhecida')})")

        # Validar resultado
        if tela_depois == tela_esperada:
            print(f"\n✅ SUCESSO! Tela mudou corretamente: {tela_antes} → {tela_depois}")
            print(f"   → Sincronização funcionando!")
            self.testes_ok += 1
            return True
        else:
            print(f"\n❌ FALHA! Tela esperada: {tela_esperada}, obtida: {tela_depois}")
            print(f"   → Lógica do ladder pode estar incorreta")
            self.testes_falha += 1
            return False

    def testar_todas_teclas(self):
        """Teste completo: todas as teclas mapeadas"""
        print("\n" + "=" * 70)
        print("TESTE COMPLETO: Navegação por Todas as Teclas")
        print("=" * 70)

        for tecla, tela_esperada in TECLA_PARA_TELA.items():
            self.testar_mudanca_por_tecla(tecla, tela_esperada)
            time.sleep(1)  # Pausa entre testes

    def testar_monitoramento_continuo(self, duracao_segundos=30):
        """Teste 4: Monitoramento contínuo (para teste manual)"""
        print("\n" + "=" * 70)
        print(f"TESTE: Monitoramento Contínuo ({duracao_segundos}s)")
        print("=" * 70)
        print("\n💡 Pressione teclas na IHM física e observe a sincronização\n")

        tela_anterior = None
        inicio = time.time()

        while (time.time() - inicio) < duracao_segundos:
            tela_atual = self.ler_tela_atual()

            if tela_atual is not None and tela_atual != tela_anterior:
                timestamp = time.strftime("%H:%M:%S")
                mudanca = f"{tela_anterior or '?'} → {tela_atual}"
                print(f"[{timestamp}] Tela mudou: {mudanca} ({TELAS.get(tela_atual, 'Desconhecida')})")
                tela_anterior = tela_atual

            time.sleep(0.25)  # Poll a cada 250ms (igual IHM web)

        print(f"\n✅ Monitoramento concluído")
        self.testes_ok += 1

    def exibir_resumo(self):
        """Exibe resumo dos testes"""
        print("\n" + "=" * 70)
        print("📊 RESUMO DOS TESTES")
        print("=" * 70)

        total = self.testes_ok + self.testes_falha
        taxa_sucesso = (self.testes_ok / total * 100) if total > 0 else 0

        print(f"\nTotal de testes: {total}")
        print(f"✅ Sucessos: {self.testes_ok}")
        print(f"❌ Falhas: {self.testes_falha}")
        print(f"📈 Taxa de sucesso: {taxa_sucesso:.1f}%")

        if self.testes_falha == 0:
            print("\n🎉 TODOS OS TESTES PASSARAM!")
            print("   → Modificação do ladder está correta")
            print("   → IHM web pode usar registro 0x0860 para sincronização")
        else:
            print("\n⚠️  ALGUNS TESTES FALHARAM")
            print("   → Revise a lógica do ladder")
            print("   → Verifique se o programa foi gravado corretamente")

    def executar_bateria_completa(self):
        """Executa todos os testes automatizados"""
        print("\n" + "=" * 70)
        print(" BATERIA COMPLETA DE TESTES - SINCRONIZAÇÃO IHM")
        print("=" * 70)
        print(f" Data: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f" Arquivo: clp_pronto_COM_IHM_WEB.sup")
        print("=" * 70)

        if not self.conectar():
            sys.exit(1)

        try:
            # Teste 1: Leitura básica
            if not self.testar_leitura_inicial():
                print("\n❌ ABORTANDO: Registro 0x0860 não existe ou não é legível")
                print("   → A modificação do ladder NÃO foi aplicada")
                return

            # Teste 2: Navegação por teclas
            self.testar_todas_teclas()

            # Teste 3: Monitoramento (opcional)
            resposta = input("\n❓ Executar monitoramento contínuo (30s)? [s/N]: ")
            if resposta.lower() == 's':
                self.testar_monitoramento_continuo(30)

            # Resumo final
            self.exibir_resumo()

        except KeyboardInterrupt:
            print("\n\n⚠️  Testes interrompidos pelo usuário")
        except Exception as e:
            print(f"\n❌ ERRO durante testes: {e}")
            import traceback
            traceback.print_exc()
        finally:
            if self.client:
                self.client.close()
                print("\n🔌 Desconectado do CLP\n")


def main():
    testador = TestadorSincronizacaoIHM()
    testador.executar_bateria_completa()


if __name__ == "__main__":
    main()
