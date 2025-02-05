import os
import pandas as pd
import segyio
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import filedialog, messagebox, StringVar
from copy_rename_duplicates import (
    create_destination_folder, count_files_with_extension, copy_files, 
    write_log, create_repeated_folder
)
from duplicate_min_max_amplitude import process_segy_files

class FileProcessorApp(ttk.Window):
    def __init__(self):
        super().__init__(themename="darkly")  
        self.title("📂 File Processing Tool")
        self.geometry("750x650")

        # Header Label
        ttk.Label(self, text="File Processing Tool", font=("Helvetica", 18, "bold")).pack(pady=15)

        # Source Folder Selection
        self.source_label = ttk.Label(self, text="📁 Select Source Folder:")
        self.source_label.pack(pady=5)
        self.source_entry = ttk.Entry(self, width=50)
        self.source_entry.pack(pady=5)
        self.source_button = ttk.Button(self, text="Browse", command=self.select_source, bootstyle=PRIMARY)
        self.source_button.pack(pady=5)

        # Destination Folder Selection
        self.dest_label = ttk.Label(self, text="📂 Select Destination Folder:")
        self.dest_label.pack(pady=5)
        self.dest_entry = ttk.Entry(self, width=50)
        self.dest_entry.pack(pady=5)
        self.dest_button = ttk.Button(self, text="Browse", command=self.select_destination, bootstyle=PRIMARY)
        self.dest_button.pack(pady=5)

        # File Extension Selection
        self.ext_label = ttk.Label(self, text="📄 File Extension:")
        self.ext_label.pack(pady=5)
        self.file_extension_var = StringVar()
        self.file_extension_dropdown = ttk.Combobox(self, textvariable=self.file_extension_var)
        self.file_extension_dropdown["values"] = [".txt", ".jpg", ".png", ".csv", ".sgy", ".json", ".xml"]
        self.file_extension_dropdown.current(4)  
        self.file_extension_dropdown.pack(pady=5)

        # Start Processing Button
        self.start_button = ttk.Button(self, text="🚀 Start Processing", command=self.start_processing, bootstyle=SUCCESS)
        self.start_button.pack(pady=10)

        # Progress Bar
        self.progress = ttk.Progressbar(self, orient="horizontal", length=400, mode="determinate", bootstyle=SUCCESS)
        self.progress.pack(pady=10)

        # Log Display
        self.log_text = ttk.Text(self, height=5, width=70)
        self.log_text.pack(pady=10)

        # Results Table (Treeview)
        self.results_frame = ttk.LabelFrame(self, text="📊 Processed Results")
        self.results_frame.pack(fill="both", expand=True, padx=10, pady=10)

        columns = ("Filename", "Min Amplitude", "Max Amplitude", "File Size", "Textual Header Hash", "Duplicate")
        self.results_table = ttk.Treeview(self.results_frame, columns=columns, show="headings", height=8)

        for col in columns:
            self.results_table.heading(col, text=col)
            self.results_table.column(col, width=120)

        self.results_table.pack(fill="both", expand=True)

        # Refresh Button
        self.refresh_button = ttk.Button(self, text="🔄 Refresh Results", command=self.load_results, bootstyle=PRIMARY)
        self.refresh_button.pack(pady=5)

        # Status Label
        self.status_label = ttk.Label(self, text="", font=("Arial", 12, "bold"))
        self.status_label.pack(pady=10)

    def select_source(self):
        """Select source folder."""
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.source_entry.delete(0, ttk.END)
            self.source_entry.insert(0, folder_selected)

    def select_destination(self):
        """Select destination folder."""
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.dest_entry.delete(0, ttk.END)
            self.dest_entry.insert(0, folder_selected)

    def log_message(self, message):
        """Log messages to the GUI text box."""
        self.log_text.insert(ttk.END, message + "\n")
        self.log_text.see(ttk.END)

    def start_processing(self):
        """Start file processing based on user input."""
        try:
            source_path = self.source_entry.get()
            destination_path = self.dest_entry.get()
            file_extension = self.file_extension_var.get()

            if not source_path or not destination_path or not file_extension:
                messagebox.showerror("Error", "⚠️ Please select source, destination, and file extension.")
                return

            create_destination_folder(destination_path)
            self.log_message(f"📁 Destination folder created: {destination_path}")

            total_files, repeated_files = count_files_with_extension(source_path, file_extension)
            self.log_message(f"🔍 {total_files} files found with extension {file_extension}")

            self.progress["maximum"] = total_files
            self.progress["value"] = 0

            warnings, successes = copy_files(source_path, file_extension, destination_path, total_files, repeated_files)
            
            for i in range(total_files):
                self.progress["value"] += 1
                self.update_idletasks()

            self.log_message("✅ Files copied successfully!")

            write_log(destination_path, warnings, successes)
            self.log_message(f"📄 Log file created at: {os.path.join(destination_path, 'copy_log.txt')}")

            process_segy_files_in_repeated_folder(destination_path)
            self.log_message("✅ SEG-Y Processing Completed!")

            # Load results into table
            self.load_results()

        except Exception as e:
            self.log_message(f"❌ Error: {str(e)}")
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    def load_results(self):
        """Load the results from 'results.xlsx' into the table."""
        destination_path = self.dest_entry.get()
        excel_path = os.path.join(destination_path, "results.xlsx")

        if not os.path.exists(excel_path):
            messagebox.showwarning("Warning", "📄 results.xlsx not found! Please process files first.")
            return

        df = pd.read_excel(excel_path)

        # Clear old data in table
        for row in self.results_table.get_children():
            self.results_table.delete(row)

        # Insert new data
        for _, row in df.iterrows():
            self.results_table.insert("", "end", values=tuple(row))

        self.log_message("📊 Results loaded successfully!")

def process_segy_files_in_repeated_folder(destination_path):
    """Process SEG-Y files in the repeated folder and save results in an Excel file."""
    repeated_folder_path = create_repeated_folder(destination_path)
    df_segy_info = process_segy_files(repeated_folder_path)

    if df_segy_info is not None and not df_segy_info.empty:
        df_segy_info.to_excel(os.path.join(destination_path, "results.xlsx"), index=False, engine="openpyxl")
    else:
        messagebox.showwarning("Warning", "No SEG-Y file data extracted!")

if __name__ == "__main__":
    app = FileProcessorApp()
    app.mainloop()
