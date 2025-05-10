import pandas as pd
import geopandas
import unicodedata
from shapely.geometry import box
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
from tkinter import messagebox, font

#Stałe i konfiguracja
SHAPEFILE_PATH = "wojewodztwa.shp"
CSV_PATH = "polska_woj.csv"
CRS = 4326  # System współrzędnych
DEFAULT_POP_SIZE = 2000  # Do skalowania populacji

#Wczytanie danych
df = pd.read_csv(CSV_PATH)
df2 = pd.DataFrame()  # Zmienna dla wybranych miast

#Wczytanie mapy
polska = geopandas.read_file(SHAPEFILE_PATH)
polska = polska.to_crs(CRS)  # Ustawienie współrzędnych
clip = box(14, 49, 25, 55)  # Obszar mapy
window = tk.Tk()
#Funkcje pomocnicze
def usun_znaki_diakrytyczne(tekst):
    return unicodedata.normalize('NFKD', tekst.strip().lower()).encode('ascii', 'ignore').decode('ascii')

def pokaz_miasto():
    global df2
    miasto = usun_znaki_diakrytyczne(entry.get())  # Pobierz tekst z wpisu i przekształć

    # Porównanie z danymi w kolumnie 'miasto'
    mask = df['miasto'].apply(lambda x: usun_znaki_diakrytyczne(str(x))) == miasto

    if mask.any():
        nowy = df[mask]
        df2 = pd.concat([df2, nowy], ignore_index=True)

        # Rysowanie mapy
        ax.clear()
        polska.clip(clip).plot(ax=ax, color="white", edgecolor="black")
        gdf = geopandas.GeoDataFrame(df2, geometry=geopandas.points_from_xy(df2['dlug'], df2['szer']), crs="EPSG:4326")
        gdf.plot(ax=ax, color="red")
        canvas.draw()

        # Aktualizacja liczby miast
        ilosc_miast.config(text=f"Ilość miast: {len(df2)} / {len(df)}")
        entry.delete(0, tk.END)
    else:
        messagebox.showerror("Błąd", f"Miasto '{miasto.title()}' nie znaleziono w danych.")

def pokaz_populacje():
    temp_df = df2
    ax.clear()
    polska.clip(clip).plot(ax=ax, color="white", edgecolor="black")
    gdf_2 = geopandas.GeoDataFrame(temp_df, geometry=geopandas.points_from_xy(temp_df['dlug'], temp_df['szer']), crs="EPSG:4326")
    gdf_2.plot(ax=ax, color="red", markersize=temp_df['ludnosc'] / DEFAULT_POP_SIZE)
    ax.set_title("Miasta według populacji")
    canvas.draw()

def pokaz_brakujace():
    temp_df = df.merge(df2, how='left', on=df.columns.tolist(), indicator=True)
    temp_df = temp_df[temp_df['_merge'] == 'left_only'].drop(columns=['_merge'])

    ax.clear()
    polska.clip(clip).plot(ax=ax, color="white", edgecolor="black")
    gdf_2 = geopandas.GeoDataFrame(temp_df, geometry=geopandas.points_from_xy(temp_df['dlug'], temp_df['szer']), crs="EPSG:4326")
    gdf_2.plot(ax=ax, color="gray")
    ax.set_title("Brakujące miasta")
    canvas.draw()

    ilosc_miast.config(text=f"Ilość brakujących miast: {len(temp_df)}")

def powrot():
    ax.clear()
    polska.clip(clip).plot(ax=ax, color="white", edgecolor="black")
    gdf = geopandas.GeoDataFrame(df2, geometry=geopandas.points_from_xy(df2['dlug'], df2['szer']), crs="EPSG:4326")
    gdf.plot(ax=ax, color="red")
    canvas.draw()
    ilosc_miast.config(text=f"Ilość miast: {len(df2)} / {len(df)}")

def odgadniete_miasta():
    lista_miast.config(text="Ostatnie odgadnięte miasta: " + ", ".join(df2['miasto'].head(10).unique()))


#Konfiguracja GUI
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

#worzenie okna

window.title("Mapa Polski")
width, height = window.winfo_screenwidth(), window.winfo_screenheight()
window.geometry(f"{width}x{height}")

#Dodanie komponentów GUI
tk.Label(window, text="Podaj miasto:").pack()
entry = tk.Entry(window, width=30)
entry.pack()

lista_miast = tk.Label(window, text="", wraplength=300)
lista_miast.place(x=1200, y=150)

ilosc_miast = tk.Label(window, text=f"Ilość miast: {len(df2)}", wraplength=300)
ilosc_miast.pack()

#Tworzenie figury i canvasu
fig, ax = plt.subplots(figsize=(7, 7))
canvas = FigureCanvasTkAgg(fig, master=window)
polska.clip(clip).plot(ax=ax, color="white", edgecolor="black")
canvas.get_tk_widget().pack()

#Przycisk powrotu
tk.Button(window, text="Powrót do mapy", command=powrot, **button_options).place(x=1200, y=250)
tk.Button(window, text="Pokaz brakujace", command=pokaz_brakujace, **button_options).place(x=1200, y=200)
tk.Button(window, text="Wyświetlanie po populacji", command=pokaz_populacje, **button_options).place(x=100, y=300)
tk.Button(window, text="Pokaz odgadniete", command=odgadniete_miasta, **button_options).place(x=1200, y=100)

#Obsługa Entera
window.bind("<Return>", lambda event: pokaz_miasto())

#Uruchomienie GUI
window.mainloop()
