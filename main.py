import customtkinter as ctk
from vistas.login import VentanaLogin
from bd.crear_tablas import inicializar_bd

ctk.set_appearance_mode("Light") 
ctk.set_default_color_theme("green") 

if __name__ == "__main__":
    inicializar_bd() # Crea las tablas si no existen
    app = VentanaLogin()
    app.mainloop()