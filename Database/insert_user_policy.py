import sqlite3
from datetime import datetime

def initialize_database():
    """Create the database and tables if they don't exist"""
    conn = sqlite3.connect("insurance_analytics.db")
    cursor = conn.cursor()
    
    # Create Users table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Users (
        user_id TEXT PRIMARY KEY,
        name TEXT,
        email TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # Create Policies table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Policies (
        policy_id TEXT PRIMARY KEY,
        policy_name TEXT,
        category TEXT,
        premium REAL,
        coverage_amount REAL,
        term_years INTEGER,
        popularity_score INTEGER DEFAULT 0
    )
    """)
    
    # Create Recommendations table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Recommendations (
        recommendation_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT,
        policy_id TEXT,
        recommendation_score REAL,
        recommended_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES Users(user_id),
        FOREIGN KEY (policy_id) REFERENCES Policies(policy_id)
    )
    """)
    
    # Create PolicyInteractions table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS PolicyInteractions (
        interaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT,
        policy_id TEXT,
        interaction_type TEXT,
        interaction_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES Users(user_id),
        FOREIGN KEY (policy_id) REFERENCES Policies(policy_id)
    )
    """)
    
    conn.commit()
    conn.close()
    print("✅ Database initialized successfully.")

def insert_user(user_id, name, email):
    """Insert a new user into the database"""
    conn = sqlite3.connect("insurance_analytics.db")
    cursor = conn.cursor()
    
    cursor.execute("""
    INSERT OR IGNORE INTO Users (user_id, name, email)
    VALUES (?, ?, ?)
    """, (user_id, name, email))
    
    conn.commit()
    conn.close()
    print(f"✅ User {user_id} inserted successfully.")

def insert_policy(policy_id, policy_name, category, premium, coverage_amount, term_years):
    """Insert a new insurance policy"""
    conn = sqlite3.connect("insurance_analytics.db")
    cursor = conn.cursor()
    
    cursor.execute("""
    INSERT OR IGNORE INTO Policies (
        policy_id, policy_name, category, premium, coverage_amount, term_years
    ) VALUES (?, ?, ?, ?, ?, ?)
    """, (policy_id, policy_name, category, premium, coverage_amount, term_years))
    
    conn.commit()
    conn.close()
    print(f"✅ Policy {policy_id} inserted successfully.")

def record_interaction(user_id, policy_id, interaction_type):
    """Record a user interaction with a policy"""
    conn = sqlite3.connect("insurance_analytics.db")
    cursor = conn.cursor()
    
    # Record the interaction
    cursor.execute("""
    INSERT INTO PolicyInteractions (user_id, policy_id, interaction_type)
    VALUES (?, ?, ?)
    """, (user_id, policy_id, interaction_type))
    
    # Update popularity score for certain interactions
    if interaction_type in ('view', 'learn_more', 'buy_now'):
        cursor.execute("""
        UPDATE Policies
        SET popularity_score = popularity_score + 1
        WHERE policy_id = ?
        """, (policy_id,))
    
    conn.commit()
    conn.close()
    print(f"✅ Interaction recorded: {interaction_type} for policy {policy_id}")

def add_recommendation(user_id, policy_id, score):
    """Add a policy recommendation for a user"""
    conn = sqlite3.connect("insurance_analytics.db")
    cursor = conn.cursor()
    
    cursor.execute("""
    INSERT INTO Recommendations (user_id, policy_id, recommendation_score)
    VALUES (?, ?, ?)
    """, (user_id, policy_id, score))
    
    conn.commit()
    conn.close()
    print(f"✅ Recommendation added for user {user_id}")

def get_user_recommendations(user_id):
    """Get all recommendations for a user"""
    conn = sqlite3.connect("insurance_analytics.db")
    cursor = conn.cursor()
    
    cursor.execute("""
    SELECT r.recommendation_id, p.policy_name, p.category, 
           r.recommendation_score, r.recommended_at
    FROM Recommendations r
    JOIN Policies p ON r.policy_id = p.policy_id
    WHERE r.user_id = ?
    ORDER BY r.recommendation_score DESC
    """, (user_id,))
    
    recommendations = cursor.fetchall()
    conn.close()
    
    if recommendations:
        print(f"\nRecommendations for user {user_id}:")
        for rec in recommendations:
            print(f"- {rec[1]} ({rec[2]}): Score {rec[3]} on {rec[4]}")
    else:
        print(f"\nNo recommendations found for user {user_id}")

def get_popular_policies(limit=5):
    """Get the most popular policies"""
    conn = sqlite3.connect("insurance_analytics.db")
    cursor = conn.cursor()
    
    cursor.execute("""
    SELECT policy_id, policy_name, category, popularity_score
    FROM Policies
    ORDER BY popularity_score DESC
    LIMIT ?
    """, (limit,))
    
    policies = cursor.fetchall()
    conn.close()
    
    if policies:
        print("\nMost popular policies:")
        for policy in policies:
            print(f"- {policy[1]} ({policy[2]}): {policy[3]} interactions")
    else:
        print("\nNo policies found")

def main():
    """Example usage of the database functions"""
    # Initialize the database
    initialize_database()
    
    # Add sample data
    insert_user("user1", "John Doe", "john@example.com")
    insert_user("user2", "Jane Smith", "jane@example.com")
    
    insert_policy("sbipp1", "Term Life", "Protection", 5000, 1000000, 10)
    insert_policy("sbisp1", "Wealth Builder", "Savings", 10000, 500000, 15)
    insert_policy("sbiu1", "Future Gain", "ULIP", 15000, 750000, 20)
    
    # Record interactions
    record_interaction("user1", "sbipp1", "view")
    record_interaction("user1", "sbipp1", "learn_more")
    record_interaction("user2", "sbisp1", "view")
    record_interaction("user2", "sbiu1", "buy_now")
    
    # Add recommendations
    add_recommendation("user1", "sbipp1", 0.85)
    add_recommendation("user1", "sbisp1", 0.72)
    add_recommendation("user2", "sbiu1", 0.91)
    
    # Get recommendations
    get_user_recommendations("user1")
    get_user_recommendations("user2")
    
    # Get popular policies
    get_popular_policies()

if __name__ == "__main__":
    main()