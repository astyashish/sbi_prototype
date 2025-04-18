import sqlite3
import os
from datetime import datetime
import uuid
import json
from typing import Dict, List, Optional

class InsuranceTrackerDB:
    def __init__(self, db_path: str = "insurance_analytics.db"):
        self.db_path = db_path
        self.conn = None
        self._initialize_db()
        
        # Insurance plans configuration
        self.PLANS = {
            "Protection": ["sbipp1", "sbipp2", "sbipp3"],
            "Savings": ["sbisp1", "sbisp2", "sbisp3"],
            "ULIP": ["sbiu1", "sbiu2"],
            "Retirement": ["sbirp1", "sbirp2"],
            "Child": ["sbicp1"],
            "Money Back": ["sbimbp1"],
            "Whole Life": ["sbiwlp1"]
        }

    def _initialize_db(self):
        """Initialize database with all required tables"""
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(self.db_path) if os.path.dirname(self.db_path) else None)
        
        self.conn = sqlite3.connect(self.db_path)
        self.conn.execute("PRAGMA journal_mode=WAL")
        self.conn.execute("PRAGMA synchronous=NORMAL")
        self._create_tables()

    def _create_tables(self):
        """Create all required tables with proper indexes"""
        cursor = self.conn.cursor()
        
        # Users table (anonymous until login)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY,
            first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_seen TIMESTAMP,
            is_authenticated BOOLEAN DEFAULT FALSE,
            auth_id TEXT
        )""")
        
        # Sessions table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            session_id TEXT PRIMARY KEY,
            user_id TEXT,
            start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            end_time TIMESTAMP,
            ip_address TEXT,
            user_agent TEXT,
            device_type TEXT,
            os TEXT,
            browser TEXT,
            screen_resolution TEXT,
            referrer TEXT,
            country TEXT,
            city TEXT,
            FOREIGN KEY (user_id) REFERENCES users (user_id)
        )""")
        
        # Page views table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS page_views (
            view_id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            page_url TEXT,
            view_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            duration_seconds INTEGER,
            scroll_depth INTEGER,
            FOREIGN KEY (session_id) REFERENCES sessions (session_id)
        )""")
        
        # Policy interactions table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS policy_interactions (
            interaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            policy_id TEXT,
            interaction_type TEXT,
            interaction_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            duration_seconds INTEGER,
            FOREIGN KEY (session_id) REFERENCES sessions (session_id)
        )""")
        
        # Click events table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS click_events (
            event_id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            element_id TEXT,
            element_type TEXT,
            page_url TEXT,
            click_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            coordinates TEXT,
            FOREIGN KEY (session_id) REFERENCES sessions (session_id)
        )""")
        
        # Form interactions table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS form_interactions (
            interaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            form_id TEXT,
            field_name TEXT,
            interaction_type TEXT,
            interaction_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            field_value TEXT,
            FOREIGN KEY (session_id) REFERENCES sessions (session_id)
        )""")
        
        # Policy metadata table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS policies (
            policy_id TEXT PRIMARY KEY,
            category TEXT,
            name TEXT,
            base_premium REAL,
            coverage_amount REAL,
            term_years INTEGER,
            popularity_score INTEGER DEFAULT 0
        )""")
        
        # Create indexes for performance
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_sessions_user ON sessions(user_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_page_views_session ON page_views(session_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_policy_interactions ON policy_interactions(policy_id, interaction_type)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_policy_category ON policies(category)")
        
        # Initialize policy data if not exists
        if not cursor.execute("SELECT 1 FROM policies LIMIT 1").fetchone():
            self._initialize_policy_data(cursor)
        
        self.conn.commit()

    def _initialize_policy_data(self, cursor):
        """Insert initial policy data"""
        for category, plans in self.PLANS.items():
            for plan in plans:
                # Generate some realistic sample data
                base_premium = 1000 * (len(plan) + 1)  # Just for demo
                coverage = 1000000 * (len(plan) + 1)
                term = 10 if "p1" in plan else 20 if "p2" in plan else 30
                
                cursor.execute("""
                INSERT INTO policies (policy_id, category, name, base_premium, coverage_amount, term_years)
                VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    plan,
                    category,
                    f"{category} Plan {plan[-1]}",
                    base_premium,
                    coverage,
                    term
                ))

    def create_or_update_user(self, user_id: str = None, auth_id: str = None) -> str:
        """Create or update a user record, returns user_id"""
        if not user_id:
            user_id = str(uuid.uuid4())
        
        cursor = self.conn.cursor()
        cursor.execute("""
        INSERT INTO users (user_id, last_seen, is_authenticated, auth_id)
        VALUES (?, CURRENT_TIMESTAMP, ?, ?)
        ON CONFLICT(user_id) DO UPDATE SET
            last_seen = CURRENT_TIMESTAMP,
            is_authenticated = excluded.is_authenticated,
            auth_id = excluded.auth_id
        """, (user_id, bool(auth_id), auth_id))
        
        self.conn.commit()
        return user_id

    def create_session(self, user_id: str, ip_address: str, user_agent: str,
                      device_info: Dict, referrer: str = None) -> str:
        """Create a new browsing session"""
        session_id = str(uuid.uuid4())
        
        cursor = self.conn.cursor()
        cursor.execute("""
        INSERT INTO sessions (
            session_id, user_id, ip_address, user_agent,
            device_type, os, browser, screen_resolution, referrer
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            session_id,
            user_id,
            ip_address,
            user_agent,
            device_info.get('device_type'),
            device_info.get('os'),
            device_info.get('browser'),
            device_info.get('screen_resolution'),
            referrer
        ))
        
        self.conn.commit()
        return session_id

    def record_page_view(self, session_id: str, page_url: str,
                         duration: int = None, scroll_depth: int = None):
        """Record a page view event"""
        cursor = self.conn.cursor()
        cursor.execute("""
        INSERT INTO page_views (
            session_id, page_url, duration_seconds, scroll_depth
        )
        VALUES (?, ?, ?, ?)
        """, (session_id, page_url, duration, scroll_depth))
        
        self.conn.commit()

    def record_policy_interaction(self, session_id: str, policy_id: str,
                                 interaction_type: str, duration: int = None):
        """Record interaction with a policy (view, learn_more, buy_now)"""
        cursor = self.conn.cursor()
        cursor.execute("""
        INSERT INTO policy_interactions (
            session_id, policy_id, interaction_type, duration_seconds
        )
        VALUES (?, ?, ?, ?)
        """, (session_id, policy_id, interaction_type, duration))
        
        # Update popularity score
        if interaction_type in ('learn_more', 'buy_now'):
            cursor.execute("""
            UPDATE policies
            SET popularity_score = popularity_score + 1
            WHERE policy_id = ?
            """, (policy_id,))
        
        self.conn.commit()

    def record_click_event(self, session_id: str, element_id: str,
                           element_type: str, page_url: str, coordinates: Dict):
        """Record a click event anywhere on the page"""
        cursor = self.conn.cursor()
        cursor.execute("""
        INSERT INTO click_events (
            session_id, element_id, element_type, page_url, coordinates
        )
        VALUES (?, ?, ?, ?, ?)
        """, (
            session_id,
            element_id,
            element_type,
            page_url,
            json.dumps(coordinates)
        ))
        
        self.conn.commit()

    def record_form_interaction(self, session_id: str, form_id: str,
                               field_name: str, interaction_type: str,
                               field_value: str = None):
        """Record form field interactions"""
        cursor = self.conn.cursor()
        cursor.execute("""
        INSERT INTO form_interactions (
            session_id, form_id, field_name, interaction_type, field_value
        )
        VALUES (?, ?, ?, ?, ?)
        """, (
            session_id,
            form_id,
            field_name,
            interaction_type,
            field_value
        ))
        
        self.conn.commit()

    def end_session(self, session_id: str):
        """Mark a session as ended"""
        cursor = self.conn.cursor()
        cursor.execute("""
        UPDATE sessions
        SET end_time = CURRENT_TIMESTAMP
        WHERE session_id = ?
        """, (session_id,))
        
        self.conn.commit()

    def get_policy_popularity(self, limit: int = 5) -> List[Dict]:
        """Get most popular policies"""
        cursor = self.conn.cursor()
        cursor.execute("""
        SELECT policy_id, name, category, popularity_score
        FROM policies
        ORDER BY popularity_score DESC
        LIMIT ?
        """, (limit,))
        
        return [{
            'policy_id': row[0],
            'name': row[1],
            'category': row[2],
            'popularity_score': row[3]
        } for row in cursor.fetchall()]

    def get_user_behavior(self, user_id: str) -> Dict:
        """Get comprehensive behavior data for a user"""
        cursor = self.conn.cursor()
        
        # Get user sessions
        cursor.execute("""
        SELECT session_id, start_time, end_time, device_type
        FROM sessions
        WHERE user_id = ?
        ORDER BY start_time DESC
        LIMIT 10
        """, (user_id,))
        
        sessions = [{
            'session_id': row[0],
            'start_time': row[1],
            'end_time': row[2],
            'device_type': row[3]
        } for row in cursor.fetchall()]
        
        # Get policy interests
        cursor.execute("""
        SELECT p.policy_id, p.name, p.category, COUNT(*) as interaction_count
        FROM policy_interactions pi
        JOIN policies p ON pi.policy_id = p.policy_id
        JOIN sessions s ON pi.session_id = s.session_id
        WHERE s.user_id = ?
        GROUP BY p.policy_id
        ORDER BY interaction_count DESC
        LIMIT 5
        """, (user_id,))
        
        policy_interests = [{
            'policy_id': row[0],
            'name': row[1],
            'category': row[2],
            'interaction_count': row[3]
        } for row in cursor.fetchall()]
        
        return {
            'user_id': user_id,
            'sessions': sessions,
            'policy_interests': policy_interests
        }

    def close(self):
        """Close the database connection"""
        if self.conn:
            self.conn.close()

# Example Usage
if __name__ == "__main__":
    # Initialize the database
    db = InsuranceTrackerDB()
    
    try:
        # Simulate a user session
        user_id = db.create_or_update_user()
        
        # Simulate device info
        device_info = {
            'device_type': 'desktop',
            'os': 'Windows 10',
            'browser': 'Chrome',
            'screen_resolution': '1920x1080'
        }
        
        # Create a session
        session_id = db.create_session(
            user_id=user_id,
            ip_address="123.45.67.89",
            user_agent="Mozilla/5.0",
            device_info=device_info,
            referrer="google.com"
        )
        
        # Record page views
        db.record_page_view(session_id, "/insurance/protection")
        db.record_page_view(session_id, "/insurance/sbipp1", duration=45, scroll_depth=75)
        
        # Record policy interactions
        db.record_policy_interaction(session_id, "sbipp1", "view")
        db.record_policy_interaction(session_id, "sbipp1", "learn_more", duration=30)
        db.record_policy_interaction(session_id, "sbisp2", "view")
        
        # Record clicks
        db.record_click_event(
            session_id=session_id,
            element_id="compare-btn",
            element_type="button",
            page_url="/insurance/sbipp1",
            coordinates={"x": 100, "y": 200}
        )
        
        # Record form interactions
        db.record_form_interaction(
            session_id=session_id,
            form_id="premium-calculator",
            field_name="coverage_amount",
            interaction_type="change",
            field_value="1000000"
        )
        
        # End session
        db.end_session(session_id)
        
        # Get some analytics
        print("Most popular policies:")
        for policy in db.get_policy_popularity():
            print(f"{policy['name']} ({policy['category']}): {policy['popularity_score']} interactions")
        
        print("\nUser behavior:")
        print(json.dumps(db.get_user_behavior(user_id), indent=2))
        
    finally:
        db.close()