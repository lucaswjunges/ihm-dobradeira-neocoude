#!/usr/bin/env python3
"""
Modbus TCP to RTU Bridge
Converte requisições Modbus TCP (do WinSUP) para Modbus RTU (CLP serial)

Escuta em: TCP 0.0.0.0:502 (porta padrão Modbus TCP)
Conecta em: /dev/ttyUSB0 (CLP via RS485)
"""

import asyncio
import logging
from pymodbus.server import StartAsyncTcpServer
from pymodbus.datastore import ModbusSlaveContext, ModbusServerContext
from pymodbus.datastore import ModbusSparseDataBlock
from pymodbus.client import ModbusSerialClient
from pymodbus.transaction import ModbusRtuFramer

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuração do CLP
SERIAL_PORT = '/dev/ttyUSB0'
BAUDRATE = 57600
PARITY = 'N'
STOPBITS = 2
SLAVE_ID = 1
TCP_PORT = 502

# Cliente serial para o CLP
serial_client = None


class ModbusBridgeDataBlock(ModbusSparseDataBlock):
    """
    Datablock que faz bridge para o CLP serial
    """

    def __init__(self, values):
        super().__init__(values)
        self.serial_client = None

    def setValues(self, address, values):
        """Escreve no CLP via serial quando alguém escreve via TCP"""
        logger.info(f"TCP Write request: address={address}, values={values}")

        if self.serial_client and self.serial_client.is_socket_open():
            try:
                # Escrever múltiplos registros
                result = self.serial_client.write_registers(
                    address=address,
                    values=values,
                    device_id=SLAVE_ID
                )

                if not result.isError():
                    logger.info(f"✓ Write successful to CLP")
                    super().setValues(address, values)
                else:
                    logger.error(f"Write error: {result}")
            except Exception as e:
                logger.error(f"Write exception: {e}")
        else:
            logger.warning("Serial client not connected")

    def getValues(self, address, count=1):
        """Lê do CLP via serial quando alguém lê via TCP"""
        logger.info(f"TCP Read request: address={address}, count={count}")

        if self.serial_client and self.serial_client.is_socket_open():
            try:
                # Tentar ler holding registers
                result = self.serial_client.read_holding_registers(
                    address=address,
                    count=count,
                    device_id=SLAVE_ID
                )

                if not result.isError():
                    values = result.registers
                    logger.info(f"✓ Read successful from CLP: {values}")
                    # Atualizar cache local
                    super().setValues(address, values)
                    return values
                else:
                    logger.error(f"Read error: {result}")
                    # Retornar valores em cache
                    return super().getValues(address, count)

            except Exception as e:
                logger.error(f"Read exception: {e}")
                return super().getValues(address, count)
        else:
            logger.warning("Serial client not connected, returning cached values")
            return super().getValues(address, count)


async def start_bridge():
    """Inicia o bridge Modbus TCP → RTU"""

    global serial_client

    print("=" * 60)
    print("MODBUS TCP → RTU BRIDGE")
    print("=" * 60)
    print(f"TCP Server: 0.0.0.0:{TCP_PORT}")
    print(f"Serial Port: {SERIAL_PORT}")
    print(f"Serial Config: {BAUDRATE} 8{PARITY}{STOPBITS}")
    print(f"CLP Slave ID: {SLAVE_ID}")
    print()

    # Conectar ao CLP via serial
    print("Conectando ao CLP via serial...")
    serial_client = ModbusSerialClient(
        port=SERIAL_PORT,
        baudrate=BAUDRATE,
        parity=PARITY,
        stopbits=STOPBITS,
        bytesize=8,
        timeout=1.0,
        framer=ModbusRtuFramer
    )

    if not serial_client.connect():
        logger.error("❌ ERRO: Não foi possível conectar ao CLP!")
        logger.error("Verifique:")
        logger.error("  - Cabo USB conectado")
        logger.error("  - Permissões: sudo chmod 666 /dev/ttyUSB0")
        logger.error("  - Porta correta: ls -la /dev/ttyUSB*")
        return

    print("✓ Conectado ao CLP via serial\n")

    # Criar datastore com bridge
    store = ModbusBridgeDataBlock({0: 0})
    store.serial_client = serial_client

    context = ModbusServerContext(
        slaves={
            SLAVE_ID: ModbusSlaveContext(
                di=store,  # Discrete Inputs
                co=store,  # Coils
                hr=store,  # Holding Registers
                ir=store   # Input Registers
            )
        },
        single=False
    )

    # Iniciar servidor TCP
    print(f"Iniciando servidor Modbus TCP na porta {TCP_PORT}...")
    print(f"✓ Bridge ativo!\n")
    print("Configure o WinSUP com:")
    print(f"  - Protocolo: Modbus TCP ou Ethernet")
    print(f"  - IP: 127.0.0.1")
    print(f"  - Porta: {TCP_PORT}")
    print(f"  - Slave ID: {SLAVE_ID}")
    print()
    print("Aguardando conexões...\n")

    await StartAsyncTcpServer(
        context=context,
        address=("0.0.0.0", TCP_PORT)
    )


if __name__ == "__main__":
    try:
        asyncio.run(start_bridge())
    except KeyboardInterrupt:
        print("\nEncerrando bridge...")
        if serial_client:
            serial_client.close()
    except Exception as e:
        logger.error(f"Erro fatal: {e}", exc_info=True)
