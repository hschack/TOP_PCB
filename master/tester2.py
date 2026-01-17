import serial
import serial.tools.list_ports
import tkinter as tk
from tkinter import ttk
import threading
import time

class MasterGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Master Simulator - Signal Analyzer")
        self.ser = None
        self.data_history = [] # Stores last 100 points for graphing
        
        # --- Connection Header ---
        top_f = tk.Frame(root)
        top_f.pack(fill="x", padx=10, pady=5)
        self.port_var = tk.StringVar()
        self.port_combo = ttk.Combobox(top_f, textvariable=self.port_var, width=15)
        self.refresh_ports()
        self.port_combo.pack(side="left")
        
        self.conn_btn = tk.Button(top_f, text="Connect", command=self.toggle_conn)
        self.conn_btn.pack(side="left", padx=5)

        # --- Frequency Toggles ---
        tk.Label(top_f, text="Rate:").pack(side="left", padx=(20, 0))
        tk.Button(top_f, text="1 Hz", command=lambda: self.send_cmd(16, 1)).pack(side="left", padx=2)
        tk.Button(top_f, text="10 Hz", command=lambda: self.send_cmd(16, 10)).pack(side="left", padx=2)

        # --- Live Graph Canvas ---
        tk.Label(root, text="Live Signal (Wiper 1)").pack()
        self.canvas = tk.Canvas(root, width=400, height=200, bg="black")
        self.canvas.pack(padx=10, pady=5)
        # Draw scale lines
        for i in range(0, 201, 50):
            self.canvas.create_line(0, i, 400, i, fill="#333333")

        # --- Values Display ---
        self.val_label = tk.Label(root, text="Value: 0", font=("Arial", 14, "bold"))
        self.val_label.pack()

        # Start Serial Thread
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

    def update_graph(self, val):
        self.data_history.append(val)
        if len(self.data_history) > 100: self.data_history.pop(0)
        
        self.canvas.delete("plot")
        if len(self.data_history) < 2: return

        # Scale 0-4095 to 200-0 pixels (inverted for Y-axis)
        points = []
        for i, v in enumerate(self.data_history):
            x = i * 4
            y = 200 - (v * 200 / 4095)
            points.extend([x, y])
        
        self.canvas.create_line(points, fill="#00FF00", tags="plot", width=2)
        self.val_label.config(text=f"Value: {val}")

    def read_serial(self):
        while True:
            if self.ser and self.ser.is_open and self.ser.in_waiting:
                try:
                    line = self.ser.readline().decode('utf-8').strip()
                    if line.startswith("A,"):
                        val = int(line.split(',')[1]) # Monitor Pot 1
                        self.root.after(0, self.update_graph, val)
                except: pass
            time.sleep(0.01)

if __name__ == "__main__":
    root = tk.Tk()
    app = MasterGUI(root)
    root.mainloop()