def make_quiz(shape, province, title):
    import unicodedata
    import pandas as pd
    import geopandas
    from shapely.geometry import box
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    import tkinter as tk
    from tkinter import messagebox,font

    SHAPEFILE_PATH = shape
    ENCODING = 'utf-8'
    WINDOW_TITLE = title
    DEFAULT_WOJ_COUNT = 0

    # Przygotowanie danych
    gdf = geopandas.read_file(SHAPEFILE_PATH, encoding=ENCODING).to_crs(4326)
    geom = gdf['geometry'].bounds
    minx = min(geom['minx'])
    miny = min(geom['miny'])
    maxx = max(geom['maxx'])
    maxy = max(geom['maxy'])
    if (minx < maxx) and (miny < maxy):
        clip = box(minx - 0.5, miny - 0.5, maxx + 0.5, maxy + 0.5)
    elif (minx > maxx) and (miny < maxy):
        clip = box(minx - 0.5, miny - 0.5, maxx + 0.5, maxy + 0.5)

    # Zmienny stan (kontener)
    state = {
        "df2": pd.DataFrame()
    }

    # Funkcja tworząca GUI
    def start_quiz():
        # GUI
        window = tk.Tk()
        window.title(WINDOW_TITLE)
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
        fig, ax = plt.subplots(figsize=(7, 7))
        canvas = FigureCanvasTkAgg(fig, master=window)
        ax.set_title(title)
        gdf.clip(clip).plot(ax=ax, color="white", edgecolor="black")

        tk.Label(window, text="Podaj jednostkę:").pack()
        entry = tk.Entry(window, width=30)
        entry.pack()

        lista_woj = tk.Label(window, text="", wraplength=300)
        lista_woj.place(x=1200, y=150)

        ilosc_woj = tk.Label(window, text=f"Odgadnięte : {DEFAULT_WOJ_COUNT} / {len(gdf)}",
                             wraplength=300)
        ilosc_woj.pack()

        def usun_znaki_diakrytyczne(tekst):
            return unicodedata.normalize('NFKD', tekst.strip().lower()).encode('ascii', 'ignore').decode('ascii')

        def pokaz_woj():
            woj = usun_znaki_diakrytyczne(entry.get())
            mask = gdf[province].apply(lambda x: usun_znaki_diakrytyczne(str(x))) == woj

            if mask.any():
                nowy = gdf[mask]
                state["df2"] = pd.concat([state["df2"], nowy], ignore_index=True)

                ax.clear()
                gdf.clip(clip).plot(ax=ax, color="white", edgecolor="black")
                state["df2"].plot(ax=ax, color="green")
                canvas.draw()

                ilosc_woj.config(text=f"Odgadnięte : {len(state['df2'])} / {len(gdf)}")
                entry.delete(0, tk.END)
            else:
                messagebox.showerror("Błąd", f"'{woj.title()}' nie znaleziono w danych.")
        def zamkniecie():
            window.destroy()

        tk.Button(window, text="Zamknij quiz", command=zamkniecie, **button_options).place(x=1500, y=300)
        window.bind("<Return>", lambda event: pokaz_woj())
        canvas.get_tk_widget().pack()
        window.mainloop()

    # Zwracamy funkcję uruchamiającą GUI
    return start_quiz