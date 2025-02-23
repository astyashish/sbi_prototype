import google.generativeai as genai # type: ignore
import pandas as pd
import time

# Set up the Gemini API key
genai.configure(api_key="AIzaSyCMt8TKggH_yqgs2lT8iYRo1BGWK22MTYI")  # Replace with your actual API key
# Create sample user data and save to CSV

# Load user data from CSV file
csv_file = "insurance_data_example.csv"
users_df = pd.read_csv(csv_file)

def generate_score(user_data, prompt_conditions):
    """
    Uses Google Gemini AI to evaluate the user based on given conditions and return a numeric score only.
    """
    time.sleep(1)  # Delay to avoid rate limits
    try:
        model = genai.GenerativeModel("gemini-pro")

        # Define the prompt clearly to return only a numeric value
        prompt = f"""
        You are an AI that scores users from 0 to 100 based on the given conditions.

        Conditions:
        {prompt_conditions}

        User Data:
        {user_data}

        Return ONLY a numeric score. Do NOT include any explanation, text, or breakdown.
        """

        response = model.generate_content(prompt)

        # Extract raw text response
        score_text = response.text.strip()

        # Debugging: Print the API response
        print(f"API Response: {score_text}")

        # Ensure the output is a valid number
        try:
            score_value = float(score_text)
            return score_value
        except ValueError:
            print(f"Invalid score returned: {score_text}")
            return None  # Return None if the score is invalid

    except Exception as e:
        print(f"Error: {e}")
        return None  # Handle errors

# Define scoring conditions
scoring_conditions = "Evaluate the likelihood of a user purchasing insurance and the profitability for the company based on both personal and external factors. Personal factors include age (younger individuals 18-40 have higher scores), gender (females tend to have lower insurance claims), health conditions (no pre-existing conditions score higher), occupation risk (low-risk jobs score higher), income level (higher income means higher score), family dependents (more dependents increase the need for insurance), lifestyle choices (non-smokers and fitness enthusiasts score better), and policy history (no claims score higher). External factors include air pollution (high pollution reduces scores), medical infrastructure (better healthcare cities score higher), crime rates (higher crime reduces scores), natural disaster risk (zones prone to disasters reduce scores), state-specific insurance regulations (can impact the score), and cost of living (higher living costs may influence premiums). Users with lower risks, higher income, better health, and living in cities with strong healthcare systems are more likely to buy insurance and will be more profitable for the company."

# Generate scores and store them properly
users_df["Score"] = users_df.apply(lambda row: generate_score(row.to_dict(), scoring_conditions), axis=1)

# Ensure the scores are saved correctly
print(users_df)  # Debugging: Print DataFrame before saving

# Save updated dataset
users_df.to_csv("user_data_scored.csv", index=False)

print("✅ User scoring completed and saved to user_data_scored.csv")
