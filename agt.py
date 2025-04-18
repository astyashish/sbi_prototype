import os
import json
from datetime import datetime
from crewai import Agent, Task, Crew
from langchain_ibm import WatsonxLLM
from typing import Dict, List, Optional

# Set your environment variables
os.environ["WATSONX_APIKEY"] = "0ePVDekT98gfCJLgPLAiJ6u7ktfofOosRfdNuP8Mv5nK"
os.environ["SERPER_API_KEY"] = "a2d460207117ea4e1861c435a06c1cee18ed0c66"




# Configuration Class
class InsuranceConfig:
    PLANS = {
        "Protection": ["sbipp1", "sbipp2", "sbipp3"],
        "Savings": ["sbisp1", "sbisp2", "sbisp3"],
        "ULIP": ["sbiu1", "sbiu2"],
        "Retirement": ["sbirp1", "sbirp2"],
        "Child": ["sbicp1"],
        "Money Back": ["sbimbp1"],
        "Whole Life": ["sbiwlp1"]
    }
    
    @classmethod
    def get_categories(cls):
        return list(cls.PLANS.keys())
    
    @classmethod
    def get_plans(cls, category: str):
        return cls.PLANS.get(category, [])

# User Data Management
class UserDataHandler:
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.data_file = f"user_data/{user_id}.json"
        self.initialize_user_data()
    
    def initialize_user_data(self):
        """Initialize or load user data"""
        if not os.path.exists("user_data"):
            os.makedirs("user_data")
            
        if not os.path.exists(self.data_file):
            self.data = {
                "user_id": self.user_id,
                "clicks": {category: {plan: 0 for plan in InsuranceConfig.get_plans(category)} 
                          for category in InsuranceConfig.get_categories()},
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
        """Load user data from file"""
        with open(self.data_file, 'r') as f:
            self.data = json.load(f)
    
    def save_data(self):
        """Save user data to file"""
        self.data['last_updated'] = datetime.now().isoformat()
        with open(self.data_file, 'w') as f:
            json.dump(self.data, f, indent=2)
    
    def record_click(self, category: str, plan: str):
        """Record a click on a specific insurance plan"""
        if category in self.data['clicks'] and plan in self.data['clicks'][category]:
            self.data['clicks'][category][plan] += 1
            self.log_interaction(f"Clicked on {plan} in {category}")
            self.save_data()
    
    def update_preferences(self, preferences: Dict):
        """Update user preferences"""
        self.data['preferences'].update(preferences)
        self.log_interaction(f"Updated preferences: {preferences}")
        self.save_data()
    
    def update_personal_info(self, info: Dict):
        """Update personal information"""
        self.data['personal_info'].update(info)
        self.log_interaction(f"Updated personal info")
        self.save_data()
    
    def log_interaction(self, description: str):
        """Log an interaction with timestamp"""
        self.data['interaction_history'].append({
            "timestamp": datetime.now().isoformat(),
            "description": description
        })
    
    def add_recommendation(self, recommendation: Dict):
        """Add a recommendation to user's history"""
        self.data['recommendations'].append({
            "timestamp": datetime.now().isoformat(),
            "recommendation": recommendation
        })
        self.save_data()
    
    def get_recent_recommendations(self, count: int = 3):
        """Get recent recommendations"""
        return self.data['recommendations'][-count:]

# AI Analysis and Recommendation System
class InsuranceAnalyzer:
    def __init__(self):
        # Initialize LLM (in a real scenario, use environment variables for API keys)
        self.llm = self._initialize_llm()
        self.agents = self._create_agents()
    
    def _initialize_llm(self):
        """Initialize the IBM WatsonX LLM"""
        parameters = {
            "decoding_method": "greedy",
            "max_new_tokens": 500
        }
        
        return WatsonxLLM(
            model_id="meta-llama/llama-3-1-70b-instruct",
            url="https://us-south.ml.cloud.ibm.com",
            params=parameters,
            project_id="bfed6d8f-2d2d-436e-9a22-290c718f0fb0",
        )
    
    def _create_agents(self):
        """Create the multi-agent system"""
        # Behavior Analysis Agent
        behavior_analyst = Agent(
            llm=self.llm,
            role="Insurance Behavior Analyst",
            goal="Analyze user behavior to understand insurance preferences",
            backstory="You are an expert in analyzing user behavior patterns in insurance platforms",
            allow_delegation=False,
            verbose=True
        )
        
        # Recommendation Agent
        recommendation_agent = Agent(
            llm=self.llm,
            role="Insurance Recommendation Specialist",
            goal="Generate personalized insurance recommendations",
            backstory="You specialize in matching insurance products to individual customer needs",
            allow_delegation=False,
            verbose=True
        )
        
        # Persistency Agent
        persistency_agent = Agent(
            llm=self.llm,
            role="Customer Persistency Analyst",
            goal="Predict customer persistency and suggest retention strategies",
            backstory="You analyze customer behavior to predict policy renewal likelihood",
            allow_delegation=False,
            verbose=True
        )
        
        return {
            "behavior_analyst": behavior_analyst,
            "recommendation_agent": recommendation_agent,
            "persistency_agent": persistency_agent
        }
    
    def analyze_behavior(self, user_data: Dict) -> Dict:
        """Analyze user behavior patterns"""
        task = Task(
            description=f"Analyze this user's insurance browsing behavior: {user_data['clicks']}. "
                       f"Identify patterns in their preferences based on which plans they click most.",
            expected_output="A detailed analysis of the user's preferences including: "
                           "1. Preferred insurance categories "
                           "2. Specific plans of interest "
                           "3. Inferred financial goals "
                           "4. Potential needs not yet explored",
            agent=self.agents["behavior_analyst"]
        )
        
        crew = Crew(
            agents=[self.agents["behavior_analyst"]],
            tasks=[task],
            verbose=True
        )
        
        return crew.kickoff()
    
    def generate_recommendations(self, user_data: Dict, behavior_analysis: str) -> List[Dict]:
        """Generate personalized recommendations"""
        task = Task(
            description=f"Based on this user data: {user_data} and behavior analysis: {behavior_analysis}, "
                       "generate personalized insurance recommendations. Consider: "
                       "1. Their click history "
                       "2. Their personal information if available "
                       "3. Common needs for their demographic "
                       "4. Potential upselling opportunities",
            expected_output="A list of 3-5 recommended insurance plans with: "
                           "1. Plan ID and category "
                           "2. Reason for recommendation "
                           "3. Potential benefits for the user "
                           "4. Suggested communication approach",
            agent=self.agents["recommendation_agent"]
        )
        
        crew = Crew(
            agents=[self.agents["recommendation_agent"]],
            tasks=[task],
            verbose=True
        )
        
        return crew.kickoff()
    
    def predict_persistency(self, user_data: Dict) -> Dict:
        """Predict customer persistency and suggest retention strategies"""
        task = Task(
            description=f"Analyze this user's data: {user_data} to predict their likelihood of: "
                       "1. Purchasing a policy if they're a prospect "
                       "2. Renewing their policy if they're an existing customer "
                       "Also suggest retention strategies.",
            expected_output="A persistency report containing: "
                           "1. Purchase/renewal likelihood score (1-10) "
                           "2. Key factors influencing this score "
                           "3. 3 specific retention strategies "
                           "4. Optimal timing for engagement",
            agent=self.agents["persistency_agent"]
        )
        
        crew = Crew(
            agents=[self.agents["persistency_agent"]],
            tasks=[task],
            verbose=True
        )
        
        return crew.kickoff()

# Main Application Class
class SBILifePersonalizationSystem:
    def __init__(self):
        self.analyzer = InsuranceAnalyzer()
    
    def process_user(self, user_id: str):
        """Process a user through the system"""
        # Initialize user data handler
        user_handler = UserDataHandler(user_id)
        
        # Get user input (in a real app, this would come from UI)
        self._collect_user_input(user_handler)
        
        # Analyze behavior
        behavior_analysis = self.analyzer.analyze_behavior(user_handler.data)
        print(f"\nBehavior Analysis for {user_id}:\n{behavior_analysis}")
        
        # Generate recommendations
        recommendations = self.analyzer.generate_recommendations(
            user_handler.data, behavior_analysis)
        print(f"\nRecommendations for {user_id}:\n{recommendations}")
        
        # Save recommendations
        user_handler.add_recommendation({
            "analysis": behavior_analysis,
            "recommendations": recommendations
        })
        
        # Predict persistency
        persistency_report = self.analyzer.predict_persistency(user_handler.data)
        print(f"\nPersistency Report for {user_id}:\n{persistency_report}")
        
        return {
            "user_id": user_id,
            "analysis": behavior_analysis,
            "recommendations": recommendations,
            "persistency": persistency_report
        }
    
    def _collect_user_input(self, user_handler: UserDataHandler):
        """Simulate collecting user input (in a real app, this would be UI forms)"""
        print(f"\n=== Collecting Data for User: {user_handler.user_id} ===")
        
        # Simulate some clicks (in reality, tracked from website)
        print("Simulating some plan clicks...")
        user_handler.record_click("Protection", "sbipp1")
        user_handler.record_click("Protection", "sbipp1")
        user_handler.record_click("Savings", "sbisp2")
        user_handler.record_click("Retirement", "sbirp1")
        
        # Collect personal info
        personal_info = {
            "age": int(input("Enter your age: ")),
            "income": input("Enter your income range (e.g., 5-10L, 10-20L): "),
            "marital_status": input("Enter marital status (Single/Married): "),
            "dependents": int(input("Number of dependents: ")),
            "financial_goals": input("Main financial goals (comma separated): ").split(',')
        }
        user_handler.update_personal_info(personal_info)
        
        # Collect preferences
        preferences = {
            "risk_appetite": input("Risk appetite (Low/Medium/High): "),
            "preferred_term": input("Preferred policy term (Short/Medium/Long): "),
            "priority": input("Priority (Protection/Savings/Wealth): ")
        }
        user_handler.update_preferences(preferences)

# Example Usage
if __name__ == "__main__":
    system = SBILifePersonalizationSystem()
    
    # Process multiple users (in reality, this would be triggered by login)
    user_ids = ["user_001", "user_002"]  # In reality, get from authentication system
    
    for user_id in user_ids:
        print(f"\n{'='*40}")
        print(f"Processing User: {user_id}")
        print(f"{'='*40}")
        
        result = system.process_user(user_id)
        
        # Save the full result for later use
        with open(f"user_results/{user_id}_result.json", 'w') as f:
            json.dump(result, f, indent=2)
        
        print(f"\nCompleted processing for {user_id}. Results saved.")