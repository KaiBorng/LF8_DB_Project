from fastapi import FastAPI, Request, HTTPException
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import sqlite3

# ---------------------------
# DB & App Setup
# ---------------------------
def get_db():
    conn = sqlite3.connect("auto_produktion.db")
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

app = FastAPI()
templates = Jinja2Templates(directory="templates")

ALLOWED_TABLES = {"AUTO", "BESITZER", "HERSTELLER"}

# ---------------------------
# Hilfsfunktionen
# ---------------------------
def exists_by_id(cur, table: str, pk_name: str, id_value: int) -> bool:
    cur.execute(f'SELECT 1 FROM "{table}" WHERE "{pk_name}" = ?', (id_value,))
    return cur.fetchone() is not None

def count_refs(cur, table: str, fk_col: str, id_value: int) -> int:
    cur.execute(f'SELECT COUNT(*) AS cnt FROM "{table}" WHERE "{fk_col}" = ?', (id_value,))
    row = cur.fetchone()
    return int(row["cnt"]) if row else 0

# ---------------------------
# UI & Lesen (deine bestehenden Endpunkte)
# ---------------------------
@app.get("/")
def ui(request: Request):
    # Dropdown initial mit erlaubten Tabellen füllen
    return templates.TemplateResponse(
        "browser.html",
        {"request": request, "tables": sorted(list(ALLOWED_TABLES))}
    )

@app.get("/table/{table_name}")
def table_data(table_name: str):
    t = table_name.upper()
    if t not in ALLOWED_TABLES:
        raise HTTPException(status_code=404, detail="Tabelle nicht erlaubt oder nicht vorhanden.")
    db = get_db()
    cur = db.cursor()
    query = f'SELECT * FROM "{t}"'
    cur.execute(query)
    rows = cur.fetchall()
    return [dict(r) for r in rows]

@app.get("/all_cars")
def get_cars():
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT Name FROM "AUTO"')
    rows = cursor.fetchall()
    return [dict(row) for row in rows]

@app.get("/all_owners")
def get_owners():
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT Name FROM "BESITZER"')
    rows = cursor.fetchall()
    return [dict(row) for row in rows]

@app.get("/all_manufacturers")
def get_manufacturers():
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT Name FROM "HERSTELLER"')
    rows = cursor.fetchall()
    return [dict(row) for row in rows]

@app.get("/all_data")
def get_all_data():
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT * FROM "AUTO"')
    rows = cursor.fetchall()
    return [dict(row) for row in rows]

# ---------------------------
# CREATE (Hinzufügen)
# ---------------------------
class HerstellerCreate(BaseModel):
    Name: str

class BesitzerCreate(BaseModel):
    Name: str

class AutoCreate(BaseModel):
    Name: str
    Hersteller_ID: int
    Besitzer_ID: int

@app.post("/add/hersteller", status_code=201)
def add_hersteller(payload: HerstellerCreate):
    name = (payload.Name or "").strip()
    if not name:
        raise HTTPException(status_code=400, detail="Name darf nicht leer sein.")
    db = get_db()
    try:
        cur = db.cursor()
        cur.execute('INSERT INTO "HERSTELLER" (Name) VALUES (?)', (name,))
        db.commit()
        new_id = cur.lastrowid
        return {"Hersteller_ID": new_id, "Name": name}
    finally:
        db.close()

@app.post("/add/besitzer", status_code=201)
def add_besitzer(payload: BesitzerCreate):
    name = (payload.Name or "").strip()
    if not name:
        raise HTTPException(status_code=400, detail="Name darf nicht leer sein.")
    db = get_db()
    try:
        cur = db.cursor()
        cur.execute('INSERT INTO "BESITZER" (Name) VALUES (?)', (name,))
        db.commit()
        new_id = cur.lastrowid
        return {"Besitzer_ID": new_id, "Name": name}
    finally:
        db.close()

