import customtkinter as ctk

class VistaInicio(ctk.CTkFrame):
    def __init__(self, parent, controlador):
        super().__init__(parent, fg_color="transparent")
        self.controlador = controlador

        self.lbl_titulo = ctk.CTkLabel(self, text="Bienvenido al Sistema Comunitario", font=("Arial", 26, "bold"), text_color="#1E2B3C")
        self.lbl_titulo.pack(anchor="w", pady=(0, 5))
        
        self.lbl_sub = ctk.CTkLabel(self, text="Seleccione una opción en el menú lateral para comenzar a trabajar.", font=("Arial", 14), text_color="gray")
        self.lbl_sub.pack(anchor="w", pady=(0, 20))

        self.scroll_tarjetas = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll_tarjetas.pack(fill="both", expand=True)

        from vistas.familias import VistaFamilias
        from vistas.habitantes import VistaHabitantes
        from vistas.ciclos import VistaCiclos
        from vistas.entregas import VistaEntregas
        from vistas.solvencia import VistaSolvencia

        # Fila 1
        self.crear_tarjeta(0, 0, "👨‍👩‍👧‍👦 Familias y Hogares", "Gestiona la información de familias.", "#20C997", lambda: self.controlador.mostrar_vista(VistaFamilias))
        self.crear_tarjeta(0, 1, "👥 Habitantes", "Administra los datos de la comunidad.", "#007BFF", lambda: self.controlador.mostrar_vista(VistaHabitantes))
        self.crear_tarjeta(0, 2, "🔄 Ciclos Distribución", "Crea y gestiona operativos.", "#17A2B8", lambda: self.controlador.mostrar_vista(VistaCiclos))
        
        # Fila 2
        self.crear_tarjeta(1, 0, "✅ Checklist Entregas", "Pasa lista y marca las solvencias.", "#0056b3", lambda: self.controlador.mostrar_vista(VistaEntregas))
        self.crear_tarjeta(1, 1, "📊 Planillas PDF", "Genera las planillas de firmas.", "#6F42C1", lambda: self.controlador.mostrar_vista(VistaSolvencia))
        
        # Fila 3
        self.crear_tarjeta(2, 0, "💾 Exportar BD", "Crea un respaldo de seguridad.", "#28A745", self.controlador.exportar_bd)
        self.crear_tarjeta(2, 1, "📂 Cargar BD", "Restaura la base de datos.", "#DC3545", self.controlador.importar_bd)

    def crear_tarjeta(self, fila, col, titulo, desc, color_icono, comando):
        card = ctk.CTkFrame(self.scroll_tarjetas, fg_color="white", corner_radius=10, width=320, height=120)
        card.grid(row=fila, column=col, padx=15, pady=15, sticky="nsew")
        card.grid_propagate(False)
        card.bind("<Button-1>", lambda e: comando())

        barra = ctk.CTkFrame(card, width=10, fg_color=color_icono, corner_radius=0)
        barra.pack(side="left", fill="y")
        barra.bind("<Button-1>", lambda e: comando())

        contenido = ctk.CTkFrame(card, fg_color="transparent")
        contenido.pack(side="left", fill="both", expand=True, padx=15, pady=20)
        contenido.bind("<Button-1>", lambda e: comando())

        lbl_t = ctk.CTkLabel(contenido, text=titulo, font=("Arial", 16, "bold"), text_color="#1E2B3C")
        lbl_t.pack(anchor="w")
        lbl_t.bind("<Button-1>", lambda e: comando())
        
        lbl_d = ctk.CTkLabel(contenido, text=desc, font=("Arial", 12), text_color="gray")
        lbl_d.pack(anchor="w")
        lbl_d.bind("<Button-1>", lambda e: comando())