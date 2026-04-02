import tkinter as tk
from tkinter import messagebox, ttk
import customtkinter as ctk
import subprocess
import threading
import os
import sqlite3
import pandas as pd
from google import genai
from google.genai import types

# Matrix Theme Colors
BG_COLOR = "#000000"
TEXT_COLOR = "#00FF00"
BUTTON_COLOR = "#003300"
ENTRY_COLOR = "#001100"

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("green")

class MatrixApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Rising Blade System Access")
        self.geometry("1000x700")
        self.configure(fg_color=BG_COLOR)

        self.sidebar = ctk.CTkFrame(self, width=200, fg_color=BG_COLOR, border_color=TEXT_COLOR, border_width=1)
        self.sidebar.pack(side="left", fill="y", padx=10, pady=10)

        self.main_area = ctk.CTkTabview(self, fg_color=BG_COLOR, segmented_button_fg_color=BUTTON_COLOR)
        self.main_area.pack(side="right", fill="both", expand=True, padx=10, pady=10)
        
        self.db_tab = self.main_area.add("Database Explorer")
        self.chat_tab = self.main_area.add("Gemini Analysis")

        self.btn_update = ctk.CTkButton(self.sidebar, text="Run Updates", fg_color=BUTTON_COLOR, text_color=TEXT_COLOR, command=self.run_updates_terminal)
        self.btn_update.pack(pady=20, padx=10)

        self.btn_full_scrape = ctk.CTkButton(self.sidebar, text="Run Full Scrapers", fg_color=BUTTON_COLOR, text_color=TEXT_COLOR, command=self.confirm_full_scrape)
        self.btn_full_scrape.pack(pady=20, padx=10)

        # Database Explorer Setup
        self.db_selector = ctk.CTkOptionMenu(self.db_tab, values=["rising_world_members.db", "rising_world_forum.db", "steam_forum.db"], command=self.load_db_data)
        self.db_selector.pack(pady=10)
        
        self.tree_frame = ctk.CTkFrame(self.db_tab, fg_color=BG_COLOR)
        self.tree_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.tree = ttk.Treeview(self.tree_frame, columns=(), show="headings")
        self.tree.pack(side="left", fill="both", expand=True)
        
        self.scrollbar = ttk.Scrollbar(self.tree_frame, orient="vertical", command=self.tree.yview)
        self.scrollbar.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=self.scrollbar.set)
        
        # Gemini Chat Interface
        self.chat_display = ctk.CTkTextbox(self.chat_tab, fg_color=ENTRY_COLOR, text_color=TEXT_COLOR)
        self.chat_display.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.chat_input = ctk.CTkEntry(self.chat_tab, placeholder_text="Ask about forum data...", fg_color=ENTRY_COLOR, text_color=TEXT_COLOR)
        self.chat_input.pack(fill="x", padx=5, pady=5)
        
        self.send_btn = ctk.CTkButton(self.chat_tab, text="Execute", fg_color=BUTTON_COLOR, text_color=TEXT_COLOR, command=self.send_to_gemini)
        self.send_btn.pack(pady=5)

        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)
        
        self.controls = ctk.CTkFrame(self.db_tab, fg_color=BG_COLOR)
        self.controls.pack(fill="x", pady=5)
        
        self.btn_prev = ctk.CTkButton(self.controls, text="<< Prev", width=60, fg_color=BUTTON_COLOR, command=self.prev_page)
        self.btn_prev.pack(side="left", padx=5)
        self.page_label = ctk.CTkLabel(self.controls, text="Page 1", text_color=TEXT_COLOR)
        self.page_label.pack(side="left", padx=5)
        self.btn_next = ctk.CTkButton(self.controls, text="Next >>", width=60, fg_color=BUTTON_COLOR, command=self.next_page)
        self.btn_next.pack(side="left", padx=5)

        self.current_db = None
        self.current_table = None
        self.page = 0
        self.limit = 50

    def load_db_data(self, db_name):
        self.current_db = os.path.join(os.path.dirname(os.path.abspath(__file__)), db_name)
        self.page = 0
        self.refresh_table_list()

    def refresh_table_list(self):
        conn = sqlite3.connect(self.current_db)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [t[0] for t in cursor.fetchall()]
        
        if 'threads' in tables:
            self.current_table = 'threads'
        elif tables:
            self.current_table = tables[0]
        else:
            self.current_table = None
        
        if self.current_table:
            self.update_view()
        conn.close()

    def update_view(self):
        conn = sqlite3.connect(self.current_db)
        query = f"SELECT * FROM {self.current_table} LIMIT {self.limit} OFFSET {self.page * self.limit}"
        df = pd.read_sql_query(query, conn)
        
        for i in self.tree.get_children(): self.tree.delete(i)
        self.tree["columns"] = list(df.columns)
        for col in df.columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)
        for _, row in df.iterrows():
            self.tree.insert("", "end", values=list(row))
        self.page_label.configure(text=f"Page {self.page + 1}")
        conn.close()

    def next_page(self):
        self.page += 1
        self.update_view()

    def prev_page(self):
        if self.page > 0:
            self.page -= 1
            self.update_view()

    def on_tree_select(self, event):
        selected_item = self.tree.selection()
        if not selected_item: return
        item_data = self.tree.item(selected_item[0])['values']
        
        print(f"DEBUG: Selected table: {self.current_table}, Selected row: {item_data}")
        
        # If in 'threads' table, drill down to 'posts'
        if self.current_table == 'threads':
            thread_id = item_data[0] # Assuming first col is id
            self.drill_down_to_posts(thread_id)
        # If in 'posts' table, show content
        elif self.current_table == 'posts':
            self.show_post_content(item_data)
        else:
            self.show_default_details(item_data)

    def drill_down_to_posts(self, thread_id):
        self.current_table = 'posts'
        conn = sqlite3.connect(self.current_db)
        query = f"SELECT * FROM posts WHERE thread_id={thread_id}"
        df = pd.read_sql_query(query, conn)
        
        for i in self.tree.get_children(): self.tree.delete(i)
        self.tree["columns"] = list(df.columns)
        for col in df.columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150)
        for _, row in df.iterrows():
            self.tree.insert("", "end", values=list(row))
        conn.close()

    def show_post_content(self, post_data):
        detail_win = ctk.CTkToplevel(self)
        detail_win.title(f"Post by {post_data[2]}")
        detail_text = ctk.CTkTextbox(detail_win, fg_color=BG_COLOR, text_color=TEXT_COLOR, width=500, height=300)
        detail_text.pack(fill="both", expand=True, padx=10, pady=10)
        detail_text.insert("1.0", str(post_data[3]))
        detail_text.configure(state="disabled")

    def show_default_details(self, data):
        detail_win = ctk.CTkToplevel(self)
        detail_win.title("Record Details")
        detail_text = ctk.CTkTextbox(detail_win, fg_color=BG_COLOR, text_color=TEXT_COLOR)
        detail_text.pack(fill="both", expand=True, padx=10, pady=10)
        detail_text.insert("0.0", str(data))

    def send_to_gemini(self):
        user_query = self.chat_input.get()
        if not user_query: return
        self.chat_display.insert("end", f"USER: {user_query}\n")
        self.chat_input.delete(0, "end")
        
        try:
            client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
            # Using the requested model
            response = client.models.generate_content(
                model="gemini-3.1-flash-lite-preview",
                contents=f"You are a database analysis assistant for Rising World. Answer based on this context: {user_query}",
            )
            self.chat_display.insert("end", f"AI: {response.text}\n\n")
        except Exception as e:
            self.chat_display.insert("end", f"ERROR: Could not contact Gemini: {e}\n\n")
            print(f"DEBUG: Gemini API error: {e}")

    def run_updates_terminal(self):
        project_dir = os.path.dirname(os.path.abspath(__file__))
        script_path = os.path.join(project_dir, "run_all_updates.py")
        venv_python = os.path.join(project_dir, "venv", "bin", "python3")
        cmd = f'cd {project_dir} && {venv_python} {script_path}; exec bash'
        subprocess.Popen(['xterm', '-e', cmd])

    def confirm_full_scrape(self):
        if messagebox.askyesno("Confirm", "Warning: Running full scrapers is resource-intensive. Proceed?"):
            pass

if __name__ == "__main__":
    app = MatrixApp()
    app.mainloop()
