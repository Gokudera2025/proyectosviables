import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
import requests
import pandas as pd
import folium
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# Variable global para resultados
df_resultados = pd.DataFrame()

def obtener_sismos_chile(fecha_inicio, fecha_fin, magnitud_minima=3.0):
    url = "https://earthquake.usgs.gov/fdsnws/event/1/query"
    parametros = {
        "format": "geojson",
        "starttime": fecha_inicio,
        "endtime": fecha_fin,
        "minlatitude": -56,
        "maxlatitude": -17,
        "minlongitude": -75,
        "maxlongitude": -66,
        "minmagnitude": magnitud_minima
    }
    respuesta = requests.get(url, params=parametros)
    datos = respuesta.json()

    sismos = []
    for evento in datos["features"]:
        propiedades = evento["properties"]
        coordenadas = evento["geometry"]["coordinates"]
        sismos.append({
            "Lugar": propiedades["place"],
            "Magnitud": propiedades["mag"],
            "Fecha y hora": datetime.utcfromtimestamp(propiedades["time"] / 1000).strftime('%Y-%m-%d %H:%M:%S'),
            "Latitud": coordenadas[1],
            "Longitud": coordenadas[0]
        })

    return pd.DataFrame(sismos)

def mostrar_mapa_sismos(df):
    mapa = folium.Map(location=[-33.5, -70.7], zoom_start=4)
    for _, fila in df.iterrows():
        popup = f"{fila['Lugar']}<br>Magnitud: {fila['Magnitud']}<br>{fila['Fecha y hora']}"
        color = "red" if fila["Magnitud"] >= 5.0 else "orange"
        folium.CircleMarker(
            location=[fila["Latitud"], fila["Longitud"]],
            radius=5 + fila["Magnitud"],
            popup=popup,
            color=color,
            fill=True,
            fill_opacity=0.7
        ).add_to(mapa)
    mapa.save("sismos_chile.html")
    messagebox.showinfo("Mapa generado", "🗺️ El mapa ha sido guardado como 'sismos_chile.html'.")

def generar_pdf(df):
    if df.empty:
        messagebox.showwarning("Advertencia", "No hay datos para generar el PDF.")
        return

    archivo = "informe_sismos.pdf"
    c = canvas.Canvas(archivo, pagesize=letter)
    c.setFont("Helvetica", 12)
    c.drawString(30, 750, "Informe de Sismicidad en Chile")
    c.drawString(30, 735, f"Total de eventos: {len(df)}")
    c.drawString(30, 720, f"Fecha de generación: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    y = 700
    for _, fila in df.iterrows():
        linea = f"{fila['Fecha y hora']} | Mag: {fila['Magnitud']} | {fila['Lugar']}"
        c.drawString(30, y, linea)
        y -= 15
        if y < 40:
            c.showPage()
            y = 750

    c.save()
    messagebox.showinfo("Informe generado", f"📄 PDF guardado como {archivo}")

def buscar():
    inicio = fecha_inicio.get()
    fin = fecha_fin.get()
    try:
        mag = float(magnitud.get())
    except ValueError:
        messagebox.showerror("Error", "La magnitud debe ser un número.")
        return

    try:
        resultados = obtener_sismos_chile(inicio, fin, mag)
        for fila in tabla.get_children():
            tabla.delete(fila)
        if resultados.empty:
            messagebox.showinfo("Sin datos", "No se encontraron sismos.")
        else:
            for _, row in resultados.iterrows():
                tabla.insert("", "end", values=list(row))
            global df_resultados
            df_resultados = resultados
    except Exception as e:
        messagebox.showerror("Error", f"Ocurrió un error: {e}")

def generar_mapa():
    if df_resultados.empty:
        messagebox.showwarning("Advertencia", "No hay datos para generar el mapa.")
    else:
        mostrar_mapa_sismos(df_resultados)

# === Interfaz gráfica ===
ventana = tk.Tk()
ventana.title("Monitor de Sismicidad en Chile")
ventana.geometry("980x600")

tk.Label(ventana, text="Fecha Inicio:").grid(row=0, column=0, padx=10, pady=10)
fecha_inicio = DateEntry(ventana, width=12, background='darkblue', foreground='white', borderwidth=2)
fecha_inicio.grid(row=0, column=1)

tk.Label(ventana, text="Fecha Fin:").grid(row=0, column=2, padx=10)
fecha_fin = DateEntry(ventana, width=12, background='darkblue', foreground='white', borderwidth=2)
fecha_fin.grid(row=0, column=3)

tk.Label(ventana, text="Magnitud mínima:").grid(row=0, column=4, padx=10)
magnitud = tk.Entry(ventana, width=5)
magnitud.insert(0, "3.0")
magnitud.grid(row=0, column=5)

tk.Button(ventana, text="Buscar Sismos", command=buscar, bg="lightblue").grid(row=0, column=6, padx=10)
tk.Button(ventana, text="Generar Mapa", command=generar_mapa, bg="lightgreen").grid(row=0, column=7, padx=10)
tk.Button(ventana, text="Generar PDF", command=lambda: generar_pdf(df_resultados), bg="lightgray").grid(row=0, column=8, padx=10)

# Tabla de resultados
cols = ("Lugar", "Magnitud", "Fecha y hora", "Latitud", "Longitud")
tabla = ttk.Treeview(ventana, columns=cols, show='headings')
for col in cols:
    tabla.heading(col, text=col)
    tabla.column(col, anchor="center")
tabla.grid(row=1, column=0, columnspan=9, sticky="nsew", padx=10, pady=20)

ventana.grid_rowconfigure(1, weight=1)
ventana.grid_columnconfigure(8, weight=1)

ventana.mainloop()
