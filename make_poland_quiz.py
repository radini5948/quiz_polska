import pandas as pd
import geopandas
import unicodedata
import tkinter as tk
from tkinter import messagebox, font
from shapely.geometry import box
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt


def make_quiz_polska():
    shp_path = "quiz_polska/wojewodztwa.shp"
    csv_path = "quiz_polska/polska_woj.csv"
    crs = 4326
    default_pop_size = 2000
    df = pd.read_csv(csv_path)
    df2 = pd.DataFrame()
    polska = geopandas.read_file(shp_path).to_crs(crs)
    clip = box(14, 49, 25, 55)

    def start_quiz_polska():
        nonlocal df2

        def usun_znaki_diakrytyczne(tekst):
            return unicodedata.normalize('NFKD', tekst.strip().lower()).encode('ascii', 'ignore').decode('ascii')

        window = tk.Tk()
        window.title("Mapa Polski")
        width, height = window.winfo_screenwidth(), window.winfo_screenheight()
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

        tk.Label(window, text="Podaj miasto:").pack()
        entry = tk.Entry(window, width=30)
        entry.pack()

        lista_miast = tk.Label(window, text="", wraplength=300)
        lista_miast.place(x=1200, y=150)

        ilosc_miast = tk.Label(window, text=f"Ilość miast: {len(df2)}", wraplength=300)
        ilosc_miast.pack()

        fig, ax = plt.subplots(figsize=(7, 7))
        canvas = FigureCanvasTkAgg(fig, master=window)
        polska.clip(clip).plot(ax=ax, color="white", edgecolor="black")
        canvas.get_tk_widget().pack()

        def pokaz_miasto():
            nonlocal df2
            miasto = usun_znaki_diakrytyczne(entry.get())
            mask = df['miasto'].apply(lambda x: usun_znaki_diakrytyczne(str(x))) == miasto

            if mask.any():
                nowy = df[mask]
                df2 = pd.concat([df2, nowy], ignore_index=True)
                ax.clear()
                polska.clip(clip).plot(ax=ax, color="white", edgecolor="black")
                gdf = geopandas.GeoDataFrame(df2, geometry=geopandas.points_from_xy(df2['dlug'], df2['szer']), crs="EPSG:4326")
                gdf.plot(ax=ax, color="red")
                canvas.draw()
                ilosc_miast.config(text=f"Ilość miast: {len(df2)} / {len(df)}")
                entry.delete(0, tk.END)
            else:
                messagebox.showerror("Błąd", f"Miasto '{miasto.title()}' nie znaleziono w danych.")

        def pokaz_populacje():
            ax.clear()
            polska.clip(clip).plot(ax=ax, color="white", edgecolor="black")
            gdf = geopandas.GeoDataFrame(df2, geometry=geopandas.points_from_xy(df2['dlug'], df2['szer']), crs="EPSG:4326")
            gdf.plot(ax=ax, color="red", markersize=df2['ludnosc'] / default_pop_size)
            ax.set_title("Miasta według populacji")
            canvas.draw()

        def pokaz_brakujace():
            temp_df = df.merge(df2, how='left', on=df.columns.tolist(), indicator=True)
            temp_df = temp_df[temp_df['_merge'] == 'left_only'].drop(columns=['_merge'])
            ax.clear()
            polska.clip(clip).plot(ax=ax, color="white", edgecolor="black")
            gdf = geopandas.GeoDataFrame(temp_df, geometry=geopandas.points_from_xy(temp_df['dlug'], temp_df['szer']), crs="EPSG:4326")
            gdf.plot(ax=ax, color="gray")
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

        def zamkniecie():
            window.destroy()

        buttons = [
            ("Pokaż brakujące", pokaz_brakujace),
            ("Pokaż odgadnięte", odgadniete_miasta),
            ("Wyświetlanie po populacji", pokaz_populacje),
            ("Powrót do mapy", powrot),
            ("Zamknij quiz", zamkniecie),
        ]

        start_y = 100
        for i, (text, command) in enumerate(buttons):
            tk.Button(
                window,
                text=text,
                command=command,
                width=30,
                height=2,
                **button_options
            ).place(x=1500, y=start_y + i * 75)
        window.bind("<Return>", lambda event: pokaz_miasto())
        window.mainloop()

    return start_quiz_polska
