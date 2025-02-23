import google.generativeai as genai # type: ignore
import pandas as pd
import time

# Set up the Gemini API key
genai.configure(api_key="AIzaSyCMt8TKggH_yqgs2lT8iYRo1BGWK22MTYI")  # Replace with your actual API key

# Load user data from CSV file
csv_file = "user_data_scored.csv"
users_df = pd.read_csv(csv_file)

with open(r"D:\co\ins_promt.txt", "r", encoding="utf-8") as file:
    insurance_plans  = file.read()
# Define insurance plans with their respective IDs
'''
insurance_plans = {
    "Protection": ["sbipp1", "sbipp2", "sbipp3"],
    "Savings": ["sbisp1", "sbisp2", "sbisp3"],
    "ULIP": ["sbiu1", "sbiu2"],
    "Retirement": ["sbirp1", "sbirp2"],
    "Child": ["sbicp1"],
    "Money Back": ["sbimbp1"],
    "Whole Life": ["sbiwlp1"]
}

'''
def recommend_insurance(user_data):
    """
    Uses Google Gemini AI to recommend the best insurance plan based on user data and score.
    """
    time.sleep(1)  # Delay to avoid rate limits
    try:
        model = genai.GenerativeModel("gemini-pro")

        # Define the prompt clearly to return only an insurance ID
        prompt = f"""
        You are an AI that recommends the best insurance plan based on user data and score.
        
        User Data:
        {user_data}
        
        Insurance Plans:
        {insurance_plans}
        
        Return ONLY the best insurance ID(s) from the provided list. Do NOT include any explanation or text.
        """

        response = model.generate_content(prompt)

        # Extract raw text response
        plan_text = response.text.strip()

        # Debugging: Print the API response
        print(f"API Response: {plan_text}")

        return plan_text

    except Exception as e:
        print(f"Error: {e}")
        return "Error"

# Apply the function to assign insurance plans
users_df["Insurance ID"] = users_df.apply(lambda row: recommend_insurance(row.to_dict()), axis=1)

# Save the updated dataset
users_df.to_csv("user_data_scored.csv", index=False)

print("✅ Insurance recommendation completed and saved to user_data_scored.csv")
