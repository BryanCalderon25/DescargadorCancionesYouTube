import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from youtubesearchpython import VideosSearch
from yt_dlp import YoutubeDL
import re
import difflib
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
import os
from datetime import datetime

# Ruta archivo historial
HISTORIAL_PATH = os.path.join(os.getcwd(), "historial_descargas.txt")
if not os.path.exists(HISTORIAL_PATH):
    with open(HISTORIAL_PATH, 'w', encoding='utf-8') as f:
        f.write("Historial de descargas\n\n")

def registrar_en_historial(titulo, url):
    with open(HISTORIAL_PATH, 'a', encoding='utf-8') as f:
        f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {titulo} - {url}\n")

def centrar_ventana(ventana, ancho, alto):
    ventana.update_idletasks()
    ancho_pantalla = ventana.winfo_screenwidth()
    alto_pantalla = ventana.winfo_screenheight()
    x = (ancho_pantalla // 2) - (ancho // 2)
    y = (alto_pantalla // 2) - (alto // 2)
    ventana.geometry(f"{ancho}x{alto}+{x}+{y}")

def es_cancion_valida(titulo, canal, artista):
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
    titulo = re.sub(r'\(.*?\)|\[.*?\]', '', titulo)
    titulo = re.sub(r'[\\/*?:"<>|]', '', titulo)
    return titulo.strip()

def calcular_duracion_en_segundos(duracion_str):
    partes = list(map(int, duracion_str.split(":")))
    if len(partes) == 3:
        return partes[0] * 3600 + partes[1] * 60 + partes[2]
    elif len(partes) == 2:
        return partes[0] * 60 + partes[1]
    elif len(partes) == 1:
        return partes[0]
    return 0

def buscar_videos(artista, cantidad):
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

            # Filtrar canciones entre 2 y 7 minutos
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

def buscar_videos_previsualizacion(artista, cantidad):
    busqueda = VideosSearch(f"mejores canciones de {artista}", limit=20)
    lista_filtrada = []
    titulos = set()

    while len(lista_filtrada) < cantidad:
        resultado = busqueda.result()
        videos = resultado.get("result", [])
        if not videos:
            break

        for video in videos:
            titulo = video.get("title", "")
            canal = video.get("channel", {}).get("name", "")
            duracion = video.get("duration", "")
            url = video.get("link", "")

            if not duracion:
                continue

            segundos = calcular_duracion_en_segundos(duracion)
            if segundos <= 120 or segundos > 420:
                continue

            titulo_limpio = limpiar_titulo(titulo).lower()

            if not es_cancion_valida(titulo, canal, artista):
                continue

            repetido = any(difflib.SequenceMatcher(None, titulo_limpio, t).ratio() > 0.85 for t in titulos)
            if repetido:
                continue

            titulos.add(titulo_limpio)
            lista_filtrada.append({
                "titulo": titulo,
                "canal": canal,
                "duracion": duracion,
                "url": url
            })

            if len(lista_filtrada) >= cantidad:
                break

        try:
            busqueda.next()
        except Exception:
            break

    return lista_filtrada

def descargar_cancion(url, carpeta_destino):
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
    
    registrar_en_historial(titulo_limpio, url)

def descargar_varias_canciones(urls, estado_var, artista, carpeta_base):
    carpeta_artista = os.path.join(carpeta_base, artista.strip().replace(" ", "_"))
    os.makedirs(carpeta_artista, exist_ok=True)

    with ThreadPoolExecutor(max_workers=3) as ejecutor:
        futuros = [ejecutor.submit(descargar_cancion, url, carpeta_artista) for url in urls]
        for i, futuro in enumerate(as_completed(futuros), 1):
            estado_var.set(f"Descargando canciones... ({i}/{len(urls)})")

    estado_var.set(f"Descarga finalizada en: {carpeta_artista}")

def ver_historial():
    ventana_hist = tk.Toplevel(root)
    ventana_hist.title("Historial de Descargas")
    ventana_hist.resizable(False, False)
    ventana_hist.configure(bg="#121212")
    centrar_ventana(ventana_hist, 600, 400)

    estilo = ttk.Style(ventana_hist)
    estilo.theme_use('clam')
    estilo.configure("TLabel", background="#121212", foreground="#e0e0e0", font=("Segoe UI", 11))
    estilo.configure("TButton", font=("Segoe UI", 11), background="#3f51b5", foreground="white")
    estilo.map("TButton", background=[('active', '#303f9f')])

    texto_historial = tk.Text(ventana_hist, bg="#1e1e2f", fg="white", font=("Segoe UI", 10))
    texto_historial.pack(padx=10, pady=10, fill='both', expand=True)
    texto_historial.config(state='normal')

    try:
        with open(HISTORIAL_PATH, 'r', encoding='utf-8') as f:
            contenido = f.read()
        texto_historial.insert(tk.END, contenido)
    except Exception as e:
        texto_historial.insert(tk.END, f"No se pudo cargar el historial:\n{e}")

    texto_historial.config(state='disabled')

    ttk.Button(ventana_hist, text="Cerrar", command=ventana_hist.destroy).pack(pady=5)

def crear_ventana_descarga():
    ventana = tk.Toplevel(root)
    ventana.title("Descarga con Previsualización")
    ventana.resizable(False, False)
    ventana.configure(bg="#121212")
    centrar_ventana(ventana, 600, 500)

    estilo = ttk.Style(ventana)
    estilo.theme_use('clam')
    estilo.configure("TLabel", background="#121212", foreground="#e0e0e0", font=("Segoe UI", 11))
    estilo.configure("TButton", font=("Segoe UI", 11), background="#3f51b5", foreground="white")
    estilo.map("TButton", background=[('active', '#303f9f')])

    frame_form = ttk.Frame(ventana)
    frame_form.pack(padx=20, pady=15, fill='x')

    ttk.Label(frame_form, text="Nombre del artista:").grid(row=0, column=0, sticky='w')
    entrada_artista = ttk.Entry(frame_form)
    entrada_artista.grid(row=0, column=1, sticky='ew', padx=5)
    frame_form.columnconfigure(1, weight=1)

    ttk.Label(frame_form, text="Cantidad de canciones:").grid(row=1, column=0, sticky='w', pady=10)
    entrada_cantidad = ttk.Entry(frame_form)
    entrada_cantidad.grid(row=1, column=1, sticky='ew', padx=5)

    # Lista para previsualizar canciones (selección múltiple)
    lista_canciones = tk.Listbox(ventana, selectmode=tk.MULTIPLE, bg="#1e1e2f", fg="white", font=("Segoe UI", 10))
    lista_canciones.pack(padx=20, pady=5, fill='both', expand=True)

    estado_var = tk.StringVar()
    ttk.Label(ventana, textvariable=estado_var, font=("Segoe UI", 10, "italic"), background="#121212", foreground="#b0b0b0").pack(pady=5)

    def buscar_y_mostrar():
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

        estado_var.set("Buscando canciones, espere por favor...")
        lista_canciones.delete(0, tk.END)

        def tarea_busqueda():
            try:
                canciones = buscar_videos_previsualizacion(artista, cantidad)
                if not canciones:
                    estado_var.set("No se encontraron canciones válidas.")
                    return

                for i, cancion in enumerate(canciones, 1):
                    titulo = cancion["titulo"]
                    duracion = cancion["duracion"]
                    canal = cancion["canal"]
                    lista_canciones.insert(tk.END, f"{i}. {titulo} ({duracion}) - {canal}")
                lista_canciones.canciones = canciones
                estado_var.set(f"{len(canciones)} canciones encontradas. Seleccione para descargar.")
            except Exception as e:
                estado_var.set(f"Error en la búsqueda: {e}")

        threading.Thread(target=tarea_busqueda).start()

    def seleccionar_todo():
        lista_canciones.select_set(0, tk.END)
        estado_var.set(f"Todas las canciones han sido seleccionadas.")

    def deseleccionar_todo():
        lista_canciones.select_clear(0, tk.END)
        estado_var.set(f"Ninguna canción está seleccionada.")

    def iniciar_descarga():
        seleccionados = lista_canciones.curselection()
        if not seleccionados:
            messagebox.showwarning("Aviso", "Debe seleccionar al menos una canción para descargar.")
            return

        carpeta = filedialog.askdirectory(title="Seleccione la carpeta para guardar las canciones")
        if not carpeta:
            estado_var.set("Descarga cancelada. No se seleccionó carpeta.")
            return

        seleccion = [lista_canciones.canciones[i]["url"] for i in seleccionados]
        artista = entrada_artista.get().strip()

        estado_var.set("Iniciando descarga...")

        def tarea_descarga():
            descargar_varias_canciones(seleccion, estado_var, artista, carpeta)
            messagebox.showinfo("Descarga completa", f"Las canciones seleccionadas fueron descargadas correctamente.\nCarpeta: {carpeta}")
            ventana.destroy()

        threading.Thread(target=tarea_descarga).start()

    frame_botones = ttk.Frame(ventana)
    frame_botones.pack(pady=10, fill='x')

    btn_buscar = ttk.Button(frame_botones, text="Buscar", command=buscar_y_mostrar)
    btn_buscar.pack(side="left", padx=5)

    btn_seleccionar_todo = ttk.Button(frame_botones, text="Seleccionar todo", command=seleccionar_todo)
    btn_seleccionar_todo.pack(side="left", padx=5)

    btn_deseleccionar_todo = ttk.Button(frame_botones, text="Deseleccionar todo", command=deseleccionar_todo)
    btn_deseleccionar_todo.pack(side="left", padx=5)

    btn_descargar = ttk.Button(frame_botones, text="Descargar seleccionadas", command=iniciar_descarga)
    btn_descargar.pack(side="right", padx=5)

# Ventana principal 
root = tk.Tk()
root.title("Gestor de Descargas de Canciones")
root.resizable(False, False)
root.configure(bg="#121212")
centrar_ventana(root, 400, 220)

estilo_principal = ttk.Style(root)
estilo_principal.theme_use('clam')
estilo_principal.configure("TLabel", background="#121212", foreground="#e0e0e0", font=("Segoe UI", 14))
estilo_principal.configure("TButton", font=("Segoe UI", 12), background="#3f51b5", foreground="white")
estilo_principal.map("TButton", background=[('active', '#303f9f')])

ttk.Label(root, text="Gestor de Descargas").pack(pady=20)

frame_botones_principal = ttk.Frame(root)
frame_botones_principal.pack(pady=10, fill='x')

btn_nueva_descarga = ttk.Button(frame_botones_principal, text="Nueva Descarga", command=crear_ventana_descarga)
btn_nueva_descarga.pack(side="left", padx=20, expand=True)

btn_historial = ttk.Button(frame_botones_principal, text="Ver Historial", command=ver_historial)
btn_historial.pack(side="right", padx=20, expand=True)

root.mainloop()
