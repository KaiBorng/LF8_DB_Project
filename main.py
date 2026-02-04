from fastapi import FastAPI, Request, HTTPException
from fastapi.templating import Jinja2Templates
import sqlite3

def get_db():
    conn = sqlite3.connect("auto_produktion.db")
    conn.row_factory = sqlite3.Row
    # Fremdschlüssel-Constraints auch in der App aktivieren
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

app = FastAPI()
templates = Jinja2Templates(directory="templates")

ALLOWED_TABLES = {"AUTO", "BESITZER", "HERSTELLER"}

@app.get("/all_cars")
def get_cars():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT Name FROM AUTO")
    rows = cursor.fetchall()
    return [dict(row) for row in rows]

@app.get("/all_owners")
def get_owners():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT Name FROM BESITZER")
    rows = cursor.fetchall()
    return [dict(row) for row in rows]

@app.get("/all_manufacturers")
def get_manufacturers():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT Name FROM HERSTELLER")
    rows = cursor.fetchall()
    return [dict(row) for row in rows]

@app.get("/all_data")
def get_all_data():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM AUTO")
    rows = cursor.fetchall()
    return [dict(row) for row in rows]

# Deine UI-Seite (du hast sie auf "/" gelegt – das ist okay)
@app.get("/")
def ui(request: Request):
    return templates.TemplateResponse(
        "browser.html",
        {"request": request, "tables": sorted(list(ALLOWED_TABLES))}
    )

# ❗️WICHTIG: Der Decorator hat vorher gefehlt – deshalb 404!
@app.get("/table/{table_name}")
def table_data(table_name: str):
    t = table_name.upper()
    if t not in ALLOWED_TABLES:
        raise HTTPException(status_code=404, detail="Tabelle nicht erlaubt oder nicht vorhanden.")
    db = get_db()
    cur = db.cursor()
    # Tabellennamen in Quotes für Sicherheit bei Sonderzeichen
    query = f'SELECT * FROM "{t}"'
    cur.execute(query)
    rows = cur.fetchall()
    return [dict(r) for r in rows]