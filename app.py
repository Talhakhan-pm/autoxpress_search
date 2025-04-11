import requests  # ✅ Needed for VIN API calls

from flask import Flask, render_template, request
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

app = Flask(__name__)

# ✅ VIN decoder helper function
def decode_vin(vin):
    """
    Calls the NHTSA VIN decoding API and returns vehicle info as a dictionary.
    Returns an empty dict if invalid or fails.
    """
    if not vin:
        return {}
    try:
        url = f'https://vpic.nhtsa.dot.gov/api/vehicles/decodevinvaluesextended/{vin}?format=json'
        response = requests.get(url)
        data = response.json()
        if data and data['Results']:
            result = data['Results'][0]
            if result.get('Make') and result.get('ModelYear'):
                return result
    except Exception as e:
        print(f"VIN decode error: {e}")
    return {}

# ✅ Main GPT Assistant route
@app.route("/", methods=["GET", "POST"])
def index():
    questions = None
    if request.method == "POST":
        query = request.form.get("prompt", "").strip()

        prompt = f"""
You are an auto parts fitment expert working for a US-based parts sourcing company. The goal is to help human agents quickly identify the correct OEM part for a customer's vehicle.

Do not provide explanations, summaries, or filler text. Format everything in direct, clean bullet points.

Your job is to:
1. If anything is misspelled, auto-correct it to the best of your automotive knowledge.

2. Validate:
   - Confirm the vehicle exists in the US market.
   - If invalid, return:
     👉 This vehicle is not recognized in US-spec. Please clarify. Did you mean one of these: [list 2–3 real US models for that year/make]?
   - If valid, do NOT confirm it in a sentence. Just move on.

3. If valid:
   - List factory trims with engine options (displacement + type + drivetrain).
   - DO NOT repeat parsed info in sentence form

4. Ask follow-up questions, max 3:
   - Question 1: Ask about directly associated hardware needed (e.g., bumper → brackets, fog trims, sensors if applicable)
   - Question 2: Only ask follow-up if something affects fitment — like transmission type, submodel, or drivetrain. 
    Do NOT ask vague or unnecessary questions like modifications or preferences.
   - Fitment: If fitment is shared across multiple years, mention the range with platform/chassis code — you can take a guess if needed. Just say it out. No worries. 
   - If more products are involved, you can ask more questions, max 2.

5. Finish with a bolded search-optimized lookup phrase, (add a emoji of world right before the phrase):
   - Format: lowercase string including [year or range] + make + model + trim (if needed) + engine (if relevant) + oem + part name
   - Think of it as a search term for a customer to find the part. Use the most relevant keywords. Give two search terms for the same part with another name.
   - Example 1:  “🔎 2020–2022 honda civic ex oem front bumper”
   - Example 2: “🔎 2020 – 2022 honda civic ex oem bumper cover”


Hard rules:
- US-spec vehicles ONLY
- OEM parts ONLY
- NO mention of VIN, emissions, certifications
- NO summaries like “The Civic is a valid US model”
- NO extra commentary, only raw output
- Format matters — bullet points, clean, efficient

Input:
\"\"\"{query}\"\"\"
"""

        response = client.chat.completions.create(
            model="gpt-4-1106-preview",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4
        )

        questions = response.choices[0].message.content.strip()

    return render_template("index.html", questions=questions, vin_result=None)

# ✅ Manual VIN Decode route (for second form)
@app.route("/vin-decode", methods=["POST"])
def vin_decode():
    vin = request.form.get("vin", "").strip()
    vin_info = decode_vin(vin)
    return render_template("index.html", questions=None, vin_result=vin_info)

# ✅ Flask entry point
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
