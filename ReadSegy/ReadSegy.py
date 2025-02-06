import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import segyio
import numpy as np
import hashlib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

def open_segy():
    file_path = filedialog.askopenfilename(filetypes=[("SEGY files", "*.sgy;*.segy"), ("All files", "*.*")])
    if not file_path:
        return
    
    try:
        with segyio.open(file_path, "r", ignore_geometry=True) as f:
            num_traces = f.tracecount
            min_amp, max_amp = np.inf, -np.inf
            
            for i in range(num_traces):
                trace_min, trace_max = np.min(f.trace[i]), np.max(f.trace[i])
                min_amp, max_amp = min(min_amp, trace_min), max(max_amp, trace_max)
            
            textual_header_bytes = f.text[0]
            textual_header_hash = hashlib.sha256(textual_header_bytes).hexdigest()
            textual_header_formatted = "\n".join(
                [line.strip() for line in textual_header_bytes.decode("utf-8", errors="ignore").split('\n')]
            )
            
            sample_interval = f.bin[segyio.BinField.Interval] / 1000  # Convert to milliseconds
            record_length = (num_traces * sample_interval) / 1000  # Convert to seconds
            domain = "Time" if sample_interval > 0 else "Depth"
            length = num_traces * sample_interval / 1000
            coordinate_unit = f.bin.get(segyio.BinField.MeasurementSystem, "Unknown")
            
            # Update UI fields
            update_metadata(file_path, min_amp, max_amp, textual_header_hash, sample_interval, record_length, domain, length, coordinate_unit)
            
            # Update text areas
            update_text_widgets(textual_header_formatted, f)
            
            # Display SEGY data as an image
            plot_segy_image(f)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to read SEGY file: {e}")

def update_metadata(file_path, min_amp, max_amp, header_hash, sample_interval, record_length, domain, length, coordinate_unit):
    filename_var.set(file_path)
    min_amp_var.set(f"{min_amp:.2f}")
    max_amp_var.set(f"{max_amp:.2f}")
    header_hash_var.set(header_hash)
    sample_interval_var.set(f"{sample_interval:.1f} ms")
    record_length_var.set(f"{record_length:.2f} sec")
    domain_var.set(domain)
    length_var.set(f"{length:.2f} m")
    coordinate_unit_var.set(coordinate_unit)

def update_text_widgets(textual_header, f):
    ebcdic_text.delete("1.0", tk.END)
    binary_text.delete("1.0", tk.END)
    trace_text.delete("1.0", tk.END)
    
    ebcdic_text.insert(tk.END, "EBCDIC Header:\n\n" + textual_header + "\n")
    
    binary_text.insert(tk.END, "Binary Header:\n")
    for key, value in f.bin.items():
        binary_text.insert(tk.END, f"{key}: {value}\n")
    
    trace_text.insert(tk.END, f"Trace Header (First 5 Traces of {f.tracecount}):\n")
    for i in range(min(5, f.tracecount)):
        trace_text.insert(tk.END, f"Trace {i+1}:\n")
        for key, value in f.header[i].items():
            trace_text.insert(tk.END, f"  {key}: {value}\n")

def plot_segy_image(f):
    data = np.stack([f.trace[i] for i in range(f.tracecount)], axis=1)
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.imshow(data, cmap="seismic", aspect="auto", interpolation="none")
    ax.set_title("SEGY Data Visualization")
    ax.set_xlabel("Trace Number")
    ax.set_ylabel("Sample Index")
    
    for widget in frame_plot.winfo_children():
        widget.destroy()
    
    canvas = FigureCanvasTkAgg(fig, master=frame_plot)
    canvas.draw()
    canvas.get_tk_widget().pack()

# GUI Setup
root = tk.Tk()
root.title("Advanced SEGY File Reader")
root.geometry("1000x750")

metadata_frame = tk.Frame(root)
metadata_frame.pack(pady=10, fill=tk.X)

filename_var = tk.StringVar()
min_amp_var = tk.StringVar()
max_amp_var = tk.StringVar()
header_hash_var = tk.StringVar()
sample_interval_var = tk.StringVar()
record_length_var = tk.StringVar()
domain_var = tk.StringVar()
length_var = tk.StringVar()
coordinate_unit_var = tk.StringVar()

metadata_labels = ["Filename", "Min Amplitude", "Max Amplitude", "Textual Header Hash", "Sample Interval", "Record Length", "Domain", "Length", "Coordinate Unit"]
metadata_vars = [filename_var, min_amp_var, max_amp_var, header_hash_var, sample_interval_var, record_length_var, domain_var, length_var, coordinate_unit_var]

for i, (label, var) in enumerate(zip(metadata_labels, metadata_vars)):
    tk.Label(metadata_frame, text=label, font=("Arial", 10, "bold")).grid(row=i, column=0, sticky='w', padx=10, pady=2)
    tk.Entry(metadata_frame, textvariable=var, font=("Arial", 10), width=50, state='readonly').grid(row=i, column=1, padx=10, pady=2)

tab_control = ttk.Notebook(root)

tab1 = ttk.Frame(tab_control)
tab2 = ttk.Frame(tab_control)
tab3 = ttk.Frame(tab_control)

tab_control.add(tab1, text='EBCDIC Header')
tab_control.add(tab2, text='Binary Header')
tab_control.add(tab3, text='Trace Header')
tab_control.pack(expand=1, fill='both')

tk.Button(root, text="Open SEGY File", command=open_segy, font=("Arial", 12)).pack(pady=10)

ebcdic_text = tk.Text(tab1, height=15, width=100, font=("Arial", 10))
ebcdic_text.pack()

binary_text = tk.Text(tab2, height=15, width=100, font=("Arial", 10))
binary_text.pack()

trace_text = tk.Text(tab3, height=15, width=100, font=("Arial", 10))
trace_text.pack()

frame_plot = tk.Frame(root)
frame_plot.pack(pady=10)

bottom_frame = tk.Frame(root)
bottom_frame.pack(side=tk.BOTTOM, fill=tk.X)

tk.Button(bottom_frame, text="Quit", command=root.quit).pack(side=tk.RIGHT, padx=10, pady=5)
root.mainloop()
