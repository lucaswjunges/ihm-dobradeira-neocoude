#!/usr/bin/env python3
"""
test_ihm_completa.py

Script de teste automatizado para validar sistema IHM completo
Executa bateria de testes antes de implantação na fábrica

Uso:
    # Modo STUB (sem CLP - apenas validação de lógica)
    python3 test_ihm_completa.py --stub

    # Modo LIVE (com CLP conectado)
    python3 test_ihm_completa.py --port /dev/ttyUSB0
"""

import sys
import time
import argparse
from typing import List, Tuple, Callable

# Importar módulos do sistema
try:
    from modbus_client import ModbusClient, ModbusConfig
except ImportError:
    print("❌ Erro: modbus_client.py não encontrado!")
    print("   Execute este script no diretório do projeto")
    sys.exit(1)

# Cores ANSI para output
class Color:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_header(text: str):
    """Imprime cabeçalho de seção"""
    print(f"\n{Color.BOLD}{Color.BLUE}{'=' * 80}{Color.END}")
    print(f"{Color.BOLD}{Color.BLUE}{text.center(80)}{Color.END}")
    print(f"{Color.BOLD}{Color.BLUE}{'=' * 80}{Color.END}\n")

def print_test(name: str):
    """Imprime nome do teste"""
    print(f"{Color.BOLD}► {name}{Color.END}...", end=" ", flush=True)

def print_pass():
    """Imprime resultado PASSOU"""
    print(f"{Color.GREEN}✓ PASSOU{Color.END}")

def print_fail(reason: str = ""):
    """Imprime resultado FALHOU"""
    msg = f"{Color.RED}✗ FALHOU{Color.END}"
    if reason:
        msg += f" ({reason})"
    print(msg)

def print_skip(reason: str = ""):
    """Imprime resultado PULADO"""
    msg = f"{Color.YELLOW}⊘ PULADO{Color.END}"
    if reason:
        msg += f" ({reason})"
    print(msg)

def print_info(text: str):
    """Imprime informação"""
    print(f"  ℹ {text}")


