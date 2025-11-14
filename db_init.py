import sqlite3
import os

SAMPLE_HOSPITALS = [
    # id, name, lat, lon
    (1, "Asha Multispeciality Hospital", 17.4350, 78.4480),
    (2, "Sri Sai Care Clinic", 17.4410, 78.4550),
    (3, "City General Hospital", 17.4300, 78.4400),
    (4, "Neighborhood Nursing Home", 17.4200, 78.4600),
]

# Treatment price samples (hospital_id, treatment_code, treatment_name, price)
SAMPLE_TREATMENTS = [
    (1, "APPENDECTOMY", "Appendectomy", 45000),
    (2, "APPENDECTOMY", "Appendectomy", 40000),
    (3, "APPENDECTOMY", "Appendectomy", 48000),

    (1, "CATARACT_SURGERY", "Cataract Surgery", 25000),
    (3, "CATARACT_SURGERY", "Cataract Surgery", 22000),
    (4, "CATARACT_SURGERY", "Cataract Surgery", 30000),

    (1, "DIALYSIS_SESSION", "Dialysis (per session)", 2500),
    (2, "DIALYSIS_SESSION", "Dialysis (per session)", 2000),
    (4, "DIALYSIS_SESSION", "Dialysis (per session)", 2300),

    (1, "MRI_BRAIN", "MRI - Brain", 6000),
    (2, "MRI_BRAIN", "MRI - Brain", 5500),
    (3, "MRI_BRAIN", "MRI - Brain", 7000),
]

def init_db(db_path):
    created = False
    if not os.path.exists(db_path):
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute("""
            CREATE TABLE hospitals (
                id INTEGER PRIMARY KEY,
                name TEXT,
                lat REAL,
                lon REAL
            )
        """)
        c.execute("""
            CREATE TABLE hospital_treatments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                hospital_id INTEGER,
                treatment_code TEXT,
                treatment_name TEXT,
                price REAL,
                FOREIGN KEY(hospital_id) REFERENCES hospitals(id)
            )
        """)
        c.executemany("INSERT INTO hospitals (id, name, lat, lon) VALUES (?, ?, ?, ?)", SAMPLE_HOSPITALS)
        for h_id, treat_code, treat_name, price in SAMPLE_TREATMENTS:
            c.execute("INSERT INTO hospital_treatments (hospital_id, treatment_code, treatment_name, price) VALUES (?, ?, ?, ?)",
                      (h_id, treat_code, treat_name, price))
        conn.commit()
        conn.close()
        created = True
    return created

def query_hospitals_for_treatment(db_path, treatment_code):
    """
    Returns rows as dicts: id, name, lat, lon, price, treatment_name
    """
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("""
        SELECT h.id, h.name, h.lat, h.lon, ht.price, ht.treatment_name
        FROM hospital_treatments ht
        JOIN hospitals h ON ht.hospital_id = h.id
        WHERE ht.treatment_code = ?
    """, (treatment_code,))
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows