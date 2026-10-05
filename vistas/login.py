import customtkinter as ctk
import sqlite3
import os
import ctypes
from tkinter import messagebox
from PIL import Image

class VentanaLogin(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Consejo Comunal Andrés Eloy Blanco - Acceso")
        
        ruta_ico = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets', 'logo.ico')
        if os.path.exists(ruta_ico):
            self.iconbitmap(ruta_ico)
            myappid = 'consejo.comunal.andres.eloy.blanco.1.0'
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

        self.after(0, lambda: self.state("zoomed"))
        # Fondo gris azulado claro para que la tarjeta blanca resalte
        self.configure(fg_color="#E8ECF1")

        # Tarjeta de Login central con borde sutil
        self.frame_login = ctk.CTkFrame(self, fg_color="white", corner_radius=20, border_width=1, border_color="#D1D5DB")
        self.frame_login.place(relx=0.5, rely=0.5, anchor="center")

        ruta_logo = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets', 'logo.jpg')
        if os.path.exists(ruta_logo):
            img = Image.open(ruta_logo)
            self.logo_image = ctk.CTkImage(light_image=img, size=(120, 150))
            self.lbl_logo = ctk.CTkLabel(self.frame_login, image=self.logo_image, text="")
            self.lbl_logo.pack(padx=60, pady=(40, 10))

        self.lbl_titulo = ctk.CTkLabel(self.frame_login, text="C.C. Andrés Eloy Blanco", font=("Arial", 22, "bold"), text_color="#1E5631")
        self.lbl_titulo.pack(padx=60, pady=(0, 20))

        self.ent_usuario = ctk.CTkEntry(self.frame_login, placeholder_text="Usuario", width=260, height=45, corner_radius=8)
        self.ent_usuario.pack(pady=10)

        self.frame_pass = ctk.CTkFrame(self.frame_login, fg_color="transparent")
        self.frame_pass.pack(pady=10)

        self.ent_contrasena = ctk.CTkEntry(self.frame_pass, placeholder_text="Contraseña", show="*", width=215, height=45, corner_radius=8)
        self.ent_contrasena.pack(side="left", padx=(0, 5))

        self.btn_ojo = ctk.CTkButton(self.frame_pass, text="👁", width=40, height=45, fg_color="#1E5631", corner_radius=8, command=self.alternar_contrasena)
        self.btn_ojo.pack(side="left")

        self.btn_ingresar = ctk.CTkButton(self.frame_login, text="Ingresar al Sistema", width=260, height=45, font=("Arial", 15, "bold"), fg_color="#1E5631", corner_radius=8, command=self.verificar_credenciales)
        self.btn_ingresar.pack(pady=(20, 40))

        self.bind('<Return>', lambda event: self.verificar_credenciales())

    def alternar_contrasena(self):
        if self.ent_contrasena.cget("show") == "*":
            self.ent_contrasena.configure(show="")
            self.btn_ojo.configure(text="🙈")
        else:
            self.ent_contrasena.configure(show="*")
            self.btn_ojo.configure(text="👁")

    def verificar_credenciales(self):
        usuario = self.ent_usuario.get()
        contrasena = self.ent_contrasena.get()
        
        if usuario == "admin" and contrasena == "1234":
            self.abrir_menu(usuario)
            return

        ruta_bd = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'bd', 'comunidad.db')
        try:
            conexion = sqlite3.connect(ruta_bd)
            cursor = conexion.cursor()
            cursor.execute("SELECT * FROM usuarios WHERE usuario=? AND contrasena=?", (usuario, contrasena))
            resultado = cursor.fetchone()
            conexion.close()
            
            if resultado:
                self.abrir_menu(usuario)
            else:
                messagebox.showerror("Error", "Usuario o contraseña incorrectos.")
        except Exception as e:
            messagebox.showerror("Error BD", f"Falla al conectar:\n{e}")

    def abrir_menu(self, usuario):
        self.destroy()
        from vistas.app_principal import AppPrincipal
        app = AppPrincipal(usuario)
        app.mainloop()