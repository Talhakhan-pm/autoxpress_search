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
You're an auto parts expert helping a sales agent identify exact fitment for a customer.

The customer needs a {part} for a {year} {make} {model}.

Using known trim levels, configurations, body styles, and options from that year, give the top 3 **non-redundant**, **specific** questions the agent should ask to confirm fitment.

Do NOT repeat the same logic in two ways (e.g. don't say "base or higher trim" and then list trims in another question). Each question should unlock unique info about fitment.

Do NOT ask for VIN, production date, or other difficult info.

Return as sharp bullet points.
"""


        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4
        )

        questions = response.choices[0].message.content

    return render_template("index.html", questions=questions)

if __name__ == "__main__":
    app.run(debug=True)
