from fastapi import FastAPI, HTTPException
import pandas as pd
import subprocess

# Initialize FastAPI app
app = FastAPI()

# Define the CSV file path
csv_file = "user_data_scored.csv"

def execute_scr():
    """
    Execute the 'scr.py' script to update the CSV file before fetching user data.
    """
    try:
        subprocess.run(["python", "scr.py"], check=True)  # Run scr.py
        subprocess.run(["python", "ins.py"], check=True)  # Run scr.py
    except subprocess.CalledProcessError:
        raise HTTPException(status_code=500, detail="Error executing scr.py")
def execute_ins():
    """
    Execute the 'scr.py' script to update the CSV file before fetching user data.
    """
    try:
        subprocess.run(["python", "ins.py"], check=True)  # Run scr.py
    except subprocess.CalledProcessError:
        raise HTTPException(status_code=500, detail="Error executing scr.py")

@app.get("/get_user_score/{name}")
def get_user_score(name: str):
    """
    Execute 'scr.py', reload the CSV, and retrieve the insurance score for a given user.
    """
    execute_scr()  # Run scr.py before fetching the data
    execute_ins()  # Run ins.py before fetching the data
    
    # Reload updated user data
    users_df = pd.read_csv(csv_file)

    user_row = users_df[users_df["Name"].str.lower() == name.lower()]
    
    if user_row.empty:
        raise HTTPException(status_code=404, detail="User not found")
    
    user_data = user_row.iloc[0].to_dict()
    return {"Name": user_data["Name"], "Score": user_data["Score"],"Insurance ID": user_data["Insurance ID"] }

# Run the FastAPI app using: uvicorn mainapi:app --reload
