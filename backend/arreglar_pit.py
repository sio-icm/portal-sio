import sqlite3

conn = sqlite3.connect('sio_inventario.db')
cursor = conn.cursor()

try:
    cursor.execute("ALTER TABLE proyectos ADD COLUMN pit TEXT")
    print("✅ Columna 'pit' afegida correctament a la base de dades!")
except Exception as e:
    print("⚠️ Error:", e)

conn.commit()
conn.close()