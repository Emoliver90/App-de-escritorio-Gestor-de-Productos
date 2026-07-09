"""Capa de acceso a datos de la aplicación Gestor de Productos.

Este módulo centraliza todas las operaciones contra la base de datos
SQLite (crear, leer, actualizar y eliminar productos). Mantenerlo
separado de app.py sigue el principio de "separación de
responsabilidades": la interfaz gráfica no necesita saber cómo se
guardan los datos, solo qué operaciones puede pedir.
"""

import sqlite3
from pathlib import Path

# BASE_DIR apunta siempre a la carpeta donde está este archivo,
# sin importar desde qué directorio se ejecute el programa.
BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "data" / "productos.db"

# Única fuente de verdad para las categorías: se usa tanto en el
# formulario de alta como en el de edición, así evitamos que se
# desincronicen si se añade una categoría nueva en el futuro.
CATEGORIAS = ("Moviles", "Tecnologia", "Alimentos", "Deportes")


class ProductoRepository:
    """Encapsula las operaciones CRUD sobre la tabla `producto`."""

    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._crear_tabla_si_no_existe()

    def _crear_tabla_si_no_existe(self) -> None:
        """Crea la tabla `producto` si la base de datos está vacía o es nueva.

        Esto hace que la app funcione "de fábrica" (por ejemplo, recién
        clonada de GitHub sin base de datos previa) y evita el error
        "no such table: producto" si el archivo .db no tenía el esquema.
        Si la tabla ya existe (tu base de datos real con tus productos),
        esta instrucción no hace nada y tus datos quedan intactos.
        """
        with sqlite3.connect(self.db_path) as con:
            con.execute(
                """
                CREATE TABLE IF NOT EXISTS producto (
                    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT NOT NULL UNIQUE,
                    precio REAL NOT NULL,
                    categoria TEXT NOT NULL,
                    stock INTEGER NOT NULL
                )
                """
            )
            con.commit()

    def _ejecutar(self, consulta: str, parametros: tuple = ()):
        """Abre conexión, ejecuta una consulta y confirma los cambios.

        Se abre y cierra una conexión por consulta. Para una app de
        escritorio de un único usuario esto es simple y seguro; si el
        proyecto creciera (más usuarios, más consultas por segundo)
        convendría reutilizar una conexión o usar un pool.
        """
        with sqlite3.connect(self.db_path) as con:
            cursor = con.cursor()
            resultado = cursor.execute(consulta, parametros)
            con.commit()
            return resultado.fetchall()

    def listar(self):
        """Devuelve todos los productos ordenados por id."""
        return self._ejecutar("SELECT * FROM producto ORDER BY id ASC")

    def existe(self, nombre: str) -> bool:
        """True si ya hay un producto con ese nombre (sin distinguir mayúsculas)."""
        resultado = self._ejecutar(
            "SELECT 1 FROM producto WHERE LOWER(nombre) = LOWER(?)", (nombre,)
        )
        return bool(resultado)

    def crear(self, nombre: str, precio: float, categoria: str, stock: int) -> None:
        self._ejecutar(
            "INSERT INTO producto (nombre, precio, categoria, stock) VALUES (?, ?, ?, ?)",
            (nombre, precio, categoria, stock),
        )

    def actualizar(self, nombre_actual: str, nombre_nuevo: str, precio_nuevo, categoria_nueva: str) -> None:
        self._ejecutar(
            "UPDATE producto SET nombre = ?, precio = ?, categoria = ? WHERE nombre = ?",
            (nombre_nuevo, precio_nuevo, categoria_nueva, nombre_actual),
        )

    def eliminar(self, nombre: str) -> None:
        self._ejecutar("DELETE FROM producto WHERE nombre = ?", (nombre,))
