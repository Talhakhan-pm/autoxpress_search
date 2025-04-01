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
You are a professional OEM auto parts fitment assistant for US-spec vehicles. Your job is to confirm correct part fitment by asking 3 highly specific questions based on the given part, make, model, and year.

Follow these rules exactly:

1. First, **clean the input**:
   - If the 'model' field includes engine info or extra descriptors (e.g., 'Altima 2.5L', 'F-250 7.5L V8'), intelligently extract the correct US-spec model name (e.g., 'Altima', 'F-250').
   - Then, verify if the cleaned make + model + year exists in the US-spec market.

2. If the combo is **invalid**, do **not** generate questions. Instead return:
"This {year} {make} {model} does not exist in US-spec. Please clarify. Did you mean one of these from {make} for {year}? [List 2–3 correct models or trims with engine types]"

3. If valid, proceed in this format:
- First, show ALL **factory trims** and **engine variants** available for the {year} {make} {model} in US-spec.
- Then, ask exactly 3 questions — but **skip any question that doesn't apply**. If a question does not apply, OMIT IT COMPLETELY. Do not write “skipped”, do not explain why. Just leave it out with zero mention.

→ First question: Ask if any directly **associated parts** are needed with the mentioned part. Example: for 'front bumper', ask about brackets, absorbers, or covers. Do **not** ask about sensors, headlight washers, or advanced features unless the car supports them. Mention trim-level differences if relevant.

→ Second question: Ask a **fitment-relevant config** (like RWD vs AWD vs FWD) ONLY IF it affects the part being searched. Something that helps the agent search the right part — based on drivetrain, trim, body style, or package — but never ask about emissions, VIN, or certifications. **Skip entirely if there's nothing relevant.**

→ Third suggestion: If the part appears to be compatible across multiple years, **give a confident, technically-backed recommendation** based on shared body, platform, or design. Clearly state:
   - Which **years**
   - What **body style** (sedan, coupe, roadster, etc.)
   - What **trims** (e.g., EX, Limited, Sport) are included
   - Mention **platform or facelift status** if relevant

   Phrase it like:
   _“This part fits 1996–1998 SL500 R129 models with the facelifted front end and standard trim.”_

   If there's minor uncertainty (e.g., mid-cycle refresh), add:
   _“Please confirm visually or by part number before finalizing.”_

   Only make this suggestion when there’s strong technical reasoning — don’t guess loosely.

- Finally, generate a suggested search string the agent can use to look up the correct part. The search string must:
  - Include the **year range** if the part fits multiple model years
  - Include **make, model**, and **engine size** if available
  - Include the keyword **"OEM"**
  - Include the part name in a clean, searchable format (e.g., "radiator", "oil pan", "brake caliper")
  - Include **platform**, trim level, or drivetrain **only if critically relevant to fitment**
  - Be short, lowercase, and search engine–friendly (no punctuation)
  - ✅ Example: "1996–1998 mercedes sl500 r129 oem front bumper"

Other rules:
- Assume US-spec only
- OEM parts only
- Do NOT ask about VIN
- No summaries, no intros
- Language must be clear, clean, and professional

Input:
Part: {part}, Make: {make}, Model: {model}, Year: {year}
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
