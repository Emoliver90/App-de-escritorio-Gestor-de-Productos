"""App Gestor de Productos - Interfaz gráfica en Tkinter.

Aplicación de escritorio para gestionar un inventario simple de
productos (alta, edición, baja y listado), usando SQLite como
almacenamiento persistente a través del módulo database.py.
"""

import tkinter as tk
from tkinter import ttk, LabelFrame, Label, Entry, Toplevel, StringVar, CENTER, W, E, END
from tkinter.ttk import Combobox

from database import ProductoRepository, CATEGORIAS, BASE_DIR

ICON_PATH = BASE_DIR / "Recursos" / "icon.ico"


class VentanaPrincipal:
    def __init__(self, root):
        self.ventana = root
        self.repositorio = ProductoRepository()
        self.ventana.title("App Gestor de Productos")
        self.ventana.resizable(width=True, height=True)

        # wm_iconbitmap con .ico solo funciona de forma nativa en Windows.
        # Se protege con try/except para que la app no se rompa en
        # Linux/Mac o si el archivo no existe todavía.
        try:
            self.ventana.wm_iconbitmap(str(ICON_PATH))
        except tk.TclError:
            print(f"Aviso: no se pudo cargar el icono en {ICON_PATH}")

        # --- Frame Principal: formulario de alta de producto ---
        frame = LabelFrame(self.ventana, text="Registrar un Nuevo Producto", font=('Calibri', 16, 'bold'))
        frame.grid(column=0, row=0, columnspan=3, pady=20)

        self.etiqueta_nombre = Label(frame, text="Nombre: ", font=('Calibri', 13))
        self.etiqueta_nombre.grid(row=1, column=0)
        self.nombre = Entry(frame, font=('Calibri', 13))
        self.nombre.focus()
        self.nombre.grid(row=1, column=1)

        self.mensaje = Label(self.ventana, text='', fg='red')
        self.mensaje.grid(row=6, column=0, columnspan=2, sticky=W + E)

        self.etiqueta_precio = Label(frame, text="Precio: ", font=('Calibri', 13))
        self.etiqueta_precio.grid(row=2, column=0)
        self.precio = Entry(frame, font=('Calibri', 13))
        self.precio.grid(row=2, column=1)

        s = ttk.Style()
        s.configure('my.TButton', font=('Calibri', 14, 'bold'))
        self.boton_anadir = ttk.Button(frame, text="Guardar Producto", command=self.add_producto, style='my.TButton')
        self.boton_anadir.grid(row=5, columnspan=2, sticky=W + E)

        # --- Tabla de productos ---
        style = ttk.Style()
        style.configure("mystyle.Treeview", highlightthickness=0, bd=0, font=('Calibri', 11))
        style.configure("mystyle.Treeview.Heading", font=('Calibri', 13, 'bold'))
        style.layout("mystyle.Treeview", [('mystyle.Treeview.treearea', {'sticky': 'nswe'})])

        self.tabla = ttk.Treeview(self.ventana, height=20, columns=("Precio", "Categoria", "Stock"), style="mystyle.Treeview")
        self.tabla.grid(row=7, column=0, columnspan=2)
        self.tabla.heading('#0', text='Nombre', anchor=CENTER)
        self.tabla.heading('#1', text='Precio', anchor=CENTER)
        self.tabla.heading('#2', text='Categoria', anchor=CENTER)
        self.tabla.heading('#3', text='Stock', anchor=CENTER)

        self.etiqueta_categoria = Label(frame, text="Categoria: ", font=('Calibri', 13))
        self.etiqueta_categoria.grid(row=4, column=0)
        self.categoria = Combobox(frame, font=('Calibri', 13), values=CATEGORIAS, state='readonly')
        self.categoria.bind("<<ComboboxSelected>>", self.cat_producto)
        self.categoria.grid(row=4, column=1)

        self.etiqueta_stock = Label(frame, text="Stock: ", font=('Calibri', 13))
        self.etiqueta_stock.grid(row=3, column=0)
        self.stock = Entry(frame, font=('Calibri', 13))
        self.stock.grid(row=3, column=1)

        self.boton_editar = ttk.Button(self.ventana, text="EDITAR", command=self.editar_producto, style='my.TButton')
        self.boton_editar.grid(row=8, column=1, sticky=W + E)
        self.boton_eliminar = ttk.Button(self.ventana, text="ELIMINAR", command=self.del_producto, style='my.TButton')
        self.boton_eliminar.grid(row=8, column=0, sticky=W + E)

        self.get_productos()

    def cat_producto(self, event=None):
        """Actualmente el combo de categoría solo dispara un refresco.
        (Si en el futuro se quiere filtrar por categoría, aquí es donde
        habría que pasar self.categoria.get() a repositorio.listar()).
        """
        self.get_productos()

    def del_producto(self):
        self.mensaje['text'] = ''
        seleccion = self.tabla.selection()
        if not seleccion:
            self.mensaje['text'] = 'Por favor, seleccione un producto'
            return
        nombre = self.tabla.item(seleccion)['text']
        self.repositorio.eliminar(nombre)
        self.mensaje['text'] = f'Producto {nombre} eliminado con éxito'
        self.get_productos()

    def editar_producto(self):
        seleccion = self.tabla.selection()
        if not seleccion:
            self.mensaje['text'] = 'Por favor, seleccione un producto'
            return
        nombre = self.tabla.item(seleccion)['text']
        precio = self.tabla.item(seleccion)['values'][0]
        categoria = self.tabla.item(seleccion)['values'][1]
        VentanaEditarProducto(self, nombre, precio, categoria, self.mensaje)

    def get_productos(self):
        for fila in self.tabla.get_children():
            self.tabla.delete(fila)
        for registro in self.repositorio.listar():
            # registro = (id, nombre, precio, categoria, stock)
            self.tabla.insert('', 0, text=registro[1], values=registro[2:])

    # --- Validaciones del formulario de alta ---
    def validacion_nombre(self) -> bool:
        nombre = self.nombre.get().strip()
        if not nombre:
            self.mensaje['text'] = 'El nombre es obligatorio'
            return False
        if self.repositorio.existe(nombre):
            self.mensaje['text'] = 'El producto ya existe'
            return False
        return True

    def validacion_precio(self) -> bool:
        try:
            return float(self.precio.get()) > 0
        except ValueError:
            return False

    def validacion_categoria(self) -> bool:
        return self.categoria.get().strip() != ""

    def validacion_stock(self) -> bool:
        return self.stock.get().strip().isdigit()

    def add_producto(self):
        # Cada validación corta la ejecución (return) en cuanto falla,
        # así el mensaje de error que se muestra siempre corresponde
        # al primer problema real encontrado.
        if not self.validacion_nombre():
            return
        if not self.validacion_precio():
            self.mensaje['text'] = 'El precio es obligatorio y debe ser un número válido mayor que 0'
            return
        if not self.validacion_categoria():
            self.mensaje['text'] = 'La categoría es obligatoria'
            return
        if not self.validacion_stock():
            self.mensaje['text'] = 'El stock es obligatorio y debe ser un número entero'
            return

        nombre = self.nombre.get().title()
        try:
            self.repositorio.crear(nombre, float(self.precio.get()), self.categoria.get(), int(self.stock.get()))
            self.mensaje['text'] = f'Producto {nombre} añadido con éxito'
        except Exception as error:
            self.mensaje['text'] = 'El producto ya existe'
            print(f"Error al crear producto: {error}")

        self.nombre.delete(0, END)
        self.precio.delete(0, END)
        self.stock.delete(0, END)
        self.get_productos()


