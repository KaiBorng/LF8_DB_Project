from fastapi import FastAPI
import sqlite3


def get_db():
    conn = sqlite3.connect("auto_produktion.db")
    conn.row_factory = sqlite3.Row
    return conn

app = FastAPI()

@app.get("/")
def root():
    return {"message": "API läuft!"}

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
def get_owners():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT Name FROM HERSTELLER")
    rows = cursor.fetchall()
    return [dict(row) for row in rows]

@app.get("/all_data")
def get_owners():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM AUTO")
    rows = cursor.fetchall()
    return [dict(row) for row in rows]