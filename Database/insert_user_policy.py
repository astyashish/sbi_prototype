import sqlite3
from datetime import datetime

# Function to insert user into the Users table
def insert_user(user_id, name, email):
    conn = sqlite3.connect("insurance.db")
    cursor = conn.cursor()

    cursor.execute("""
    INSERT OR IGNORE INTO Users (user_id, name, email)
    VALUES (?, ?, ?)
    """, (user_id, name, email))

    conn.commit()
    conn.close()
    print("✅ User inserted successfully.")

# Function to insert a policy into the Policies table
def insert_policy(policy_id, policy_name, policy_type, premium, coverage_amount):
    conn = sqlite3.connect("insurance.db")
    cursor = conn.cursor()

    cursor.execute("""
    INSERT OR IGNORE INTO Policies (policy_id, policy_name, policy_type, premium, coverage_amount)
    VALUES (?, ?, ?, ?, ?)
    """, (policy_id, policy_name, policy_type, premium, coverage_amount))

    conn.commit()
    conn.close()
    print("✅ Policy inserted successfully.")

# Function to insert a recommendation into the Recommendations table
def insert_recommendation(user_id, policy_id, recommendation_score):
    conn = sqlite3.connect("insurance.db")
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO Recommendations (user_id, policy_id, recommendation_score, recommended_at)
    VALUES (?, ?, ?, ?)
    """, (user_id, policy_id, recommendation_score, datetime.now().isoformat()))

    conn.commit()
    conn.close()
    print("✅ Recommendation inserted successfully.")

# Function to output all information for a user
def output_user_info(user_id):
    conn = sqlite3.connect("insurance.db")
    cursor = conn.cursor()

    # Get user info
    cursor.execute("SELECT * FROM Users WHERE user_id = ?", (user_id,))
    user = cursor.fetchone()

    if user:
        print(f"\nUser Information:")
        print(f"User ID: {user[0]}")
        print(f"Name: {user[1]}")
        print(f"Email: {user[2]}")

        # Get user recommendations
        cursor.execute("""
        SELECT r.recommendation_id, p.policy_name, r.recommendation_score, r.recommended_at
        FROM Recommendations r
        JOIN Policies p ON r.policy_id = p.policy_id
        WHERE r.user_id = ?
        """, (user_id,))
        recommendations = cursor.fetchall()

        if recommendations:
            print("\nRecommendations:")
            for rec in recommendations:
                print(f"Recommendation ID: {rec[0]} | Policy: {rec[1]} | Score: {rec[2]} | Recommended At: {rec[3]}")
        else:
            print("\nNo recommendations found for this user.")

    else:
        print("\nUser not found.")

    conn.close()

# Main program that takes input and inserts data
def main():
    # Get user input for User, Policy, and Recommendation
    print("Enter user details:")

    user_id = input("User ID: ")
    name = input("Name: ")
    email = input("Email: ")

    insert_user(user_id, name, email)

    print("\nEnter policy details:")
    policy_id = input("Policy ID: ")
    policy_name = input("Policy Name: ")
    policy_type = input("Policy Type: ")
    premium = float(input("Premium: "))
    coverage_amount = float(input("Coverage Amount: "))

    insert_policy(policy_id, policy_name, policy_type, premium, coverage_amount)

    print("\nEnter recommendation details:")
    recommendation_score = float(input("Recommendation Score: "))

    insert_recommendation(user_id, policy_id, recommendation_score)

    # Output the user's information
    print("\nDisplaying all information for the user:")
    output_user_info(user_id)

if __name__ == "__main__":
    main()
