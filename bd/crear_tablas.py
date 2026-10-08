import sqlite3
import os

def inicializar_bd():
    ruta_bd = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'bd', 'comunidad.db')
    os.makedirs(os.path.dirname(ruta_bd), exist_ok=True)
    conexion = sqlite3.connect(ruta_bd)
    cursor = conexion.cursor()

    # 1. Usuarios
    cursor.execute('''CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT, usuario TEXT UNIQUE NOT NULL, contrasena TEXT NOT NULL)''')

    # 2. Familias / Hogares (Se usa "calle" para filtrar)
    cursor.execute('''CREATE TABLE IF NOT EXISTS familias (
        id_hogar INTEGER PRIMARY KEY AUTOINCREMENT, calle TEXT NOT NULL, numero_casa TEXT, 
        jefe_familia TEXT NOT NULL, cedula_jefe TEXT UNIQUE NOT NULL, nro_carga_familiar INTEGER NOT NULL, 
        estatus TEXT DEFAULT 'Activo',
        fecha_nacimiento TEXT)''')

    # 3. Habitantes
    cursor.execute('''CREATE TABLE IF NOT EXISTS habitantes (
        id_beneficiario INTEGER PRIMARY KEY AUTOINCREMENT, cedula TEXT UNIQUE, 
        id_hogar INTEGER, nombres TEXT NOT NULL, genero TEXT, parentesco TEXT, fecha_nacimiento TEXT,
        FOREIGN KEY (id_hogar) REFERENCES familias(id_hogar))''')

    # 4. Inventario
    cursor.execute('''CREATE TABLE IF NOT EXISTS inventario (
        id_producto INTEGER PRIMARY KEY AUTOINCREMENT, descripcion TEXT NOT NULL, cantidad INTEGER NOT NULL)''')

    # 5. Ciclos de Distribución (Actualizado a tu esquema)
    cursor.execute('''CREATE TABLE IF NOT EXISTS ciclos (
        id_ciclo INTEGER PRIMARY KEY AUTOINCREMENT, nombre_ciclo TEXT NOT NULL UNIQUE, 
        fecha_inicio TEXT, fecha_fin TEXT, precio REAL NOT NULL, bolsas_disponibles INTEGER, estatus TEXT DEFAULT 'Activo')''')

    # 6. Tabla Puente: Calles vinculadas a un Ciclo
    cursor.execute('''CREATE TABLE IF NOT EXISTS ciclos_calles (
        id_ciclo INTEGER, calle TEXT,
        FOREIGN KEY (id_ciclo) REFERENCES ciclos(id_ciclo))''')

    # 7. Entregas y Pagos (Transaccional - Vinculado al Hogar)
    cursor.execute('''CREATE TABLE IF NOT EXISTS entregas (
        id_transaccion INTEGER PRIMARY KEY AUTOINCREMENT, id_ciclo INTEGER, id_hogar INTEGER, 
        estado_pago TEXT DEFAULT 'Debe', fecha_pago TEXT, metodo_pago TEXT, recibo TEXT,
        estado_entrega TEXT DEFAULT 'Pendiente', fecha_entrega TEXT,
        FOREIGN KEY (id_ciclo) REFERENCES ciclos(id_ciclo),
        FOREIGN KEY (id_hogar) REFERENCES familias(id_hogar))''')

    # Admin por defecto
    cursor.execute("INSERT OR IGNORE INTO usuarios (usuario, contrasena) VALUES ('admin', '1234')")
    
    conexion.commit()
    conexion.close()

if __name__ == '__main__':
    inicializar_bd()
    print("Base de datos estructurada con éxito.")