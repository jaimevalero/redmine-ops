import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from typing import List
from loguru import logger
from werkzeug.utils import secure_filename
import os

from redmine_ops.RedmineProcessor import RedmineProcessor

class Application(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Redmine Issue Importer")
        self.geometry("500x500")

        self.username = tk.StringVar()
        self.password = tk.StringVar()

        self.create_widgets()
        self.arrange_widgets()

    def create_widgets(self):
        self.username_label = tk.Label(self, text="Username")
        self.username_entry = tk.Entry(self, textvariable=self.username)

        self.password_label = tk.Label(self, text="Password")
        self.password_entry = tk.Entry(self, show="*", textvariable=self.password)

        self.upload_button = tk.Button(self, text="Upload Files", command=self.upload_files)

    def arrange_widgets(self):
        self.username_label.grid(row=0, column=0, sticky="e", padx=(175, 0))
        self.username_entry.grid(row=0, column=1, sticky="w", padx=(0, 175))
        self.password_label.grid(row=1, column=0, sticky="e", padx=(175, 0))
        self.password_entry.grid(row=1, column=1, sticky="w", padx=(0, 175))
        self.upload_button.grid(row=2, column=0, columnspan=2)

    def upload_files(self):
        files = filedialog.askopenfilenames()
        if files:
            username = self.username.get()
            password = self.password.get()
            self.process_files(username, password, files)

    def process_files(self, username: str, password: str, files: List[str]):
        try:
            with RedmineProcessor(username, password) as processor:
                excel_files = self.save_temp_files(files)
                results = processor.process_files(excel_files)
                self.show_results(results)
        except Exception as e:
            logger.exception(f"Error processing files: {str(e)}")
            messagebox.showerror("Error", "Error processing files")

    def save_temp_files(self, files: List[str]):
        file_paths = []
        for file in files:
            filename = secure_filename(file)
            file_path = self.create_temp_file(file, filename)
            file_paths.append(file_path)
        return file_paths

    def create_temp_file(self, file: str, filename: str):
        temp_file_path = f"tmptmp-{filename}"
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
        with open(file, 'rb') as f_in, open(temp_file_path, 'wb') as f_out:
            f_out.write(f_in.read())
        return temp_file_path

    def show_results(self, results):
        results_window = tk.Toplevel(self)
        results_window.title("Results")
        table = ttk.Treeview(results_window, columns=('ID', 'Project', 'Subject'), show='headings')
        table.heading('ID', text='ID')
        table.heading('Project', text='Project')
        table.heading('Subject', text='Subject')
        for result in results:
            table.insert('', 'end', values=(result.id, result.project, result.subject))
        table.pack()

if __name__ == '__main__':
    app = Application()
    app.mainloop()