import sqlite3


def sample_data():
    conn = sqlite3.connect("auto_produktion.db")
    conn.execute("PRAGMA foreign_keys = ON;")
    cur = conn.cursor()

    hersteller_liste = [
        ("Contoso Motors",),
        ("Fabrik AG",),
        ("Autowerk GmbH",),
        ("Speedster Co.",),
        ("Nordic Cars",),
        ("Berlin Automotive",),
        ("Elbtal Motors",),
        ("Thunder Cars",),
        ("EcoDrive Inc.",),
        ("Prime AutoTech",)
    ]

    cur.executemany(
        "INSERT INTO HERSTELLER (Name) VALUES (?)",
        hersteller_liste
    )

    besitzer_liste = [
        ("Max Mustermann",),
        ("Joe Mama",),
        ("Ben Dover",),
        ("Sarah Müller",),
        ("Jonas Schmidt",),
        ("Laura Schneider",),
        ("Felix Bauer",),
        ("Nina Fischer",),
        ("Tobias Richter",),
        ("Emma Hoffmann",)
    ]

    cur.executemany(
        "INSERT INTO BESITZER (Name) VALUES (?)",
        besitzer_liste
    )

    auto_namen = [
        "Electra One",
        "Pulse Drive",
        "Terra Rover",
        "Canyon Runner",
        "Imperia Deluxe",
        "Crystal Via",
        "Monarch Essence",
        "Ventura GT",
        "Solaris V8",
        "Nova Striker",
    ]

    cur.execute("SELECT Hersteller_ID FROM HERSTELLER")
    hersteller_ids = [row[0] for row in cur.fetchall()]

    cur.execute("SELECT Besitzer_ID FROM BESITZER")
    besitzer_ids = [row[0] for row in cur.fetchall()]

    # Besitzer IDs definieren
    max_id = besitzer_ids[0]  # Max Mustermann
    joe_id = besitzer_ids[1]  # Joe Mama

    auto_liste = []
    for i, name in enumerate(auto_namen):
        auto_liste.append((
            name,
            hersteller_ids[i],
            besitzer_ids[i]
        ))

    # (Max)
    auto_liste.append(("Canyon Runner", hersteller_ids[3], max_id))
    auto_liste.append(("Ventura GT", hersteller_ids[7], max_id))

    # (Joe)
    auto_liste.append(("Monarch Essence", hersteller_ids[6], joe_id))
    auto_liste.append(("Nova Striker", hersteller_ids[9], joe_id))

    cur.executemany(
        "INSERT INTO AUTO (Name, Hersteller_ID, Besitzer_ID) VALUES (?,?,?)",
        auto_liste
    )

    conn.commit()
    conn.close()


if __name__ == "__main__":
    sample_data()
