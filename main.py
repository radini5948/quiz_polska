import math

import pandas as pd
import geopandas
import geodatasets
from shapely.geometry import box
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
from tkinter import messagebox

# Wczytanie danych
df = pd.read_csv("polska_woj.csv")
df2 = pd.DataFrame()

# Wczytanie mapy
polska = geopandas.read_file(("wojewodztwa.shp"))
polska = polska.to_crs(4326)
clip = box(14, 49, 25, 55)

# --- GUI ---
window = tk.Tk()
window.title("Mapa Polski")

# Pole do wpisywania miasta
tk.Label(window, text="Podaj miasto:").pack()
entry = tk.Entry(window, width=30)
entry.pack()

# Lista wybranych miast
lista_miast = tk.Label(window, text="Wybrane miasta: brak", wraplength=300)
lista_miast.pack()

# --- Tworzenie figury i canvasu tylko raz ---
fig, ax = plt.subplots(figsize=(5, 5))
canvas = FigureCanvasTkAgg(fig, master=window)
polska.clip(clip).plot(ax=ax, color="white", edgecolor="black")
canvas.get_tk_widget().pack()
#plt.show()
# --- Główna funkcja rysująca mapę ---
def pokaz_miasto():
    global df2
    miasto = entry.get().strip().lower()  # konwersja do małych liter

    # porównanie z kolumną 'miasto', też w małych literach
    mask = df['miasto'].str.lower() == miasto

    if mask.any():
        nowy = df[mask]
        df2 = pd.concat([df2, nowy], ignore_index=True)

        ax.clear()
        polska.clip(clip).plot(ax=ax, color="white", edgecolor="black")
        gdf = geopandas.GeoDataFrame(
            df2, geometry=geopandas.points_from_xy(df2['dlug'], df2['szer']), crs="EPSG:4326"
        )
        gdf.plot(ax=ax, color="red",markersize=gdf['ludnosc'] / 2000)
        ax.set_title("Wybrane miasta")

        canvas.draw()
        lista_miast.config(text="Wybrane miasta: " + ", ".join(df2['miasto'].unique()))
        entry.delete(0, tk.END)
    else:
        messagebox.showerror("Błąd", f"Miasto '{miasto.title()}' nie znaleziono w danych.")

# --- Obsługa Entera (przekazuje event, więc trzeba osobną funkcję lub wrapper) ---
def pokaz_miasto_enter(event):
    pokaz_miasto()




# Przycisk
tk.Button(window, text="Pokaż na mapie", command=pokaz_miasto).pack(pady=5)

# Obsługa klawisza Enter
window.bind("<Return>", pokaz_miasto_enter)

# Start GUI
window.mainloop()