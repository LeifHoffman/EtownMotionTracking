# db_seed.py
import sqlite3
from datetime import datetime, timedelta
import random

conn = sqlite3.connect("motion_tracking.db")
cur = conn.cursor()

athletes = [
    ("Vincent", "Junior",   "6-1",  185),
    ("Evan", "Senior",   "6-3",  180),
    ("James", "Sophomore","5-11", 190),
    ("Leif", "Junior",   "5-10", 165),
    ("Sarah", "Senior",   "5-6",  135),
    ("Emma", "Freshman", "5-9",  145),
    ("Michael", "Junior",   "6-4",  210),
    ("Jessica", "Sophomore","5-5",  130),
]

cur.executemany(
    "INSERT INTO athletes (name, year, height, weight) VALUES (?,?,?,?)",
    athletes
)
conn.commit()

cur.execute("SELECT id, name FROM athletes")
athlete_rows = cur.fetchall()

base_date = datetime.now() - timedelta(days=180)

for athlete_id, name in athlete_rows:
    jump_baseline = random.uniform(16.0, 22.0)
    sprint_baseline = random.uniform(4.5, 5.2)

    for i in range(8):
        session_date = base_date + timedelta(days=i * 22 + random.randint(0, 5))
        stype = "jump" if i % 2 == 0 else "sprint"

        cur.execute(
            "INSERT INTO sessions (athlete_id, started_at, ended_at, frame_count, session_type, video_filename) VALUES (?,?,?,?,?,?)",
            (
                athlete_id,
                session_date.isoformat(),
                (session_date + timedelta(minutes=random.randint(5, 20))).isoformat(),
                random.randint(200, 900),
                stype,
                f"recording_{name}_{session_date.strftime('%Y%m%d')}.mp4"
            )
        )
        session_id = cur.lastrowid

        if stype == "jump":
            value = round(jump_baseline + (i * 0.15) + random.uniform(-0.3, 0.3), 2)
            cur.execute(
                "INSERT INTO results (session_id, metric_name, metric_value) VALUES (?,?,?)",
                (session_id, "jump_height_in", value)
            )
        else:
            value = round(sprint_baseline - (i * 0.02) + random.uniform(-0.05, 0.05), 3)
            cur.execute(
                "INSERT INTO results (session_id, metric_name, metric_value) VALUES (?,?,?)",
                (session_id, "sprint_time_s", value)
            )

conn.commit()
cur.close()
conn.close()
print("Seed complete.")