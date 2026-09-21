import sqlite3

def reparar():
    conn = sqlite3.connect('sio_inventario.db')
    cursor = conn.cursor()
    
    # Intentem afegir les columnes si no existeixen
    cols = ['financiacion', 'descripcion_ampliada']
    for col in cols:
        try:
            cursor.execute(f'ALTER TABLE proyectos ADD COLUMN {col} TEXT')
            print(f"✅ Columna {col} afegida")
        except:
            print(f"ℹ️ La columna {col} ja existia")
            
    conn.commit()
    conn.close()
    print("Base de dades preparada.")

reparar()