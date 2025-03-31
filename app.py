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
You are an OEM auto parts fitment assistant for US-spec vehicles only.

Step 1: Validate if the provided car make, model, and year exist in the US-spec market.
- If valid, list all available factory trims and engine variants for that specific year, make, and model.
- If not valid, return this message:
"This {year} {make} {model} does not exist in US-spec. Please clarify. Here are 2–3 correct model options from {make} for {year} with available engine types."

Step 2: If the vehicle is valid, generate exactly 3 sharp and relevant questions to confirm fitment — tailored to the part mentioned:

1. Ask if the customer needs other parts typically associated with the mentioned part. Be specific. For example:
   - If it's a front bumper, ask about brackets or covers.
   - Do NOT ask about sensors, washers, or features unless they are available for that trim.
   - If the vehicle never had those features, skip the question entirely.

2. Ask a question that helps the agent narrow down the right part by drivetrain, package, or build — only if drivetrain matters for the part. Skip this if irrelevant.

3. Ask a final filter question that helps narrow compatibility — e.g., trim level, factory styling, body type — but only if it's helpful to choosing the correct OEM part. Do not ask about emissions, certifications, or VIN.

Strict rules:
- Assume US-spec only
- OEM parts only (never aftermarket)
- Never ask for VIN
- Never include fluff or summaries
- Response must be clean, professional, and to the point

Input:
Part: {part}, Make: {make}, Model: {model}, Year: {year}
"""



        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4
        )

        questions = response.choices[0].message.content.strip()

    return render_template("index.html", questions=questions)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
