# setup_db.py
import sqlite3
from pathlib import Path

DB_FILENAME = "auto_produktion.db"

DDL_SCRIPT = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS HERSTELLER (
    Hersteller_ID INTEGER PRIMARY KEY,
    Name          TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS BESITZER (
    Besitzer_ID INTEGER PRIMARY KEY,
    Name        TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS AUTO (
    Auto_ID        INTEGER PRIMARY KEY,
    Name           TEXT    NOT NULL,
    Hersteller_ID  INTEGER NOT NULL,
    Besitzer_ID    INTEGER NOT NULL,
    CONSTRAINT fk_auto_hersteller
        FOREIGN KEY (Hersteller_ID)
        REFERENCES HERSTELLER(Hersteller_ID)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,
    CONSTRAINT fk_auto_besitzer
        FOREIGN KEY (Besitzer_ID)
        REFERENCES BESITZER(Besitzer_ID)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
);

-- Performance: Indizes auf den FK-Spalten
CREATE INDEX IF NOT EXISTS idx_auto_hersteller ON AUTO(Hersteller_ID);
CREATE INDEX IF NOT EXISTS idx_auto_besitzer   ON AUTO(Besitzer_ID);
"""


def create_database(db_path: Path):
    # 1) Verbindung zur persistenten Datei
    conn = sqlite3.connect(db_path)
    try:
        # 2) Fremdschlüssel aktivieren (pro Verbindung nötig in SQLite)
        conn.execute("PRAGMA foreign_keys = ON;")

        # 3) Tabellen & Indizes anlegen (idempotent)
        conn.executescript(DDL_SCRIPT)

        conn.commit()

        # 4) Mini-Check: Tabellen auflisten (kein Daten-Insert!)
        cur = conn.cursor()
        cur.execute("""
                    SELECT name
                    FROM sqlite_master
                    WHERE type = 'table'
                    ORDER BY name;
                    """)
        tables = [r[0] for r in cur.fetchall()]

    finally:
        conn.close()


def main():
    db_path = Path(DB_FILENAME)
    create_database(db_path)

def get_db():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn

if __name__ == "__main__":
    main()