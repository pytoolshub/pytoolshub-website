from flask import Flask, render_template, request, jsonify
import json

app = Flask(__name__)

# -------------------------
# HOME PAGE
# -------------------------
@app.route('/')
def home():
    return render_template('home.html')


# -------------------------
# CALCULATOR
# -------------------------
@app.route('/calculator')
def calculator():
    return render_template('calculator.html')


# -------------------------
# UNIT CONVERTER
# -------------------------
@app.route('/converter', methods=['GET', 'POST'])
def converter():
    if request.method == 'POST':
        try:
            category = request.form.get("category")
            value = float(request.form.get("value"))
            from_unit = request.form.get("from")
            to_unit = request.form.get("to")

            conversions = {
                "Length": {
                    "Meter": 1,
                    "Kilometer": 0.001,
                    "Centimeter": 100,
                    "Millimeter": 1000
                },
                "Weight": {
                    "Gram": 1,
                    "Kilogram": 0.001,
                    "Milligram": 1000
                }
            }

            if category not in conversions:
                return jsonify({"error": "Invalid Category"}), 400

            if from_unit not in conversions[category] or to_unit not in conversions[category]:
                return jsonify({"error": "Invalid Units"}), 400

            result = (value * conversions[category][to_unit]) / conversions[category][from_unit]

            return jsonify({"result": result})

        except Exception as e:
            return jsonify({"error": str(e)}), 500

    return render_template('converter.html')


# -------------------------
# JSON FORMATTER
# -------------------------
@app.route('/json-formatter', methods=['GET', 'POST'])
def json_formatter():
    if request.method == 'POST':
        try:
            input_json = request.form.get('jsonInput', '')

            parsed = json.loads(input_json)
            formatted_json = json.dumps(parsed, indent=4)

            return jsonify({"success": True, "formatted": formatted_json})

        except json.JSONDecodeError:
            return jsonify({"success": False, "error": "Invalid JSON"})

    return render_template('json_formatter.html')


# -------------------------
# TEXT TOOLS
# -------------------------
@app.route('/text-tools', methods=['GET', 'POST'])
def text_tools():
    if request.method == 'POST':
        text = request.form.get('inputText', '')

        response = {
            "uppercase": text.upper(),
            "lowercase": text.lower(),
            "titlecase": text.title(),
            "wordcount": len(text.split())
        }

        return jsonify(response)

    return render_template('text_tools.html')


# -------------------------
# AGE CALCULATOR
# -------------------------
@app.route('/age')
def age():
    return render_template('age.html')


# -------------------------
# BMI CALCULATOR
# -------------------------
@app.route('/bmi')
def bmi():
    return render_template('bmi.html')


# -------------------------
# PASSWORD GENERATOR
# -------------------------
@app.route('/password')
def password():
    return render_template('password.html')


# -------------------------
# QR CODE GENERATOR
# -------------------------
@app.route('/qr')
def qr():
    return render_template('qr.html')


# -------------------------
# RUN APP
# -------------------------
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=81)
