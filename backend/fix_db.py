import sqlite3
conn = sqlite3.connect('sio_inventario.db')
cursor = conn.cursor()
cursor.execute("PRAGMA table_info(proyectos)")
columnas = [info[1] for info in cursor.fetchall()]
print("Columnes actuals a la taula 'proyectos':", columnas)
conn.close()