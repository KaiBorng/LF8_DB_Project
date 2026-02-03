```mermaid
---
title: LF8 ERM Auto_Produktion
config:
    layout: elk
---
erDiagram
    HERSTELLER ||--|{ AUTO: verkauft
    BESITZER ||--|{ AUTO: gehoert

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