class VentanaEditarProducto:
    def __init__(self, ventana_principal, nombre, precio, categoria, mensaje):
        self.ventana_principal = ventana_principal
        self.nombre = nombre
        self.precio = precio
        self.categoria = categoria
        self.mensaje = mensaje
        self.ventana_editar = Toplevel()
        self.ventana_editar.title("Editar Producto")

        frame_ep = LabelFrame(self.ventana_editar, text="Editar el siguiente Producto", font=('Calibri', 16, 'bold'))
        frame_ep.grid(row=0, column=0, columnspan=2, pady=20, padx=20)

        Label(frame_ep, text="Nombre antiguo: ", font=('Calibri', 13)).grid(row=1, column=0)
        Entry(frame_ep, textvariable=StringVar(self.ventana_editar, value=nombre), state='readonly',
              font=('Calibri', 13)).grid(row=1, column=1)

        Label(frame_ep, text="Nombre nuevo: ", font=('Calibri', 13)).grid(row=2, column=0)
        self.input_nombre_nuevo = Entry(frame_ep, font=('Calibri', 13))
        self.input_nombre_nuevo.grid(row=2, column=1)
        self.input_nombre_nuevo.focus()

        Label(frame_ep, text="Precio antiguo: ", font=('Calibri', 13)).grid(row=3, column=0)
        Entry(frame_ep, textvariable=StringVar(self.ventana_editar, value=precio), state='readonly',
              font=('Calibri', 13)).grid(row=3, column=1)

        Label(frame_ep, text="Precio nuevo: ", font=('Calibri', 13)).grid(row=4, column=0)
        self.input_precio_nuevo = Entry(frame_ep, font=('Calibri', 13))
        self.input_precio_nuevo.grid(row=4, column=1)

        Label(frame_ep, text="Categoria antigua: ", font=('Calibri', 13)).grid(row=5, column=0)
        Entry(frame_ep, textvariable=StringVar(self.ventana_editar, value=categoria), state='readonly',
              font=('Calibri', 13)).grid(row=5, column=1)

        Label(frame_ep, text="Categoria nueva: ", font=('Calibri', 13)).grid(row=6, column=0)
        self.input_categoria_nueva = Combobox(frame_ep, font=('Calibri', 13), values=CATEGORIAS)
        self.input_categoria_nueva.grid(row=6, column=1)

        ttk.Style().configure('my.TButton', font=('Calibri', 14, 'bold'))
        ttk.Button(frame_ep, text="Actualizar Producto", style='my.TButton',
                   command=self.actualizar).grid(row=7, columnspan=2, sticky=W + E)

    def actualizar(self):
        nuevo_nombre = self.input_nombre_nuevo.get().strip() or self.nombre
        nuevo_precio = self.input_precio_nuevo.get().strip() or self.precio
        nueva_categoria = self.input_categoria_nueva.get().strip() or self.categoria

        try:
            float(nuevo_precio)
        except ValueError:
            self.mensaje['text'] = 'El precio debe ser un número válido'
            return

        self.ventana_principal.repositorio.actualizar(self.nombre, nuevo_nombre, nuevo_precio, nueva_categoria)
        self.mensaje['text'] = f'El producto {self.nombre} ha sido actualizado con éxito'
        self.ventana_editar.destroy()
        self.ventana_principal.get_productos()


if __name__ == "__main__":
    root = tk.Tk()
    app = VentanaPrincipal(root)
    root.mainloop()
