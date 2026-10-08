import customtkinter as ctk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime

def calcular_edad(fecha_nac_str):
    if not fecha_nac_str:
        return "N/A"
    try:
        fn = datetime.strptime(fecha_nac_str, "%Y-%m-%d")
        hoy = datetime.today()
        edad = hoy.year - fn.year - ((hoy.month, hoy.day) < (fn.month, fn.day))

        if edad < 0:
            return "Inválida"
            
        return edad
    except ValueError:
        return "N/A"

class VistaFamilias(ctk.CTkFrame):
    def __init__(self, parent, controlador):
        super().__init__(parent, fg_color="transparent")
        self.controlador = controlador

        ctk.CTkLabel(self, text="Directorio de Familias", font=("Arial", 24, "bold"), text_color="#1E2B3C").pack(anchor="w", pady=(0, 20))

        self.frame_botones = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_botones.pack(fill="x", pady=10)

        self.btn_nuevo = ctk.CTkButton(self.frame_botones, text="➕ Nueva Familia", font=("Arial", 14, "bold"), fg_color="#1E5631", command=lambda: self.abrir_modal())
        self.btn_nuevo.pack(side="left", padx=(0, 10))

        self.btn_editar = ctk.CTkButton(self.frame_botones, text="✏️ Editar", font=("Arial", 14, "bold"), fg_color="#007BFF", command=self.editar_seleccion)
        self.btn_editar.pack(side="left", padx=10)

        self.btn_eliminar = ctk.CTkButton(self.frame_botones, text="🗑️ Eliminar", font=("Arial", 14, "bold"), fg_color="#DC3545", command=self.eliminar_seleccion)
        self.btn_eliminar.pack(side="left", padx=10)

        ctk.CTkLabel(self.frame_botones, text="🔍 Buscar:").pack(side="left", padx=(30, 5))
        self.e_buscar = ctk.CTkEntry(self.frame_botones, placeholder_text="Cédula, nombre o calle...", width=250)
        self.e_buscar.pack(side="left", padx=5)
        self.e_buscar.bind("<KeyRelease>", self.filtrar_datos)

        self.frame_tabla = ctk.CTkFrame(self, fg_color="white", corner_radius=10)
        self.frame_tabla.pack(fill="both", expand=True)
        
        estilo = ttk.Style()
        estilo.theme_use("default")
        estilo.configure("Treeview", rowheight=35, font=("Arial", 12), borderwidth=0)
        estilo.configure("Treeview.Heading", font=("Arial", 12, "bold"), background="#F4F6F9", foreground="#1E2B3C")

        self.tabla = ttk.Treeview(self.frame_tabla, columns=("ID", "Calle", "Casa", "Jefe", "Cédula", "F. Nacimiento", "Edad", "Carga", "Estatus"), show="headings")
        self.tabla.heading("ID", text="ID")
        self.tabla.heading("Calle", text="Calle")
        self.tabla.heading("Casa", text="Casa")
        self.tabla.heading("Jefe", text="Jefe de Familia")
        self.tabla.heading("Cédula", text="Cédula")
        self.tabla.heading("F. Nacimiento", text="F. Nacimiento")
        self.tabla.heading("Edad", text="Edad")
        self.tabla.heading("Carga", text="Carga Fam.")
        self.tabla.heading("Estatus", text="Estatus")
        
        self.tabla.column("ID", width=40, anchor="center", stretch=False)
        self.tabla.column("Calle", width=110, anchor="center")
        self.tabla.column("Casa", width=60, anchor="center")
        self.tabla.column("Jefe", width=200, anchor="w")
        self.tabla.column("Cédula", width=100, anchor="center")
        self.tabla.column("F. Nacimiento", width=110, anchor="center")
        self.tabla.column("Edad", width=60, anchor="center")
        self.tabla.column("Carga", width=90, anchor="center")
        self.tabla.column("Estatus", width=90, anchor="center")
        
        self.tabla.pack(fill="both", expand=True, padx=20, pady=20)
        self.cargar_datos()

    def conectar_bd(self):
        return sqlite3.connect(self.controlador.ruta_bd)

    def cargar_datos(self):
        for f in self.tabla.get_children(): self.tabla.delete(f)
        try:
            conexion = self.conectar_bd()
            for fila in conexion.cursor().execute("SELECT id_hogar, calle, numero_casa, jefe_familia, cedula_jefe, fecha_nacimiento, nro_carga_familiar, estatus FROM familias"):
                id_h, calle, casa, jefe, ced, f_nac, carga, estatus = fila
                edad = calcular_edad(f_nac)
                f_nac_mostrar = f_nac if f_nac else "N/A"
                self.tabla.insert("", "end", values=(id_h, calle, casa, jefe, ced, f_nac_mostrar, edad, carga, estatus))
            conexion.close()
        except Exception as e:
            messagebox.showerror("Error BD", f"Error al cargar datos:\n{e}")

    def filtrar_datos(self, event=None):
        termino = self.e_buscar.get().lower()
        for f in self.tabla.get_children(): self.tabla.delete(f)
        try:
            conexion = self.conectar_bd()
            for fila in conexion.cursor().execute("SELECT id_hogar, calle, numero_casa, jefe_familia, cedula_jefe, fecha_nacimiento, nro_carga_familiar, estatus FROM familias"):
                id_h, calle, casa, jefe, ced, f_nac, carga, estatus = fila
                edad = calcular_edad(f_nac)
                f_nac_mostrar = f_nac if f_nac else "N/A"
                fila_completa = (id_h, calle, casa, jefe, ced, f_nac_mostrar, edad, carga, estatus)
                texto_fila = " ".join(str(val).lower() for val in fila_completa)
                if termino in texto_fila:
                    self.tabla.insert("", "end", values=fila_completa)
            conexion.close()
        except Exception as e:
            messagebox.showerror("Error BD", f"Error al filtrar datos:\n{e}")

    def eliminar_seleccion(self):
        item = self.tabla.focus()
        if not item: return
        id_fam = self.tabla.item(item, 'values')[0]
        if messagebox.askyesno("Confirmar", "¿Eliminar esta familia y sus habitantes?"):
            conexion = self.conectar_bd()
            conexion.cursor().execute("DELETE FROM habitantes WHERE id_hogar=?", (id_fam,))
            conexion.cursor().execute("DELETE FROM familias WHERE id_hogar=?", (id_fam,))
            conexion.commit()
            conexion.close()
            self.cargar_datos()

    def editar_seleccion(self):
        item = self.tabla.focus()
        if not item: return
        self.abrir_modal(self.tabla.item(item, 'values'))

    def abrir_modal(self, datos=None):
        modal = ctk.CTkToplevel(self.controlador)
        modal.title("Formulario Familia")
        modal.geometry("400x400")
        modal.grab_set()

        e_calle = ctk.CTkEntry(modal, placeholder_text="Calle / Sector", width=300)
        e_calle.pack(pady=8)
        e_casa = ctk.CTkEntry(modal, placeholder_text="Número de Casa", width=300)
        e_casa.pack(pady=8)
        e_jefe = ctk.CTkEntry(modal, placeholder_text="Nombre del Jefe", width=300)
        e_jefe.pack(pady=8)
        e_ced = ctk.CTkEntry(modal, placeholder_text="Cédula", width=300)
        e_ced.pack(pady=8)
        
        e_fnac = ctk.CTkEntry(modal, placeholder_text="Fecha Nac. (AAAA-MM-DD)", width=300)
        e_fnac.pack(pady=8)
        
        e_carga = ctk.CTkEntry(modal, placeholder_text="Carga Familiar", width=300)
        e_carga.pack(pady=8)
        c_estatus = ctk.CTkComboBox(modal, values=["Activo", "Suspendido", "Mudado"], width=300)
        c_estatus.pack(pady=8)

        if datos:
            e_calle.insert(0, datos[1])
            e_casa.insert(0, datos[2])
            e_jefe.insert(0, datos[3])
            e_ced.insert(0, datos[4])
            if datos[5] != "N/A":
                e_fnac.insert(0, datos[5])
            e_carga.insert(0, datos[7])
            c_estatus.set(datos[8])

        def guardar():
            fnac_val = e_fnac.get().strip()
            if fnac_val:
                try:
                    # Convierte el texto ingresado a un objeto de fecha
                    fecha_ingresada = datetime.strptime(fnac_val, "%Y-%m-%d").date()
                    hoy = datetime.today().date()

                    # Validación contra fechas futuras (edades negativas)
                    if fecha_ingresada > hoy:
                        messagebox.showerror("Error", "La fecha de nacimiento no puede ser una fecha futura.")
                        return

                except ValueError:
                    messagebox.showerror("Error", "La fecha debe tener el formato AAAA-MM-DD (Ej: 1990-05-15)")
                    return

            conexion = self.conectar_bd()
            try:
                if datos:
                    conexion.cursor().execute(
                        "UPDATE familias SET calle=?, numero_casa=?, jefe_familia=?, cedula_jefe=?, fecha_nacimiento=?, nro_carga_familiar=?, estatus=? WHERE id_hogar=?",
                        (e_calle.get(), e_casa.get(), e_jefe.get(), e_ced.get(), fnac_val, e_carga.get(), c_estatus.get(), datos[0])
                    )
                else:
                    conexion.cursor().execute(
                        "INSERT INTO familias (calle, numero_casa, jefe_familia, cedula_jefe, fecha_nacimiento, nro_carga_familiar, estatus) VALUES (?,?,?,?,?,?,?)",
                        (e_calle.get(), e_casa.get(), e_jefe.get(), e_ced.get(), fnac_val, e_carga.get(), c_estatus.get())
                    )
                conexion.commit()
                modal.destroy()
                self.cargar_datos()
                self.e_buscar.delete(0, 'end')
            except sqlite3.IntegrityError:
                messagebox.showerror("Error", "Cédula duplicada.")
            finally:
                conexion.close()

        ctk.CTkButton(modal, text="💾 Guardar", fg_color="#1E5631", width=300, command=guardar).pack(pady=20)