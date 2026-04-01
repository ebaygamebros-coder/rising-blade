import sqlite3
import os
import tkinter as tk
from tkinter import ttk, messagebox

class DatabaseViewer:
    def __init__(self, root):
        self.root = root
        self.root.title("Rising World Scrapper - Database Viewer")
        self.root.geometry("1000x600")

        # List of databases from your project
        self.db_paths = [
            '~/Desktop/Rising-World-Scrapper/steam_forum.db',
            '~/Desktop/Rising-World-Scrapper/rising_world_forum.db',
            '~/Desktop/Rising-World-Scrapper/rising_world_members.db'
        ]

        # UI Layout
        top_frame = tk.Frame(self.root)
        top_frame.pack(pady=10, fill=tk.X)

        tk.Label(top_frame, text="Select Database:").pack(side=tk.LEFT, padx=5)
        self.db_var = tk.StringVar()
        self.db_combo = ttk.Combobox(top_frame, textvariable=self.db_var, values=self.db_paths, width=60)
        self.db_combo.pack(side=tk.LEFT, padx=5)
        self.db_combo.bind("<<ComboboxSelected>>", self.load_tables)

        tk.Label(top_frame, text="Table:").pack(side=tk.LEFT, padx=5)
        self.table_var = tk.StringVar()
        self.table_combo = ttk.Combobox(top_frame, textvariable=self.table_var)
        self.table_combo.pack(side=tk.LEFT, padx=5)
        self.table_combo.bind("<<ComboboxSelected>>", self.view_data)

        # Data Table View
        self.tree_frame = tk.Frame(self.root)
        self.tree_frame.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)
        
        self.tree = ttk.Treeview(self.tree_frame, show='headings')
        self.vsb = ttk.Scrollbar(self.tree_frame, orient="vertical", command=self.tree.yview)
        self.hsb = ttk.Scrollbar(self.tree_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=self.vsb.set, xscrollcommand=self.hsb.set)

        self.tree.grid(column=0, row=0, sticky='nsew')
        self.vsb.grid(column=1, row=0, sticky='ns')
        self.hsb.grid(column=0, row=1, sticky='ew')
        
        self.tree_frame.grid_columnconfigure(0, weight=1)
        self.tree_frame.grid_rowconfigure(0, weight=1)

    def get_conn(self):
        path = os.path.expanduser(self.db_var.get())
        if not os.path.exists(path):
            messagebox.showerror("Error", f"Database not found at:\n{path}")
            return None
        return sqlite3.connect(path)

    def load_tables(self, event=None):
        conn = self.get_conn()
        if conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = [t[0] for t in cursor.fetchall()]
            self.table_combo['values'] = tables
            if tables:
                self.table_combo.current(0)
                self.view_data()
            conn.close()

    def view_data(self, event=None):
        table_name = self.table_var.get()
        if not table_name:
            return

        conn = self.get_conn()
        if not conn:
            return
            
        cursor = conn.cursor()
        try:
            # Fetch headers
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = [info[1] for info in cursor.fetchall()]
            
            # Fetch data
            cursor.execute(f"SELECT * FROM {table_name} LIMIT 500")
            rows = cursor.fetchall()

            # Clear and rebuild tree
            self.tree.delete(*self.tree.get_children())
            self.tree["columns"] = columns
            
            for col in columns:
                self.tree.heading(col, text=col)
                self.tree.column(col, width=150, anchor=tk.W)

            for row in rows:
                self.tree.insert("", tk.END, values=row)
                
        except Exception as e:
            messagebox.showerror("Query Error", str(e))
        finally:
            conn.close()

if __name__ == "__main__":
    root = tk.Tk()
    app = DatabaseViewer(root)
    root.mainloop()