class TesteIHM:
    """Classe para executar bateria de testes do sistema IHM"""

    def __init__(self, stub_mode: bool, port: str):
        """
        Inicializa teste

        Args:
            stub_mode: Se True, usa modo stub (sem CLP)
            port: Porta serial (ex: /dev/ttyUSB0)
        """
        self.stub_mode = stub_mode
        self.port = port
        self.client: ModbusClient = None
        self.tests_passed = 0
        self.tests_failed = 0
        self.tests_skipped = 0

    def run_test(self, name: str, test_func: Callable) -> bool:
        """
        Executa um teste individual

        Args:
            name: Nome do teste
            test_func: Função de teste (retorna True se passou)

        Returns:
            True se teste passou, False caso contrário
        """
        print_test(name)
        try:
            result = test_func()
            if result is True:
                print_pass()
                self.tests_passed += 1
                return True
            elif result is None:
                print_skip()
                self.tests_skipped += 1
                return False
            else:
                print_fail(str(result) if isinstance(result, str) else "")
                self.tests_failed += 1
                return False
        except Exception as e:
            print_fail(str(e))
            self.tests_failed += 1
            return False

    def test_modbus_connection(self) -> bool:
        """Teste 1: Conexão Modbus"""
        config = ModbusConfig(port=self.port)
        self.client = ModbusClient(stub_mode=self.stub_mode, config=config)

        if self.client.connect():
            if self.stub_mode:
                print_info("Modo STUB - simulação ativa")
            else:
                print_info(f"Conectado em {self.port}")
            return True
        else:
            return "Falha ao conectar"

    def test_read_encoder(self) -> bool:
        """Teste 2: Leitura do encoder"""
        encoder = self.client.get_encoder_angle()
        if encoder is not None:
            print_info(f"Encoder = {encoder}")
            return True
        return "Encoder retornou None"

    def test_read_angles(self) -> bool:
        """Teste 3: Leitura dos 3 ângulos"""
        angle1 = self.client.read_angle_1()
        angle2 = self.client.read_angle_2()
        angle3 = self.client.read_angle_3()

        if angle1 is None or angle2 is None or angle3 is None:
            return "Um ou mais ângulos retornou None"

        print_info(f"Ângulo 1 = {angle1}°, Ângulo 2 = {angle2}°, Ângulo 3 = {angle3}°")
        return True

    def test_write_angle_1(self) -> bool:
        """Teste 4: Escrita Ângulo 1"""
        test_value = 90
        if not self.client.write_angle_1(test_value):
            return "Falha ao escrever"

        time.sleep(0.3)

        read_value = self.client.read_angle_1()
        if read_value != test_value:
            return f"Esperado {test_value}°, lido {read_value}°"

        print_info(f"Escrito e validado: {test_value}°")
        return True

    def test_write_angle_2(self) -> bool:
        """Teste 5: Escrita Ângulo 2"""
        test_value = 120
        if not self.client.write_angle_2(test_value):
            return "Falha ao escrever"

        time.sleep(0.3)

        read_value = self.client.read_angle_2()
        if read_value != test_value:
            return f"Esperado {test_value}°, lido {read_value}°"

        print_info(f"Escrito e validado: {test_value}°")
        return True

    def test_write_angle_3(self) -> bool:
        """Teste 6: Escrita Ângulo 3"""
        test_value = 45
        if not self.client.write_angle_3(test_value):
            return "Falha ao escrever"

        time.sleep(0.3)

        read_value = self.client.read_angle_3()
        if read_value != test_value:
            return f"Esperado {test_value}°, lido {read_value}°"

        print_info(f"Escrito e validado: {test_value}°")
        return True

    def test_write_angle_validation(self) -> bool:
        """Teste 7: Validação de limites (0-360)"""
        # Tentar escrever valor fora da faixa
        if self.client.write_angle_1(400):
            return "Aceitou valor > 360 (deveria rejeitar)"

        if self.client.write_angle_1(-10):
            return "Aceitou valor < 0 (deveria rejeitar)"

        print_info("Valores inválidos rejeitados corretamente")
        return True

    def test_press_keys(self) -> bool:
        """Teste 8: Pressão de teclas"""
        keys_to_test = ['K1', 'K5', 'S1', 'ENTER', 'ESC']
        failed_keys = []

        for key in keys_to_test:
            if not self.client.press_key(key):
                failed_keys.append(key)
            time.sleep(0.15)

        if failed_keys:
            return f"Teclas falharam: {', '.join(failed_keys)}"

        print_info(f"{len(keys_to_test)} teclas enviadas com sucesso")
        return True

    def test_read_inputs(self) -> bool:
        """Teste 9: Leitura de entradas digitais"""
        inputs_read = []
        failed = False

        for i in range(8):
            reg_addr = 256 + i  # E0-E7
            result = self.client.read_register(reg_addr)
            if result is not None:
                inputs_read.append(bool(result & 0x0001))
            else:
                failed = True
                break

        if failed:
            return "Falha ao ler uma ou mais entradas"

        print_info(f"E0-E7: {inputs_read}")
        return True

    def test_read_outputs(self) -> bool:
        """Teste 10: Leitura de saídas digitais"""
        outputs_read = []
        failed = False

        for i in range(8):
            reg_addr = 384 + i  # S0-S7
            result = self.client.read_register(reg_addr)
            if result is not None:
                outputs_read.append(bool(result & 0x0001))
            else:
                failed = True
                break

        if failed:
            return "Falha ao ler uma ou mais saídas"

        print_info(f"S0-S7: {outputs_read}")
        return True

    def test_32bit_register_handling(self) -> bool:
        """Teste 11: Manipulação de registros 32-bit"""
        # Testar leitura de encoder (32-bit)
        encoder = self.client.get_encoder_angle()
        if encoder is None:
            return "Encoder retornou None"

        # Encoder é 32-bit, pode ser grande
        print_info(f"Encoder 32-bit = {encoder} (0x{encoder:08X})")
        return True

    def test_performance_read(self) -> bool:
        """Teste 12: Performance de leitura (10 iterações)"""
        iterations = 10
        start_time = time.time()

        for _ in range(iterations):
            encoder = self.client.get_encoder_angle()
            if encoder is None:
                return f"Falha na leitura (iteração {_+1})"

        elapsed = time.time() - start_time
        avg_time = (elapsed / iterations) * 1000  # ms

        print_info(f"{iterations} leituras em {elapsed:.2f}s (média: {avg_time:.1f}ms)")

        if avg_time > 100:
            return f"Leitura muito lenta: {avg_time:.1f}ms"

        return True

    def cleanup(self):
        """Desconecta cliente Modbus"""
        if self.client:
            self.client.disconnect()
            print_info("Cliente Modbus desconectado")

    def run_all_tests(self):
        """Executa toda a bateria de testes"""
        print_header("TESTE AUTOMATIZADO - SISTEMA IHM COMPLETO")

        mode_str = "STUB (Simulação)" if self.stub_mode else f"LIVE (CLP em {self.port})"
        print(f"Modo: {Color.BOLD}{mode_str}{Color.END}\n")

        # FASE 1: Conexão
        print_header("FASE 1: COMUNICAÇÃO MODBUS")
        self.run_test("Conexão Modbus", self.test_modbus_connection)

        if self.client is None or not self.client.connected:
            print(f"\n{Color.RED}✗ Falha na conexão - abortando testes{Color.END}")
            return

        # FASE 2: Leituras
        print_header("FASE 2: LEITURA DE DADOS")
        self.run_test("Leitura de encoder", self.test_read_encoder)
        self.run_test("Leitura de ângulos (1, 2, 3)", self.test_read_angles)
        self.run_test("Leitura de entradas digitais (E0-E7)", self.test_read_inputs)
        self.run_test("Leitura de saídas digitais (S0-S7)", self.test_read_outputs)
        self.run_test("Manipulação 32-bit", self.test_32bit_register_handling)

        # FASE 3: Escritas
        print_header("FASE 3: ESCRITA DE DADOS")
        self.run_test("Escrita de Ângulo 1 (90°)", self.test_write_angle_1)
        self.run_test("Escrita de Ângulo 2 (120°)", self.test_write_angle_2)
        self.run_test("Escrita de Ângulo 3 (45°)", self.test_write_angle_3)
        self.run_test("Validação de limites (0-360)", self.test_write_angle_validation)

        # FASE 4: Comandos
        print_header("FASE 4: COMANDOS (TECLAS)")
        self.run_test("Pressão de teclas (K1, K5, S1, ENTER, ESC)", self.test_press_keys)

        # FASE 5: Performance
        print_header("FASE 5: PERFORMANCE")
        self.run_test("Performance de leitura (10x)", self.test_performance_read)

        # Cleanup
        self.cleanup()

        # Resultado Final
        print_header("RESULTADO FINAL")
        total_tests = self.tests_passed + self.tests_failed + self.tests_skipped

        print(f"Total de testes: {total_tests}")
        print(f"{Color.GREEN}✓ Passaram: {self.tests_passed}{Color.END}")
        print(f"{Color.RED}✗ Falharam: {self.tests_failed}{Color.END}")
        print(f"{Color.YELLOW}⊘ Pulados: {self.tests_skipped}{Color.END}")

        success_rate = (self.tests_passed / total_tests * 100) if total_tests > 0 else 0
        print(f"\nTaxa de sucesso: {success_rate:.1f}%")

        if self.tests_failed == 0:
            print(f"\n{Color.GREEN}{Color.BOLD}╔════════════════════════════════════════╗{Color.END}")
            print(f"{Color.GREEN}{Color.BOLD}║   ✓ TODOS OS TESTES PASSARAM!         ║{Color.END}")
            print(f"{Color.GREEN}{Color.BOLD}║   Sistema pronto para produção        ║{Color.END}")
            print(f"{Color.GREEN}{Color.BOLD}╚════════════════════════════════════════╝{Color.END}\n")
            return 0
        else:
            print(f"\n{Color.RED}{Color.BOLD}╔════════════════════════════════════════╗{Color.END}")
            print(f"{Color.RED}{Color.BOLD}║   ✗ TESTES FALHARAM                   ║{Color.END}")
            print(f"{Color.RED}{Color.BOLD}║   Revise erros antes de implantar     ║{Color.END}")
            print(f"{Color.RED}{Color.BOLD}╚════════════════════════════════════════╝{Color.END}\n")
            return 1


def main():
    """Função principal"""
    parser = argparse.ArgumentParser(
        description='Teste automatizado do sistema IHM completo',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:

  # Teste em modo STUB (sem CLP - apenas validação de lógica)
  python3 test_ihm_completa.py --stub

  # Teste com CLP conectado
  python3 test_ihm_completa.py --port /dev/ttyUSB0

  # Teste com CLP em porta alternativa
  python3 test_ihm_completa.py --port /dev/ttyUSB1
        """
    )

    parser.add_argument(
        '--port',
        default='/dev/ttyUSB0',
        help='Porta serial do CLP (ex: /dev/ttyUSB0)'
    )

    parser.add_argument(
        '--stub',
        action='store_true',
        help='Usar modo stub (simulação, sem CLP)'
    )

    args = parser.parse_args()

    # Criar instância de teste
    teste = TesteIHM(stub_mode=args.stub, port=args.port)

    # Executar testes
    exit_code = teste.run_all_tests()

    sys.exit(exit_code)


if __name__ == '__main__':
    main()
