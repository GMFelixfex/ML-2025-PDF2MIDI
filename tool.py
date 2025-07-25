import tkinter as tk
from tkinter import filedialog, scrolledtext
import subprocess
import threading
import os
from tomidi import mxl_to_midi  # Importiere deine Konvertierungsfunktion

class AudiverisGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("PDF zu MIDI Konverter")

        # Datei-Auswahl
        self.file_label = tk.Label(self, text="Keine Datei ausgewählt")
        self.file_label.pack(pady=5)

        self.select_button = tk.Button(self, text="PDF auswählen", command=self.select_file)
        self.select_button.pack()

        # Start Button
        self.start_button = tk.Button(self, text="Konvertierung starten", command=self.start_conversion, state=tk.DISABLED)
        self.start_button.pack(pady=5)

        # Ausgabefenster für Logs
        self.log_output = scrolledtext.ScrolledText(self, width=80, height=10)
        self.log_output.pack(pady=5)

        self.selected_file = None
        self.filename = None
        self.process = None

    def select_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("PDF Dateien", "*.pdf")])
        if file_path:
            self.selected_file = file_path
            self.filename = os.path.splitext(os.path.basename(self.selected_file))[0]
            self.file_label.config(text=file_path)
            self.start_button.config(state=tk.NORMAL)

    def start_conversion(self):
        if not self.selected_file:
            return
        self.start_button.config(state=tk.DISABLED)
        self.log_output.delete(1.0, tk.END)
        threading.Thread(target=self.run_audiveris, daemon=True).start()


    def run_audiveris(self):
        def log_gui(msg):
        # aus einem Worker‑Thread niemals direkt in Tk schreiben:
            self.log_output.after(0, lambda: (
                self.log_output.insert(tk.END, msg),
                self.log_output.see(tk.END)
            ))
        # Pfad zur audiveris.exe anpassen
        exe_path = './Audiveris/audiveris.exe'

        output_folder = './MXL/'
        midi_folder = './MIDI/'

        output_path = os.path.join(output_folder, self.filename)
        midi_path = os.path.join(midi_folder, self.filename + '.mid')
        
        cmd = [exe_path, '-batch', '-export', self.selected_file, '-output', output_path]

        self.process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, encoding="utf-8", errors="replace", text=True)

        for line in self.process.stdout:
            self.log_output.insert(tk.END, line)
            self.log_output.see(tk.END)  # Scrollt automatisch runter

        self.process.wait()
        if self.process.returncode == 0:
            self.log_output.insert(tk.END, "\nAudiveris erfolgreich beendet. Starte MIDI-Konvertierung...\n")
            try:
                if os.path.exists(midi_path):
                    os.remove(midi_path)  # Entferne alten Ordner, falls vorhanden
                mxl_to_midi(self.filename, log_callback=log_gui)  # Deinen Converter aufrufen
                self.log_output.insert(tk.END, f"MIDI-Konvertierung erfolgreich.\n")
            except Exception as e:
                self.log_output.insert(tk.END, f"Fehler bei MIDI-Konvertierung: {e}\n")
        else:
            self.log_output.insert(tk.END, f"\nAudiveris Fehler! Exit-Code {self.process.returncode}\n")

        self.log_output.insert(tk.END, f"\nFertig mit Exit-Code {self.process.returncode}\n")
        self.start_button.config(state=tk.NORMAL)
        
if __name__ == "__main__":
    app = AudiverisGUI()
    app.mainloop()
