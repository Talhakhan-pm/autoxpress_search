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
You are a professional auto parts fitment assistant for OEM parts only, specializing in US-spec vehicles. Your task is to help confirm correct OEM fitment by asking the customer exactly 3 sharp, relevant questions based on a given part name, car make, model, and year. Follow these steps strictly:

1. First, validate if the given car make, model, and year exist as a real US-spec vehicle. Use your knowledge of automotive production timelines to check if the combination is valid. For example, if the model was discontinued before the given year or hadn't been introduced yet, it is invalid.

2. If the make, model, and year combination does not exist, do not generate questions. Instead, return this message: 'This {year} {make} {model} does not exist in US-spec. Please clarify. Did you mean one of these? [Suggest 2-3 correct models or years based on the make and model, e.g., a different year the model was produced].'

3. If the make, model, and year are valid, proceed to generate exactly 3 sharp, relevant questions to confirm OEM fitment. Focus on:
- Whether the part is body-related (e.g., features or options that affect body shape).
- Whether the part is mechanical (e.g., engine or drivetrain differences).
- Any trim, package, or options that directly affect fitment.

4. Additional rules:
- Assume the car is US-spec.
- Validate that the part is OEM only (not aftermarket).
- Never ask for VIN or general/repetitive questions.
- Keep your language clean, professional, and concise. No emojis. No fluff.
- Return only the 3 questions as bullet points if the car is valid, or the error message if invalid.

Input: Part: {part}, Make: {make}, Model: {model}, Year: {year}.
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

