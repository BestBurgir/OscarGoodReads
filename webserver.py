from functools import cached_property  # Importa la función cached_property del módulo functools
from http.cookies import SimpleCookie  # Importa la clase SimpleCookie del módulo http.cookies
from http.server import BaseHTTPRequestHandler, HTTPServer  # Importa las clases BaseHTTPRequestHandler y HTTPServer del módulo http.server
from urllib.parse import parse_qsl, urlparse  # Importa las funciones parse_qsl y urlparse del módulo urllib.parse
import re  # Importa el módulo re para trabajar con expresiones regulares
import redis  # Importa el módulo redis para interactuar con una base de datos Redis
import uuid  # Importa el módulo uuid para generar identificadores únicos

# Lista de rutas y los métodos correspondientes
mappings = [
    (r"^/books/(?P<book_id>\d+)$", "get_book"),  # Ruta para obtener información de un libro
    (r"^/search", "get_by_search"),  # Ruta para buscar libros
    (r"^/$", "index"),  # Ruta de la página de inicio
]

# Conexión a la base de datos Redis
r = redis.StrictRedis(host="localhost", port=6379, db=0)

# Clase que maneja las solicitudes HTTP
class WebRequestHandler(BaseHTTPRequestHandler):
    @property
    def query_data(self):  # Propiedad para obtener los datos de la consulta de la URL
        return dict(parse_qsl(self.url.query))

    @property
    def url(self):  # Propiedad para obtener la URL de la solicitud
        return urlparse(self.path)

    # Método para procesar la búsqueda de libros
    def search(self):
        self.send_response(200)  # Enviar respuesta con código de éxito
        self.send_header("content-type", "text/html")  # Enviar encabezado de tipo de contenido
        self.end_headers()  # Finalizar los encabezados de la respuesta
        index_page = f"<h1>{self.query_data['q'].split()}</h1>".encode("utf-8")  # Crear contenido HTML de la respuesta
        self.wfile.write(index_page)  # Escribir el contenido en el cuerpo de la respuesta
    
    # Método para obtener las cookies de la solicitud HTTP
    def cookies(self):
        return SimpleCookie(self.headers.get("Cookie"))  # Devuelve las cookies como un objeto SimpleCookie

    # Método para obtener o crear un ID de sesión
    def get_session(self):
        cookies = self.cookies()  # Obtener las cookies de la solicitud
        if not cookies:  # Si no hay cookies en la solicitud
            session_id = uuid.uuid4()  # Generar un nuevo ID de sesión
        else:  # Si hay cookies en la solicitud
            session_id = cookies["session_id"].value  # Obtener el valor del ID de sesión de las cookies
        return session_id  # Devolver el ID de sesión

    # Método para escribir una cookie en la respuesta HTTP
    def write_session_cookie(self, session_id):
        cookies = SimpleCookie()  # Crear un objeto SimpleCookie
        cookies["session_id"] = session_id  # Establecer el valor del ID de sesión en la cookie
        cookies["session_id"]["max-age"] = 1000  # Establecer la duración máxima de la cookie
        self.send_header("Set-Cookie", cookies.output(header=""))  # Enviar la cookie en el encabezado de la respuesta

    # Maneja las solicitudes GET
    def do_GET(self):
        self.url_mapping_response()  # Procesar la solicitud según la URL

    # Mapea las URL a los métodos correspondientes y maneja la respuesta
    def url_mapping_response(self):
        for pattern, method in mappings:  # Iterar sobre las rutas y métodos definidos
            match = self.get_params(pattern, self.path)  # Obtener los parámetros de la URL según el patrón
            if match is not None:  # Si se encuentra una coincidencia de URL
                md = getattr(self, method)  # Obtener el método correspondiente al patrón
                md(**match)  # Llamar al método con los parámetros obtenidos
                return  # Salir del bucle después de procesar la solicitud
            
        self.send_response(404)  # Enviar respuesta de recurso no encontrado
        self.end_headers()  # Finalizar los encabezados de la respuesta
        self.wfile.write("Not Found".encode("utf-8"))  # Escribir mensaje de error en el cuerpo de la respuesta

    # Obtiene los parámetros de la URL según un patrón de expresión regular
    def get_params(self, pattern, path):
        match = re.match(pattern, path)  # Buscar coincidencias del patrón en la URL
        if match:  # Si se encuentra una coincidencia
            return match.groupdict()  # Devolver los
