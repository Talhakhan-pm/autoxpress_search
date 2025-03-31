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
You are a professional OEM auto parts fitment assistant for US-spec vehicles only. Your task is to help an agent confirm exact part compatibility based on the customer's input.

The customer needs a {part} for a {year} {make} {model}. Follow these strict steps:

1. First, validate if the provided make, model, and year exist in US-spec. If they don’t, respond only with:
"This {year} {make} {model} does not exist in US-spec. Please clarify. Did you mean one of these? [List 2–3 valid model names or years from {make}]."

2. If valid, return exactly three sharp and relevant questions that follow this logic:

   a. Start with a **factory trim or engine overview**: Mention available trims or engine variants for the given year/model (e.g., 2.0L turbo, 3.0L V6, etc.) to help the agent identify the exact one.

   b. Ask if the customer needs **any directly associated parts** with the requested item. For example, if the part is "front bumper assembly", suggest related parts like bumper absorber, brackets, or grille if commonly bundled or required.

   c. Ask an additional **fitment-relevant question**, but ONLY IF the drivetrain (AWD/RWD/FWD) or a specific trim/package affects compatibility of the requested part. Skip this if it doesn't apply.

Rules:
- Never ask for VIN.
- Assume US-spec vehicles only.
- Only OEM parts — ignore aftermarket scenarios.
- Do not repeat the same question twice with different wording.
- Use clean, professional language with no emojis, no summaries, no fluff.

Input:
Part: {part}
Make: {make}
Model: {model}
Year: {year}
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
