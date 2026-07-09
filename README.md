# 🛒 App Gestor de Productos

Aplicación de escritorio para gestionar un inventario de productos (alta, edición, baja y listado), desarrollada en **Python** con **Tkinter** para la interfaz gráfica y **SQLite** como base de datos.

![Python](https://img.shields.io/badge/Python-3.12%2B-blue)
![Tkinter](https://img.shields.io/badge/GUI-Tkinter-orange)
![SQLite](https://img.shields.io/badge/DB-SQLite-lightgrey)

## ✨ Funcionalidades

- **Alta de productos**: nombre, precio, categoría y stock, con validación de cada campo.
- **Listado en tabla** (Treeview) ordenado por id, con estilo personalizado.
- **Edición** de un producto seleccionado (nombre, precio y categoría).
- **Eliminación** de un producto seleccionado.
- Persistencia en una base de datos **SQLite** local.

## 📂 Estructura del proyecto

```
.
├── app.py            # Interfaz gráfica (Tkinter) y flujo de la aplicación
├── database.py        # Capa de acceso a datos (ProductoRepository) sobre SQLite
├── data/
│   └── productos.db   # Base de datos SQLite (se crea sola si no existe)
├── Recursos/
│   └── icon.ico        # Icono de la ventana (solo se aplica en Windows)
└── README.md
```

La separación entre `app.py` (interfaz) y `database.py` (datos) sigue el principio de
**separación de responsabilidades**: la interfaz no sabe cómo se guardan los productos,
solo pide operaciones (`listar`, `crear`, `actualizar`, `eliminar`) a través de
`ProductoRepository`.

## 🚀 Instalación y uso

1. Cloná el repositorio:
   ```bash
   git clone https://github.com/tu-usuario/gestor-productos.git
   cd gestor-productos
   ```
2. Este proyecto solo usa la librería estándar de Python (`tkinter`, `sqlite3`), así que
   no hace falta instalar dependencias externas. Solo necesitás Python 3.10 o superior
   con Tkinter disponible (en Linux, si no lo tenés: `sudo apt install python3-tk`).
3. Ejecutá la aplicación:
   ```bash
   python3 app.py
   ```

La base de datos `data/productos.db` se crea automáticamente en el primer arranque si no existe.

## 🛠️ Tecnologías

- Python 3
- Tkinter / ttk (interfaz gráfica)
- SQLite3 (persistencia)

## 🧭 Mejoras futuras

Estas son mejoras que tiene sentido abordar en próximas versiones, pero que quedan
fuera del alcance de esta primera versión "limpia" del proyecto:

- **Tests automatizados**: agregar pruebas unitarias para `ProductoRepository` (usando
  una base de datos SQLite en memoria, `sqlite3.connect(":memory:")`) y pruebas de
  validación del formulario, para evitar regresiones como el bug de validación que
  tenía la versión anterior.
- **Editar precio y stock desde el mismo formulario de edición**: hoy `stock` no se
  puede modificar en `VentanaEditarProducto`.
- **Logging en vez de `print`**: usar el módulo `logging` con niveles (INFO, ERROR) en
  lugar de `print()` para poder diagnosticar problemas en producción.
- **Manejo de errores más específico**: capturar `sqlite3.OperationalError` /
  `sqlite3.DatabaseError` en vez de un `Exception` genérico al crear un producto.
- **Confirmación antes de eliminar**: agregar un `messagebox.askyesno` antes de borrar
  un producto, para evitar borrados accidentales.
- **Búsqueda y filtrado real por categoría**: actualmente el combobox de categoría no
  filtra la tabla, solo refresca el listado completo.
- **Empaquetado como ejecutable**: generar un `.exe` (Windows) o binario (Linux/Mac)
  con `PyInstaller` para distribuir la app sin necesitar Python instalado.
- **Migraciones de base de datos**: si el esquema crece, usar una librería simple de
  migraciones en vez de asumir que la tabla `producto` ya existe con esa estructura.
- **Internacionalización (i18n)**: extraer los textos de la interfaz a un archivo de
  strings para poder soportar más de un idioma.
- **Tipado estático**: completar type hints en todos los métodos y validar con `mypy`.

## 📝 Licencia

Proyecto personal con fines de aprendizaje / portfolio.
