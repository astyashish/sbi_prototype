import sqlite3

conn = sqlite3.connect("insurance.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS Users (
    user_id TEXT PRIMARY KEY,
    name TEXT,
    email TEXT
);
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS Policies (
    policy_id TEXT PRIMARY KEY,
    policy_name TEXT,
    policy_type TEXT,
    premium REAL,
    coverage_amount REAL
);
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS Recommendations (
    recommendation_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT,
    policy_id TEXT,
    recommendation_score REAL,
    recommended_at TEXT,
    FOREIGN KEY (user_id) REFERENCES Users(user_id),
    FOREIGN KEY (policy_id) REFERENCES Policies(policy_id)
);
""")

conn.commit()
conn.close()
print("? Tables created successfully in 'insurance.db'")
