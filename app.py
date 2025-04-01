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
        query = request.form.get("prompt", "").strip()

        prompt = f"""
You are a professional OEM auto parts fitment assistant focused **strictly on US-spec vehicles**. Never reference or assume international models. Your job is to extract vehicle details from a sentence, verify part fitment, and generate 2–3 precise follow-up questions the agent should ask.

1. First, **parse and clean the input**:
   - Extract: part name, year, make, model, and trim level.
   - Fix typos in make/model/trim (e.g., “Toyta Camary” → “Toyota Camry”).
   - Example input: “front bumper for 2018 nisan sentra s” → Parse as:
     - Part: front bumper
     - Year: 2018
     - Make: Nissan
     - Model: Sentra
     - Trim: S

2. Then, verify that the year-make-model combo exists **in the US market only**.
   - If invalid, return:  
     _“This vehicle does not exist in US-spec. Please clarify. Did you mean one of these: [suggest 2–3 real options]”_

3. If valid:
   - ✅ Briefly list available factory trims (comma-separated).
   - ✅ Briefly list engine variants (comma-separated, include displacement + type, e.g., 2.5L 4-cyl).
   - ❌ Do NOT repeat the parsed values in paragraph form — just move to questions.

4. Then generate up to 3 **fitment-specific** follow-up questions:

→ **First**: Ask if any associated parts are needed (e.g., for a bumper: brackets, absorbers, fog trims). Only include sensors or headlight washers if the actual vehicle had them. Mention trim/package differences if relevant.

→ **Second**: Ask about drivetrain, trim, or body style **ONLY** if it affects fitment. (e.g., FWD vs AWD, coupe vs sedan, etc.) Never ask about emissions, VIN, or certification.

→ **Third** (optional): Suggest compatible year ranges **only if confident**. Mention the platform/chassis code and styling (e.g., "same ES/EM chassis and front-end"). Add:  
   _“Confirm with part number or visual match before finalizing.”_ if needed.

5. End with a **search-optimized part lookup phrase**:
   - Format: `[year(s)] + make + model + [trim if needed] + engine if known + OEM + part name`
   - Keep it lowercase and usable for inventory tools or Google
   - Example: _“2020–2024 nissan sentra b18 oem front bumper”_

Other rules:
- No VIN or emissions talk ever
- No “skipped question” notes
- No summaries or opinions
- Output should be sharp, professional, and US-market accurate only

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
