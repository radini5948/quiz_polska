import pandas as pd
import geopandas
import geodatasets
from shapely.geometry import box
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
from tkinter import messagebox
df = pd.read_csv('lubuskie_woj.csv')
world = geopandas.read_file(("wojewodztwa.shp"))

gdf = geopandas.GeoDataFrame(
            df, geometry=geopandas.points_from_xy(df['dlug'], df['szer']), crs="EPSG:2180"
        )
fig,ax = plt.subplots(figsize = (10,10))
world.plot(ax = ax)
plt.show()