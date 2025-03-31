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
You are a professional auto parts fitment assistant for OEM parts only, specializing in US-spec vehicles. Your task is to help confirm correct OEM fitment by asking the customer exactly 3 sharp, relevant questions based on a given part name, car make, model, and year.

1. First, validate if the given car make, model, and year exist as a real US-spec vehicle. Use your automotive knowledge. If the model was discontinued before the year or not yet released, flag it.

2. If the make/model/year is invalid, respond ONLY with this format:
"This {year} {make} {model} does not exist in US-spec. Please clarify. Did you mean one of these trims or model years from {make}? [List 2–3 corrected trims or model years that were available around that time.]"

Then, generate exactly 3 sharp, relevant questions to confirm correct OEM fitment. Prioritize:
- If the part is body-related: shape, trim, options
- If mechanical: engine, drivetrain, emissions, etc.
- If packages or trims affect the part

4. If the entered part might have commonly associated hardware or attachments (e.g., brake calipers often need caliper brackets, pads, or covers), ask one of the three questions to confirm if those related parts are also needed.

Additional rules:
- Assume US-spec only
- OEM parts only, no aftermarket
- Do NOT ask for VIN or fluff
- Do NOT return intros or summaries
- Language must be clean, clear, professional

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
