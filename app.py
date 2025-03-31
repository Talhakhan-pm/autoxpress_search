from flask import Flask, render_template, request
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

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
You are an automotive parts fitment expert working for a US-based OEM parts company. A customer is requesting a {part} for a {year} {make} {model}. You must help a sales agent identify the exact questions to ask the customer in order to confirm part fitment.

Follow these exact rules:

1. Assume the part is **OEM** only. Do not consider aftermarket variations.
2. All vehicles are **US-spec** — avoid global trims or market confusion.
3. Tailor your questions based on the part type:
   - If the part is **mechanical** (e.g., transmission, brakes, suspension), focus on drivetrain, engine size, and performance packages.
   - If the part is **body-related** (e.g., bumper, headlight), focus on trims, sensors, fog lights, cameras, etc.
4. Do NOT ask for VIN, production date, or anything difficult for the customer to find.
5. DO NOT ask questions that can be inferred. For example:
   - If the vehicle only comes in one body style, don't ask “sedan or coupe?”
   - If only one engine is available for that trim and year, don't ask “engine size?”
6. Use known fitment knowledge to **verify basic compatibility yourself**.
7. If the entered **trim or model doesn't exist**, reply with a clarification and suggest possible correct options (e.g., “Did you mean SR, SV, or S trim?”).
8. Keep the response short and professional — no emojis, no extra commentary.

Output ONLY the 3 most important and specific questions needed to narrow down exact fitment.
Format the response as bullet points.
"""


        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4
        )

        questions = response.choices[0].message.content

    return render_template("index.html", questions=questions)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host="0.0.0.0", port=port)