@app.post("/add/auto", status_code=201)
def add_auto(payload: AutoCreate):
    name = (payload.Name or "").strip()
    if not name:
        raise HTTPException(status_code=400, detail="Name darf nicht leer sein.")
    if payload.Hersteller_ID is None or payload.Besitzer_ID is None:
        raise HTTPException(status_code=400, detail="Hersteller_ID und Besitzer_ID sind Pflichtfelder.")

    db = get_db()
    try:
        cur = db.cursor()

        # FK-Prüfung
        if not exists_by_id(cur, "HERSTELLER", "Hersteller_ID", int(payload.Hersteller_ID)):
            raise HTTPException(status_code=400, detail=f"Hersteller_ID {payload.Hersteller_ID} existiert nicht.")
        if not exists_by_id(cur, "BESITZER", "Besitzer_ID", int(payload.Besitzer_ID)):
            raise HTTPException(status_code=400, detail=f"Besitzer_ID {payload.Besitzer_ID} existiert nicht.")

        cur.execute(
            'INSERT INTO "AUTO" (Name, Hersteller_ID, Besitzer_ID) VALUES (?, ?, ?)',
            (name, int(payload.Hersteller_ID), int(payload.Besitzer_ID))
        )
        db.commit()
        new_id = cur.lastrowid
        return {
            "Auto_ID": new_id,
            "Name": name,
            "Hersteller_ID": payload.Hersteller_ID,
            "Besitzer_ID": payload.Besitzer_ID
        }
    finally:
        db.close()

# ---------------------------
# DELETE (Löschen)
# ---------------------------
@app.delete("/delete/auto/{auto_id}")
def delete_auto(auto_id: int):
    db = get_db()
    try:
        cur = db.cursor()
        if not exists_by_id(cur, "AUTO", "Auto_ID", auto_id):
            raise HTTPException(status_code=404, detail=f"Auto_ID {auto_id} nicht gefunden.")
        cur.execute('DELETE FROM "AUTO" WHERE "Auto_ID" = ?', (auto_id,))
        db.commit()
        return {"deleted": True, "Auto_ID": auto_id}
    finally:
        db.close()

@app.delete("/delete/hersteller/{hersteller_id}")
def delete_hersteller(hersteller_id: int):
    db = get_db()
    try:
        cur = db.cursor()
        if not exists_by_id(cur, "HERSTELLER", "Hersteller_ID", hersteller_id):
            raise HTTPException(status_code=404, detail=f"Hersteller_ID {hersteller_id} nicht gefunden.")
        # FK-Referenzen prüfen (ON DELETE RESTRICT)
        cnt = count_refs(cur, "AUTO", "Hersteller_ID", hersteller_id)
        if cnt > 0:
            raise HTTPException(
                status_code=409,
                detail=f"Löschen nicht möglich: {cnt} AUTO-Datensatz/Datensätze verweisen auf diesen Hersteller."
            )
        cur.execute('DELETE FROM "HERSTELLER" WHERE "Hersteller_ID" = ?', (hersteller_id,))
        db.commit()
        return {"deleted": True, "Hersteller_ID": hersteller_id}
    finally:
        db.close()

@app.delete("/delete/besitzer/{besitzer_id}")
def delete_besitzer(besitzer_id: int):
    db = get_db()
    try:
        cur = db.cursor()
        if not exists_by_id(cur, "BESITZER", "Besitzer_ID", besitzer_id):
            raise HTTPException(status_code=404, detail=f"Besitzer_ID {besitzer_id} nicht gefunden.")
        # FK-Referenzen prüfen (ON DELETE RESTRICT)
        cnt = count_refs(cur, "AUTO", "Besitzer_ID", besitzer_id)
        if cnt > 0:
            raise HTTPException(
                status_code=409,
                detail=f"Löschen nicht möglich: {cnt} AUTO-Datensatz/Datensätze verweisen auf diesen Besitzer."
            )
        cur.execute('DELETE FROM "BESITZER" WHERE "Besitzer_ID" = ?', (besitzer_id,))
        db.commit()
        return {"deleted": True, "Besitzer_ID": besitzer_id}
    finally:
        db.close()