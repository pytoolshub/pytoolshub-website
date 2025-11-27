from flask import Flask, render_template, request, jsonify
import random
import qrcode
from PIL import Image
import base64
from io import BytesIO
from datetime import datetime
import json

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
        height = float(request.form["height"]) / 100
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
        generated_password = "".join(random.choice(chars) for _ in range(length))
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


# ---------------- CALCULATOR API ----------------
@app.route("/api/calc", methods=["POST"])
def api_calc():
    data = request.json
    a = float(data["a"])
    b = float(data["b"])
    op = data["op"]

    if op == "+": result = a + b
    elif op == "-": result = a - b
    elif op == "*": result = a * b
    elif op == "/": result = a / b
    else: result = "Invalid operation"

    return jsonify({"result": result})


# ---------------- CONVERTER API ----------------
@app.route("/api/convert", methods=["POST"])
def api_convert():
    data = request.json
    value = float(data["value"])
    from_unit = data["from"]
    to_unit = data["to"]

    length_units = {
        "meter": 1,
        "kilometer": 0.001,
        "centimeter": 100,
        "millimeter": 1000
    }

    if from_unit in length_units and to_unit in length_units:
        result = value * (length_units[to_unit] / length_units[from_unit])
        return jsonify({"result": result})
    else:
        return jsonify({"error": "Invalid units"})


# ---------------- JSON FORMATTER API ----------------
@app.route("/api/format_json", methods=["POST"])
def api_format_json():
    try:
        input_data = request.json["data"]
        parsed = json.loads(input_data)
        return jsonify({"result": json.dumps(parsed, indent=4)})
    except Exception as e:
        return jsonify({"error": str(e)})


# ---------------- TEXT TOOLS API ----------------
@app.route("/api/text", methods=["POST"])
def api_text_tools():
    data = request.json
    text = data["text"]
    action = data["action"]

    if action == "upper":
        return jsonify({"result": text.upper()})
    elif action == "lower":
        return jsonify({"result": text.lower()})
    elif action == "title":
        return jsonify({"result": text.title()})
    else:
        return jsonify({"error": "Invalid action"})


# ---------------- RUN SERVER ----------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=81, debug=True)
