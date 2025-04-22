import sqlite3
import uuid
from datetime import datetime
from typing import Dict, Optional

class InsuranceDatabase:
    def __init__(self, db_path: str = "insurance_analytics.db"):
        """Initialize the database connection and create tables"""
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path)
        self._create_tables()
        self._initialize_policies()
        
    def _create_tables(self):
        """Create all required tables if they don't exist"""
        cursor = self.conn.cursor()
        
        # Users table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY,
            first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_seen TIMESTAMP,
            ip_address TEXT,
            user_agent TEXT
        )
        """)
        
        # Policies table (contains all insurance products)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS policies (
            policy_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            description TEXT,
            base_premium REAL,
            coverage_amount REAL,
            term_years INTEGER,
            popularity INTEGER DEFAULT 0
        )
        """)
        
        # User sessions table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            session_id TEXT PRIMARY KEY,
            user_id TEXT,
            start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            end_time TIMESTAMP,
            device_type TEXT,
            os TEXT,
            browser TEXT,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
        """)
        
        # Page views table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS page_views (
            view_id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            page_url TEXT NOT NULL,
            view_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            duration_seconds INTEGER,
            FOREIGN KEY (session_id) REFERENCES sessions(session_id)
        )
        """)
        
        # Policy interactions table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS policy_interactions (
            interaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            policy_id TEXT,
            interaction_type TEXT CHECK(interaction_type IN ('view', 'details', 'calculate', 'apply')),
            interaction_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (session_id) REFERENCES sessions(session_id),
            FOREIGN KEY (policy_id) REFERENCES policies(policy_id)
        )
        """)
        
        # Form submissions table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS form_submissions (
            submission_id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            form_type TEXT,
            data_json TEXT,
            submit_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (session_id) REFERENCES sessions(session_id)
        )
        """)
        
        self.conn.commit()
    
    def _initialize_policies(self):
        """Initialize the database with all insurance policies"""
        cursor = self.conn.cursor()
        
        # Check if policies already exist
        cursor.execute("SELECT COUNT(*) FROM policies")
        if cursor.fetchone()[0] > 0:
            return
            
        # Protection Plans
        protection_plans = [
            ("sbipp1", "Term Life Protection", "Protection", "Basic term life insurance", 5000, 1000000, 10),
            ("sbipp2", "Enhanced Life Cover", "Protection", "Higher coverage term life", 8000, 2000000, 15),
            ("sbipp3", "Family Protection", "Protection", "Whole family coverage", 12000, 3000000, 20)
        ]
        
        # Savings Plans
        savings_plans = [
            ("sbisp1", "Wealth Builder", "Savings", "Regular savings with life cover", 10000, 500000, 15),
            ("sbisp2", "Future Secure", "Savings", "Long-term savings plan", 15000, 750000, 20),
            ("sbisp3", "Money Grow", "Savings", "High-yield savings", 20000, 1000000, 25)
        ]
        
        # ULIP Plans
        ulip_plans = [
            ("sbiu1", "Wealth Gain", "ULIP", "Market-linked returns", 12000, 800000, 10),
            ("sbiu2", "Future Gain", "ULIP", "Long-term wealth creation", 18000, 1200000, 15)
        ]
        
        # Insert all policies
        all_plans = protection_plans + savings_plans + ulip_plans
        cursor.executemany(
            "INSERT INTO policies (policy_id, name, category, description, base_premium, coverage_amount, term_years) VALUES (?, ?, ?, ?, ?, ?, ?)",
            all_plans
        )
        
        self.conn.commit()
    
    def create_user(self, ip_address: str, user_agent: str) -> str:
        """Create a new user record and return user ID"""
        user_id = str(uuid.uuid4())
        cursor = self.conn.cursor()
        
        cursor.execute(
            "INSERT INTO users (user_id, last_seen, ip_address, user_agent) VALUES (?, CURRENT_TIMESTAMP, ?, ?)",
            (user_id, ip_address, user_agent)
        )
        
        self.conn.commit()
        return user_id
    
    def create_session(self, user_id: str, device_info: Dict) -> str:
        """Create a new browsing session for a user"""
        session_id = str(uuid.uuid4())
        cursor = self.conn.cursor()
        
        cursor.execute(
            """INSERT INTO sessions (
                session_id, user_id, device_type, os, browser
            ) VALUES (?, ?, ?, ?, ?)""",
            (
                session_id,
                user_id,
                device_info.get('device_type'),
                device_info.get('os'),
                device_info.get('browser')
            )
        )
        
        self.conn.commit()
        return session_id
    
    def record_page_view(self, session_id: str, page_url: str, duration: Optional[int] = None):
        """Record a page view event"""
        cursor = self.conn.cursor()
        
        cursor.execute(
            "INSERT INTO page_views (session_id, page_url, duration_seconds) VALUES (?, ?, ?)",
            (session_id, page_url, duration)
        )
        
        self.conn.commit()
    
    def record_policy_interaction(self, session_id: str, policy_id: str, interaction_type: str):
        """Record a user interaction with a policy"""
        cursor = self.conn.cursor()
        
        # Record the interaction
        cursor.execute(
            "INSERT INTO policy_interactions (session_id, policy_id, interaction_type) VALUES (?, ?, ?)",
            (session_id, policy_id, interaction_type)
        )
        
        # Update popularity count
        cursor.execute(
            "UPDATE policies SET popularity = popularity + 1 WHERE policy_id = ?",
            (policy_id,)
        )
        
        self.conn.commit()
    
    def record_form_submission(self, session_id: str, form_type: str, form_data: Dict):
        """Record a form submission"""
        cursor = self.conn.cursor()
        
        cursor.execute(
            "INSERT INTO form_submissions (session_id, form_type, data_json) VALUES (?, ?, ?)",
            (session_id, form_type, json.dumps(form_data))
        )
        
        self.conn.commit()
    
    def end_session(self, session_id: str):
        """Mark a session as ended"""
        cursor = self.conn.cursor()
        
        cursor.execute(
            "UPDATE sessions SET end_time = CURRENT_TIMESTAMP WHERE session_id = ?",
            (session_id,)
        )
        
        self.conn.commit()
    
    def get_popular_policies(self, limit: int = 5) -> list:
        """Get the most popular policies by interaction count"""
        cursor = self.conn.cursor()
        
        cursor.execute("""
            SELECT policy_id, name, category, popularity 
            FROM policies 
            ORDER BY popularity DESC 
            LIMIT ?
        """, (limit,))
        
        return cursor.fetchall()
    
    def get_user_journey(self, user_id: str) -> dict:
        """Get all activity for a specific user"""
        cursor = self.conn.cursor()
        
        # Get user info
        cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        user = cursor.fetchone()
        
        if not user:
            return None
            
        result = {
            'user_id': user[0],
            'sessions': []
        }
        
        # Get all sessions for this user
        cursor.execute("SELECT * FROM sessions WHERE user_id = ? ORDER BY start_time", (user_id,))
        sessions = cursor.fetchall()
        
        for session in sessions:
            session_data = {
                'session_id': session[0],
                'start_time': session[2],
                'end_time': session[3],
                'pages': [],
                'policy_interactions': []
            }
            
            # Get page views for this session
            cursor.execute("SELECT page_url, view_time FROM page_views WHERE session_id = ?", (session[0],))
            session_data['pages'] = cursor.fetchall()
            
            # Get policy interactions for this session
            cursor.execute("""
                SELECT p.name, pi.interaction_type, pi.interaction_time 
                FROM policy_interactions pi
                JOIN policies p ON pi.policy_id = p.policy_id
                WHERE pi.session_id = ?
            """, (session[0],))
            session_data['policy_interactions'] = cursor.fetchall()
            
            result['sessions'].append(session_data)
        
        return result
    
    def close(self):
        """Close the database connection"""
        if self.conn:
            self.conn.close()

# Example usage
if __name__ == "__main__":
    db = InsuranceDatabase()
    
    try:
        # Create a test user
        user_id = db.create_user("192.168.1.1", "Mozilla/5.0")
        
        # Create a session
        session_id = db.create_session(user_id, {
            'device_type': 'desktop',
            'os': 'Windows',
            'browser': 'Chrome'
        })
        
        # Record some page views
        db.record_page_view(session_id, "/insurance")
        db.record_page_view(session_id, "/insurance/protection", 30)
        
        # Record policy interactions
        db.record_policy_interaction(session_id, "sbipp1", "view")
        db.record_policy_interaction(session_id, "sbipp1", "details")
        
        # End session
        db.end_session(session_id)
        
        # Get popular policies
        print("Most popular policies:")
        for policy in db.get_popular_policies():
            print(f"- {policy[1]} ({policy[2]}): {policy[3]} views")
        
        # Get user journey
        print("\nUser journey:")
        journey = db.get_user_journey(user_id)
        print(f"User {journey['user_id']} had {len(journey['sessions'])} sessions")
        
    finally:
        db.close()