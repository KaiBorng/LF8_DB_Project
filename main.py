from fastapi import FastAPI
from setup_db import get_db

app = FastAPI()

@app.get("/")
def root():
    return {"message": "API läuft!"}


@app.get("/cars")
def get_cars():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM cars")
    rows = cursor.fetchall()
    return [dict(row) for row in rows]
