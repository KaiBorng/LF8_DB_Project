import sqlite3

conn = sqlite3.connect("auto_produktion.db")
cur = conn.cursor()

print("\nAlle Autos:")
for row in cur.execute("""
                       SELECT a.Auto_ID, a.Name, h.Name, b.Name
                       FROM AUTO a
                                JOIN HERSTELLER h ON h.Hersteller_ID = a.Hersteller_ID
                                JOIN BESITZER b ON b.Besitzer_ID = a.Besitzer_ID
                       """):
    print(row)

conn.close()
