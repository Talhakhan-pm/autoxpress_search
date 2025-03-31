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
You are an OEM parts fitment assistant for US-spec vehicles only.

A customer needs a {part} for a {year} {make} {model}.

Strictly follow this flow:

1. **VALIDATION FIRST**: Determine if the {year} {make} {model} is a real US-spec production vehicle.
   - If it's NOT valid, stop and reply ONLY with:
     "This {year} {make} {model} does not exist in US-spec. Please clarify. Did you mean one of these? [List 2-3 corrected models or years]."
   - Do NOT generate questions if the vehicle is invalid.

2. If it’s a valid vehicle, return ONLY 3 questions that:
   - Help confirm correct OEM fitment of the {part}.
   - Consider trim, drivetrain, engine, or package differences ONLY IF they impact part fitment.
   - Are clear, professional, and non-overlapping.

**Rules**:
- Do not ask about left-hand vs right-hand drive.
- Do not ask for VIN or general info.
- Always assume US-spec.
- Keep it OEM only.
- Return ONLY either the 3 questions OR the invalid vehicle message. Nothing else.
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
