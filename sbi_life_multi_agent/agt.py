import os
import json
from datetime import datetime
import random
from typing import Dict, List, Optional
import time

# Set environment variables at the top for clarity
os.environ["WATSONX_APIKEY"] = "0ePVDekT98gfCJLgPLAiJ6u7ktfofOosRfdNuP8Mv5nK"
os.environ["SERPER_API_KEY"] = "a2d460207117ea4e1861c435a06c1cee18ed0c66"

# Initialize policy data - moved out of functions for better performance
POLICIES = {
    "sbipp1": {
        "name": "SBI Life - Shield Plus",
        "type": "Protection",
        "description": "Term life insurance with high coverage",
        "premium": "₹10,000/year",
        "coverage": "₹1 Crore",
        "duration": "10-30 years",
        "features": ["High death benefit", "Affordable premiums", "Flexible terms"]
    },
    "sbipp2": {
        "name": "SBI Life - Smart Protection",
        "type": "Protection",
        "description": "Term plan with return of premium",
        "premium": "₹15,000/year",
        "coverage": "₹75 Lakhs",
        "duration": "15-25 years",
        "features": ["Premium return", "Critical illness cover", "Tax benefits"]
    },
    "sbisp1": {
        "name": "SBI Life - Savings Plus",
        "type": "Savings",
        "description": "Endowment plan with guaranteed returns",
        "premium": "₹50,000/year",
        "coverage": "₹10 Lakhs",
        "duration": "10-20 years",
        "features": ["Guaranteed returns", "Bonus additions", "Loan facility"]
    },
    "sbirp1": {
        "name": "SBI Life - Retirement Plus",
        "type": "Retirement",
        "description": "Pension plan with life cover",
        "premium": "₹60,000/year",
        "coverage": "₹15 Lakhs",
        "duration": "Till retirement",
        "features": ["Regular pension", "Life cover", "Tax-free maturity"]
    },
    "sbicp1": {
        "name": "SBI Life - Child Plan",
        "type": "Child",
        "description": "Education savings with insurance cover",
        "premium": "₹20,000/year",
        "coverage": "₹5 Lakhs",
        "duration": "10-15 years",
        "features": ["Education fund", "Waiver of premium", "Flexible payout options"]
    }
}

# Pre-compute categories and plans by category for faster lookup
CATEGORIES = list(set([p["type"] for p in POLICIES.values()]))
PLANS_BY_CATEGORY = {category: [pid for pid, p in POLICIES.items() if p["type"] == category] 
                    for category in CATEGORIES}

class UserDataHandler:
    def __init__(self, user_id: str):
        self.user_id = user_id
        os.makedirs("user_data", exist_ok=True)
        self.data_file = f"user_data/{user_id}.json"
        self.initialize_user_data()
    
    def initialize_user_data(self):
        if not os.path.exists(self.data_file):
            self.data = {
                "user_id": self.user_id,
                "clicks": {category: {plan: 0 for plan in PLANS_BY_CATEGORY[category]} 
                          for category in CATEGORIES},
                "preferences": {},
                "personal_info": {},
                "interaction_history": [],
                "recommendations": [],
                "created_at": datetime.now().isoformat(),
                "last_updated": datetime.now().isoformat()
            }
            self.save_data()
        else:
            self.load_data()
    
    def load_data(self):
        with open(self.data_file, 'r') as f:
            self.data = json.load(f)
    
    def save_data(self):
        self.data['last_updated'] = datetime.now().isoformat()
        with open(self.data_file, 'w') as f:
            json.dump(self.data, f, indent=2)
    
    def record_click(self, category: str, plan: str, count: int = 1):
        if category in self.data['clicks'] and plan in self.data['clicks'][category]:
            self.data['clicks'][category][plan] += count
            self.log_interaction(f"Clicked on {plan} in {category} {count} times")
            self.save_data()
    
    def update_preferences(self, preferences: Dict):
        self.data['preferences'].update(preferences)
        self.log_interaction(f"Updated preferences: {preferences}")
        self.save_data()
    
    def update_personal_info(self, info: Dict):
        self.data['personal_info'].update(info)
        self.log_interaction("Updated personal info")
        self.save_data()
    
    def log_interaction(self, description: str):
        self.data['interaction_history'].append({
            "timestamp": datetime.now().isoformat(),
            "description": description
        })
    
    def add_recommendation(self, recommendation: Dict):
        self.data['recommendations'].append({
            "timestamp": datetime.now().isoformat(),
            "recommendation": recommendation
        })
        self.save_data()

