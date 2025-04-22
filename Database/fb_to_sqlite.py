import sqlite3
import firebase_admin
from firebase_admin import auth, credentials, firestore
from datetime import datetime
import os

class UserDataSync:
    def __init__(self, db_path="userdata.db"):
        # Initialize Firebase
        try:
            self.cred = credentials.Certificate("firebase-adminsdk.json")
            firebase_admin.initialize_app(self.cred)
            self.auth = auth
            self.firestore = firestore.client()
        except Exception as e:
            print(f"⚠️ Firebase initialization error: {str(e)}")
            self.auth = None
            self.firestore = None

        # Initialize SQLite database
        self.db_path = db_path
        self._init_db()
        self.current_user = None

    def _init_db(self):
        """Initialize SQLite database with proper schema"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Drop existing tables if they exist to ensure clean schema
            cursor.execute("DROP TABLE IF EXISTS users")
            cursor.execute("DROP TABLE IF EXISTS user_activities")
            cursor.execute("DROP INDEX IF EXISTS idx_user_activities_user")
            cursor.execute("DROP INDEX IF EXISTS idx_user_activities_policy")

            # Create users table with all columns
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                uid TEXT PRIMARY KEY,
                email TEXT NOT NULL,
                first_name TEXT,
                last_name TEXT,
                display_name TEXT GENERATED ALWAYS AS (first_name || ' ' || last_name) STORED,
                phone TEXT,
                income INTEGER,
                age INTEGER,
                marital_status TEXT,
                dependents INTEGER,
                occupation TEXT,
                address TEXT,
                city TEXT,
                state TEXT,
                zip_code TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP,
                risk_profile TEXT,
                total_premium_paid REAL DEFAULT 0,
                total_coverage REAL DEFAULT 0,
                firebase_sync_time TIMESTAMP
            )
            """)

            # Create user_activities table with additional fields
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_activities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                activity_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                activity_type TEXT,
                policy_id TEXT,
                policy_name TEXT,
                policy_category TEXT,
                premium_amount REAL,
                coverage_amount REAL,
                term_years INTEGER,
                payment_method TEXT,
                agent_id TEXT,
                notes TEXT,
                duration_seconds INTEGER DEFAULT 0,
                interest_score INTEGER DEFAULT 5,
                device_type TEXT DEFAULT 'Unknown',
                FOREIGN KEY(user_id) REFERENCES users(uid)
            )
            """)

            # Create indexes for better performance
            cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_user_activities_user 
            ON user_activities(user_id)
            """)
            
            cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_user_activities_policy 
            ON user_activities(policy_id)
            """)

            conn.commit()
            conn.close()
            print(f"✅ Database initialized at {os.path.abspath(self.db_path)}")
        except sqlite3.Error as e:
            print(f"❌ Database initialization error: {str(e)}")

    def _get_uid_from_email(self, email):
        """Generate UID from email prefix (before @)"""
        return email.split('@')[0]

    def _execute_query(self, query, params=(), fetch=False):
        """Execute SQL query with error handling"""
        try:
            conn = sqlite3.connect(self.db_path)
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

    def sync_user_from_firebase(self, email):
        """Fetch user from Firebase and sync to SQLite"""
        if not self.auth:
            print("⚠️ Firebase not initialized")
            return False

        try:
            # Get Firebase user
            fb_user = self.auth.get_user_by_email(email)
            uid = self._get_uid_from_email(email)
            self.current_user = {'uid': uid, 'email': email, 'fb_uid': fb_user.uid}
            
            # Get additional data from Firestore
            user_ref = self.firestore.collection("users").document(fb_user.uid)
            user_data = user_ref.get().to_dict() or {}
            
            # Prepare user record with all fields
            now = datetime.now().isoformat()
            user_record = (
                uid,
                email,
                user_data.get('firstName', ''),
                user_data.get('lastName', ''),
                user_data.get('phone', ''),
                user_data.get('income', 0),
                user_data.get('age', 0),
                user_data.get('maritalStatus', ''),
                user_data.get('dependents', 0),
                user_data.get('occupation', ''),
                user_data.get('address', ''),
                user_data.get('city', ''),
                user_data.get('state', ''),
                user_data.get('zipCode', ''),
                now,  # last_login
                user_data.get('riskProfile', 'MEDIUM'),
                0,  # total_premium_paid (updated by activities)
                0,  # total_coverage (updated by activities)
                now   # firebase_sync_time
            )
            
            # Insert/update user with all columns
            columns = [
                'uid', 'email', 'first_name', 'last_name', 'phone',
                'income', 'age', 'marital_status', 'dependents', 'occupation',
                'address', 'city', 'state', 'zip_code', 'last_login',
                'risk_profile', 'total_premium_paid', 'total_coverage',
                'firebase_sync_time'
            ]
            
            placeholders = ','.join(['?'] * len(columns))
            query = f"""
            INSERT OR REPLACE INTO users ({','.join(columns)})
            VALUES ({placeholders})
            """
            
            result = self._execute_query(query, user_record)
            if result is not None:
                print(f"✅ User {email} synced to database (UID: {uid})")
                return True
            return False
            
        except Exception as e:
            print(f"❌ Sync failed: {str(e)}")
            return False

    def record_activity(self, activity_data):
        """Record user activity in database with enhanced fields"""
        if not self.current_user:
            print("⚠️ No user logged in")
            return False
            
        required_fields = ['activity_type', 'policy_id']
        for field in required_fields:
            if field not in activity_data:
                print(f"❌ Missing required field: {field}")
                return False
                
        try:
            # Insert activity with all available fields
            result = self._execute_query("""
            INSERT INTO user_activities (
                user_id, activity_type, policy_id, policy_name,
                policy_category, premium_amount, coverage_amount,
                term_years, payment_method, agent_id, notes,
                duration_seconds, interest_score, device_type
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                self.current_user['uid'],
                activity_data['activity_type'],
                activity_data['policy_id'],
                activity_data.get('policy_name', ''),
                activity_data.get('policy_category', ''),
                activity_data.get('premium_amount', 0),
                activity_data.get('coverage_amount', 0),
                activity_data.get('term_years', 1),
                activity_data.get('payment_method', ''),
                activity_data.get('agent_id', ''),
                activity_data.get('notes', ''),
                activity_data.get('duration_seconds', 0),
                activity_data.get('interest_score', 5),  # Default 5/10
                activity_data.get('device_type', 'Unknown')
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
                    datetime.now().isoformat(),
                    self.current_user['uid']
                ))
            
            print(f"✅ Activity recorded: {activity_data['activity_type']}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to record activity: {str(e)}")
            return False

    def get_user_profile(self, email=None):
        """Get complete user profile with activities"""
        uid = self._get_uid_from_email(email) if email else (
            self.current_user['uid'] if self.current_user else None)
        if not uid:
            print("⚠️ No user specified")
            return None
            
        # Get user details
        user = self._execute_query("""
        SELECT * FROM users WHERE uid = ?
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
            'address': user[0][11],
            'city': user[0][12],
            'state': user[0][13],
            'zip_code': user[0][14],
            'created_at': user[0][15],
            'last_login': user[0][16],
            'risk_profile': user[0][17],
            'total_premium_paid': user[0][18],
            'total_coverage': user[0][19]
        }
        
        # Get user activities with additional fields
        activities = self._execute_query("""
        SELECT 
            activity_date, activity_type, policy_id, policy_name,
            premium_amount, coverage_amount, term_years, duration_seconds,
            interest_score, device_type
        FROM user_activities
        WHERE user_id = ?
        ORDER BY activity_date DESC
        LIMIT 100
        """, (uid,), fetch=True)
        
        user_data['activities'] = [
            {
                'date': act[0],
                'type': act[1],
                'policy_id': act[2],
                'policy_name': act[3],
                'premium': act[4],
                'coverage': act[5],
                'term': act[6],
                'duration_seconds': act[7],
                'interest_score': act[8],
                'device_type': act[9]
            } for act in activities
        ] if activities else []
        
        # Calculate time spent per policy
        user_data['time_spent'] = self._calculate_time_spent(uid)
        
        return user_data

    def _calculate_time_spent(self, uid):
        """Calculate total time spent per policy"""
        time_data = self._execute_query("""
        SELECT policy_id, SUM(duration_seconds)
        FROM user_activities
        WHERE user_id = ? AND duration_seconds > 0
        GROUP BY policy_id
        ORDER BY SUM(duration_seconds) DESC
        """, (uid,), fetch=True)
        
        return {policy: seconds for policy, seconds in time_data} if time_data else {}

    def get_policy_stats(self, email=None):
        """Get policy statistics for user"""
        uid = self._get_uid_from_email(email) if email else (
            self.current_user['uid'] if self.current_user else None)
        if not uid:
            print("⚠️ No user specified")
            return None
            
        stats = {
            'total_views': 0,
            'total_purchases': 0,
            'total_premium': 0,
            'total_coverage': 0,
            'policies_viewed': set(),
            'policies_owned': set(),
            'average_interest': {}
        }
        
        activities = self._execute_query("""
        SELECT activity_type, policy_id, premium_amount, coverage_amount, interest_score
        FROM user_activities
        WHERE user_id = ?
        """, (uid,), fetch=True)
        
        if activities:
            from collections import defaultdict
            policy_scores = defaultdict(list)
            
            for act in activities:
                if act[0] == 'POLICY_VIEW':
                    stats['total_views'] += 1
                    stats['policies_viewed'].add(act[1])
                    policy_scores[act[1]].append(act[4])
                elif act[0] == 'POLICY_PURCHASE':
                    stats['total_purchases'] += 1
                    stats['total_premium'] += act[2] or 0
                    stats['total_coverage'] += act[3] or 0
                    stats['policies_owned'].add(act[1])
        
            # Calculate average interest per policy
            for policy, scores in policy_scores.items():
                stats['average_interest'][policy] = sum(scores)/len(scores)
        
        # Convert sets to lists
        stats['policies_viewed'] = list(stats['policies_viewed'])
        stats['policies_owned'] = list(stats['policies_owned'])
        
        return stats

if __name__ == "__main__":
    print("=== Insurance User Data Sync ===")
    sync = UserDataSync()
    
    try:
        # Test with sample user
        test_email = "astystudio@gmail.com"
        
        # 1. Sync user from Firebase (simulated)
        print(f"\n1. Syncing user {test_email}...")
        sync.current_user = {
            'uid': sync._get_uid_from_email(test_email),
            'email': test_email,
            'fb_uid': 'firebase_uid_123'
        }
        
        # Simulate user record
        sync._execute_query("""
        INSERT OR REPLACE INTO users (
            uid, email, first_name, last_name, phone, income, age,
            marital_status, dependents, occupation, address, city,
            state, zip_code, last_login, risk_profile,
            total_premium_paid, total_coverage, firebase_sync_time
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            'astystudio', test_email, 'John', 'Doe', '9876543210',
            500000, 35, 'Married', 2, 'Engineer', '123 Main St',
            'Mumbai', 'Maharashtra', '400001', datetime.now().isoformat(),
            'LOW', 0, 0, datetime.now().isoformat()
        ))
        
        # 2. Record sample activities with enhanced fields
        print("\n2. Recording sample activities...")
        activities = [
            {
                'activity_type': 'POLICY_VIEW',
                'policy_id': 'sbipp1',
                'policy_name': 'Term Life Basic',
                'policy_category': 'Protection',
                'duration_seconds': 120,
                'interest_score': 7,
                'device_type': 'Mobile'
            },
            {
                'activity_type': 'POLICY_VIEW',
                'policy_id': 'sbisp1',
                'policy_name': 'Wealth Builder',
                'policy_category': 'Savings',
                'duration_seconds': 45,
                'interest_score': 5,
                'device_type': 'Desktop'
            },
            {
                'activity_type': 'POLICY_PURCHASE',
                'policy_id': 'sbipp1',
                'policy_name': 'Term Life Basic',
                'premium_amount': 12000,
                'coverage_amount': 500000,
                'term_years': 10,
                'payment_method': 'Credit Card',
                'duration_seconds': 300,
                'interest_score': 9,
                'device_type': 'Desktop'
            }
        ]
        
        for act in activities:
            sync.record_activity(act)
        
        # 3. Get user profile
        print("\n3. Fetching user profile...")
        profile = sync.get_user_profile(test_email)
        if profile:
            print(f"\nUser Profile for {profile['display_name']}:")
            print(f"Email: {profile['email']}")
            print(f"Risk Profile: {profile['risk_profile']}")
            print(f"Total Premium Paid: ₹{profile['total_premium_paid']:,}")
            print(f"Total Coverage: ₹{profile['total_coverage']:,}")
            
            print("\nTime Spent per Policy:")
            for policy, seconds in profile['time_spent'].items():
                print(f"- {policy}: {seconds//60}m {seconds%60}s")
            
            print("\nRecent Activities:")
            for act in profile['activities'][:3]:  # Show first 3 activities
                print(f"- {act['date']}: {act['type']} {act['policy_name']}")
                print(f"  Duration: {act['duration_seconds']}s")
                print(f"  Interest: {act['interest_score']}/10")
                print(f"  Device: {act['device_type']}")
        
        # 4. Get policy statistics
        print("\n4. Policy Statistics:")
        stats = sync.get_policy_stats(test_email)
        if stats:
            print(f"Total Views: {stats['total_views']}")
            print(f"Total Purchases: {stats['total_purchases']}")
            print(f"Total Premium: ₹{stats['total_premium']:,}")
            print("\nAverage Interest Scores:")
            for policy, score in stats['average_interest'].items():
                print(f"- {policy}: {score:.1f}/10")
        
    except Exception as e:
        print(f"❌ Error during test: {str(e)}")
    finally:
        print("\nTest completed")