import customtkinter as ctk
import sqlite3
import os
import datetime
from tkinter import messagebox

class VistaEntregas(ctk.CTkFrame):
    def __init__(self, parent, controlador):
        super().__init__(parent, fg_color="transparent")
        self.controlador = controlador

        ctk.CTkLabel(self, text="Checklist de Entregas y Solvencia", font=("Arial", 24, "bold"), text_color="#1E2B3C").pack(anchor="w", pady=(0, 15))

        # --- SECCIÓN 1: CARGA Y GUARDADO ---
        self.frame_top = ctk.CTkFrame(self, fg_color="white", corner_radius=10)
        self.frame_top.pack(fill="x", pady=5)

        conexion = self.conectar_bd()
        ciclos_db = conexion.cursor().execute("SELECT id_ciclo, nombre_ciclo FROM ciclos").fetchall()
        conexion.close()
        
        self.dicc_ciclos = {c[1]: c[0] for c in ciclos_db}
        opciones_ciclo = list(self.dicc_ciclos.keys())

        ctk.CTkLabel(self.frame_top, text="1. Seleccione Operativo:").pack(side="left", padx=(20, 10), pady=15)
        
        self.combo_ciclo = ctk.CTkComboBox(self.frame_top, values=opciones_ciclo if opciones_ciclo else ["Sin Ciclos"], width=200)
        self.combo_ciclo.pack(side="left", padx=10, pady=15)

        self.btn_cargar = ctk.CTkButton(self.frame_top, text="🔄 Cargar Checklist", fg_color="#007BFF", font=("Arial", 14, "bold"), command=self.generar_checklist)
        self.btn_cargar.pack(side="left", padx=10, pady=15)

        self.btn_guardar = ctk.CTkButton(self.frame_top, text="💾 GUARDAR CAMBIOS", fg_color="#1E5631", font=("Arial", 14, "bold"), command=self.guardar_todo)
        self.btn_guardar.pack(side="right", padx=20, pady=15)

        # --- SECCIÓN 2: BUSCADOR Y FILTROS ---
        self.frame_filtros = ctk.CTkFrame(self, fg_color="white", corner_radius=10)
        self.frame_filtros.pack(fill="x", pady=5)

        ctk.CTkLabel(self.frame_filtros, text="🔍 Buscar:").pack(side="left", padx=(20, 5), pady=15)
        self.e_buscar = ctk.CTkEntry(self.frame_filtros, placeholder_text="Nombre, Cédula, Calle o Casa...", width=250)
        self.e_buscar.pack(side="left", padx=5, pady=15)
        self.e_buscar.bind("<KeyRelease>", self.aplicar_filtros) # Filtra al escribir

        ctk.CTkLabel(self.frame_filtros, text="Filtrar por Solvencia:").pack(side="left", padx=(30, 5), pady=15)
        self.combo_filtro_pago = ctk.CTkComboBox(self.frame_filtros, values=["Todos", "PAGADO", "Debe", "Exonerado"], command=self.aplicar_filtros)
        self.combo_filtro_pago.pack(side="left", padx=5, pady=15)

        # --- SECCIÓN 3: ÁREA DE CHECKLIST ---
        self.scroll_frame = ctk.CTkScrollableFrame(self, fg_color="#F4F6F9")
        self.scroll_frame.pack(fill="both", expand=True, pady=10)

        self.diccionario_estados = {}
        self.filas_widgets = [] # Guarda las referencias para poder ocultarlas/mostrarlas con los filtros

    def conectar_bd(self):
        return sqlite3.connect(self.controlador.ruta_bd)

    def generar_checklist(self):
        if self.combo_ciclo.get() == "Sin Ciclos": return
        id_ciclo = self.dicc_ciclos[self.combo_ciclo.get()]
        
        # Limpiar interfaz anterior
        for widget in self.scroll_frame.winfo_children(): widget.destroy()
        self.diccionario_estados.clear()
        self.filas_widgets.clear()

        conexion = self.conectar_bd()
        cursor = conexion.cursor()
        
        consulta = '''
            SELECT e.id_transaccion, f.calle, f.numero_casa, f.jefe_familia, f.cedula_jefe, 
                   e.estado_pago, e.estado_entrega, e.metodo_pago, e.recibo
            FROM entregas e
            JOIN familias f ON e.id_hogar = f.id_hogar
            WHERE e.id_ciclo = ?
            ORDER BY f.calle, f.numero_casa
        '''
        registros = cursor.execute(consulta, (id_ciclo,)).fetchall()
        conexion.close()

        if not registros:
            ctk.CTkLabel(self.scroll_frame, text="No hay familias vinculadas a este ciclo.", font=("Arial", 14)).pack(pady=20)
            return

        for reg in registros:
            id_trans, calle, casa, jefe, cedula, est_pago, est_entrega, metodo, recibo = reg
            
            fila = ctk.CTkFrame(self.scroll_frame, corner_radius=8, fg_color="white", border_width=1, border_color="#E0E0E0")
            fila.pack(fill="x", pady=5, padx=5)

            # --- Textos de Información ---
            texto_info = f"Calle: {calle} | Casa: {casa} | {jefe} (CI: {cedula})"
            texto_busqueda = texto_info.lower() # Para el buscador
            
            ctk.CTkLabel(fila, text=texto_info, font=("Arial", 13, "bold"), text_color="#1E2B3C", width=360, anchor="w").pack(side="left", padx=10, pady=15)

            # Variables
            var_pago = ctk.StringVar(value=est_pago)
            var_entrega = ctk.StringVar(value=est_entrega)

            # --- Controles (De derecha a izquierda) ---
            
            # 1. Combobox Entrega
            def aplicar_color_entrega(choice, opt_menu):
                if choice == "ENTREGADO": opt_menu.configure(fg_color="#28A745", button_color="#218838")
                else: opt_menu.configure(fg_color="#FFC107", button_color="#E0A800")
            
            menu_entrega = ctk.CTkOptionMenu(fila, values=["Pendiente", "ENTREGADO"], variable=var_entrega, width=120)
            menu_entrega.configure(command=lambda choice, om=menu_entrega: aplicar_color_entrega(choice, om))
            menu_entrega.pack(side="right", padx=5)
            aplicar_color_entrega(est_entrega, menu_entrega)

            # 2. Combobox Solvencia (Pago)
            def aplicar_color_pago(choice, opt_menu):
                if choice == "PAGADO": opt_menu.configure(fg_color="#28A745", button_color="#218838")
                elif choice == "Debe": opt_menu.configure(fg_color="#DC3545", button_color="#C82333")
                elif choice == "Exonerado": opt_menu.configure(fg_color="#17A2B8", button_color="#138496")
            
            menu_pago = ctk.CTkOptionMenu(fila, values=["Debe", "PAGADO", "Exonerado"], variable=var_pago, width=110)
            menu_pago.configure(command=lambda choice, om=menu_pago: aplicar_color_pago(choice, om))
            menu_pago.pack(side="right", padx=(5, 10))
            aplicar_color_pago(est_pago, menu_pago)

            # 3. Entry Referencia
            e_ref = ctk.CTkEntry(fila, placeholder_text="Referencia", width=120, height=28)
            if recibo: e_ref.insert(0, recibo)
            e_ref.pack(side="right", padx=5)

            # 4. Combobox Método de Pago
            c_metodo = ctk.CTkComboBox(fila, values=["Efectivo", "Pago Móvil", "Transferencia", "N/A"], width=130, height=28)
            c_metodo.set(metodo if metodo else "Método...")
            c_metodo.pack(side="right", padx=5)

            # Guardamos los controles para la BD
            self.diccionario_estados[id_trans] = {
                "pago": var_pago, 
                "entrega": var_entrega,
                "metodo": c_metodo,
                "recibo": e_ref
            }

            # Guardamos la fila para el motor de búsqueda
            self.filas_widgets.append({
                "frame": fila,
                "texto_busqueda": texto_busqueda,
                "var_pago": var_pago
            })

    def aplicar_filtros(self, event=None):
        termino = self.e_buscar.get().lower()
        filtro_p = self.combo_filtro_pago.get()

        for fila in self.filas_widgets:
            # Verifica si el texto coincide
            match_texto = termino in fila["texto_busqueda"]
            # Verifica si el estado de pago coincide (o si está en "Todos")
            match_pago = (filtro_p == "Todos") or (filtro_p == fila["var_pago"].get())

            # Muestra u oculta la fila sin borrar la información
            if match_texto and match_pago:
                fila["frame"].pack(fill="x", pady=5, padx=5)
            else:
                fila["frame"].pack_forget()

    def guardar_todo(self):
        if not self.diccionario_estados: return
        
        fecha_hoy = datetime.date.today().strftime("%d/%m/%Y")
        conexion = self.conectar_bd()
        cursor = conexion.cursor()
        
        for id_trans, variables in self.diccionario_estados.items():
            pago = variables["pago"].get()
            entrega = variables["entrega"].get()
            metodo = variables["metodo"].get()
            recibo = variables["recibo"].get()
            
            if metodo == "Método...": metodo = "" # Limpiar texto por defecto
            
            cursor.execute('''
                UPDATE entregas 
                SET estado_pago=?, estado_entrega=?, metodo_pago=?, recibo=?, fecha_pago=?, fecha_entrega=?
                WHERE id_transaccion=?
            ''', (pago, entrega, metodo, recibo, fecha_hoy, fecha_hoy, id_trans))

        conexion.commit()
        conexion.close()
        messagebox.showinfo("Éxito", "Todos los estados, métodos y referencias han sido guardados correctamente.")