import customtkinter as ctk
from tkinter import ttk, messagebox
import sqlite3

class VistaHabitantes(ctk.CTkFrame):
    def __init__(self, parent, controlador):
        super().__init__(parent, fg_color="transparent")
        self.controlador = controlador

        ctk.CTkLabel(self, text="Habitantes de la Comunidad", font=("Arial", 24, "bold"), text_color="#1E2B3C").pack(anchor="w", pady=(0, 20))

        self.frame_botones = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_botones.pack(fill="x", pady=10)

        self.btn_nuevo = ctk.CTkButton(self.frame_botones, text="➕ Agregar Habitante", font=("Arial", 14, "bold"), fg_color="#1E5631", command=lambda: self.abrir_modal())
        self.btn_nuevo.pack(side="left", padx=(0, 10))

        self.btn_editar = ctk.CTkButton(self.frame_botones, text="✏️ Editar", font=("Arial", 14, "bold"), fg_color="#007BFF", command=self.editar_seleccion)
        self.btn_editar.pack(side="left", padx=10)

        self.btn_eliminar = ctk.CTkButton(self.frame_botones, text="🗑️ Eliminar", font=("Arial", 14, "bold"), fg_color="#DC3545", command=self.eliminar_seleccion)
        self.btn_eliminar.pack(side="left", padx=10)

        # BARRA DE BÚSQUEDA AÑADIDA AL LADO DEL BOTÓN ELIMINAR
        ctk.CTkLabel(self.frame_botones, text="🔍 Buscar:").pack(side="left", padx=(30, 5))
        self.e_buscar = ctk.CTkEntry(self.frame_botones, placeholder_text="Nombre, cédula o familia...", width=250)
        self.e_buscar.pack(side="left", padx=5)
        self.e_buscar.bind("<KeyRelease>", self.filtrar_datos)

        self.frame_tabla = ctk.CTkFrame(self, fg_color="white", corner_radius=10)
        self.frame_tabla.pack(fill="both", expand=True)
        
        estilo = ttk.Style()
        estilo.theme_use("default")
        estilo.configure("Treeview", rowheight=35, font=("Arial", 12), borderwidth=0)
        estilo.configure("Treeview.Heading", font=("Arial", 12, "bold"), background="#F4F6F9", foreground="#1E2B3C")

        self.tabla = ttk.Treeview(self.frame_tabla, columns=("ID", "Nombres", "Cédula", "Familia (Jefe)", "Parentesco", "Género"), show="headings")
        for col in self.tabla["columns"]:
            self.tabla.heading(col, text=col)
            self.tabla.column(col, anchor="center")
        self.tabla.pack(fill="both", expand=True, padx=20, pady=20)
        self.cargar_datos()

    def conectar_bd(self):
        return sqlite3.connect(self.controlador.ruta_bd)

    def cargar_datos(self):
        for f in self.tabla.get_children(): self.tabla.delete(f)
        conexion = self.conectar_bd()
        for fila in conexion.cursor().execute("SELECT h.id_beneficiario, h.nombres, h.cedula, f.jefe_familia, h.parentesco, h.genero FROM habitantes h JOIN familias f ON h.id_hogar = f.id_hogar"):
            self.tabla.insert("", "end", values=fila)
        conexion.close()

    def filtrar_datos(self, event=None):
        termino = self.e_buscar.get().lower()
        for f in self.tabla.get_children(): self.tabla.delete(f)
        conexion = self.conectar_bd()
        for fila in conexion.cursor().execute("SELECT h.id_beneficiario, h.nombres, h.cedula, f.jefe_familia, h.parentesco, h.genero FROM habitantes h JOIN familias f ON h.id_hogar = f.id_hogar"):
            texto_fila = " ".join(str(val).lower() for val in fila)
            if termino in texto_fila:
                self.tabla.insert("", "end", values=fila)
        conexion.close()

    def eliminar_seleccion(self):
        item = self.tabla.focus()
        if not item: return
        id_hab = self.tabla.item(item, 'values')[0]
        if messagebox.askyesno("Confirmar", "¿Eliminar este habitante?"):
            conexion = self.conectar_bd()
            conexion.cursor().execute("DELETE FROM habitantes WHERE id_beneficiario=?", (id_hab,))
            conexion.commit()
            conexion.close()
            self.cargar_datos()

    def editar_seleccion(self):
        item = self.tabla.focus()
        if not item: return
        self.abrir_modal(self.tabla.item(item, 'values'))

    def abrir_modal(self, datos=None):
        modal = ctk.CTkToplevel(self.controlador)
        modal.title("Formulario Habitante")
        modal.geometry("400x450")
        modal.grab_set()

        conexion = self.conectar_bd()
        familias = conexion.cursor().execute("SELECT id_hogar, jefe_familia FROM familias").fetchall()
        id_hogar_actual = conexion.cursor().execute("SELECT id_hogar FROM habitantes WHERE id_beneficiario=?", (datos[0],)).fetchone()[0] if datos else None
        conexion.close()

        opciones_fam = [f"{f[0]} - {f[1]}" for f in familias]

        c_familia = ctk.CTkComboBox(modal, values=opciones_fam if opciones_fam else ["No hay familias"], width=300)
        c_familia.pack(pady=10)
        e_nom = ctk.CTkEntry(modal, placeholder_text="Nombres y Apellidos", width=300)
        e_nom.pack(pady=10)
        e_ced = ctk.CTkEntry(modal, placeholder_text="Cédula", width=300)
        e_ced.pack(pady=10)
        c_parentesco = ctk.CTkComboBox(modal, values=["Jefe(a)", "Hijo(a)", "Cónyuge", "Padre/Madre", "Otro"], width=300)
        c_parentesco.pack(pady=10)
        c_genero = ctk.CTkComboBox(modal, values=["Masculino", "Femenino"], width=300)
        c_genero.pack(pady=10)

        if datos:
            for opc in opciones_fam:
                if opc.startswith(f"{id_hogar_actual} -"): c_familia.set(opc); break
            e_nom.insert(0, datos[1]); e_ced.insert(0, datos[2])
            c_parentesco.set(datos[4]); c_genero.set(datos[5])

        def guardar():
            id_hogar = c_familia.get().split(" - ")[0]
            conexion = self.conectar_bd()
            try:
                if datos:
                    conexion.cursor().execute("UPDATE habitantes SET id_hogar=?, nombres=?, cedula=?, parentesco=?, genero=? WHERE id_beneficiario=?",
                                              (id_hogar, e_nom.get(), e_ced.get(), c_parentesco.get(), c_genero.get(), datos[0]))
                else:
                    conexion.cursor().execute("INSERT INTO habitantes (id_hogar, nombres, cedula, parentesco, genero) VALUES (?,?,?,?,?)",
                                              (id_hogar, e_nom.get(), e_ced.get(), c_parentesco.get(), c_genero.get()))
                conexion.commit()
                modal.destroy()
                self.cargar_datos()
                self.e_buscar.delete(0, 'end')
            except sqlite3.IntegrityError:
                messagebox.showerror("Error", "Cédula duplicada.")
            finally:
                conexion.close()

        ctk.CTkButton(modal, text="💾 Guardar", fg_color="#1E5631", width=300, command=guardar).pack(pady=20)