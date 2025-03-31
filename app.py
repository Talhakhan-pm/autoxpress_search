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
You are an auto parts fitment expert for OEM parts only.

A customer is looking for a {part} for a {year} {make} {model} (US-spec vehicle).

1. If the provided make/model/year combination is invalid, flag it immediately and suggest a few correct alternatives from that make around that year.
2. If valid, ask ONLY the top 3 most important, sharp, specific questions the agent should ask to ensure correct OEM part fitment.
3. Do NOT ask for VIN.
4. Consider trim, drivetrain, and package differences if they’re relevant to fitment.
5. Do NOT ask overlapping questions — make each one count.
6. Keep language clear and professional.

Return the result as bullet points only, no intro or summary.
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