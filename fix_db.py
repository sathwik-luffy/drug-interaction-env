with open("server/database.py", "w", encoding="utf-8") as f:
    f.write('''import sqlite3
import json
import os
from datetime import datetime

DB_PATH = os.getenv("DB_PATH", "/tmp/drug_interaction.db")

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    c = conn.cursor()

    # Patients table
    c.execute("""
        CREATE TABLE IF NOT EXISTS patients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            age INTEGER,
            weight INTEGER,
            gender TEXT,
            allergies TEXT,
            conditions TEXT,
            medications TEXT,
            issues TEXT,
            is_safe INTEGER,
            difficulty TEXT
        )
    """)

    # Episodes table
    c.execute("""
        CREATE TABLE IF NOT EXISTS episodes (
            id TEXT PRIMARY KEY,
            task_name TEXT,
            patient_name TEXT,
            started_at TEXT,
            completed_at TEXT,
            total_steps INTEGER DEFAULT 0,
            final_score REAL DEFAULT 0.0,
            model_name TEXT DEFAULT "unknown"
        )
    """)

    # Steps table
    c.execute("""
        CREATE TABLE IF NOT EXISTS steps (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            episode_id TEXT,
            step_number INTEGER,
            action_text TEXT,
            safety_verdict TEXT,
            reward REAL,
            correct_verdict REAL,
            issue_detection REAL,
            explanation_quality REAL,
            medical_terminology REAL,
            created_at TEXT
        )
    """)

    # Leaderboard table
    c.execute("""
        CREATE TABLE IF NOT EXISTS leaderboard (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            model_name TEXT,
            task_name TEXT,
            score REAL,
            episode_id TEXT,
            created_at TEXT
        )
    """)

    conn.commit()

    # Seed patients if empty
    c.execute("SELECT COUNT(*) FROM patients")
    count = c.fetchone()[0]
    if count == 0:
        _seed_patients(c)
        conn.commit()

    conn.close()

def _seed_patients(c):
    patients = [
        ("John Smith", 45, 80, "Male", "none", json.dumps(["hypertension"]), json.dumps(["Lisinopril 10mg once daily"]), json.dumps([]), 1, "easy"),
        ("Robert Lee", 55, 90, "Male", "none", json.dumps(["type 2 diabetes", "hypertension"]), json.dumps(["Metformin 500mg twice daily", "Amlodipine 5mg once daily"]), json.dumps([]), 1, "easy"),
        ("Lisa Taylor", 50, 72, "Female", "none", json.dumps(["hypertension", "high cholesterol"]), json.dumps(["Amlodipine 10mg once daily", "Atorvastatin 20mg once daily"]), json.dumps([]), 1, "easy"),
        ("James Brown", 60, 85, "Male", "aspirin", json.dumps(["chest pain"]), json.dumps(["Aspirin 100mg once daily", "Clopidogrel 75mg once daily"]), json.dumps(["Patient allergic to Aspirin"]), 0, "easy"),
        ("Mary Johnson", 62, 65, "Female", "none", json.dumps(["atrial fibrillation", "depression"]), json.dumps(["Warfarin 5mg once daily", "Aspirin 100mg once daily", "Sertraline 50mg once daily"]), json.dumps(["Warfarin+Aspirin increases bleeding risk", "Warfarin+Sertraline increases bleeding risk"]), 0, "medium"),
        ("Susan Chen", 70, 58, "Female", "penicillin", json.dumps(["pneumonia", "heart failure"]), json.dumps(["Amoxicillin 500mg three times daily", "Furosemide 40mg once daily"]), json.dumps(["Amoxicillin contains penicillin - patient is allergic"]), 0, "medium"),
        ("Emma Davis", 35, 70, "Female", "none", json.dumps(["depression", "anxiety"]), json.dumps(["Sertraline 50mg once daily", "Alprazolam 0.5mg twice daily"]), json.dumps(["Sertraline+Alprazolam CNS depression risk"]), 0, "medium"),
        ("Michael Wong", 58, 75, "Male", "none", json.dumps(["hypertension", "depression"]), json.dumps(["Metoprolol 50mg twice daily", "Fluoxetine 20mg once daily", "Tramadol 50mg as needed"]), json.dumps(["Tramadol+Fluoxetine serotonin syndrome risk", "Metoprolol+Fluoxetine interaction"]), 0, "medium"),
        ("David Wilson", 78, 55, "Male", "sulfa drugs", json.dumps(["kidney disease", "heart failure", "diabetes"]), json.dumps(["Metformin 1000mg twice daily", "Ibuprofen 400mg three times daily", "Furosemide 40mg once daily", "Digoxin 0.25mg once daily", "Glibenclamide 5mg once daily"]), json.dumps(["Metformin risky with kidney disease", "Ibuprofen contraindicated with kidney disease", "Glibenclamide+Furosemide interaction"]), 0, "hard"),
        ("Patricia Moore", 82, 52, "Female", "penicillin", json.dumps(["osteoporosis", "kidney disease", "hypertension", "depression"]), json.dumps(["Amoxicillin 500mg three times daily", "Ibuprofen 400mg twice daily", "Lisinopril 10mg once daily", "Sertraline 50mg once daily", "Alendronate 70mg weekly"]), json.dumps(["Amoxicillin - penicillin allergy", "Ibuprofen contraindicated with kidney disease", "Ibuprofen reduces Lisinopril effectiveness"]), 0, "hard"),
    ]
    c.executemany("INSERT INTO patients (name, age, weight, gender, allergies, conditions, medications, issues, is_safe, difficulty) VALUES (?,?,?,?,?,?,?,?,?,?)", patients)

def get_random_patient(difficulty):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM patients WHERE difficulty=? ORDER BY RANDOM() LIMIT 1", (difficulty,))
    row = c.fetchone()
    conn.close()
    if row:
        return {
            "name": row["name"], "age": row["age"], "weight": row["weight"],
            "gender": row["gender"], "allergies": row["allergies"],
            "conditions": json.loads(row["conditions"]),
            "medications": json.loads(row["medications"]),
            "issues": json.loads(row["issues"]),
            "safe": bool(row["is_safe"]),
            "difficulty": row["difficulty"]
        }
    return None

def log_episode(episode_id, task_name, patient_name, model_name="unknown"):
    conn = get_connection()
    conn.execute("INSERT OR IGNORE INTO episodes (id, task_name, patient_name, started_at, model_name) VALUES (?,?,?,?,?)",
                 (episode_id, task_name, patient_name, datetime.utcnow().isoformat(), model_name))
    conn.commit()
    conn.close()

def log_step(episode_id, step_number, action_text, safety_verdict, reward, scores):
    conn = get_connection()
    conn.execute("""INSERT INTO steps (episode_id, step_number, action_text, safety_verdict, reward,
                    correct_verdict, issue_detection, explanation_quality, medical_terminology, created_at)
                    VALUES (?,?,?,?,?,?,?,?,?,?)""",
                 (episode_id, step_number, action_text[:500], safety_verdict, reward,
                  scores.get("correct_verdict", 0), scores.get("issue_detection", 0),
                  scores.get("explanation_quality", 0), scores.get("medical_terminology", 0),
                  datetime.utcnow().isoformat()))
    conn.commit()
    conn.close()

def complete_episode(episode_id, total_steps, final_score):
    conn = get_connection()
    conn.execute("UPDATE episodes SET completed_at=?, total_steps=?, final_score=? WHERE id=?",
                 (datetime.utcnow().isoformat(), total_steps, final_score, episode_id))
    conn.commit()
    conn.close()

def update_leaderboard(model_name, task_name, score, episode_id):
    conn = get_connection()
    conn.execute("INSERT INTO leaderboard (model_name, task_name, score, episode_id, created_at) VALUES (?,?,?,?,?)",
                 (model_name, task_name, score, episode_id, datetime.utcnow().isoformat()))
    conn.commit()
    conn.close()

def get_leaderboard(limit=10):
    conn = get_connection()
    c = conn.cursor()
    c.execute("""SELECT model_name, AVG(score) as avg_score, COUNT(*) as runs, MAX(score) as best_score
                 FROM leaderboard GROUP BY model_name ORDER BY avg_score DESC LIMIT ?""", (limit,))
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows

def get_episode_history(limit=20):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM episodes ORDER BY started_at DESC LIMIT ?", (limit,))
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows
''')
print("database.py done!")