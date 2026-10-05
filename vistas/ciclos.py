import customtkinter as ctk
from tkinter import ttk, messagebox
import sqlite3
import datetime

class VistaCiclos(ctk.CTkFrame):
    def __init__(self, parent, controlador):
        super().__init__(parent, fg_color="transparent")
        self.controlador = controlador
        self.construir_interfaz_lista()

    def conectar_bd(self):
        return sqlite3.connect(self.controlador.ruta_bd)

    def construir_interfaz_lista(self):
        for w in self.winfo_children(): w.destroy()

        frame_top = ctk.CTkFrame(self, fg_color="transparent")
        frame_top.pack(fill="x", pady=(0, 20))
        
        ctk.CTkLabel(frame_top, text="Ciclos de Distribución", font=("Arial", 24, "bold"), text_color="#1E2B3C").pack(side="left")
        
        self.btn_eliminar = ctk.CTkButton(frame_top, text="🗑️ Eliminar", font=("Arial", 14, "bold"), fg_color="#DC3545", command=self.eliminar_seleccion)
        self.btn_eliminar.pack(side="right", padx=5)

        self.btn_editar = ctk.CTkButton(frame_top, text="✏️ Editar", font=("Arial", 14, "bold"), fg_color="#007BFF", command=self.editar_seleccion)
        self.btn_editar.pack(side="right", padx=5)

        self.btn_nuevo = ctk.CTkButton(frame_top, text="+ Nuevo Ciclo", font=("Arial", 14, "bold"), fg_color="#1E5631", command=self.construir_interfaz_crear)
        self.btn_nuevo.pack(side="right", padx=5)

        self.frame_tabla = ctk.CTkFrame(self, fg_color="white", corner_radius=10)
        self.frame_tabla.pack(fill="both", expand=True)

        estilo = ttk.Style()
        estilo.theme_use("default")
        estilo.configure("Treeview", rowheight=40, font=("Arial", 11), borderwidth=0)
        estilo.configure("Treeview.Heading", font=("Arial", 12, "bold"), background="#F4F6F9", foreground="#1E2B3C")

        self.tabla = ttk.Treeview(self.frame_tabla, columns=("ID", "Nombre", "Fechas", "Precio", "Estado"), show="headings")
        self.tabla.heading("ID", text="ID")
        self.tabla.heading("Nombre", text="Ciclo")
        self.tabla.heading("Fechas", text="Inicio - Fin")
        self.tabla.heading("Precio", text="Precio Bolsa")
        self.tabla.heading("Estado", text="Estatus")
        
        self.tabla.column("ID", width=50, anchor="center")
        self.tabla.column("Fechas", width=200, anchor="center")
        self.tabla.column("Precio", width=100, anchor="center")
        self.tabla.column("Estado", width=100, anchor="center")
        
        self.tabla.pack(fill="both", expand=True, padx=20, pady=20)
        self.tabla.bind("<Double-1>", self.abrir_dashboard_ciclo)
        self.cargar_ciclos()

    def cargar_ciclos(self):
        # ESTA ES LA LÍNEA QUE FALTABA Y CAUSABA LA DUPLICACIÓN VISUAL:
        for f in self.tabla.get_children(): self.tabla.delete(f)
        
        conexion = self.conectar_bd()
        for c in conexion.cursor().execute("SELECT id_ciclo, nombre_ciclo, fecha_inicio, fecha_fin, precio, estatus FROM ciclos"):
            self.tabla.insert("", "end", values=(c[0], c[1], f"{c[2]} al {c[3]}", f"${c[4]:.2f}", c[5]))
        conexion.close()

    def eliminar_seleccion(self):
        item = self.tabla.focus()
        if not item: 
            messagebox.showwarning("Atención", "Seleccione un ciclo para eliminar.")
            return
        id_c = self.tabla.item(item, 'values')[0]
        if messagebox.askyesno("Confirmar", "¿Eliminar este ciclo? Se borrarán todos los registros de pago y entrega asociados."):
            conexion = self.conectar_bd()
            conexion.cursor().execute("DELETE FROM entregas WHERE id_ciclo=?", (id_c,))
            conexion.cursor().execute("DELETE FROM ciclos_calles WHERE id_ciclo=?", (id_c,))
            conexion.cursor().execute("DELETE FROM ciclos WHERE id_ciclo=?", (id_c,))
            conexion.commit()
            conexion.close()
            self.cargar_ciclos()

    def editar_seleccion(self):
        item = self.tabla.focus()
        if not item:
            messagebox.showwarning("Atención", "Seleccione un ciclo para editar.")
            return
        id_c = self.tabla.item(item, 'values')[0]
        
        conexion = self.conectar_bd()
        datos = conexion.cursor().execute("SELECT nombre_ciclo, fecha_inicio, fecha_fin, precio, estatus FROM ciclos WHERE id_ciclo=?", (id_c,)).fetchone()
        conexion.close()

        modal = ctk.CTkToplevel(self.controlador)
        modal.title("Editar Datos del Ciclo")
        modal.geometry("350x450")
        modal.grab_set()

        e_nombre = ctk.CTkEntry(modal, placeholder_text="Nombre", width=300)
        e_nombre.insert(0, datos[0])
        e_nombre.pack(pady=10)

        e_inicio = ctk.CTkEntry(modal, placeholder_text="Fecha Inicio", width=300)
        e_inicio.insert(0, datos[1])
        e_inicio.pack(pady=10)

        e_fin = ctk.CTkEntry(modal, placeholder_text="Fecha Fin", width=300)
        e_fin.insert(0, datos[2])
        e_fin.pack(pady=10)

        e_precio = ctk.CTkEntry(modal, placeholder_text="Precio", width=300)
        e_precio.insert(0, datos[3])
        e_precio.pack(pady=10)

        c_estatus = ctk.CTkComboBox(modal, values=["Activo", "Cerrado"], width=300)
        c_estatus.set(datos[4])
        c_estatus.pack(pady=10)

        def guardar():
            conexion = self.conectar_bd()
            conexion.cursor().execute("UPDATE ciclos SET nombre_ciclo=?, fecha_inicio=?, fecha_fin=?, precio=?, estatus=? WHERE id_ciclo=?",
                                      (e_nombre.get(), e_inicio.get(), e_fin.get(), float(e_precio.get()), c_estatus.get(), id_c))
            conexion.commit()
            conexion.close()
            modal.destroy()
            self.cargar_ciclos()

        ctk.CTkButton(modal, text="💾 Guardar Cambios", fg_color="#1E5631", width=300, command=guardar).pack(pady=20)

    # --- Creación de Nuevo Ciclo ---
    def construir_interfaz_crear(self):
        for w in self.winfo_children(): w.destroy()
        ctk.CTkLabel(self, text="Crear Nuevo Ciclo", font=("Arial", 24, "bold"), text_color="#1E2B3C").pack(anchor="w", pady=(0, 20))

        frame_form = ctk.CTkFrame(self, fg_color="white", corner_radius=10)
        frame_form.pack(fill="both", expand=True)

        f_datos = ctk.CTkFrame(frame_form, fg_color="transparent")
        f_datos.pack(fill="x", padx=30, pady=20)
        
        self.e_nombre = ctk.CTkEntry(f_datos, placeholder_text="Nombre (Ej: Octubre 2026)", width=300)
        self.e_nombre.grid(row=0, column=0, padx=10, pady=10)
        self.e_inicio = ctk.CTkEntry(f_datos, placeholder_text="Fecha Inicio", width=200)
        self.e_inicio.grid(row=0, column=1, padx=10, pady=10)
        self.e_fin = ctk.CTkEntry(f_datos, placeholder_text="Fecha Fin", width=200)
        self.e_fin.grid(row=0, column=2, padx=10, pady=10)
        self.e_precio = ctk.CTkEntry(f_datos, placeholder_text="Precio ($)", width=150)
        self.e_precio.grid(row=1, column=0, padx=10, pady=10, sticky="w")

        ctk.CTkLabel(frame_form, text="Seleccionar Calles Participantes:", font=("Arial", 16, "bold")).pack(anchor="w", padx=40)
        self.frame_calles = ctk.CTkScrollableFrame(frame_form, height=150, fg_color="#F4F6F9")
        self.frame_calles.pack(fill="x", padx=40, pady=10)

        conexion = self.conectar_bd()
        calles = conexion.cursor().execute("SELECT DISTINCT calle FROM familias").fetchall()
        conexion.close()

        self.vars_calles = {}
        for calle in calles:
            var = ctk.IntVar(value=1)
            ctk.CTkCheckBox(self.frame_calles, text=calle[0], variable=var).pack(anchor="w", pady=5, padx=10)
            self.vars_calles[calle[0]] = var

        f_acciones = ctk.CTkFrame(frame_form, fg_color="transparent")
        f_acciones.pack(fill="x", padx=40, pady=20)
        ctk.CTkButton(f_acciones, text="Cancelar", fg_color="gray", command=self.construir_interfaz_lista).pack(side="left")
        ctk.CTkButton(f_acciones, text="Confirmar y Crear", fg_color="#28A745", command=self.guardar_ciclo).pack(side="right")

    def guardar_ciclo(self):
        calles_sel = [c for c, v in self.vars_calles.items() if v.get() == 1]
        conexion = self.conectar_bd()
        cursor = conexion.cursor()
        try:
            cursor.execute("INSERT INTO ciclos (nombre_ciclo, fecha_inicio, fecha_fin, precio) VALUES (?,?,?,?)",
                           (self.e_nombre.get(), self.e_inicio.get(), self.e_fin.get(), float(self.e_precio.get())))
            id_ciclo = cursor.lastrowid

            for calle in calles_sel:
                cursor.execute("INSERT INTO ciclos_calles (id_ciclo, calle) VALUES (?,?)", (id_ciclo, calle))
                for hogar in cursor.execute("SELECT id_hogar FROM familias WHERE calle=?", (calle,)).fetchall():
                    cursor.execute("INSERT INTO entregas (id_ciclo, id_hogar) VALUES (?,?)", (id_ciclo, hogar[0]))

            conexion.commit()
            self.construir_interfaz_lista()
        except Exception as e:
            messagebox.showerror("Error", f"Verifique los datos.\n{e}")
        finally:
            conexion.close()

    def abrir_dashboard_ciclo(self, event):
        item = self.tabla.focus()
        if not item: return
        self.ciclo_actual_id = self.tabla.item(item, 'values')[0]

        for w in self.winfo_children(): w.destroy()

        frame_top = ctk.CTkFrame(self, fg_color="transparent")
        frame_top.pack(fill="x", pady=(0, 20))
        ctk.CTkLabel(frame_top, text="Dashboard del Ciclo", font=("Arial", 22, "bold"), text_color="#1E2B3C").pack(side="left")
        ctk.CTkButton(frame_top, text="⬅ Volver", fg_color="gray", command=self.construir_interfaz_lista).pack(side="right")

        self.f_tabla = ctk.CTkFrame(self, fg_color="white", corner_radius=10)
        self.f_tabla.pack(side="left", fill="both", expand=True)

        self.tabla_h = ttk.Treeview(self.f_tabla, columns=("ID_T", "Casa", "Jefe", "Calle", "Pago", "Entrega"), show="headings")
        for col in self.tabla_h["columns"]:
            self.tabla_h.heading(col, text=col)
            self.tabla_h.column(col, anchor="center")
        self.tabla_h.pack(fill="both", expand=True, padx=10, pady=10)
        self.cargar_datos_dashboard()

    def cargar_datos_dashboard(self):
        for f in self.tabla_h.get_children(): self.tabla_h.delete(f)
        conexion = self.conectar_bd()
        for fila in conexion.cursor().execute("SELECT e.id_transaccion, f.numero_casa, f.jefe_familia, f.calle, e.estado_pago, e.estado_entrega FROM entregas e JOIN familias f ON e.id_hogar = f.id_hogar WHERE e.id_ciclo = ?", (self.ciclo_actual_id,)):
            self.tabla_h.insert("", "end", values=fila)
        conexion.close()