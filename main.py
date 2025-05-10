import math

import pandas as pd
import geopandas
# import geodatasets
from shapely.geometry import box
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
from tkinter import messagebox, font


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
lista_miast = tk.Label(window, text="", wraplength=300)
lista_miast.place(x=1200,y=150)


ilosc_miast = tk.Label(window, text="Liczba miast: " + str(len(df)), wraplength=300)
ilosc_miast.pack()

# --- Tworzenie figury i canvasu tylko raz ---
fig, ax = plt.subplots(figsize=(7, 7))
canvas = FigureCanvasTkAgg(fig, master=window)
polska.clip(clip).plot(ax=ax, color="white", edgecolor="black")
canvas.get_tk_widget().pack()


# plt.show()
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
        #ax.set_title("Wybrane miasta")
        gdf.plot(ax=ax, color="red")
        canvas.draw()

        #lista_miast.config(text="Wybrane miasta: " + ", ".join(df2['miasto'].unique()))
        ilosc_miast.config(text="Ilość miast: " + str(len(df2)) + " / " + str(len(df)))
        entry.delete(0, tk.END)

    else:
        messagebox.showerror("Błąd", f"Miasto '{miasto.title()}' nie znaleziono w danych.")


# --- Obsługa Entera (przekazuje event, więc trzeba osobną funkcję lub wrapper) ---

def pokaz_miasto_enter(event):
    pokaz_miasto()

def pokaz_populacje():
    temp_df = df2
    ax.clear()
    polska.clip(clip).plot(ax=ax, color="white", edgecolor="black")
    gdf_2 = geopandas.GeoDataFrame(
        temp_df, geometry=geopandas.points_from_xy(temp_df['dlug'], temp_df['szer']), crs="EPSG:4326"
    )
    gdf_2.plot(ax=ax, color="red", markersize=temp_df['ludnosc'] / 2000)
    ax.set_title("Wybrane miasta")

    canvas.draw()
def pokaz_brakujace():
    temp_df = df
    temp_df = temp_df.merge(df2, how='left', on=temp_df.columns.tolist(), indicator=True)
    temp_df = temp_df[temp_df['_merge'] == 'left_only'].drop(columns=['_merge'])
    ax.clear()
    polska.clip(clip).plot(ax=ax, color="white", edgecolor="black")
    gdf_2 = geopandas.GeoDataFrame(
        temp_df, geometry=geopandas.points_from_xy(temp_df['dlug'], temp_df['szer']), crs="EPSG:4326"
    )

    gdf_2.plot(ax=ax, color="gray")
    ax.set_title("Wybrane miasta")

    canvas.draw()

    # lista_miast.config(text="Wybrane miasta: " + ", ".join(df2['miasto'].unique()))
    ilosc_miast.config(text="Ilość miast brakujących miast: " + str(len(temp_df)) )

def powrot():
    ax.clear()
    polska.clip(clip).plot(ax=ax, color="white", edgecolor="black")
    gdf = geopandas.GeoDataFrame(
        df2, geometry=geopandas.points_from_xy(df2['dlug'], df2['szer']), crs="EPSG:4326"
    )
    # ax.set_title("Wybrane miasta")
    gdf.plot(ax=ax, color="red")
    canvas.draw()
    ilosc_miast.config(text="Ilość miast: " + str(len(df2)) + " / " + str(len(df)))

def odgadniete_miasta():
    lista_miast.config(text="Ostatnie odgadnięte miasta: " + ", ".join(df2['miasto'].head(10).unique()))


# Przycisk
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

tk.Button(window, text="Powrót do mapy", command=powrot, **button_options).place(x=1200, y=250)
tk.Button(window, text="Pokaz brakujace", command=pokaz_brakujace, **button_options).place(x=1200, y=200)

# Obsługa klawisza Enter
window.bind("<Return>", pokaz_miasto_enter)
width = window.winfo_screenwidth()
height = window.winfo_screenheight()
window.geometry("%dx%d" % (width, height))
tk.Button(window,text="Wyświetlanie po populacji", command=pokaz_populacje, **button_options).place(x=100, y=300)
tk.Button(window, text="Pokaz odgadniete", command=odgadniete_miasta,**button_options).place(x=1200, y=100)
# Start GUI
window.mainloop()
