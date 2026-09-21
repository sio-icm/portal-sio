import sqlite3

def afegir_columnes():
    try:
        conn = sqlite3.connect('sio_inventario.db')
        c = conn.cursor()
        # Afegim les dues columnes noves
        c.execute("ALTER TABLE proyectos ADD COLUMN descripcion_corta TEXT")
        c.execute("ALTER TABLE proyectos ADD COLUMN descripcion_ampliada TEXT")
        conn.commit()
        print("✅ Columnes afegides correctament!")
    except Exception as e:
        print("Avís (segurament ja existeixen):", e)
    finally:
        conn.close()

afegir_columnes()