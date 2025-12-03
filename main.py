from flask import Flask, render_template, request, jsonify
import json
import datetime
import qrcode
import io
import base64

app = Flask(__name__)

# ==========================
# ROUTE: HOME
# ==========================
@app.route('/')
def home():
    return render_template('index.html')


# ==========================
# ROUTE: CALCULATOR PAGE
# ==========================
@app.route('/calculator')
def calculator():
    return render_template('calculator.html')


# API for calculator
@app.route('/api/calculate', methods=['POST'])
def api_calculate():
    try:
        data = request.get_json()
        a = float(data.get("a", 0))
        b = float(data.get("b", 0))
        op = data.get("operator")

        if op == '+':
            result = a + b
        elif op == '-':
            result = a - b
        elif op == '*':
            result = a * b
        elif op == '/':
            if b == 0:
                return jsonify({"error": "Cannot divide by zero"}), 400
            result = a / b
        else:
            return jsonify({"error": "Invalid operator"}), 400

        return jsonify({"result": result})

    except Exception as e:
        return jsonify({"error": str(e)}), 400


# ==========================
# ROUTE: UNIT CONVERTER PAGE
# ==========================
@app.route('/converter')
def converter():
    return render_template('converter.html')


# API for unit converter
@app.route('/api/convert', methods=['POST'])
def api_convert():
    try:
        data = request.get_json()
        value = float(data.get("value"))
        category = data.get("category")
        from_unit = data.get("from_unit")
        to_unit = data.get("to_unit")

        # LENGTH CONVERSIONS (meters base)
        length_units = {
            "meter": 1,
            "kilometer": 1000,
            "centimeter": 0.01,
            "millimeter": 0.001,
            "mile": 1609.34,
            "yard": 0.9144,
            "foot": 0.3048,
            "inch": 0.0254
        }

        # WEIGHT (kg base)
        weight_units = {
            "kilogram": 1,
            "gram": 0.001,
            "milligram": 0.000001,
            "pound": 0.453592,
            "ounce": 0.0283495
        }

        if category == "length":
            result = value * (length_units[from_unit] / length_units[to_unit])

        elif category == "weight":
            result = value * (weight_units[from_unit] / weight_units[to_unit])

        elif category == "temperature":
            if from_unit == "celsius":
                if to_unit == "fahrenheit":
                    result = (value * 9/5) + 32
                elif to_unit == "kelvin":
                    result = value + 273.15
                else:
                    result = value

            elif from_unit == "fahrenheit":
                if to_unit == "celsius":
                    result = (value - 32) * 5/9
                elif to_unit == "kelvin":
                    result = (value - 32) * 5/9 + 273.15
                else:
                    result = value

            elif from_unit == "kelvin":
                if to_unit == "celsius":
                    result = value - 273.15
                elif to_unit == "fahrenheit":
                    result = (value - 273.15) * 9/5 + 32
                else:
                    result = value

            else:
                return jsonify({"error": "Invalid temperature conversion"}), 400
        else:
            return jsonify({"error": "Invalid category"}), 400

        return jsonify({"result": result})

    except Exception as e:
        return jsonify({"error": str(e)}), 400


# ==========================
# ROUTE: JSON FORMATTER PAGE
# ==========================
@app.route('/json-formatter')
def json_formatter():
    return render_template('json_formatter.html')


# API: Format JSON
@app.route('/api/format-json', methods=['POST'])
def api_format_json():
    try:
        data = request.get_json()
        json_string = data.get("json_string")
        indent = int(data.get("indent", 2))

        parsed = json.loads(json_string)
        formatted = json.dumps(parsed, indent=indent)

        return jsonify({"formatted": formatted})

    except Exception as e:
        return jsonify({"error": str(e)}), 400


# ==========================
# ROUTE: TEXT TOOLS PAGE
# ==========================
@app.route('/text-tools')
def text_tools():
    return render_template('text_tools.html')


# API: Text Tools
@app.route('/api/text-tools', methods=['POST'])
def api_text_tools():
    try:
        data = request.get_json()
        text = data.get("text", "")
        action = data.get("action")

        if action == "uppercase":
            result = text.upper()
        elif action == "lowercase":
            result = text.lower()
        elif action == "titlecase":
            result = text.title()
        elif action == "reverse":
            result = text[::-1]
        else:
            return jsonify({"error": "Invalid action"}), 400

        return jsonify({"result": result})

    except Exception as e:
        return jsonify({"error": str(e)}), 400


# ==========================
# ROUTE: BMI PAGE
# ==========================
@app.route('/bmi', methods=['GET', 'POST'])
def bmi():
    bmi_value = None
    if request.method == "POST":
        weight = float(request.form.get("weight"))
        height = float(request.form.get("height")) / 100  # Convert cm to m
        bmi_value = round(weight / (height * height), 2)

    return render_template('bmi.html', bmi=bmi_value)


# ==========================
# PASSWORD GENERATOR
# ==========================
@app.route('/password-generator')
def password_generator():
    return render_template('password.html')


# ==========================
# QR CODE GENERATOR
# ==========================
@app.route('/qr-code')
def qr_code():
    return render_template('qr.html')


# ==========================
# AGE CALCULATOR
# ==========================
@app.route('/age-calculator')
def age_calculator():
    return render_template('age.html')


# ==========================
# RUN APP
# ==========================
if __name__ == "__main__":
    app.run(debug=True)
