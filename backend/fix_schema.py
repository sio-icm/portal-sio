import sqlite3

conn = sqlite3.connect('sio_inventario.db')
cursor = conn.cursor()

columnas = [('financiacion', 'TEXT'), ('descripcion_ampliada', 'TEXT')]

for col, tipo in columnas:
    try:
        cursor.execute(f'ALTER TABLE proyectos ADD COLUMN {col} {tipo}')
        print(f"✅ Columna '{col}' afegida.")
    except sqlite3.OperationalError:
        print(f"⚠️ La columna '{col}' ja existia.")

conn.commit()
conn.close()