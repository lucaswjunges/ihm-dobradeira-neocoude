#!/usr/bin/env python3
"""
modbus_tester_gui.py

Interface gráfica simples para testar Modbus RTU - equivalente ao Modbus Poll.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from pymodbus.client import ModbusSerialClient
import threading
import time

class ModbusTesterGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Modbus RTU Tester - Equivalente Modbus Poll")
        self.root.geometry("900x700")

        self.client = None
        self.polling = False
        self.poll_thread = None

        self.create_widgets()

    def create_widgets(self):
        # Frame de Conexão
        conn_frame = ttk.LabelFrame(self.root, text="Configuração de Conexão", padding=10)
        conn_frame.pack(fill="x", padx=10, pady=5)

        # Porta
        ttk.Label(conn_frame, text="Porta:").grid(row=0, column=0, sticky="w", padx=5)
        self.port_var = tk.StringVar(value="/dev/ttyUSB0")
        ttk.Entry(conn_frame, textvariable=self.port_var, width=15).grid(row=0, column=1, padx=5)

        # Baudrate
        ttk.Label(conn_frame, text="Baudrate:").grid(row=0, column=2, sticky="w", padx=5)
        self.baud_var = tk.StringVar(value="57600")
        ttk.Combobox(conn_frame, textvariable=self.baud_var,
                    values=["9600", "19200", "38400", "57600", "115200"],
                    width=10).grid(row=0, column=3, padx=5)

        # Parity
        ttk.Label(conn_frame, text="Parity:").grid(row=0, column=4, sticky="w", padx=5)
        self.parity_var = tk.StringVar(value="N")
        ttk.Combobox(conn_frame, textvariable=self.parity_var,
                    values=["N", "E", "O"],
                    width=5).grid(row=0, column=5, padx=5)

        # Stop bits
        ttk.Label(conn_frame, text="Stop bits:").grid(row=1, column=0, sticky="w", padx=5)
        self.stopbits_var = tk.StringVar(value="2")
        ttk.Combobox(conn_frame, textvariable=self.stopbits_var,
                    values=["1", "2"],
                    width=5).grid(row=1, column=1, padx=5)

        # Slave ID
        ttk.Label(conn_frame, text="Slave ID:").grid(row=1, column=2, sticky="w", padx=5)
        self.slave_var = tk.StringVar(value="1")
        ttk.Entry(conn_frame, textvariable=self.slave_var, width=5).grid(row=1, column=3, padx=5)

        # Botões de conexão
        self.btn_connect = ttk.Button(conn_frame, text="Conectar", command=self.connect)
        self.btn_connect.grid(row=1, column=4, padx=5)

        self.btn_disconnect = ttk.Button(conn_frame, text="Desconectar", command=self.disconnect, state="disabled")
        self.btn_disconnect.grid(row=1, column=5, padx=5)

        # Status
        self.status_var = tk.StringVar(value="⚪ Desconectado")
        ttk.Label(conn_frame, textvariable=self.status_var, font=("Arial", 10, "bold")).grid(row=1, column=6, padx=10)

        # Frame de Leitura
        read_frame = ttk.LabelFrame(self.root, text="Leitura Modbus", padding=10)
        read_frame.pack(fill="x", padx=10, pady=5)

        # Função Modbus
        ttk.Label(read_frame, text="Função:").grid(row=0, column=0, sticky="w", padx=5)
        self.function_var = tk.StringVar(value="03 - Read Holding Registers")
        function_combo = ttk.Combobox(read_frame, textvariable=self.function_var,
                                     values=["01 - Read Coils",
                                            "02 - Read Discrete Inputs",
                                            "03 - Read Holding Registers",
                                            "04 - Read Input Registers"],
                                     width=30)
        function_combo.grid(row=0, column=1, padx=5, columnspan=2)

        # Endereço inicial
        ttk.Label(read_frame, text="Endereço:").grid(row=0, column=3, sticky="w", padx=5)
        self.address_var = tk.StringVar(value="256")
        ttk.Entry(read_frame, textvariable=self.address_var, width=10).grid(row=0, column=4, padx=5)

        # Quantidade
        ttk.Label(read_frame, text="Quantidade:").grid(row=0, column=5, sticky="w", padx=5)
        self.count_var = tk.StringVar(value="8")
        ttk.Entry(read_frame, textvariable=self.count_var, width=10).grid(row=0, column=6, padx=5)

        # Botões de leitura
        ttk.Button(read_frame, text="Ler Uma Vez", command=self.read_once).grid(row=1, column=0, padx=5, pady=5, columnspan=2)

        self.btn_poll = ttk.Button(read_frame, text="Iniciar Polling (1s)", command=self.start_polling)
        self.btn_poll.grid(row=1, column=2, padx=5, pady=5, columnspan=2)

        self.btn_stop_poll = ttk.Button(read_frame, text="Parar Polling", command=self.stop_polling, state="disabled")
        self.btn_stop_poll.grid(row=1, column=4, padx=5, pady=5, columnspan=2)

        # Frame de Escrita
        write_frame = ttk.LabelFrame(self.root, text="Escrita Modbus (Force Coil)", padding=10)
        write_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(write_frame, text="Endereço Coil:").grid(row=0, column=0, sticky="w", padx=5)
        self.coil_addr_var = tk.StringVar(value="160")
        ttk.Entry(write_frame, textvariable=self.coil_addr_var, width=10).grid(row=0, column=1, padx=5)

        ttk.Button(write_frame, text="Force ON (100ms)", command=lambda: self.force_coil(True)).grid(row=0, column=2, padx=5)
        ttk.Button(write_frame, text="Force OFF", command=lambda: self.force_coil(False)).grid(row=0, column=3, padx=5)

        # Resultado
        result_frame = ttk.LabelFrame(self.root, text="Resultado", padding=10)
        result_frame.pack(fill="both", expand=True, padx=10, pady=5)

        self.result_text = scrolledtext.ScrolledText(result_frame, height=20, font=("Courier", 10))
        self.result_text.pack(fill="both", expand=True)

        # Botão limpar
        ttk.Button(result_frame, text="Limpar Log", command=self.clear_log).pack(pady=5)

    def log(self, message):
        """Adiciona mensagem ao log com timestamp"""
        timestamp = time.strftime("%H:%M:%S")
        self.result_text.insert("end", f"[{timestamp}] {message}\n")
        self.result_text.see("end")

    def clear_log(self):
        self.result_text.delete("1.0", "end")

    def connect(self):
        try:
            self.client = ModbusSerialClient(
                port=self.port_var.get(),
                baudrate=int(self.baud_var.get()),
                parity=self.parity_var.get(),
                stopbits=int(self.stopbits_var.get()),
                bytesize=8,
                timeout=1.0,
                handle_local_echo=False
            )

            if self.client.connect():
                self.status_var.set("🟢 Conectado")
                self.btn_connect.config(state="disabled")
                self.btn_disconnect.config(state="normal")
                self.log(f"✓ Conectado a {self.port_var.get()} @ {self.baud_var.get()} baud")
            else:
                self.log("❌ Falha na conexão!")
                messagebox.showerror("Erro", "Não foi possível conectar à porta serial")
        except Exception as e:
            self.log(f"❌ Erro: {e}")
            messagebox.showerror("Erro", str(e))

    def disconnect(self):
        if self.polling:
            self.stop_polling()

        if self.client:
            self.client.close()
            self.client = None

        self.status_var.set("⚪ Desconectado")
        self.btn_connect.config(state="normal")
        self.btn_disconnect.config(state="disabled")
        self.log("✓ Desconectado")

    def read_once(self):
        if not self.client:
            messagebox.showwarning("Aviso", "Conecte primeiro!")
            return

        try:
            function = self.function_var.get()
            address = int(self.address_var.get())
            count = int(self.count_var.get())
            slave_id = int(self.slave_var.get())

            self.log(f"\n→ Lendo: Função={function}, Addr={address}, Count={count}, Slave={slave_id}")

            if "01" in function:  # Read Coils
                response = self.client.read_coils(address=address, count=count, device_id=slave_id)
                if not response.isError():
                    self.log(f"✓ Coils: {response.bits[:count]}")
                    for i, bit in enumerate(response.bits[:count]):
                        symbol = "●" if bit else "○"
                        self.log(f"  [{address+i}] = {symbol} {bit}")
                else:
                    self.log(f"❌ Erro: {response}")

            elif "02" in function:  # Read Discrete Inputs
                response = self.client.read_discrete_inputs(address=address, count=count, device_id=slave_id)
                if not response.isError():
                    self.log(f"✓ Discrete Inputs:")
                    for i, bit in enumerate(response.bits[:count]):
                        symbol = "●" if bit else "○"
                        self.log(f"  E{i} [{address+i}] = {symbol} {bit}")
                else:
                    self.log(f"❌ Erro: {response}")

            elif "03" in function:  # Read Holding Registers
                response = self.client.read_holding_registers(address=address, count=count, device_id=slave_id)
                if not response.isError():
                    self.log(f"✓ Holding Registers:")
                    for i, reg in enumerate(response.registers):
                        self.log(f"  [{address+i}] = {reg} (0x{reg:04X})")
                else:
                    self.log(f"❌ Erro: {response}")

            elif "04" in function:  # Read Input Registers
                response = self.client.read_input_registers(address=address, count=count, device_id=slave_id)
                if not response.isError():
                    self.log(f"✓ Input Registers:")
                    for i, reg in enumerate(response.registers):
                        self.log(f"  [{address+i}] = {reg} (0x{reg:04X})")
                else:
                    self.log(f"❌ Erro: {response}")

        except Exception as e:
            self.log(f"❌ Exceção: {e}")

    def poll_loop(self):
        """Loop de polling em thread separada"""
        while self.polling:
            try:
                self.read_once()
                time.sleep(1)
            except:
                break

    def start_polling(self):
        if not self.client:
            messagebox.showwarning("Aviso", "Conecte primeiro!")
            return

        self.polling = True
        self.btn_poll.config(state="disabled")
        self.btn_stop_poll.config(state="normal")
        self.poll_thread = threading.Thread(target=self.poll_loop, daemon=True)
        self.poll_thread.start()
        self.log("▶️ Polling iniciado (1 segundo)")

    def stop_polling(self):
        self.polling = False
        self.btn_poll.config(state="normal")
        self.btn_stop_poll.config(state="disabled")
        self.log("⏸️ Polling parado")

    def force_coil(self, value):
        if not self.client:
            messagebox.showwarning("Aviso", "Conecte primeiro!")
            return

        try:
            address = int(self.coil_addr_var.get())
            slave_id = int(self.slave_var.get())

            # Force ON
            response = self.client.write_coil(address=address, value=value, device_id=slave_id)
            if not response.isError():
                self.log(f"✓ Coil {address} = {'ON' if value else 'OFF'}")

                if value:
                    # Se forçar ON, espera 100ms e força OFF (simula botão)
                    time.sleep(0.1)
                    response = self.client.write_coil(address=address, value=False, device_id=slave_id)
                    if not response.isError():
                        self.log(f"✓ Coil {address} = OFF (após 100ms)")
            else:
                self.log(f"❌ Erro ao forçar coil: {response}")

        except Exception as e:
            self.log(f"❌ Exceção: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ModbusTesterGUI(root)
    root.mainloop()
