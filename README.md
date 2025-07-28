# Descargador de Canciones desde YouTube

Este programa en Python permite buscar y descargar canciones oficiales desde YouTube en formato `.mp3`. Tiene filtros para evitar versiones no deseadas como en vivo, covers o remixes. Usa `yt_dlp` para descargar y `ffmpeg` para convertir el audio.

---

## Características

* Busca canciones oficiales por artista automáticamente.
* Filtra resultados no deseados: versiones en vivo, letras, covers, remixes, etc.
* Descarga varias canciones al mismo tiempo con múltiples hilos.
* Convierte a `.mp3` con calidad 192 kbps.
* Interfaz gráfica sencilla con `Tkinter`.
* Guarda las canciones organizadas en carpetas por artista.

---

## Requisitos

* Python 3.8 o superior (Windows 10 o 11).
* Instalar las librerías `yt_dlp` y `youtube-search-python` (desde terminal en modo administrador).
* Tener `ffmpeg` instalado y agregado al `PATH` del sistema.

---

## Instalación

### 1. Instalación de librerías Python

Abrir la terminal como administrador y ejecutar:

```bash
pip install yt_dlp youtube-search-python
```

### 2. Instalar y configurar FFmpeg en Windows

`ffmpeg` es necesario para convertir los archivos a `.mp3`. Para instalarlo:

1. Descargar la versión completa desde:
   [https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-full.7z](https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-full.7z)

2. Extraer el contenido en una carpeta, por ejemplo:
   `C:\ffmpeg`

3. Localizar la subcarpeta:
   `C:\ffmpeg\bin`

4. Agregar esa ruta al `PATH`:

   * Abrir **Configuración avanzada del sistema** → **Variables de entorno**
   * Buscar la variable `Path` en “Variables del sistema” → clic en **Editar**
   * Clic en **Nuevo** y pegar `C:\ffmpeg\bin`
   * Guardar los cambios

5. Comprobar en la terminal:

```bash
ffmpeg -version
```

Si muestra la versión, la instalación fue correcta.

---

## Uso

1. Ejecutar el script `descargar.py`.
2. En la ventana principal, presionar **"Nueva Descarga"**.
3. Ingresar el nombre del artista y la cantidad de canciones a buscar.
4. Elegir la carpeta donde se guardarán las canciones.
5. El programa buscará, descargará y convertirá las canciones a `.mp3`.

---

## Detalles técnicos

* Usa `difflib.SequenceMatcher` para evitar canciones repetidas.
* Limpia los títulos para evitar caracteres inválidos en los archivos.
* Limita duración entre 2 y 7 minutos para evitar versiones no deseadas.
* Usa `ThreadPoolExecutor` para descargar varias canciones sin congelar la interfaz.

---

## Organización del proyecto

* `descargar.py`: script principal con la lógica y la interfaz.
* `es_cancion_valida()`: función que filtra títulos y canales no oficiales o no deseados.
* `buscar_videos()`: busca canciones oficiales desde YouTube.
* `descargar_cancion()`: descarga y convierte una canción.
* `crear_ventana_descarga()`: crea la ventana para ingresar datos y lanzar la descarga.

---


