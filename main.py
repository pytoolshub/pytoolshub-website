from flask import Flask, render_template, request
import random
import qrcode
from PIL import Image
import base64
from io import BytesIO
from datetime import datetime

app = Flask(__name__)


# ---------------- HOME ----------------
@app.route("/")
def home():
    return render_template("home.html")


# ---------------- BMI CALCULATOR ----------------
@app.route("/bmi", methods=["GET", "POST"])
def bmi():
    bmi_result = None
    if request.method == "POST":
        weight = float(request.form["weight"])
        height = float(request.form["height"]) / 100  # convert cm to meters
        bmi_value = weight / (height * height)
        bmi_result = round(bmi_value, 2)
    return render_template("bmi.html", result=bmi_result)


# ---------------- PASSWORD GENERATOR ----------------
@app.route("/password", methods=["GET", "POST"])
def password():
    generated_password = None
    if request.method == "POST":
        length = int(request.form["length"])
        chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*"
        generated_password = "".join(
            random.choice(chars) for _ in range(length))
    return render_template("password.html", password=generated_password)


# ---------------- QR CODE GENERATOR ----------------
@app.route("/qr", methods=["GET", "POST"])
def qr_generator():
    qr_image = None
    if request.method == "POST":
        data = request.form["data"]
        img = qrcode.make(data)

        buffer = BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)

        qr_image = base64.b64encode(buffer.getvalue()).decode()

    return render_template("qr.html", qr_image=qr_image)


# ---------------- AGE CALCULATOR ----------------
@app.route("/age", methods=["GET", "POST"])
def age():
    result = None
    if request.method == "POST":
        dob = request.form['dob']
        dob_date = datetime.strptime(dob, "%Y-%m-%d")
        today = datetime.today()

        years = today.year - dob_date.year
        months = today.month - dob_date.month
        days = today.day - dob_date.day

        if days < 0:
            months -= 1
            days += 30
        if months < 0:
            years -= 1
            months += 12

        result = {"years": years, "months": months, "days": days}

    return render_template("age.html", age=result)

# ---------------- CALCULATOR ----------------
@app.route("/calculator", methods=["GET", "POST"])
def calculator():
    result = None
    if request.method == "POST":
        num1 = float(request.form["num1"])
        num2 = float(request.form["num2"])
        operation = request.form["operation"]

        if operation == "add":
            result = num1 + num2
        elif operation == "subtract":
            result = num1 - num2
        elif operation == "multiply":
            result = num1 * num2
        elif operation == "divide":
            result = num1 / num2

    return render_template("calculator.html", result=result)


# ---------------- CONVERTER ----------------
@app.route("/converter", methods=["GET", "POST"])
def converter():
    result = None
    if request.method == "POST":
        value = float(request.form["value"])
        unit = request.form["unit"]

        if unit == "cm-to-m":
            result = value / 100
        elif unit == "m-to-cm":
            result = value * 100

    return render_template("converter.html", result=result)


# ---------------- JSON FORMATTER ----------------
@app.route("/json-formatter", methods=["GET", "POST"])
def json_formatter():
    formatted = None
    if request.method == "POST":
        raw_json = request.form["json_input"]
        try:
            import json
            parsed = json.loads(raw_json)
            formatted = json.dumps(parsed, indent=4)
        except:
            formatted = "Invalid JSON!"

    return render_template("json_formatter.html", result=formatted)


# ---------------- TEXT TOOLS ----------------
@app.route("/text-tools", methods=["GET", "POST"])
def text_tools():
    result = None
    if request.method == "POST":
        text = request.form["text"]
        action = request.form["action"]

        if action == "upper":
            result = text.upper()
        elif action == "lower":
            result = text.lower()
        elif action == "title":
            result = text.title()

    return render_template("text_tools.html", result=result)

# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=81, debug=True)
