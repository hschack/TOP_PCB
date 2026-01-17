import serial
import serial.tools.list_ports
import tkinter as tk
from tkinter import ttk
import threading
import time

class MasterGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Master Signal Analyzer - Multi-Wiper")
        self.ser = None
        self.data_history = []
        self.selected_wiper = tk.IntVar(value=0) # Default to Wiper 1 (Index 0)
        
        # --- Top Frame: Connection & Rate ---
        top_f = tk.LabelFrame(root, text=" System Control ", padx=10, pady=5)
        top_f.pack(fill="x", padx=10, pady=5)
        
        self.port_var = tk.StringVar()
        self.port_combo = ttk.Combobox(top_f, textvariable=self.port_var, width=12)
        self.refresh_ports()
        self.port_combo.pack(side="left")
        
        self.conn_btn = tk.Button(top_f, text="Connect", command=self.toggle_conn, width=10)
        self.conn_btn.pack(side="left", padx=5)

        tk.Label(top_f, text="| Rate:").pack(side="left", padx=5)
        tk.Button(top_f, text="1 Hz", command=lambda: self.send_cmd(16, 1)).pack(side="left", padx=2)
        tk.Button(top_f, text="10 Hz", command=lambda: self.send_cmd(16, 10)).pack(side="left", padx=2)

        # --- Selector Frame: Choose Wiper ---
        select_f = tk.LabelFrame(root, text=" Select Wiper to Graph ", padx=10, pady=5)
        select_f.pack(fill="x", padx=10, pady=5)
        
        for i in range(4):
            tk.Radiobutton(select_f, text=f"Wiper {i+1}", variable=self.selected_wiper, 
                           value=i, command=self.clear_graph).pack(side="left", expand=True)

        # --- Live Graph Canvas ---
        self.canvas = tk.Canvas(root, width=400, height=200, bg="black", highlightthickness=0)
        self.canvas.pack(padx=10, pady=5)
        
        # Draw background grid
        for i in range(0, 201, 50):
            self.canvas.create_line(0, i, 400, i, fill="#222222")

        # --- Big Value Display ---
        self.val_label = tk.Label(root, text="0000", font=("Courier", 30, "bold"), fg="#00FF00", bg="black")
        self.val_label.pack(fill="x", padx=10, pady=5)

        threading.Thread(target=self.read_serial, daemon=True).start()

    def refresh_ports(self):
        self.port_combo['values'] = [p.device for p in serial.tools.list_ports.comports()]
        if self.port_combo['values']: self.port_combo.current(0)

    def toggle_conn(self):
        if self.ser and self.ser.is_open:
            self.ser.close()
            self.conn_btn.config(text="Connect", bg="SystemButtonFace")
        else:
            try:
                self.ser = serial.Serial(self.port_var.get(), 115200, timeout=0.1)
                self.conn_btn.config(text="Disconnect", bg="salmon")
            except Exception as e: print(e)

    def send_cmd(self, leds, hz):
        if self.ser and self.ser.is_open:
            self.ser.write(f"SET,{leds},{hz}\n".encode())

    def clear_graph(self):
        self.data_history = []
        self.canvas.delete("plot")

    def update_graph(self, values):
        idx = self.selected_wiper.get()
        current_val = values[idx]
        
        self.data_history.append(current_val)
        if len(self.data_history) > 100: self.data_history.pop(0)
        
        self.canvas.delete("plot")
        if len(self.data_history) < 2: return

        points = []
        for i, v in enumerate(self.data_history):
            x = i * 4
            y = 200 - (v * 200 / 4095)
            points.extend([x, y])
        
        self.canvas.create_line(points, fill="#00FF00", tags="plot", width=2)
        self.val_label.config(text=f"{current_val:04d}")

    def read_serial(self):
        while True:
            if self.ser and self.ser.is_open and self.ser.in_waiting:
                try:
                    line = self.ser.readline().decode('utf-8').strip()
                    if line.startswith("A,"):
                        # Extract the 4 values: A,V1,V2,V3,V4*CS
                        data_part = line.split('*')[0]
                        parts = data_part.split(',')
                        vals = [int(parts[1]), int(parts[2]), int(parts[3]), int(parts[4])]
                        self.root.after(0, self.update_graph, vals)
                except: pass
            time.sleep(0.01)

if __name__ == "__main__":
    root = tk.Tk()
    app = MasterGUI(root)
    root.mainloop()