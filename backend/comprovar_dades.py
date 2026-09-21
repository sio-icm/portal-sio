import sqlite3
conn = sqlite3.connect('sio_inventario.db')
cursor = conn.cursor()
cursor.execute("SELECT count(*) FROM proyectos")
count = cursor.fetchone()[0]
print(f"✅ TENS {count} PROJECTES GUARDATS A LA BASE DE DADES.")
conn.close()