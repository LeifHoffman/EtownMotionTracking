# db_init.py
import sqlite3

conn = sqlite3.connect("motion_tracking.db")
cur = conn.cursor()

cur.executescript("""
CREATE TABLE IF NOT EXISTS athletes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    team TEXT,
    year TEXT,
    height TEXT,
    weight INTEGER,
    major TEXT
);

CREATE TABLE IF NOT EXISTS sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    athlete_id INTEGER NOT NULL,
    started_at TEXT NOT NULL,
    ended_at TEXT,
    frame_count INTEGER DEFAULT 0,
    session_type TEXT CHECK(session_type IN ('jump','sprint','other')) DEFAULT 'other',
    video_filename TEXT,
    FOREIGN KEY (athlete_id) REFERENCES athletes(id)
);

CREATE TABLE IF NOT EXISTS results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER NOT NULL,
    metric_name TEXT NOT NULL,
    metric_value REAL NOT NULL,
    FOREIGN KEY (session_id) REFERENCES sessions(id)
);
""")

conn.commit()
conn.close()
print("DB initialized.")