# Muestra la página de inicio con un formulario de búsqueda
def index(self):
    self.send_response(200)  # Enviar respuesta con código de éxito
    self.send_header("Content-Type", "text/html")  # Enviar encabezado de tipo de contenido
    self.end_headers()  # Finalizar los encabezados de la respuesta
    with open('html/index.html') as f:  # Abrir el archivo HTML de la página de inicio
        response = f.read()  # Leer el contenido del archivo
    self.wfile.write(response.encode("utf-8"))  # Escribir el contenido en el cuerpo de la respuesta

# Maneja la búsqueda de libros y muestra los resultados
def get_by_search(self):
    if self.query_data and 'q' in self.query_data:  # Verificar si hay datos de consulta y si la clave 'q' está presente
        booksInter = r.sinter(self.query_data['q'].split(' '))  # Obtener la intersección de conjuntos de libros basada en la consulta
        lista = []
        for b in booksInter:  # Decodificar los resultados y agregarlos a una lista
            y = b.decode()
            lista.append(y)
    
        if not lista:  # Si la lista está vacía
            self.index()  # Redirigir a la página de inicio
        else:
            for book in lista:  # Procesar cada libro encontrado
                self.get_book(book)  # Obtener información detallada del libro

    self.send_response(200)  # Enviar respuesta con código de éxito
    self.send_header('Content-type', 'text/html')  # Enviar encabezado de tipo de contenido
    self.end_headers()  # Finalizar los encabezados de la respuesta

# Obtiene recomendaciones de libros para el usuario basadas en su historial de lectura
def get_recomendation(self, session_id, book_id):
    books = r.lrange(f"session:{session_id}", 0, -1)  # Obtener la lista de libros leídos por el usuario
    books_read = {book.decode('utf-8').split(':')[1] for book in books}  # Crear un conjunto de libros leídos
    all_books = {'1', '2', '3', '4', '5'}  # Lista de todos los libros disponibles
    books_to_recommend = all_books - books_read  # Calcular los libros que aún no se han leído
    if len(books_read) >= 3:  # Si el usuario ha leído al menos 3 libros
        if books_to_recommend:  # Si hay libros disponibles para recomendar
            return f"Te recomendamos leer el libro : {books_to_recommend.pop()}"  # Devolver la recomendación
        else: 
            return "Ya has leido todos los libros"  # Indicar que el usuario ha leído todos los libros disponibles
    else:
        return "Lee al menos tres libros para obtener recomendaciones"  # Indicar que el usuario debe leer más libros para recibir recomendaciones

# Obtiene información sobre un libro y muestra la información al usuario
def get_book(self, book_id):
    session_id = self.get_session()  # Obtener el ID de sesión del usuario
    r.lpush(f"session:{session_id}", f"book:{book_id}")  # Agregar el libro a la lista de libros leídos por el usuario
    book_recomendation = self.get_recomendation(session_id, book_id)  # Obtener una recomendación de libro para el usuario
    self.send_response(200)  # Enviar respuesta con código de éxito
    self.send_header("Content-Type", "text/html")  # Enviar encabezado de tipo de contenido
    self.write_session_cookie(session_id)  # Escribir una cookie con el ID de sesión
    self.end_headers()  # Finalizar los encabezados de la respuesta

    book_info = r.get(f"book:{book_id}")  # Obtener información detallada del libro
    if book_info is not None:
        book_info = book_info.decode('utf-8')  # Decodificar la información del libro
    else:
        book_info = "<h1>No existe el libro</h1>"  # Indicar que el libro no existe

    self.wfile.write(str(book_info).encode("utf-8"))  # Escribir la información del libro en el cuerpo de la respuesta
    
    self.wfile.write(f"session:{session_id}\n".encode("utf-8"))  # Escribir el ID de sesión en el cuerpo de la respuesta
    
    book_list = r.lrange(f"session:{session_id}", 0, -1)  # Obtener la lista de libros leídos por el usuario
    for book in book_list:  # Iterar sobre la lista de libros leídos
        book_id = book.decode('utf-8')  # Decodificar el ID del libro
        self.wfile.write(book_id.encode('utf-8'))  # Escribir el ID del libro en el cuerpo de la respuesta

    if book_recomendation:  # Si hay una recomendación de libro
       self.wfile.write(f"<p>Recomendacion:{book_recomendation}</p            .encode('utf-8'))  # Escribir la recomendación en el cuerpo de la respuesta

# Mensaje de inicio del servidor
print("Server starting.")
# Crear una instancia del servidor HTTP en el puerto 8000 y usar WebRequestHandler para manejar las solicitudes
server = HTTPServer(("0.0.0.0", 8000), WebRequestHandler)
# Iniciar el servidor y mantenerlo en funcionamiento
server.serve_forever()


