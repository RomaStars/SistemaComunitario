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

        # Columnas actualizadas
        # 1. Definir columnas (incluyendo Fecha de Nacimiento y Edad)
        self.tabla = ttk.Treeview(self.frame_tabla, columns=("ID", "Nombres", "Cédula", "F. Nacimiento", "Edad", "Familia (Jefe)", "Parentesco", "Género"), show="headings")
        
        # 2. Configurar Encabezados
        self.tabla.heading("ID", text="ID")
        self.tabla.heading("Nombres", text="Nombres")
        self.tabla.heading("Cédula", text="Cédula")
        self.tabla.heading("F. Nacimiento", text="F. Nacimiento")
        self.tabla.heading("Edad", text="Edad")
        self.tabla.heading("Familia (Jefe)", text="Familia (Jefe)")
        self.tabla.heading("Parentesco", text="Parentesco")
        self.tabla.heading("Género", text="Género")

        # 3. Anchos específicos y alineaciones (estilo Familias)
        self.tabla.column("ID", width=40, anchor="center", stretch=False)
        self.tabla.column("Nombres", width=180, anchor="w")
        self.tabla.column("Cédula", width=100, anchor="center")
        self.tabla.column("F. Nacimiento", width=110, anchor="center")
        self.tabla.column("Edad", width=60, anchor="center")
        self.tabla.column("Familia (Jefe)", width=160, anchor="w")
        self.tabla.column("Parentesco", width=110, anchor="center")
        self.tabla.column("Género", width=100, anchor="center")
        self.tabla.pack(fill="both", expand=True, padx=20, pady=20)
        self.cargar_datos()

    def conectar_bd(self):
        return sqlite3.connect(self.controlador.ruta_bd)

    def cargar_datos(self):
        for f in self.tabla.get_children(): self.tabla.delete(f)
        try:
            conexion = self.conectar_bd()
            for fila in conexion.cursor().execute("SELECT h.id_beneficiario, h.nombres, h.cedula, h.fecha_nacimiento, f.jefe_familia, h.parentesco, h.genero FROM habitantes h JOIN familias f ON h.id_hogar = f.id_hogar"):
                id_b, nom, ced, f_nac, jefe, par, gen = fila
                edad = calcular_edad(f_nac)
                f_nac_mostrar = f_nac if f_nac else "N/A"
                self.tabla.insert("", "end", values=(id_b, nom, ced, f_nac_mostrar, edad, jefe, par, gen))
            conexion.close()
        except Exception as e:
            messagebox.showerror("Error BD", f"Error al cargar datos:\n{e}")

    def filtrar_datos(self, event=None):
        termino = self.e_buscar.get().lower()
        for f in self.tabla.get_children(): self.tabla.delete(f)
        try:
            conexion = self.conectar_bd()
            for fila in conexion.cursor().execute("SELECT h.id_beneficiario, h.nombres, h.cedula, h.fecha_nacimiento, f.jefe_familia, h.parentesco, h.genero FROM habitantes h JOIN familias f ON h.id_hogar = f.id_hogar"):
                id_b, nom, ced, f_nac, jefe, par, gen = fila
                edad = calcular_edad(f_nac)
                f_nac_mostrar = f_nac if f_nac else "N/A"
                fila_completa = (id_b, nom, ced, f_nac_mostrar, edad, jefe, par, gen)
                texto_fila = " ".join(str(val).lower() for val in fila_completa)
                if termino in texto_fila:
                    self.tabla.insert("", "end", values=fila_completa)
            conexion.close()
        except Exception as e:
            messagebox.showerror("Error BD", f"Error al filtrar datos:\n{e}")

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
        modal.geometry("400x350")
        modal.grab_set()

        conexion = self.conectar_bd()
        familias = conexion.cursor().execute("SELECT id_hogar, jefe_familia FROM familias").fetchall()
        id_hogar_actual = conexion.cursor().execute("SELECT id_hogar FROM habitantes WHERE id_beneficiario=?", (datos[0],)).fetchone()[0] if datos else None
        conexion.close()

        opciones_fam = [f"{f[0]} - {f[1]}" for f in familias]

        c_familia = ctk.CTkComboBox(modal, values=opciones_fam if opciones_fam else ["No hay familias"], width=300)
        c_familia.pack(pady=8)
        e_nom = ctk.CTkEntry(modal, placeholder_text="Nombres y Apellidos", width=300)
        e_nom.pack(pady=8)
        e_ced = ctk.CTkEntry(modal, placeholder_text="Cédula", width=300)
        e_ced.pack(pady=8)
        
        e_fnac = ctk.CTkEntry(modal, placeholder_text="Fecha Nac. (AAAA-MM-DD)", width=300)
        e_fnac.pack(pady=8)
        
        c_parentesco = ctk.CTkComboBox(modal, values=["Jefe(a)", "Hijo(a)", "Cónyuge", "Padre/Madre", "Otro"], width=300)
        c_parentesco.pack(pady=8)
        c_genero = ctk.CTkComboBox(modal, values=["Masculino", "Femenino"], width=300)
        c_genero.pack(pady=8)

        if datos:
            for opc in opciones_fam:
                if opc.startswith(f"{id_hogar_actual} -"): c_familia.set(opc); break
            e_nom.insert(0, datos[1])
            e_ced.insert(0, datos[2])
            if datos[3] != "N/A":
                e_fnac.insert(0, datos[3])
            c_parentesco.set(datos[6])
            c_genero.set(datos[7])

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

            id_hogar = c_familia.get().split(" - ")[0]
            conexion = self.conectar_bd()
            try:
                if datos:
                    conexion.cursor().execute(
                        "UPDATE habitantes SET id_hogar=?, nombres=?, cedula=?, fecha_nacimiento=?, parentesco=?, genero=? WHERE id_beneficiario=?",
                        (id_hogar, e_nom.get(), e_ced.get(), fnac_val, c_parentesco.get(), c_genero.get(), datos[0])
                    )
                else:
                    conexion.cursor().execute(
                        "INSERT INTO habitantes (id_hogar, nombres, cedula, fecha_nacimiento, parentesco, genero) VALUES (?,?,?,?,?,?)",
                        (id_hogar, e_nom.get(), e_ced.get(), fnac_val, c_parentesco.get(), c_genero.get())
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