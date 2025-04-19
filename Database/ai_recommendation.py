import sqlite3
from datetime import datetime

conn = sqlite3.connect("insurance.db")
cursor = conn.cursor()

ai_output = {
    "user_id": "user123",
    "recommendations": [
        {"policy_id": "policyA", "score": 0.95},
        {"policy_id": "policyB", "score": 0.89}
    ]
}

cursor.execute("INSERT OR IGNORE INTO Users (user_id, name, email) VALUES (?, ?, ?)",
               ("user123", "John Doe", "john@example.com"))

cursor.execute("INSERT OR IGNORE INTO Policies (policy_id, policy_name, policy_type, premium, coverage_amount) VALUES (?, ?, ?, ?, ?)",
               ("policyA", "Health Plus", "Health", 4000, 100000))
cursor.execute("INSERT OR IGNORE INTO Policies (policy_id, policy_name, policy_type, premium, coverage_amount) VALUES (?, ?, ?, ?, ?)",
               ("policyB", "Secure Life", "Life", 6000, 200000))

for rec in ai_output["recommendations"]:
    cursor.execute("""
        INSERT INTO Recommendations (user_id, policy_id, recommendation_score, recommended_at)
        VALUES (?, ?, ?, ?)
    """, (ai_output["user_id"], rec["policy_id"], rec["score"], datetime.now().isoformat()))

conn.commit()
conn.close()
print("? AI recommendations inserted into the database.")
