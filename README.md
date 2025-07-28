# 🎵 Descargador de Canciones desde YouTube

Este programa en Python permite buscar y descargar canciones oficiales desde YouTube en formato `.mp3`. Tiene filtros para evitar versiones no deseadas como en vivo, covers o remixes. Usa `yt_dlp` para descargar y `ffmpeg` para convertir el audio.


## ✅ Características

- Búsqueda automática de canciones oficiales por artista.
- Filtro inteligente para evitar versiones en vivo, lyrics, covers o remixes.
- Descarga en paralelo con múltiples hilos (`ThreadPoolExecutor`).
- Conversión automática a `.mp3` con calidad 192 kbps (`ffmpeg`).
- Interfaz gráfica amigable desarrollada con `Tkinter`.
- Organización de canciones en carpetas por artista.
- Vista previa con opción de selección múltiple antes de descargar.
- Acceso al historial completo de descargas desde la interfaz.


## 💻 Requisitos

- **Python 3.8 o superior** (Windows 10 u 11 recomendado).
- Librerías de Python: `yt_dlp`, `youtube-search-python`.
- Tener `ffmpeg` instalado y agregado al `PATH` del sistema.


## 📦 Instalación

### 1. Instalar librerías de Python

Abre la terminal como administrador y ejecuta:

```bash
pip install yt_dlp youtube-search-python
```

### 2. Instalar y configurar FFmpeg

1. Descarga la versión completa desde:  
   [https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-full.7z](https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-full.7z)

2. Extrae el contenido en una carpeta, por ejemplo:  
   `C:\ffmpeg`

3. Ubica la subcarpeta:  
   `C:\ffmpeg\bin`

4. Agrega esa ruta al `PATH` del sistema:
   - Abre **Configuración avanzada del sistema** → **Variables de entorno**
   - En "Variables del sistema", selecciona la variable `Path` y haz clic en **Editar**
   - Haz clic en **Nuevo** y pega: `C:\ffmpeg\bin`
   - Guarda los cambios

5. Verifica la instalación:

```bash
ffmpeg -version
```

Si muestra la versión, la instalación fue exitosa.


## 🚀 Uso del programa

1. Ejecuta el script `descargar.py`.
2. En la ventana principal, haz clic en **"Nueva Descarga"**.
3. Ingresa el **nombre del artista** y la **cantidad de canciones** a buscar.
4. Selecciona las canciones desde la lista de resultados mostrada.
5. Elige una carpeta para guardar los archivos descargados.
6. El programa descargará y convertirá las canciones seleccionadas a `.mp3`.
7. Puedes ver el historial completo haciendo clic en **"Ver Historial"**.



## ⚙️ Detalles técnicos

- Utiliza `difflib.SequenceMatcher` para detectar y evitar canciones repetidas.
- Limpieza de nombres de archivos para evitar errores por caracteres inválidos.
- Filtro de duración: solo canciones entre **2 y 7 minutos**.
- Interfaz fluida gracias al uso de `ThreadPoolExecutor`.
- Filtros aplicados por título, canal, duración y coincidencia de artista.
- Historial guardado automáticamente en `historial_descargas.txt`.



## 🗂️ Organización del Proyecto

descargar.py: Script principal con la lógica e interfaz del programa.

es_cancion_valida(): Filtra títulos y canales no oficiales o no deseados.

buscar_videos(): Busca canciones oficiales en YouTube.

buscar_videos_previsualizacion(): Lista canciones para previsualización y selección.

descargar_cancion(): Descarga y convierte una canción a .mp3.

descargar_varias_canciones(): Controla múltiples descargas con barra de progreso.

registrar_en_historial(): Guarda título, fecha y URL en el historial.

crear_ventana_descarga(): Ventana para ingresar datos y seleccionar canciones.

ver_historial(): Muestra el historial completo en una ventana emergente.