class InsuranceRecommender:
    """Streamlined recommender that doesn't rely on slow API calls"""
    
    def __init__(self):
        self.policies = POLICIES
    
    def analyze_user(self, user_data: Dict) -> Dict:
        # Get user info
        age = user_data['personal_info'].get('age', 30)
        income = user_data['personal_info'].get('income', '5-10L')
        marital_status = user_data['personal_info'].get('marital_status', 'Single')
        dependents = user_data['personal_info'].get('dependents', 0)
        financial_goals = user_data['personal_info'].get('financial_goals', [])
        
        # Get preferences
        risk_appetite = user_data['preferences'].get('risk_appetite', 'Medium')
        preferred_term = user_data['preferences'].get('preferred_term', 'Medium')
        priority = user_data['preferences'].get('priority', 'Protection')
        
        # Calculate browsing behavior scores
        click_scores = {}
        for category, plans in user_data['clicks'].items():
            for plan_id, clicks in plans.items():
                if plan_id in self.policies:
                    click_scores[plan_id] = clicks
        
        # Generate scores for policies based on user profile
        policy_scores = {}
        
        for policy_id, policy in self.policies.items():
            score = 0
            
            # Add click score (user interest)
            score += click_scores.get(policy_id, 0) * 10
            
            # Age-based scoring
            if policy['type'] == 'Protection' and age < 35:
                score += 30
            elif policy['type'] == 'Child' and dependents > 0:
                score += 30 * dependents
            elif policy['type'] == 'Retirement' and age > 30:
                score += (age - 30) * 2  # Increases with age
            elif policy['type'] == 'Savings':
                if any(goal.lower().strip() in ['house', 'home', 'car', 'education'] for goal in financial_goals):
                    score += 25
            
            # Priority alignment
            if policy['type'] == priority:
                score += 40
            
            # Risk appetite alignment
            if risk_appetite == 'Low' and policy['type'] in ['Protection', 'Savings']:
                score += 20
            elif risk_appetite == 'Medium' and policy['type'] in ['Savings', 'Child']:
                score += 20
            elif risk_appetite == 'High' and policy['type'] in ['ULIP', 'Whole Life']:
                score += 20
            
            # Term preference alignment
            if preferred_term == 'Short' and '10' in policy.get('duration', ''):
                score += 15
            elif preferred_term == 'Medium' and any(term in policy.get('duration', '') for term in ['15', '20']):
                score += 15
            elif preferred_term == 'Long' and any(term in policy.get('duration', '') for term in ['25', '30']):
                score += 15
            
            policy_scores[policy_id] = score
        
        # Sort policies by score
        sorted_policies = sorted(policy_scores.items(), key=lambda x: x[1], reverse=True)
        top_policies = sorted_policies[:3]
        
        # Generate analysis text
        analysis = self._generate_analysis_text(user_data, top_policies)
        
        return {
            "analysis": analysis,
            "recommended_policy_ids": [pid for pid, score in top_policies],
            "scores": {pid: score for pid, score in top_policies}
        }
    
    def _generate_analysis_text(self, user_data: Dict, top_policies: List) -> str:
        """Generate analysis text without API calls"""
        age = user_data['personal_info'].get('age', 0)
        income = user_data['personal_info'].get('income', '')
        dependents = user_data['personal_info'].get('dependents', 0)
        risk_appetite = user_data['preferences'].get('risk_appetite', 'Medium')
        
        # Start with user profile summary
        analysis = f"## User Profile Analysis\n\n"
        analysis += f"Based on your profile as a {age}-year-old with "
        analysis += f"{dependents} dependents and a {risk_appetite.lower()} risk appetite, "
        
        # Add needs analysis
        analysis += "we've identified these key insurance needs:\n\n"
        
        if age < 30:
            analysis += "- Early career stage: Focus on building financial security with basic protection\n"
        elif 30 <= age < 45:
            analysis += "- Mid-career stage: Balance between protection and long-term savings\n"
        else:
            analysis += "- Late career stage: Focus on retirement planning and wealth preservation\n"
            
        if dependents > 0:
            analysis += f"- Family protection: Coverage needs for {dependents} dependents\n"
            if any(d.strip().lower() == 'education' for d in user_data['personal_info'].get('financial_goals', [])):
                analysis += "- Education planning: Funding needs for children's education\n"
        
        # Add recommendation rationale
        analysis += "\n## Recommendation Rationale\n\n"
        for pid, score in top_policies:
            policy = self.policies.get(pid, {})
            analysis += f"### {policy.get('name', pid)}\n"
            analysis += f"- Type: {policy.get('type', 'Unknown')}\n"
            analysis += f"- Recommendation score: {score}\n"
            analysis += f"- Key benefits: {', '.join(policy.get('features', ['N/A']))}\n"
            analysis += f"- Suitability: "
            
            # Add custom suitability text based on policy type
            if policy.get('type') == 'Protection':
                analysis += "Provides essential financial security for you and your dependents\n"
            elif policy.get('type') == 'Child':
                analysis += "Secures your child's future education and financial needs\n"
            elif policy.get('type') == 'Retirement':
                analysis += "Builds your retirement corpus for financial independence\n"
            elif policy.get('type') == 'Savings':
                analysis += "Helps achieve your financial goals with guaranteed returns\n"
            else:
                analysis += "Meets your specific insurance needs as identified\n"
            
            analysis += "\n"
        
        return analysis

