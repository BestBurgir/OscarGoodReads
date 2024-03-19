import os
import re
import redis
from bs4 import BeautifulSoup

# Conexión a Redis
r = redis.StrictRedis(host="localhost", port=6379, db=0)

# Función para cargar el contenido de un directorio en Redis
def load_dir(path):
    files = os.listdir(path)

    for f in files:
        # Verificar si el nombre del archivo corresponde al formato esperado
        match = re.match(r"^book(\d+).html$", f)
        if match is not None:
            with open(path + f) as file:
                html = file.read()
                book_id = match.group(1)
                # Crear el índice para la búsqueda de palabras
                create_index(book_id, html)
                # Guardar el contenido del libro en Redis
                r.set(f"book:{book_id}", html)
                print(f"{file} loaded into redis")

# Función para crear un índice de palabras para búsqueda
def create_index(book_id, html):
    soup = BeautifulSoup(html, 'html.parser')
    # Obtener el texto del HTML y dividirlo en palabras
    ts = soup.get_text().split(' ')
    for t in ts:
        # Agregar el ID del libro a un conjunto asociado a cada palabra
        r.sadd(t, book_id)

# Cargar los archivos HTML de libros en el directorio "html/books/" en Redis
load_dir("html/books/")
