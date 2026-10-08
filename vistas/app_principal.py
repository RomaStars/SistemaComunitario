import customtkinter as ctk
from tkinter import messagebox, filedialog
import shutil
import os
import sys

from vistas.inicio import VistaInicio
from vistas.familias import VistaFamilias
from vistas.habitantes import VistaHabitantes
from vistas.ciclos import VistaCiclos
from vistas.entregas import VistaEntregas
from vistas.solvencia import VistaSolvencia

class AppPrincipal(ctk.CTk):
    def __init__(self, usuario_actual):
        super().__init__()
        self.title("Sistema Comunitario")
        
        ruta_ico = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets', 'logo.ico')
        if os.path.exists(ruta_ico):
            self.iconbitmap(ruta_ico)

        self.after(0, lambda: self.state("zoomed"))
        self.configure(fg_color="#F4F6F9")
        
        self.usuario_actual = usuario_actual
        self.ruta_bd = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'bd', 'comunidad.db')

        # BARRA LATERAL
        self.sidebar = ctk.CTkFrame(self, width=280, corner_radius=0, fg_color="#1E2B3C")
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        self.lbl_logo = ctk.CTkLabel(self.sidebar, text="👥 Sistema Comunitario", font=("Arial", 18, "bold"), text_color="white")
        self.lbl_logo.pack(pady=(30, 40))

        self.crear_boton_menu("🏠 Inicio", lambda: self.mostrar_vista(VistaInicio))
        self.crear_boton_menu("👨‍👩‍👧‍👦 Familias y Hogares", lambda: self.mostrar_vista(VistaFamilias))
        self.crear_boton_menu("👥 Habitantes", lambda: self.mostrar_vista(VistaHabitantes))
        self.crear_boton_menu("🔄 Ciclos de Distribución", lambda: self.mostrar_vista(VistaCiclos))
        self.crear_boton_menu("✅ Checklist de Entregas", lambda: self.mostrar_vista(VistaEntregas))
        self.crear_boton_menu("📊 Reportes y Planillas", lambda: self.mostrar_vista(VistaSolvencia))

        ctk.CTkLabel(self.sidebar, text="").pack(expand=True)

        self.crear_boton_menu("💾 Exportar BD", self.exportar_bd, color_hover="#218838")
        self.crear_boton_menu("📂 Cargar BD", self.importar_bd, color_hover="#C82333")
        
        btn_salir = ctk.CTkButton(self.sidebar, text="🚪 Cerrar Sesión", anchor="w", fg_color="#DC3545", 
                                  text_color="white", hover_color="#C82333", font=("Arial", 15, "bold"), 
                                  height=45, command=self.cerrar_sesion)
        btn_salir.pack(fill="x", padx=15, pady=(5, 20))

        # ÁREA DE CONTENIDO
        self.main_area = ctk.CTkFrame(self, fg_color="transparent")
        self.main_area.pack(side="right", fill="both", expand=True)

        self.topbar = ctk.CTkFrame(self.main_area, height=60, corner_radius=0, fg_color="white")
        self.topbar.pack(fill="x", side="top")
        
        self.lbl_usuario = ctk.CTkLabel(self.topbar, text=f"👤 Operador: {self.usuario_actual.upper()}", font=("Arial", 14, "bold"), text_color="#1E2B3C")
        self.lbl_usuario.pack(side="right", padx=30, pady=15)

        self.contenido_dinamico = ctk.CTkFrame(self.main_area, fg_color="transparent")
        self.contenido_dinamico.pack(fill="both", expand=True, padx=30, pady=20)

        self.mostrar_vista(VistaInicio)

    def crear_boton_menu(self, texto, comando, color_hover="#2C3E50"):
        btn = ctk.CTkButton(self.sidebar, text=texto, anchor="w", fg_color="transparent", 
                            text_color="white", hover_color=color_hover, font=("Arial", 15), 
                            height=45, command=comando)
        btn.pack(fill="x", padx=15, pady=5)

    def mostrar_vista(self, ClaseVista):
        for widget in self.contenido_dinamico.winfo_children():
            widget.destroy()
        vista = ClaseVista(self.contenido_dinamico, self)
        vista.pack(fill="both", expand=True)

    def exportar_bd(self):
        destino = filedialog.asksaveasfilename(defaultextension=".db", initialfile="comunidad_respaldo.db", filetypes=[("Base de Datos", "*.db")])
        if destino:
            try:
                shutil.copy(self.ruta_bd, destino)
                messagebox.showinfo("Éxito", "La base de datos se exportó correctamente.")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo exportar la base de datos:\n{e}")

    def importar_bd(self):
        origen = filedialog.askopenfilename(filetypes=[("Base de Datos", "*.db")])
        if origen:
            if messagebox.askyesno("Advertencia", "Esto reemplazará toda la información actual del sistema. ¿Estás seguro de continuar?"):
                try:
                    # 1. Copiar y reemplazar el archivo de base de datos
                    shutil.copy(origen, self.ruta_bd)
                    
                    messagebox.showinfo(
                        "Éxito", 
                        "Base de datos cargada correctamente.\nEl sistema se reiniciará automáticamente."
                    )
                    
                    # 2. Obtener ejecutable y argumentos
                    python = sys.executable
                    
                    # 3. Reemplazar proceso actual por una nueva instancia
                    os.execl(python, python, *sys.argv)

                except Exception as e:
                    messagebox.showerror("Error", f"No se pudo cargar la base de datos:\n{e}")

    def cerrar_sesion(self):
        self.destroy()