class SBILifePersonalizationSystem:
    def __init__(self):
        self.recommender = InsuranceRecommender()
        os.makedirs("user_results", exist_ok=True)
    
    def process_user(self, user_id: str, fast_mode: bool = False):
        user_handler = UserDataHandler(user_id)
        
        if not fast_mode:
            self._collect_user_input(user_handler)
        else:
            self._collect_user_input_fast(user_handler)
        
        print(f"\nAnalyzing user {user_id}...")
        analysis_result = self.recommender.analyze_user(user_handler.data)
        
        # Save the comprehensive analysis
        user_handler.add_recommendation(analysis_result)
        result_file = f"user_results/{user_id}_analysis.json"
        with open(result_file, 'w') as f:
            json.dump(analysis_result, f, indent=2)
        
        # Print the recommended policies with details
        self._print_recommendations(analysis_result['recommended_policy_ids'])
        
        return analysis_result
    
    def _collect_user_input_fast(self, user_handler: UserDataHandler):
        """Collect user input more efficiently with defaults and bulk options"""
        print(f"\n=== Quick Data Collection for User: {user_handler.user_id} ===")
        
        # Browsing behavior - bulk entry
        print("\nEnter browsing counts for policy types (0-10):")
        # For each category, ask for just one number that will be distributed
        for category in CATEGORIES:
            try:
                total_views = int(input(f"Total views for {category} policies (0-30): "))
                if 0 <= total_views <= 30:
                    # Distribute views among policies in this category
                    plans = PLANS_BY_CATEGORY[category]
                    if plans:
                        # Give more weight to first policy in category
                        if len(plans) > 1 and total_views > 0:
                            # 60% to first, rest distributed evenly
                            first_plan_views = min(int(total_views * 0.6), total_views)
                            remaining_views = total_views - first_plan_views
                            views_per_plan = remaining_views // (len(plans) - 1) if len(plans) > 1 else 0
                            
                            user_handler.record_click(category, plans[0], first_plan_views)
                            for plan in plans[1:]:
                                user_handler.record_click(category, plan, views_per_plan)
                        else:
                            # Just one plan or distribute evenly
                            views_per_plan = total_views // len(plans)
                            for plan in plans:
                                user_handler.record_click(category, plan, views_per_plan)
            except ValueError:
                print("Using default value of 0")
        
        # Personal info - simplified
        print("\n=== Personal Information (press Enter for defaults) ===")
        age = input("Enter your age [30]: ") or "30"
        income = input("Enter your income range (e.g., 5-10L) [5-10L]: ") or "5-10L"
        marital_status = input("Marital status (Single/Married) [Single]: ") or "Single"
        dependents = input("Number of dependents [0]: ") or "0"
        goals = input("Main financial goals (comma separated) [retirement, house]: ") or "retirement, house"
        
        personal_info = {
            "age": int(age),
            "income": income,
            "marital_status": marital_status,
            "dependents": int(dependents),
            "financial_goals": [g.strip() for g in goals.split(',')]
        }
        user_handler.update_personal_info(personal_info)
        
        # Preferences - simplified
        print("\n=== Preferences (press Enter for defaults) ===")
        risk_appetite = input("Risk appetite (Low/Medium/High) [Medium]: ") or "Medium"
        preferred_term = input("Preferred policy term (Short/Medium/Long) [Medium]: ") or "Medium"
        priority = input("Priority (Protection/Savings/Retirement) [Protection]: ") or "Protection"
        
        preferences = {
            "risk_appetite": risk_appetite,
            "preferred_term": preferred_term,
            "priority": priority
        }
        user_handler.update_preferences(preferences)
    
    def _collect_user_input(self, user_handler: UserDataHandler):
        """Original detailed data collection method"""
        print(f"\n=== Collecting Data for User: {user_handler.user_id} ===")
        
        # Collect browsing behavior
        print("\nPlease enter your browsing behavior (enter policy IDs you've viewed):")
        for category in CATEGORIES:
            print(f"\n{category} Policies:")
            for pid in PLANS_BY_CATEGORY[category]:
                policy = POLICIES.get(pid, {})
                print(f"{pid}: {policy.get('name', 'Unknown')}")
                
                while True:
                    try:
                        views = int(input(f"How many times did you view {pid}? (0-10): "))
                        if 0 <= views <= 10:
                            for _ in range(views):
                                user_handler.record_click(category, pid)
                            break
                        print("Please enter a number between 0 and 10")
                    except ValueError:
                        print("Please enter a valid number")
        
        # Collect personal info
        print("\n=== Personal Information ===")
        personal_info = {
            "age": self._get_valid_input("Enter your age: ", int, min_val=18, max_val=100),
            "income": self._get_valid_input("Enter your income range (e.g., 5-10L, 10-20L): ", str),
            "marital_status": self._get_valid_input("Enter marital status (Single/Married/Divorced/Widowed): ", str,
                                                  options=["Single", "Married", "Divorced", "Widowed"]),
            "dependents": self._get_valid_input("Number of dependents: ", int, min_val=0),
            "financial_goals": input("Main financial goals (comma separated): ").split(',')
        }
        user_handler.update_personal_info(personal_info)
        
        # Collect preferences
        print("\n=== Preferences ===")
        preferences = {
            "risk_appetite": self._get_valid_input("Risk appetite (Low/Medium/High): ", str,
                                                 options=["Low", "Medium", "High"]),
            "preferred_term": self._get_valid_input("Preferred policy term (Short/Medium/Long): ", str,
                                                  options=["Short", "Medium", "Long"]),
            "priority": self._get_valid_input("Priority (Protection/Savings/Wealth): ", str,
                                            options=["Protection", "Savings", "Wealth"])
        }
        user_handler.update_preferences(preferences)
    
    def _get_valid_input(self, prompt: str, type_func, options=None, min_val=None, max_val=None):
        while True:
            try:
                value = input(prompt)
                if type_func == str and options and value not in options:
                    print(f"Please enter one of: {', '.join(options)}")
                    continue
                
                converted = type_func(value)
                
                if min_val is not None and converted < min_val:
                    print(f"Value must be at least {min_val}")
                    continue
                
                if max_val is not None and converted > max_val:
                    print(f"Value must be at most {max_val}")
                    continue
                
                return converted
            except ValueError:
                print(f"Please enter a valid {type_func.__name__}")
    
    def _print_recommendations(self, policy_ids: List[str]):
        print("\n=== Final Recommended Policies ===")
        for pid in policy_ids:
            policy = POLICIES.get(pid, {})
            print(f"\nPolicy ID: {pid}")
            print(f"Name: {policy.get('name', 'Unknown')}")
            print(f"Type: {policy.get('type', 'Unknown')}")
            print(f"Description: {policy.get('description', 'No description')}")
            print(f"Premium: {policy.get('premium', 'N/A')}")
            print(f"Coverage: {policy.get('coverage', 'N/A')}")
            print(f"Duration: {policy.get('duration', 'N/A')}")
            print(f"Key Features: {', '.join(policy.get('features', ['None']))}")

# Example Usage
if __name__ == "__main__":
    system = SBILifePersonalizationSystem()
    
    # Process sample user
    user_id = input("Enter user ID (or press Enter for default 'user_001'): ") or "user_001"
    print(f"\n{'='*40}")
    print(f"Processing User: {user_id}")
    print(f"{'='*40}")
    
    # Ask for quick mode
    fast_mode = input("Use quick data collection mode? (y/n) [y]: ").lower() != 'n'
    
    # Process the user
    start_time = time.time()
    result = system.process_user(user_id, fast_mode)
    end_time = time.time()
    
    # Print the recommended policy IDs and timing
    print("\nRecommended Policy IDs:")
    for pid in result['recommended_policy_ids']:
        print(f"- {pid}")
    
    print(f"\nProcessing completed in {end_time - start_time:.2f} seconds")
    