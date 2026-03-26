```mermaid
---
title: LF8 ERM Auto_Produktion
config:
    layout: elk
---
erDiagram
    HERSTELLER only one--zero or more AUTO: verkauft
    BESITZER zero or one--zero or more AUTO: gehoert

    HERSTELLER {
        integer Hersteller_ID PK
        string Name
    }

    AUTO {
        integer Auto_ID PK
        string Name
        string Hersteller_ID FK
    }

    BESITZER {
        integer Besitzer_ID PK
        string Name
        integer Auto_ID FK
    }
 ```
1. Run [setup_db.py](setup_db.py),  it Initializes the database.
2. Run [sample_data.py](sample_data.py), it creates some test Data in the database.
3. Run [check_data.py](check_data.py), to check if the initialization was a success.
4. Go to the Bash and type uvicorn main:app --reload 
5. You have access to the database via browser (https://localhost:8000)