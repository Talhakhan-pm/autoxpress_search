from flask import Flask, render_template, request
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    questions = None
    if request.method == "POST":
        part = request.form["part"]
        make = request.form["make"]
        model = request.form["model"]
        year = request.form["year"]

        prompt = f"""
You are a professional auto parts fitment assistant for OEM parts only, specializing in US-spec vehicles.

A customer is looking for a {part} for a {year} {make} {model}.

Follow these exact instructions:

1. First, validate if the {year} {make} {model} exists as a real US-spec vehicle.
   - If the combination is invalid, respond with:
     "This {year} {make} {model} does not exist in US-spec. Please clarify. Did you mean one of these? [List 2-3 corrected options]."
   - Do not continue if it's invalid.

2. If valid, generate **exactly 3 sharp, specific, and non-overlapping questions** to confirm OEM part fitment.

3. Focus only on:
   - Trim, engine, drivetrain, or package differences that affect fitment.
   - Mechanical or body-related dependencies tied to OEM fitment.

4. Rules:
   - Never ask for VIN.
   - Never ask about left-hand/right-hand drive.
   - Assume all vehicles are US-spec.
   - Keep it 100% OEM, clean, and professional.
   - Format your response as bullet points only. No introduction, no emojis, no fluff.

Only return bullet points or the invalid model message. No exceptions.
"""

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4
        )

        questions = response.choices[0].message.content.strip()

    return render_template("index.html", questions=questions)

if __name__ == "__main__":
    app.run(debug=True)
