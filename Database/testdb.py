import sqlite3
from datetime import datetime
import uuid
from prettytable import PrettyTable
import random

class InsuranceDemo:
    def __init__(self):
        self.db = sqlite3.connect("insurance_analytics.db")
        self._initialize_db()
        self._add_sample_policies()
        
    def _initialize_db(self):
        """Create tables if they don't exist"""
        cursor = self.db.cursor()
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY,
            name TEXT,
            email TEXT,
            age INTEGER,
            income INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS policies (
            policy_id TEXT PRIMARY KEY,
            name TEXT,
            category TEXT,
            premium REAL,
            coverage REAL,
            term_years INTEGER,
            popularity INTEGER DEFAULT 0
        )
        """)
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS clicks (
            click_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            element_id TEXT,
            element_type TEXT,
            page_url TEXT,
            click_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
        """)
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS policy_views (
            view_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            policy_id TEXT,
            view_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            duration_seconds INTEGER,
            FOREIGN KEY (user_id) REFERENCES users(user_id),
            FOREIGN KEY (policy_id) REFERENCES policies(policy_id)
        )
        """)
        
        self.db.commit()
    
    def _add_sample_policies(self):
        """Add sample insurance policies if they don't exist"""
        cursor = self.db.cursor()
        
        # Check if policies already exist
        cursor.execute("SELECT COUNT(*) FROM policies")
        if cursor.fetchone()[0] == 0:
            policies = [
                ("term1", "Term Life Basic", "Life Insurance", 5000, 1000000, 10),
                ("term2", "Term Life Plus", "Life Insurance", 8000, 2000000, 15),
                ("health1", "Health Shield", "Health Insurance", 12000, 500000, 1),
                ("health2", "Family Health", "Health Insurance", 20000, 1000000, 1),
                ("vehicle1", "Auto Secure", "Vehicle Insurance", 6000, 800000, 1),
                ("travel1", "Travel Safe", "Travel Insurance", 3000, 500000, 1)
            ]
            
            cursor.executemany(
                "INSERT INTO policies (policy_id, name, category, premium, coverage, term_years) VALUES (?, ?, ?, ?, ?, ?)",
                policies
            )
            self.db.commit()
    
    def add_test_user(self):
        """Add a test user with random data"""
        user_id = str(uuid.uuid4())
        names = ["John Doe", "Jane Smith", "Robert Johnson", "Emily Davis", "Michael Brown"]
        domains = ["gmail.com", "yahoo.com", "outlook.com", "example.com"]
        
        name = random.choice(names)
        email = f"{name.split()[0].lower()}.{name.split()[1].lower()}@{random.choice(domains)}"
        age = random.randint(25, 65)
        income = random.randint(30000, 150000)
        
        cursor = self.db.cursor()
        cursor.execute(
            "INSERT INTO users (user_id, name, email, age, income) VALUES (?, ?, ?, ?, ?)",
            (user_id, name, email, age, income)
        )
        self.db.commit()
        return user_id
    
    def record_click(self, user_id, element_id, element_type, page_url):
        """Record a click event"""
        cursor = self.db.cursor()
        cursor.execute(
            "INSERT INTO clicks (user_id, element_id, element_type, page_url) VALUES (?, ?, ?, ?)",
            (user_id, element_id, element_type, page_url)
        )
        self.db.commit()
    
    def record_policy_view(self, user_id, policy_id, duration=None):
        """Record a policy view"""
        cursor = self.db.cursor()
        cursor.execute(
            "INSERT INTO policy_views (user_id, policy_id, duration_seconds) VALUES (?, ?, ?)",
            (user_id, policy_id, duration)
        )
        
        # Update popularity
        cursor.execute(
            "UPDATE policies SET popularity = popularity + 1 WHERE policy_id = ?",
            (policy_id,)
        )
        self.db.commit()
    
    def show_users(self):
        """Display all users in a table"""
        cursor = self.db.cursor()
        cursor.execute("SELECT * FROM users")
        users = cursor.fetchall()
        
        table = PrettyTable()
        table.field_names = ["User ID", "Name", "Email", "Age", "Income", "Created At"]
        
        for user in users:
            table.add_row(user)
        
        print("\nUsers in Database:")
        print(table)
    
    def show_policies(self):
        """Display all policies in a table"""
        cursor = self.db.cursor()
        cursor.execute("SELECT * FROM policies")
        policies = cursor.fetchall()
        
        table = PrettyTable()
        table.field_names = ["Policy ID", "Name", "Category", "Premium", "Coverage", "Term", "Popularity"]
        
        for policy in policies:
            table.add_row(policy)
        
        print("\nInsurance Policies:")
        print(table)
    
    def show_clicks(self, user_id=None):
        """Display click data"""
        cursor = self.db.cursor()
        
        if user_id:
            cursor.execute("SELECT * FROM clicks WHERE user_id = ?", (user_id,))
        else:
            cursor.execute("SELECT * FROM clicks")
        
        clicks = cursor.fetchall()
        
        table = PrettyTable()
        table.field_names = ["Click ID", "User ID", "Element", "Type", "Page", "Time"]
        
        for click in clicks:
            table.add_row(click)
        
        print("\nClick Data:")
        print(table)
    
    def show_policy_views(self, user_id=None):
        """Display policy views"""
        cursor = self.db.cursor()
        
        if user_id:
            cursor.execute("""
                SELECT pv.view_id, pv.user_id, p.name, p.category, pv.view_time, pv.duration_seconds 
                FROM policy_views pv
                JOIN policies p ON pv.policy_id = p.policy_id
                WHERE pv.user_id = ?
            """, (user_id,))
        else:
            cursor.execute("""
                SELECT pv.view_id, pv.user_id, p.name, p.category, pv.view_time, pv.duration_seconds 
                FROM policy_views pv
                JOIN policies p ON pv.policy_id = p.policy_id
            """)
        
        views = cursor.fetchall()
        
        table = PrettyTable()
        table.field_names = ["View ID", "User ID", "Policy", "Category", "View Time", "Duration"]
        
        for view in views:
            table.add_row(view)
        
        print("\nPolicy Views:")
        print(table)
    
    def generate_test_data(self, num_users=3):
        """Generate complete test data"""
        for _ in range(num_users):
            user_id = self.add_test_user()
            
            # Simulate browsing behavior
            pages = ["/home", "/insurance", "/insurance/life", "/insurance/health"]
            elements = ["nav-link", "learn-more", "compare-btn", "apply-now"]
            
            for page in pages:
                self.record_click(
                    user_id=user_id,
                    element_id=f"menu-{random.randint(1,5)}",
                    element_type="nav-link",
                    page_url=page
                )
                
                if "insurance" in page:
                    # View 1-3 random policies
                    cursor = self.db.cursor()
                    cursor.execute("SELECT policy_id FROM policies WHERE category LIKE ?", 
                                 (f"%{page.split('/')[-1]}%",) if "insurance/" in page else ("%",))
                    policies = cursor.fetchall()
                    
                    if policies:
                        for _ in range(random.randint(1, 3)):
                            policy = random.choice(policies)[0]
                            self.record_policy_view(user_id, policy, random.randint(5, 120))
                            self.record_click(
                                user_id=user_id,
                                element_id=f"policy-{policy}",
                                element_type="policy-card",
                                page_url=f"/policy/{policy}"
                            )
            
            print(f"\nGenerated test data for user {user_id}")
    
    def close(self):
        """Close the database connection"""
        self.db.close()

# Main demo
if __name__ == "__main__":
    demo = InsuranceDemo()
    
    try:
        print("Insurance Analytics Database Demo")
        print("="*50)
        
        # Generate test data
        demo.generate_test_data(2)
        
        # Show all data
        demo.show_users()
        demo.show_policies()
        demo.show_clicks()
        demo.show_policy_views()
        
    finally:
        demo.close()