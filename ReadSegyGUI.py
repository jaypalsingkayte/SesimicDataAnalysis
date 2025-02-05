import os
import segyio
import pandas as pd
import numpy as np
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import filedialog, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class SegyReaderApp(ttk.Window):
    def __init__(self):
        super().__init__(themename="darkly")  
        self.title("📂 SEG-Y File Reader")
        self.geometry("900x650")

        # Header Label
        ttk.Label(self, text="SEG-Y File Reader", font=("Helvetica", 18, "bold")).pack(pady=10)

        # File Selection
        self.file_label = ttk.Label(self, text="📁 Select SEG-Y File:")
        self.file_label.pack(pady=5)
        self.file_entry = ttk.Entry(self, width=60)
        self.file_entry.pack(pady=5)
        self.file_button = ttk.Button(self, text="Browse", command=self.select_file, bootstyle=PRIMARY)
        self.file_button.pack(pady=5)

        # Load Button
        self.load_button = ttk.Button(self, text="📄 Load SEG-Y", command=self.load_segy, bootstyle=SUCCESS)
        self.load_button.pack(pady=10)

        # Progress Bar
        self.progress = ttk.Progressbar(self, orient="horizontal", length=500, mode="determinate", bootstyle=SUCCESS)
        self.progress.pack(pady=5)

        # Table Frame
        self.tree_frame = ttk.LabelFrame(self, text="📋 SEG-Y Metadata")
        self.tree_frame.pack(fill="both", expand=True, padx=10, pady=10)

        columns = ("Field", "Value")
        self.tree = ttk.Treeview(self.tree_frame, columns=columns, show="headings", height=10)

        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=300)

        self.tree.pack(fill="both", expand=True)

        # Trace Visualization Button
        self.plot_button = ttk.Button(self, text="📊 Plot Trace Data", command=self.plot_traces, bootstyle=INFO)
        self.plot_button.pack(pady=5)

        # Status Label
        self.status_label = ttk.Label(self, text="", font=("Arial", 12, "bold"))
        self.status_label.pack(pady=5)

    def select_file(self):
        """Select a SEG-Y file."""
        file_selected = filedialog.askopenfilename(filetypes=[("SEG-Y Files", "*.sgy;*.segy")])
        if file_selected:
            self.file_entry.delete(0, ttk.END)
            self.file_entry.insert(0, file_selected)

    def log_message(self, message):
        """Log messages to the status label."""
        self.status_label.config(text=message, foreground="white")

    def load_segy(self):
        """Load and display SEG-Y metadata."""
        segy_file = self.file_entry.get()

        if not segy_file or not os.path.exists(segy_file):
            messagebox.showerror("Error", "⚠️ Please select a valid SEG-Y file.")
            return

        self.progress["value"] = 0
        self.log_message(f"📂 Loading {os.path.basename(segy_file)}...")

        try:
            with segyio.open(segy_file, "r", ignore_geometry=True) as f:
                self.progress["value"] = 25

                # Extract header information
                file_size = round(os.path.getsize(segy_file) / (1024 ** 2), 2)  # File size in MB
                trace_count = f.tracecount
                sample_rate = f.bin[segyio.BinField.Interval] / 1000  # Convert to milliseconds
                num_samples = f.samples.size

                # Read textual header
                textual_header = "".join(f.text[0]).strip()
                header_hash = hash(textual_header)

                self.progress["value"] = 50

                # Clear previous table data
                for row in self.tree.get_children():
                    self.tree.delete(row)

                # Insert data into the table
                metadata = [
                    ("File Name", os.path.basename(segy_file)),
                    ("File Size (MB)", f"{file_size} MB"),
                    ("Total Traces", trace_count),
                    ("Sample Rate (ms)", sample_rate),
                    ("Samples per Trace", num_samples),
                    ("Textual Header Hash", header_hash)
                ]

                for field, value in metadata:
                    self.tree.insert("", "end", values=(field, value))

                self.progress["value"] = 75

                self.segy_file = segy_file  # Store for plotting traces
                self.traces = f.trace.raw[:]  # Store trace data

                self.progress["value"] = 100
                self.log_message("✅ SEG-Y file loaded successfully!")

        except Exception as e:
            messagebox.showerror("Error", f"❌ Failed to load SEG-Y file:\n{str(e)}")
            self.log_message("❌ Failed to load SEG-Y file!")

    def plot_traces(self):
        """Plot first 5 traces from the loaded SEG-Y file."""
        if not hasattr(self, "traces"):
            messagebox.showerror("Error", "⚠️ Please load a SEG-Y file first.")
            return

        try:
            fig, ax = plt.subplots(figsize=(6, 4))
            for i in range(min(5, len(self.traces))):  # Plot only first 5 traces
                ax.plot(self.traces[i], label=f"Trace {i+1}")

            ax.set_title("SEG-Y Trace Data")
            ax.set_xlabel("Sample Index")
            ax.set_ylabel("Amplitude")
            ax.legend()

            # Embed Matplotlib Figure into GUI
            top = ttk.Toplevel(self)
            top.title("📊 Trace Plot")
            canvas = FigureCanvasTkAgg(fig, master=top)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)

        except Exception as e:
            messagebox.showerror("Error", f"❌ Failed to plot traces:\n{str(e)}")

if __name__ == "__main__":
    app = SegyReaderApp()
    app.mainloop()
