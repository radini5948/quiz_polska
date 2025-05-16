from tkinter import font
from make_poland_quiz import make_quiz_polska
from make_quiz import make_quiz
import pandas as pd
import tkinter as tk

def start_main_app():
    window = tk.Tk()
    window.title("Quizy by Radosław Beta")
    width = window.winfo_screenwidth()
    height = window.winfo_screenheight()
    window.geometry(f"{width}x{height}")
    custom_font = font.Font(family="Helvetica", size=12, weight="bold")
    button_options = {
        "font": custom_font,
        "bg": "#4CAF50",
        "fg": "white",
        "activebackground": "#45a049",
        "activeforeground": "white",
        "bd": 2,
        "relief": "raised",
        "padx": 10,
        "pady": 5
    }
    kraje = pd.read_csv("kraje.csv")

    # Lista przycisków oparta na danych z pliku CSV
    przyciski_danych = [
        {"label": "Turcja", "index": 0},
        {"label": "Rzeczypospolita Obojga Narodów", "index": 1},
        {"label": "Województwa Polski", "index": 2},
        {"label": "Wszystkie gminy Polski", "index": 3},
        {"label": "Włochy", "index": 4},
        {"label": "USA", "index": 5},
        {"label": "Indie", "index": 6},
        {"label": "Brazylia", "index": 7}
    ]

    # Tworzenie przycisków w pętli
    for i, item in enumerate(przyciski_danych):
        idx = item["index"]
        shape = kraje.at[idx, 'shape']
        province = kraje.at[idx, 'province']
        title = kraje.at[idx, 'title']

        tk.Button(
            window,
            text=item["label"],
            command=make_quiz(shape, province, title),
            **button_options,
            width=30,
            height=2
        ).place(x=800, y=100 + i * 75)

    def powrot_do_logowania():
        window.destroy()
        from users_db import run_login_gui
        run_login_gui()
    # Oddzielny przycisk dla wszystkich miast Polski
    start_quiz_polska = make_quiz_polska()
    tk.Button(
        window,
        text="Wszystkie miasta Polski",
        command=start_quiz_polska,
        **button_options,
        width=30,
        height=2
    ).place(x=800, y=100 + len(przyciski_danych) * 75)
    tk.Button(window, text="Powrót do ekranu logowania", command=powrot_do_logowania, bg="red", width=43, height=2, padx=10, pady=5).place(
        x=800, y=775)
    tk.Button(window, text="Wyjście", command=window.destroy, bg="red", width=43, height=2, padx=10, pady=5).place(
        x=800, y=850)
    window.mainloop()
