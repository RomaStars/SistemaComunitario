import customtkinter as ctk
from tkinter import messagebox, filedialog
import sqlite3
import os
from fpdf import FPDF

class VistaSolvencia(ctk.CTkFrame):
    def __init__(self, parent, controlador):
        super().__init__(parent, fg_color="transparent")
        self.controlador = controlador

        ctk.CTkLabel(self, text="Planilla de Control y Firmas", font=("Arial", 24, "bold"), text_color="#1E2B3C").pack(anchor="w", pady=(0, 20))

        self.frame_central = ctk.CTkFrame(self, fg_color="white", corner_radius=10)
        self.frame_central.pack(fill="both", expand=True)

        conexion = self.conectar_bd()
        ciclos = conexion.cursor().execute("SELECT nombre_ciclo FROM ciclos").fetchall()
        conexion.close()
        
        ctk.CTkLabel(self.frame_central, text="Seleccione el Ciclo a Imprimir:", font=("Arial", 16)).pack(pady=(40, 10))
        self.combo_ciclo = ctk.CTkComboBox(self.frame_central, values=[c[0] for c in ciclos] if ciclos else ["Sin ciclos"], width=400, height=40)
        self.combo_ciclo.pack(pady=15)

        ctk.CTkButton(self.frame_central, text="📄 Descargar Planilla PDF", width=400, height=50, font=("Arial", 16, "bold"), fg_color="#1E5631", command=self.generar_pdf).pack(pady=30)

    def conectar_bd(self):
        return sqlite3.connect(self.controlador.ruta_bd)

    def generar_pdf(self):
        ciclo = self.combo_ciclo.get()
        if ciclo == "Sin ciclos": return

        conexion = self.conectar_bd()
        solventes = conexion.cursor().execute('''SELECT f.calle, f.numero_casa, f.jefe_familia, f.cedula_jefe 
            FROM entregas e JOIN ciclos c ON e.id_ciclo = c.id_ciclo JOIN familias f ON e.id_hogar = f.id_hogar
            WHERE c.nombre_ciclo = ? AND e.estado_pago = 'PAGADO' ORDER BY f.calle, f.numero_casa ASC''', (ciclo,)).fetchall()
        conexion.close()

        if not solventes:
            messagebox.showwarning("Atención", "No hay familias registradas como PAGADO en este ciclo.")
            return

        pdf = FPDF(orientation='P', unit='mm', format='A4')
        pdf.add_page()
        
        ruta_logo = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets', 'logo.jpg')
        if os.path.exists(ruta_logo): pdf.image(ruta_logo, x=10, y=8, w=25)

        pdf.set_font("Arial", 'B', 14)
        pdf.cell(0, 10, "CONSEJO COMUNAL ANDRES ELOY BLANCO", align='C', new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 8, f"PLANILLA DE CONTROL DE ENTREGAS Y FIRMAS", align='C', new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Arial", '', 11)
        pdf.cell(0, 8, f"Operativo / Ciclo: {ciclo}", align='C', new_x="LMARGIN", new_y="NEXT")
        pdf.ln(10)

        pdf.set_font("Arial", 'B', 10)
        pdf.cell(10, 10, "N", 1, 0, 'C'); pdf.cell(25, 10, "Calle/Casa", 1, 0, 'C')
        pdf.cell(70, 10, "Jefe de Familia", 1, 0, 'C'); pdf.cell(35, 10, "Cedula", 1, 0, 'C')
        pdf.cell(50, 10, "Firma de Recibido", 1, 1, 'C')

        pdf.set_font("Arial", '', 10)
        for i, fam in enumerate(solventes):
            pdf.cell(10, 10, str(i + 1), 1, 0, 'C')
            pdf.cell(25, 10, f"{fam[0]}/{fam[1]}", 1, 0, 'C')
            pdf.cell(70, 10, fam[2], 1, 0, 'L')
            pdf.cell(35, 10, fam[3], 1, 0, 'C')
            pdf.cell(50, 10, "", 1, 1, 'C')

        pdf.ln(25)
        
        # --- MODIFICACIÓN DE LA AUTORIDAD ---
        pdf.set_font("Arial", 'B', 11)
        pdf.cell(0, 6, "Arnando Pérez", align='C', new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Arial", '', 11)
        pdf.cell(0, 6, "Director", align='C', new_x="LMARGIN", new_y="NEXT")
        # ------------------------------------

        ruta_guardado = filedialog.asksaveasfilename(defaultextension=".pdf", initialfile=f"Planilla_Entregas_{ciclo}.pdf", filetypes=[("PDF", "*.pdf")])
        if ruta_guardado:
            pdf.output(ruta_guardado)
            messagebox.showinfo("Éxito", f"Planilla guardada exitosamente.")