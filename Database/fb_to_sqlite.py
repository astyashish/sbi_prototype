import sqlite3
import firebase_admin
from firebase_admin import auth, credentials, firestore
from datetime import datetime
import os
import time

class InsuranceUserDB:
    def __init__(self, db_path="Database/userdata.db"):
        # Initialize Firebase
        try:
            self.cred = credentials.Certificate("Database/firebase-adminsdk.json")
            firebase_admin.initialize_app(self.cred)
            self.auth = auth
            self.firestore = firestore.client()
        except Exception as e:
            print(f"⚠️ Firebase init error: {str(e)}")
            self.auth = None
            self.firestore = None

        # Initialize SQLite database
        self.db_path = db_path
        self._init_db()
        self.current_user = None

    def _init_db(self):
        """Initialize database schema with proper tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Create users table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            uid TEXT PRIMARY KEY,
            email TEXT UNIQUE NOT NULL COLLATE NOCASE,
            first_name TEXT,
            last_name TEXT,
            display_name TEXT,
            phone TEXT,
            income INTEGER,
            age INTEGER,
            marital_status TEXT CHECK(marital_status IN ('Single', 'Married', 'Divorced', 'Widowed')),
            dependents INTEGER,
            occupation TEXT,
            risk_profile TEXT CHECK(risk_profile IN ('LOW', 'MEDIUM', 'HIGH')),
            total_premium_paid INTEGER DEFAULT 0,
            total_coverage INTEGER DEFAULT 0,
            last_login INTEGER,
            created_at INTEGER,
            firebase_sync_time INTEGER
        )
        """)

        # Create user_activities table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_activities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            activity_time INTEGER,
            activity_type TEXT CHECK(activity_type IN (
                'POLICY_VIEW', 'POLICY_DETAILS', 'QUOTE_REQUEST', 
                'POLICY_PURCHASE', 'CLAIM_SUBMITTED', 'PAYMENT_MADE',
                'DOCUMENT_UPLOAD', 'CUSTOMER_SUPPORT'
            )),
            policy_id TEXT,
            duration_seconds INTEGER DEFAULT 0,
            premium_amount INTEGER DEFAULT 0,
            coverage_amount INTEGER DEFAULT 0,
            interest_score INTEGER DEFAULT 5,
            device_type TEXT,
            location TEXT,
            FOREIGN KEY(user_id) REFERENCES users(uid) ON DELETE CASCADE
        )
        """)

        # Create indexes
        cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_activities_user 
        ON user_activities(user_id, activity_time)
        """)
        
        cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_activities_policy 
        ON user_activities(policy_id, activity_type)
        """)

        conn.commit()
        conn.close()
        print(f"✅ Database initialized at {os.path.abspath(self.db_path)}")

    def _get_uid_from_email(self, email):
        """Generate UID from email prefix (before @)"""
        return email.split('@')[0].lower()

    def _execute_query(self, query, params=(), fetch=False):
        """Execute SQL query with error handling"""
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.cursor()
            cursor.execute(query, params)
            if fetch:
                result = cursor.fetchall()
            else:
                result = cursor.rowcount
                conn.commit()
            return result
        except sqlite3.Error as e:
            print(f"❌ Database error: {str(e)}")
            return None
        finally:
            conn.close()

    def add_or_update_user(self, email, user_data=None):
        """Add or update user in the database"""
        if not user_data:
            user_data = {}
            
        uid = self._get_uid_from_email(email)
        now = int(time.time())
        display_name = f"{user_data.get('first_name', '')} {user_data.get('last_name', '')}".strip()
        
        # Check if user exists
        existing = self._execute_query(
            "SELECT 1 FROM users WHERE uid = ?", 
            (uid,), 
            fetch=True
        )
        
        if existing:
            # Update existing user
            result = self._execute_query("""
            UPDATE users SET 
                email = ?,
                first_name = ?,
                last_name = ?,
                display_name = ?,
                phone = ?,
                income = ?,
                age = ?,
                marital_status = ?,
                dependents = ?,
                occupation = ?,
                risk_profile = ?,
                last_login = ?,
                firebase_sync_time = ?
            WHERE uid = ?
            """, (
                email,
                user_data.get('first_name', ''),
                user_data.get('last_name', ''),
                display_name,
                user_data.get('phone', ''),
                user_data.get('income', 0),
                user_data.get('age', 0),
                user_data.get('marital_status', 'Single'),
                user_data.get('dependents', 0),
                user_data.get('occupation', ''),
                user_data.get('risk_profile', 'MEDIUM'),
                now,
                now,
                uid
            ))
            print(f"✅ Updated existing user {email}")
        else:
            # Insert new user
            result = self._execute_query("""
            INSERT INTO users (
                uid, email, first_name, last_name, display_name,
                phone, income, age, marital_status, dependents,
                occupation, risk_profile, total_premium_paid,
                total_coverage, last_login, created_at, firebase_sync_time
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                uid,
                email,
                user_data.get('first_name', ''),
                user_data.get('last_name', ''),
                display_name,
                user_data.get('phone', ''),
                user_data.get('income', 0),
                user_data.get('age', 0),
                user_data.get('marital_status', 'Single'),
                user_data.get('dependents', 0),
                user_data.get('occupation', ''),
                user_data.get('risk_profile', 'MEDIUM'),
                0,  # total_premium_paid
                0,  # total_coverage
                now,  # last_login
                now,  # created_at
                now   # firebase_sync_time
            ))
            print(f"✅ Created new user {email}")
        
        self.current_user = {'uid': uid, 'email': email}
        return result is not None

    def sync_user_from_firebase(self, email):
        """Fetch user from Firebase and sync to SQLite"""
        if not self.auth:
            print("⚠️ Firebase not initialized")
            return False

        try:
            # Get Firebase user
            fb_user = self.auth.get_user_by_email(email)
            uid = self._get_uid_from_email(email)
            
            # Get additional data from Firestore
            user_ref = self.firestore.collection("users").document(fb_user.uid)
            fb_data = user_ref.get().to_dict() or {}
            
            # Prepare user data for our database
            user_data = {
                'first_name': fb_data.get('firstName', ''),
                'last_name': fb_data.get('lastName', ''),
                'phone': fb_data.get('phone', ''),
                'income': fb_data.get('income', 0),
                'age': fb_data.get('age', 0),
                'marital_status': fb_data.get('maritalStatus', 'Single'),
                'dependents': fb_data.get('dependents', 0),
                'occupation': fb_data.get('occupation', ''),
                'risk_profile': fb_data.get('riskProfile', 'MEDIUM')
            }
            
            return self.add_or_update_user(email, user_data)
            
        except Exception as e:
            print(f"❌ Sync failed: {str(e)}")
            return False

    def record_activity(self, activity_data):
        """Record user activity with all tracking fields"""
        if not self.current_user:
            print("⚠️ No user logged in")
            return False
            
        required = ['activity_type', 'policy_id']
        if any(f not in activity_data for f in required):
            print(f"❌ Missing required fields: {required}")
            return False
                
        try:
            # Insert activity
            self._execute_query("""
            INSERT INTO user_activities (
                user_id, activity_time, activity_type, policy_id,
                duration_seconds, premium_amount, coverage_amount,
                interest_score, device_type, location
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                self.current_user['uid'],
                int(time.time()),
                activity_data['activity_type'],
                activity_data['policy_id'],
                activity_data.get('duration_seconds', 0),
                activity_data.get('premium_amount', 0),
                activity_data.get('coverage_amount', 0),
                min(max(activity_data.get('interest_score', 5), 1), 10),
                activity_data.get('device_type', ''),
                activity_data.get('location', '')
            ))
            
            # Update user totals if purchase
            if activity_data['activity_type'] == 'POLICY_PURCHASE':
                self._execute_query("""
                UPDATE users 
                SET total_premium_paid = total_premium_paid + ?,
                    total_coverage = total_coverage + ?,
                    last_login = ?
                WHERE uid = ?
                """, (
                    activity_data.get('premium_amount', 0),
                    activity_data.get('coverage_amount', 0),
                    int(time.time()),
                    self.current_user['uid']
                ))
            
            print(f"✅ Activity recorded: {activity_data['activity_type']}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to record activity: {str(e)}")
            return False

    def get_user_profile(self, email=None):
        """Get complete user profile with insights"""
        uid = self._get_uid_from_email(email) if email else (
            self.current_user['uid'] if self.current_user else None)
        if not uid:
            print("⚠️ No user specified")
            return None
            
        # Get user details
        user = self._execute_query("""
        SELECT 
            uid, email, first_name, last_name, display_name,
            phone, income, age, marital_status, dependents,
            occupation, risk_profile, total_premium_paid, total_coverage,
            last_login, created_at
        FROM users WHERE uid = ?
        """, (uid,), fetch=True)
        
        if not user or len(user) == 0:
            return None
            
        user_data = {
            'uid': user[0][0],
            'email': user[0][1],
            'first_name': user[0][2],
            'last_name': user[0][3],
            'display_name': user[0][4],
            'phone': user[0][5],
            'income': user[0][6],
            'age': user[0][7],
            'marital_status': user[0][8],
            'dependents': user[0][9],
            'occupation': user[0][10],
            'risk_profile': user[0][11],
            'total_premium_paid': user[0][12],
            'total_coverage': user[0][13],
            'last_login': datetime.fromtimestamp(user[0][14]),
            'created_at': datetime.fromtimestamp(user[0][15])
        }
        
        # Get personalized insights
        user_data['policy_preferences'] = self._get_policy_preferences(uid)
        user_data['activity_stats'] = self._get_activity_stats(uid)
        
        return user_data

    def _get_policy_preferences(self, uid):
        """Calculate user's policy preferences"""
        insights = {
            'most_viewed': None,
            'time_spent': {},
            'purchase_likelihood': {},
            'recommended_policies': []
        }
        
        # Get view counts and time spent
        views = self._execute_query("""
        SELECT policy_id, COUNT(*), SUM(duration_seconds)
        FROM user_activities
        WHERE user_id = ? AND activity_type = 'POLICY_VIEW'
        GROUP BY policy_id
        ORDER BY COUNT(*) DESC
        LIMIT 5
        """, (uid,), fetch=True)
        
        if views:
            insights['most_viewed'] = views[0][0]
            insights['time_spent'] = {v[0]: v[2] for v in views}
        
        # Calculate purchase likelihood
        activities = self._execute_query("""
        SELECT policy_id, activity_type, interest_score
        FROM user_activities
        WHERE user_id = ? AND activity_type IN ('POLICY_VIEW', 'POLICY_DETAILS')
        """, (uid,), fetch=True)
        
        if activities:
            from collections import defaultdict
            policy_scores = defaultdict(int)
            for policy, act_type, score in activities:
                weight = 2 if act_type == 'POLICY_DETAILS' else 1
                policy_scores[policy] += score * weight
            
            insights['purchase_likelihood'] = dict(
                sorted(policy_scores.items(), key=lambda x: x[1], reverse=True)[:3]
            )
        
        # Simple recommendation logic
        purchased = self._execute_query("""
        SELECT DISTINCT policy_id FROM user_activities
        WHERE user_id = ? AND activity_type = 'POLICY_PURCHASE'
        """, (uid,), fetch=True)
        
        purchased_set = {p[0] for p in purchased} if purchased else set()
        likely = set(insights['purchase_likelihood'].keys())
        insights['recommended_policies'] = list(likely - purchased_set)[:3]
        
        return insights

    def _get_activity_stats(self, uid):
        """Get comprehensive activity statistics"""
        stats = {
            'total_activities': 0,
            'activity_types': {},
            'devices_used': {},
            'locations': {},
            'time_of_day': {'morning': 0, 'afternoon': 0, 'evening': 0, 'night': 0}
        }
        
        activities = self._execute_query("""
        SELECT activity_type, device_type, location, activity_time
        FROM user_activities
        WHERE user_id = ?
        """, (uid,), fetch=True)
        
        if activities:
            stats['total_activities'] = len(activities)
            
            for act_type, device, loc, act_time in activities:
                # Count activity types
                stats['activity_types'][act_type] = stats['activity_types'].get(act_type, 0) + 1
                
                # Count devices
                if device:
                    stats['devices_used'][device] = stats['devices_used'].get(device, 0) + 1
                
                # Count locations
                if loc:
                    stats['locations'][loc] = stats['locations'].get(loc, 0) + 1
                
                # Time of day analysis
                hour = datetime.fromtimestamp(act_time).hour
                if 5 <= hour < 12:
                    stats['time_of_day']['morning'] += 1
                elif 12 <= hour < 17:
                    stats['time_of_day']['afternoon'] += 1
                elif 17 <= hour < 21:
                    stats['time_of_day']['evening'] += 1
                else:
                    stats['time_of_day']['night'] += 1
        
        return stats

# Example Usage
if __name__ == "__main__":
    print("=== Insurance User Database ===")
    db = InsuranceUserDB()
    
    try:
        # Test with different email addresses
        test_users = [
            {
                "email": "astystudio@gmail.com",
                "first_name": "Asty",
                "last_name": "Studio",
                "phone": "9876543210",
                "income": 500000,
                "age": 35,
                "marital_status": "Married",
                "dependents": 2,
                "occupation": "Developer",
                "risk_profile": "MEDIUM"
            },
            {
                "email": "test2.user@example.com",
                "first_name": "Test2",
                "last_name": "User2",
                "phone": "9876543211",
                "income": 300000,
                "age": 28,
                "marital_status": "Single",
                "dependents": 0,
                "occupation": "Designer",
                "risk_profile": "LOW"
            }
        ]
        
        for user_data in test_users:
            email = user_data.pop("email")
            
            # 1. Add user
            print(f"\n1. Adding user {email}...")
            db.add_or_update_user(email, user_data)
            
            # Set as current user
            db.current_user = {'uid': db._get_uid_from_email(email), 'email': email}
            
            # 2. Record sample activities
            print("2. Recording sample activities...")
            activities = [
                {
                    'activity_type': 'POLICY_VIEW',
                    'policy_id': 'sbipp1',
                    'duration_seconds': 45,
                    'interest_score': 7,
                    'device_type': 'Mobile',
                    'location': 'Mumbai'
                },
                {
                    'activity_type': 'POLICY_DETAILS',
                    'policy_id': 'sbipp1',
                    'duration_seconds': 120,
                    'interest_score': 8,
                    'device_type': 'Desktop',
                    'location': 'Mumbai'
                },
                {
                    'activity_type': 'POLICY_PURCHASE',
                    'policy_id': 'sbipp1',
                    'premium_amount': 12000,
                    'coverage_amount': 500000,
                    'device_type': 'Desktop',
                    'location': 'Mumbai'
                }
            ]
            
            for act in activities:
                db.record_activity(act)
            
            # 3. Get user profile
            print("3. Getting user profile...")
            profile = db.get_user_profile(email)
            if profile:
                print(f"\nUser Profile for {profile['display_name']}:")
                print(f"Email: {profile['email']}")
                print(f"Risk Profile: {profile['risk_profile']}")
                print(f"Total Premium Paid: ₹{profile['total_premium_paid']:,}")
                print(f"Total Coverage: ₹{profile['total_coverage']:,}")
                
                print("\nTime Spent per Policy:")
                for policy, seconds in profile['policy_preferences']['time_spent'].items():
                    print(f"- {policy}: {seconds//60}m {seconds%60}s")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    finally:
        print("\nTest completed")