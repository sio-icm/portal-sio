import sqlite3

def crear_base_datos():
    # Conecta a la base de datos (creará el archivo 'sio_inventario.db' si no existe)
    conexion = sqlite3.connect('sio_inventario.db')
    cursor = conexion.cursor()

    # Crea la tabla principal de instrumentos
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS instrumentos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        categoria TEXT NOT NULL,
        subcategoria TEXT,
        nombre TEXT NOT NULL,
        marca TEXT,
        estado TEXT DEFAULT 'Disponible',
        ultima_calibracion TEXT,
        descripcion TEXT,
        parametros_tecnicos TEXT,
        imagen TEXT
    )
    ''')

    # Comprueba si la tabla está vacía y, si lo está, inserta un equipo de prueba
    cursor.execute("SELECT COUNT(*) FROM instrumentos")
    if cursor.fetchone()[0] == 0:
        cursor.execute('''
        INSERT INTO instrumentos (
            categoria, subcategoria, nombre, marca, estado, 
            ultima_calibracion, descripcion, parametros_tecnicos
        )
        VALUES (
            'Física', 'CTDs', 'Sonda Multiparamètrica (Prova)', 'Sea-Bird', 'Disponible', 
            '2026-05-10', '<b>Descripció General</b><br>Aquest és un equip de prova generat des de la base de dades SQL.', 
            '• Temperatura<br>• Conductivitat<br>• Pressió'
        )
        ''')
        print("✅ Equip de prova inserit correctament.")

    # Guarda los cambios y cierra la conexión
    conexion.commit()
    conexion.close()
    print("✅ Base de dades 'sio_inventario.db' creada i estructurada amb èxit.")

if __name__ == '__main__':
    crear_base_datos()