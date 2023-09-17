import tkinter as tk
from tkinter import filedialog


class InputForm(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Input Form")

        # Configure the root window to stretch
        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)

        self.create_widgets()

    def create_widgets(self):
        # Label and entry widget for the pincode
        self.pincode_label = tk.Label(self, text="Enter Pincode:")
        self.pincode_label.grid(row=0, column=0, padx=10, pady=5)
        self.pincode_entry = tk.Entry(self)
        self.pincode_entry.grid(row=0, column=1, padx=10, pady=5, sticky="ew")

        # Label and entry widget for the folder path
        self.folder_label = tk.Label(self, text="Select a Folder:")
        self.folder_label.grid(row=1, column=0, padx=10, pady=5)
        self.folder_path_var = tk.StringVar()
        self.folder_path_entry = tk.Entry(self, textvariable=self.folder_path_var, state='readonly')
        self.folder_path_entry.grid(row=1, column=1, padx=10, pady=5, sticky="ew")

        # Button to open the folder dialog
        self.folder_browse_button = tk.Button(self, text="Browse", command=self.open_folder_dialog)
        self.folder_browse_button.grid(row=1, column=2, padx=10, pady=5)

        # Button to submit the form
        self.submit_button = tk.Button(self, text="Submit", command=self.submit_and_close)
        self.submit_button.grid(row=2, column=0, columnspan=3, padx=10, pady=10)

    def open_folder_dialog(self):
        folder_path = filedialog.askdirectory()
        self.folder_path_var.set(folder_path)

    def submit_and_close(self):
        pincode = self.pincode_entry.get()
        folder_path = self.folder_path_var.get()

        # You can perform actions with the pincode and folder_path here
        print(f"Pincode: {pincode}")
        print(f"Folder Path: {folder_path}")

        # Close the UI window
        self.destroy()


if __name__ == "__main__":
    app = InputForm()
    app.mainloop()
