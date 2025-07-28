import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from youtubesearchpython import VideosSearch
from yt_dlp import YoutubeDL
import re
import difflib
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
import os

def centrar_ventana(ventana, ancho, alto):
    ventana.update_idletasks()
    ancho_pantalla = ventana.winfo_screenwidth()
    alto_pantalla = ventana.winfo_screenheight()
    x = (ancho_pantalla // 2) - (ancho // 2)
    y = (alto_pantalla // 2) - (alto // 2)
    ventana.geometry(f"{ancho}x{alto}+{x}+{y}")

def es_cancion_valida(titulo, canal, artista):
    """
    Verifica si un video es válido para descargar como canción oficial,
    filtrando versiones no deseadas como en vivo, remix, karaoke, etc.
    """
    titulo_lower = titulo.lower()
    canal_lower = canal.lower()
    artista_lower = artista.lower()
    filtros_no_deseados = ['en vivo', 'live', 'mix', 'lyric', 'cover', 'karaoke', 'instrumental', 'remix']

    if any(filtro in titulo_lower for filtro in filtros_no_deseados) or any(filtro in canal_lower for filtro in filtros_no_deseados):
        return False

    es_oficial = ('official' in titulo_lower) or ('video oficial' in titulo_lower) or ('official' in canal_lower) or ('oficial' in canal_lower)
    if es_oficial:
        return True

    if artista_lower in titulo_lower or artista_lower in canal_lower:
        return True

    similitud = difflib.SequenceMatcher(None, artista_lower, titulo_lower).ratio()
    return similitud >= 0.3

def limpiar_titulo(titulo):
    """
    Elimina textos entre paréntesis o corchetes y caracteres inválidos en el nombre del archivo.
    """
    titulo = re.sub(r'\(.*?\)|\[.*?\]', '', titulo)
    titulo = re.sub(r'[\\/*?:"<>|]', '', titulo)
    return titulo.strip()

def calcular_duracion_en_segundos(duracion_str):
    """
    Convierte una duración de video en formato HH:MM:SS o MM:SS a segundos.
    """
    partes = list(map(int, duracion_str.split(":")))
    if len(partes) == 3:
        return partes[0] * 3600 + partes[1] * 60 + partes[2]
    elif len(partes) == 2:
        return partes[0] * 60 + partes[1]
    elif len(partes) == 1:
        return partes[0]
    return 0

def buscar_videos(artista, cantidad):
    """
    Busca videos en YouTube relacionados con el artista y filtra los que son canciones oficiales,
    que cumplen con duración y que no están repetidos.
    """
    busqueda = VideosSearch(f"mejores canciones de {artista}", limit=20)
    titulos_filtrados = []
    urls = []

    while len(urls) < cantidad:
        resultado = busqueda.result()
        if not resultado or "result" not in resultado:
            break

        videos = resultado["result"]
        if not videos:
            break

        for video in videos:
            titulo = video.get("title", "")
            canal = video.get("channel", {}).get("name", "")
            duracion = video.get("duration", "")

            if not duracion:
                continue


            segundos = calcular_duracion_en_segundos(duracion)
            """
    Busca videos que sean mayores a 2 minutos y menores a 7 minutos.
    """
            if segundos <= 120: 
                continue
            if segundos > 420:
                continue

            titulo_limpio = limpiar_titulo(titulo).lower()

            if not es_cancion_valida(titulo, canal, artista):
                continue

            repetido = any(difflib.SequenceMatcher(None, titulo_limpio, t).ratio() > 0.85 for t in titulos_filtrados)
            if repetido:
                continue

            titulos_filtrados.append(titulo_limpio)
            urls.append(video.get("link", ""))

            if len(urls) >= cantidad:
                break

        try:
            busqueda.next()
        except Exception:
            break

    return urls

def descargar_cancion(url, carpeta_destino):
    """
    Descarga el audio de un video de YouTube en formato mp3 en la carpeta indicada.
    """
    try:
        with YoutubeDL({'quiet': True}) as ydl:
            info = ydl.extract_info(url, download=False)
            titulo = info.get('title', f'youtube_{info.get("id", "sin_nombre")}')
    except Exception:
        titulo = f'youtube_{url.split("=")[-1]}'

    titulo_limpio = limpiar_titulo(titulo)

    opciones_descarga = {
        'format': 'bestaudio/best',
        'quiet': True,
        'outtmpl': os.path.join(carpeta_destino, f'{titulo_limpio}.%(ext)s'),
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'noplaylist': True,
    }

    with YoutubeDL(opciones_descarga) as ydl:
        ydl.download([url])

def descargar_varias_canciones(urls, estado_var, artista, carpeta_base):
    """
    Gestiona la descarga de varias canciones en paralelo usando hilos.
    Actualiza la variable de estado con el progreso.
    """
    carpeta_artista = os.path.join(carpeta_base, artista.strip().replace(" ", "_"))
    os.makedirs(carpeta_artista, exist_ok=True)

    with ThreadPoolExecutor(max_workers=3) as ejecutor:
        futuros = [ejecutor.submit(descargar_cancion, url, carpeta_artista) for url in urls]
        for i, futuro in enumerate(as_completed(futuros), 1):
            estado_var.set(f"Descargando canciones... ({i}/{len(urls)})")

    estado_var.set(f"Descarga finalizada en: {carpeta_artista}")

def crear_ventana_descarga():
    ventana = tk.Toplevel(root)
    ventana.title("Nueva Descarga")
    ventana.resizable(False, False)
    ventana.configure(bg="#1e1e2f")
    centrar_ventana(ventana, 500, 300)

    estilo = ttk.Style(ventana)
    estilo.theme_use('clam')
    estilo.configure("TLabel", background="#1e1e2f", foreground="#ffffff", font=("Arial", 12))
    estilo.configure("TEntry", font=("Arial", 12))
    estilo.configure("TButton", font=("Arial", 12), background="#4caf50", foreground="white")
    estilo.map("TButton", background=[('active', '#45a049')])

    ttk.Label(ventana, text="Descarga de Canciones Oficiales").pack(pady=15)

    frame_form = ttk.Frame(ventana)
    frame_form.pack(pady=10, padx=20, fill='x')

    ttk.Label(frame_form, text="Nombre del artista:").grid(row=0, column=0, sticky='w')
    entrada_artista = ttk.Entry(frame_form)
    entrada_artista.grid(row=0, column=1, sticky='ew', padx=5)
    frame_form.columnconfigure(1, weight=1)

    ttk.Label(frame_form, text="Cantidad de canciones:").grid(row=1, column=0, sticky='w', pady=10)
    entrada_cantidad = ttk.Entry(frame_form)
    entrada_cantidad.grid(row=1, column=1, sticky='ew', padx=5)

    estado_var = tk.StringVar()
    ttk.Label(ventana, textvariable=estado_var, font=("Arial", 10, "italic")).pack(pady=10)

    def iniciar_descarga():
        artista = entrada_artista.get().strip()
        cantidad_str = entrada_cantidad.get().strip()

        if not artista:
            messagebox.showwarning("Aviso", "Por favor, ingrese el nombre del artista.")
            return

        try:
            cantidad = int(cantidad_str)
            if cantidad <= 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Aviso", "Cantidad inválida. Debe ser un número entero positivo.")
            return

        carpeta = filedialog.askdirectory(title="Seleccione la carpeta para guardar las canciones")
        if not carpeta:
            estado_var.set("Descarga cancelada. No se seleccionó carpeta.")
            return

        estado_var.set("Buscando canciones, espere por favor...")

        def tarea_busqueda_descarga():
            try:
                urls = buscar_videos(artista, cantidad)
                if not urls:
                    estado_var.set("No se encontraron canciones válidas.")
                    return
                estado_var.set(f"{len(urls)} canciones encontradas. Iniciando descarga...")
                descargar_varias_canciones(urls, estado_var, artista, carpeta)
                ventana.destroy()  # Cierra la ventana secundaria al terminar la descarga
            except Exception as e:
                estado_var.set(f"Error en la búsqueda o descarga: {e}")

        threading.Thread(target=tarea_busqueda_descarga).start()

    ttk.Button(ventana, text="Buscar y Descargar", command=iniciar_descarga).pack(pady=15)

# Ventana principal
root = tk.Tk()
root.title("Gestor de Descargas de Canciones")
root.resizable(False, False)
root.configure(bg="#1e1e2f")
centrar_ventana(root, 400, 200)

estilo_principal = ttk.Style(root)
estilo_principal.theme_use('clam')
estilo_principal.configure("TLabel", background="#1e1e2f", foreground="#ffffff", font=("Arial", 12))
estilo_principal.configure("TButton", font=("Arial", 12), background="#4caf50", foreground="white")
estilo_principal.map("TButton", background=[('active', '#45a049')])

ttk.Label(root, text="Descargador de Canciones - Múltiples Búsquedas").pack(pady=30)
ttk.Button(root, text="Nueva Descarga", command=crear_ventana_descarga).pack(pady=20)

root.mainloop()
