from fastapi import FastAPI, Form, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import sqlite3
import uvicorn
import uuid
import os

app = FastAPI()

app.mount("/frontend", StaticFiles(directory="frontend", html=True), name="frontend")

# Home - show HTML
@app.get("/")
async def read_root():
    return {"message": "Go to /frontend/index.html to access the form"}

@app.post("/submit")
async def submit_form(
    name: str = Form(...),
    email: str = Form(...),
    age: int = Form(...),
    income: float = Form(...),
    plan_type: str = Form(...)
):
    conn = sqlite3.connect("C:/Databases/insurance.db")
    cursor = conn.cursor()

    user_id = str(uuid.uuid4())
    cursor.execute("INSERT INTO Users (user_id, name, email) VALUES (?, ?, ?)", (user_id, name, email))

    # Map plan_type to some policies manually
    recommended = {
        "Protection": "sbipp1",
        "Savings": "sbisp1",
        "ULIP": "sbiu1",
        "Retirement": "sbirp1",
        "Child": "sbicp1",
        "Money Back": "sbimbp1",
        "Whole Life": "sbiwlp1"
    }

    policy_id = recommended.get(plan_type, "sbipp1")
    cursor.execute("""
        INSERT INTO Recommendations (user_id, policy_id, recommendation_score, recommended_at)
        VALUES (?, ?, ?, datetime('now'))
    """, (user_id, policy_id, 0.9))

    conn.commit()
    conn.close()

    return JSONResponse(content={"message": f"Thank you {name}, recommended plan: {plan_type}"})
