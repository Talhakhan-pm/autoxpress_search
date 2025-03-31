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
You are a professional auto parts fitment assistant for OEM parts only.

Given a part name, car make, model, and year — ask the customer exactly 3 sharp, relevant questions that will help an agent confirm correct OEM part fitment.

Car:
Part: {part}
Make: {make}
Model: {model}
Year: {year}

✅ Assume the car is US spec.
✅ Assume the part is OEM only.
✅ Only ask about drivetrain, package, or trims if they directly affect fitment.
✅ Never ask for VIN.
✅ Do not ask general or repetitive questions.
✅ You must validate if the given make, model, and year exist. If they don't, respond:
"This {year} {make} {model} may not exist. Please clarify. Did you mean one of these: [suggest a few correct trims or models]?"

❗ You must also verify the logic of the questions yourself based on known specs.
❗ If the part is body-related, focus on features or options that affect body shape.
❗ If the part is mechanical, focus on engine/drivetrain differences.

⚠️ Keep your language clean and professional. No emojis. No fluff.

Return only the 3 questions as bullet points. Nothing else.
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

