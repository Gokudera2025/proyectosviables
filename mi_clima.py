
from tkinter import *
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import requests
import json

# Cargar las ciudades desde el archivo JSON
with open("ciudades_chile.json", "r", encoding="utf-8") as f:
    ciudades_data = json.load(f)

ciudades_nombres = [c["ciudad"] for c in ciudades_data]

# Crear ventana principal
ventana = Tk()
ventana.title("MiClima")
ventana.geometry("750x500")
ventana.configure(bg="#cceeff")

# Función para obtener coordenadas de ciudad
def obtener_coordenadas(nombre_ciudad):
    for ciudad in ciudades_data:
        if ciudad["ciudad"] == nombre_ciudad:
            return ciudad["lat"], ciudad["lon"]
    return None, None

# Función para obtener el clima
def consultar_clima():
    ciudad = combo_ciudades.get()
    lat, lon = obtener_coordenadas(ciudad)
    if lat is None:
        messagebox.showerror("Error", "Ciudad no encontrada.")
        return

    url = (
        f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}"
        "&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,windspeed_10m_max,weathercode"
        "&timezone=auto"
    )
    try:
        respuesta = requests.get(url)
        datos = respuesta.json()
        mostrar_clima(datos)
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo obtener el clima.\n{e}")

# Función para interpretar weathercode y retornar texto
def obtener_icono_weathercode(codigo):
    codigos = {
        0: "☀️ Despejado",
        1: "🌤 Parcialmente nublado",
        2: "⛅ Nublado",
        3: "☁️ Muy nublado",
        45: "🌫 Niebla",
        51: "🌧 Lluvia ligera",
        61: "🌧 Lluvia moderada",
        71: "❄️ Nieve",
        80: "🌧 Chubascos"
    }
    return codigos.get(codigo, "❓ Desconocido")

# Mostrar clima en la tabla
def mostrar_clima(datos):
    for row in tabla.get_children():
        tabla.delete(row)

    fechas = datos["daily"]["time"]
    temp_max = datos["daily"]["temperature_2m_max"]
    temp_min = datos["daily"]["temperature_2m_min"]
    viento = datos["daily"]["windspeed_10m_max"]
    weather = datos["daily"]["weathercode"]

    for i in range(len(fechas)):
        icono = obtener_icono_weathercode(weather[i])
        tabla.insert("", "end", values=(
            fechas[i], icono, f"{temp_max[i]}°C", f"{temp_min[i]}°C", f"{viento[i]} km/h"
        ))

# Elementos de la interfaz
titulo = Label(ventana, text="MiClima - Chile", font=("Helvetica", 20, "bold"), bg="#cceeff")
titulo.pack(pady=10)

frame = Frame(ventana, bg="#cceeff")
frame.pack(pady=5)

label_ciudad = Label(frame, text="Selecciona ciudad:", bg="#cceeff")
label_ciudad.pack(side=LEFT, padx=5)

combo_ciudades = ttk.Combobox(frame, values=ciudades_nombres, width=30)
combo_ciudades.set("Santiago")
combo_ciudades.pack(side=LEFT, padx=5)

boton_consultar = Button(frame, text="Consultar clima", bg="#66b3ff", command=consultar_clima)
boton_consultar.pack(side=LEFT, padx=10)

# Tabla de clima
tabla = ttk.Treeview(ventana, columns=("Fecha", "Estado", "Máx", "Mín", "Viento"), show="headings")
tabla.heading("Fecha", text="Fecha")
tabla.heading("Estado", text="Estado")
tabla.heading("Máx", text="Temp Máx")
tabla.heading("Mín", text="Temp Mín")
tabla.heading("Viento", text="Viento")

tabla.pack(pady=15, fill=BOTH, expand=True)

ventana.mainloop()
