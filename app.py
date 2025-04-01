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
You are a professional OEM auto parts fitment assistant for US-spec vehicles. Your job is to extract vehicle information from a sentence, confirm correct part fitment, and generate 2–3 highly specific follow-up questions the agent should ask the customer.

1. First, **parse and clean the input**:
   - Intelligently extract the part name, year, make, model, and trim level from the input sentence.
   - If any words are misspelled (e.g., 'Toyta Camary' instead of 'Toyota Camry'), correct them automatically.
   - Example input: “front bumper for 2018 nisan sentra s” → Parse as:
     - Part: front bumper
     - Year: 2018
     - Make: Nissan
     - Model: Sentra
     - Trim: S

2. Then, verify that the parsed year, make, and model exist in the US-spec market.
   - If the combination is invalid, return this message:
   "This vehicle does not exist in US-spec. Please clarify. Did you mean one of these: [suggest 2–3 correct models/trims for that year and make]"

3. If valid, proceed as follows:

- First, show the **factory trims** and **engine variants** available for the parsed vehicle.
- Then, generate up to 3 specific questions — but **only include questions that are truly relevant** (skip the rest silently).

→ First question: Ask if any directly **associated parts** are needed with the mentioned part. Example: for 'front bumper', ask about brackets, absorbers, or covers. Only include sensors or headlight washers if the vehicle actually came with them. Mention trim-level or package differences if relevant.

→ Second question: Ask a **fitment-relevant configuration** (like FWD vs AWD) ONLY IF it matters for the part in question. This can include trim, drivetrain, body style, or factory packages — but NEVER ask about emissions, VIN, or certification.

→ Third suggestion: Suggest compatible year ranges **only if** you're confident the part is unchanged across those years. Back it with reasoning (platform, body style, generation, etc).
   - Example: _“This part fits 2020–2024 Sentra models with the same B18 chassis and front-end design.”_
   - Be very specific: include body style, platform (e.g., R129, B18), and trims if they matter.
   - If the input year is the **first year of a known generation** and later years use the same design, **include the full range**.
   - If there's any uncertainty, add: _“Confirm with part number or visual match before finalizing.”_

4. Then, create a clean, search-optimized phrase the agent can use to find the correct part:
   - Must include: [year or year range] + make + model + engine (if known) + OEM + part name
   - Include platform or trim **only if critical**
   - Make it lowercase and searchable, like:  
     _“2020–2024 nissan sentra b18 oem front bumper”_

Other rules:
- Assume US-spec only
- Only handle OEM parts
- No VIN, no emission package talk
- Never mention “skipped question”
- No summaries or fluff — just results

Input:
\"\"\"{query}\"\"\"
"""


        response = client.chat.completions.create(
            model="gpt-4-1106-preview",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4
        )

        questions = response.choices[0].message.content.strip()

    return render_template("index.html", questions=questions)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
