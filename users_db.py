import tkinter as tk
from tkinter import messagebox
import psycopg2
import bcrypt
import subprocess

from tkinter import ttk


def connect_db():
    return psycopg2.connect(
        dbname="**********",
        user="********",
        password="*********",
        host="*****",
        port="****"
    )


def hash_password(password: str) -> bytes:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode(), salt)


def check_password(password: str, hashed: bytes) -> bool:
    return bcrypt.checkpw(password.encode(), hashed)


def register(entry_username, entry_password):
    username = entry_username.get()
    password = entry_password.get()

    if not username or not password:
        messagebox.showwarning("Błąd", "Uzupełnij wszystkie pola.")
        return

    hashed = hash_password(password).decode()

    try:
        conn = connect_db()
        cur = conn.cursor()
        cur.execute("INSERT INTO users (username, password_hash) VALUES (%s, %s)", (username, hashed))
        conn.commit()
        cur.close()
        conn.close()
        messagebox.showinfo("Sukces", "Rejestracja zakończona sukcesem.")
    except psycopg2.IntegrityError:
        conn.rollback()
        messagebox.showerror("Błąd", "Użytkownik już istnieje.")
    except Exception as e:
        messagebox.showerror("Błąd", f"Wystąpił błąd: {e}")


def login(entry_username, entry_password, root_window):
    username = entry_username.get()
    password = entry_password.get()

    try:
        conn = connect_db()
        cur = conn.cursor()
        cur.execute("SELECT password_hash FROM users WHERE username = %s", (username,))
        result = cur.fetchone()
        cur.close()
        conn.close()

        if result and check_password(password, result[0].encode()):
            messagebox.showinfo("Sukces", f"Witaj, {username}!")
            from start_main_app import start_main_app
            root_window.destroy()
            start_main_app()
        else:
            messagebox.showerror("Błąd", "Nieprawidłowy login lub hasło.")
    except Exception as e:
        messagebox.showerror("Błąd", f"Wystąpił błąd: {e}")


def run_login_gui():
    root = tk.Tk()
    root.title("Quizyy by Radosław Beta")

    # Stałe wymiary i centrowanie
    window_width = 400
    window_height = 250
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width // 2) - (window_width // 2)
    y = (screen_height // 2) - (window_height // 2)
    root.geometry(f"{window_width}x{window_height}+{x}+{y}")
    root.resizable(True, True)

    # Ramka logowania
    frame = ttk.LabelFrame(root, text="Zaloguj się lub zarejestruj", padding=20)
    frame.pack(expand=True)

    # Styl
    font_label = ("Arial", 12)
    font_entry = ("Arial", 12)
    font_button = ("Arial", 11)

    # Nazwa użytkownika
    ttk.Label(frame, text="Nazwa użytkownika:", font=font_label).grid(row=0, column=0, sticky="w", pady=5)
    entry_username = ttk.Entry(frame, font=font_entry)
    entry_username.grid(row=0, column=1, pady=5)

    # Hasło
    ttk.Label(frame, text="Hasło:", font=font_label).grid(row=1, column=0, sticky="w", pady=5)
    entry_password = ttk.Entry(frame, show="*", font=font_entry)
    entry_password.grid(row=1, column=1, pady=5)

    # Przyciski
    ttk.Button(frame, text="Zaloguj się", command=lambda: login(entry_username, entry_password, root)).grid(row=2, column=0, pady=15)
    ttk.Button(frame, text="Zarejestruj się", command=lambda: register(entry_username, entry_password)).grid(row=2, column=1)
    ttk.Button(root, text="Wyjście", command=root.destroy).pack(pady=(0, 10))

    root.mainloop()

