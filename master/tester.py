import serial
import serial.tools.list_ports
import tkinter as tk
from tkinter import ttk
import threading
import csv
import time

class MasterGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Master Simulator Pro - ATtiny3226")
        self.ser = None
        self.running = True
        self.is_logging = False

        # --- Top Frame: Connection ---
        conn_frame = tk.LabelFrame(root, text=" Connection ", padx=10, pady=5)
        conn_frame.pack(fill="x", padx=10, pady=5)

        self.port_var = tk.StringVar()
        self.port_combo = ttk.Combobox(conn_frame, textvariable=self.port_var)
        self.refresh_ports()
        self.port_combo.pack(side="left", padx=5)

        self.conn_btn = tk.Button(conn_frame, text="Connect", command=self.toggle_connection, bg="lightgray")
        self.conn_btn.pack(side="left", padx=5)

        # --- Middle Frame: Analog Values ---
        val_frame = tk.LabelFrame(root, text=" Slave Data (12-bit) ", padx=10, pady=5)
        val_frame.pack(fill="x", padx=10, pady=5)

        self.bars = []
        self.labels = []
        for i in range(4):
            f = tk.Frame(val_frame)
            f.pack(fill="x", pady=2)
            tk.Label(f, text=f"Pot {i+1}:", width=8).pack(side="left")
            bar = ttk.Progressbar(f, length=250, maximum=4095)
            bar.pack(side="left", padx=5)
            lbl = tk.Label(f, text="0", width=6)
            lbl.pack(side="left")
            self.bars.append(bar)
            self.labels.append(lbl)

        # --- Bottom Frame: LED Control (1 by 1) ---
        led_frame = tk.LabelFrame(root, text=" LED Control (Bitmask) ", padx=10, pady=5)
        led_frame.pack(fill="x", padx=10, pady=5)

        self.led_vars = []
        led_names = ["Sec2 OFF (1)", "Sec2 ON (2)", "Sec1 OFF (4)", "Sec1 ON (8)", "Power Solid (16)", "Power Blink (32)"]
        for i in range(6):
            var = tk.BooleanVar()
            chk = tk.Checkbutton(led_frame, text=led_names[i], variable=var, command=self.send_command)
            chk.grid(row=i//2, column=i%2, sticky="w", padx=20)
            self.led_vars.append(var)

        # --- Frequency & Logging ---
        bot_frame = tk.Frame(root, padx=10, pady=5)
        bot_frame.pack(fill="x")

        tk.Label(bot_frame, text="Hz:").pack(side="left")
        self.hz_spinner = tk.Spinbox(bot_frame, from_=1, to=20, width=5, command=self.send_command)
        self.hz_spinner.pack(side="left", padx=5)

        self.log_btn = tk.Button(bot_frame, text="Start Log", command=self.toggle_logging)
        self.log_btn.pack(side="right", padx=5)

        # Background Thread
        threading.Thread(target=self.read_serial, daemon=True).start()

    def refresh_ports(self):
        ports = [p.device for p in serial.tools.list_ports.comports()]
        self.port_combo['values'] = ports
        if ports: self.port_combo.current(0)

    def toggle_connection(self):
        if self.ser and self.ser.is_open:
            self.ser.close()
            self.conn_btn.config(text="Connect", bg="lightgray")
        else:
            try:
                self.ser = serial.Serial(self.port_var.get(), 115200, timeout=0.1)
                self.conn_btn.config(text="Disconnect", bg="salmon")
            except Exception as e:
                print(f"Error: {e}")

    def send_command(self):
        if not self.ser or not self.ser.is_open: return
        
        # Calculate Bitmask
        led_byte = 0
        for i, var in enumerate(self.led_vars):
            if var.get():
                led_byte |= (1 << i)
        
        hz = self.hz_spinner.get()
        cmd = f"SET,{led_byte},{hz}\n"
        self.ser.write(cmd.encode())

    def toggle_logging(self):
        if not self.is_logging:
            self.log_file = open(f"log_{int(time.time())}.csv", 'w', newline='')
            self.writer = csv.writer(self.log_file)
            self.writer.writerow(["Time", "P1", "P2", "P3", "P4"])
            self.is_logging = True
            self.log_btn.config(text="Stop Log", bg="red")
        else:
            self.is_logging = False
            self.log_file.close()
            self.log_btn.config(text="Start Log", bg="systemButtonFace")

    def read_serial(self):
        while self.running:
            if self.ser and self.ser.is_open and self.ser.in_waiting > 0:
                try:
                    line = self.ser.readline().decode('utf-8').strip()
                    if line.startswith("A,"):
                        data = line.split('*')[0].split(',')
                        for i in range(4):
                            val = int(data[i+1])
                            self.bars[i]['value'] = val
                            self.labels[i].config(text=str(val))
                        if self.is_logging:
                            self.writer.writerow([time.strftime("%H:%M:%S")] + data[1:5])
                except: pass
            time.sleep(0.01)

if __name__ == "__main__":
    root = tk.Tk()
    app = MasterGUI(root)
    root.mainloop()