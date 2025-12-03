# main.py
from flask import Flask, render_template, request, jsonify, send_from_directory
import json
import qrcode
import base64
from io import BytesIO
from datetime import datetime
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG)


# ----------------------
# Helper responders
# ----------------------
def json_ok(result):
    return jsonify({"ok": True, "result": result})


def json_err(msg, status=400):
    return jsonify({"ok": False, "error": msg}), status


# ----------------------
# Pages (render templates you provided)
# ----------------------
@app.route("/")
def home():
    return render_template("home.html")


@app.route("/calculator")
def calculator_page():
    return render_template("calculator.html")


@app.route("/converter")
def converter_page():
    return render_template("converter.html")


@app.route("/json-formatter")
def json_formatter_page():
    return render_template("json_formatter.html")


@app.route("/text-tools")
def text_tools_page():
    return render_template("text_tools.html")


@app.route("/bmi", methods=["GET", "POST"])
def bmi_page():
    bmi_result = None
    if request.method == "POST":
        try:
            weight = float(request.form.get("weight", 0))
            height_cm = float(request.form.get("height", 0))
            height_m = height_cm / 100.0 if height_cm else 0
            if height_m <= 0:
                bmi_result = None
            else:
                bmi_result = round(weight / (height_m * height_m), 2)
        except Exception as e:
            app.logger.exception("BMI error")
            bmi_result = None
    return render_template("bmi.html", bmi=bmi_result)


@app.route("/password")
def password_page():
    return render_template("password.html")


@app.route("/qr", methods=["GET", "POST"])
def qr_page():
    qr_image = None
    if request.method == "POST":
        text = request.form.get("data", "")
        if text:
            img = qrcode.make(text)
            buf = BytesIO()
            img.save(buf, format="PNG")
            buf.seek(0)
            qr_image = base64.b64encode(buf.getvalue()).decode()
    return render_template("qr.html", qr_image=qr_image)


@app.route("/age", methods=["GET", "POST"])
def age_page():
    result = None
    if request.method == "POST":
        dob = request.form.get("dob")
        try:
            dob_dt = datetime.strptime(dob, "%Y-%m-%d")
            today = datetime.today()
            years = today.year - dob_dt.year
            months = today.month - dob_dt.month
            days = today.day - dob_dt.day
            if days < 0:
                months -= 1
                days += 30
            if months < 0:
                years -= 1
                months += 12
            result = {"years": years, "months": months, "days": days}
        except Exception:
            app.logger.exception("Age calculation error")
            result = None
    return render_template("age.html", age=result)


# serve favicon if present
@app.route('/favicon.ico')
def favicon():
    return send_from_directory('static', 'favicon.ico')


# ----------------------
# API: Calculator
# Template calls: POST /api/calculate with { num1, num2, operation }
# operations in template: 'add','subtract','multiply','divide'
# ----------------------
@app.route("/api/calculate", methods=["POST"])
def api_calculate():
    try:
        data = request.get_json(force=True)
        num1 = float(data.get("num1", 0))
        num2 = float(data.get("num2", 0))
        op = (data.get("operation") or "").lower()

        if op in ("add", "+"):
            result = num1 + num2
        elif op in ("subtract", "-"):
            result = num1 - num2
        elif op in ("multiply", "*", "times"):
            result = num1 * num2
        elif op in ("divide", "/"):
            if num2 == 0:
                return json_err("Division by zero", 400)
            result = num1 / num2
        else:
            return json_err("Invalid operation", 400)

        return jsonify({"result": result})
    except Exception as e:
        app.logger.exception("Calculator API error")
        return json_err(str(e), 500)


# ----------------------
# API: Converter
# Template posts to /api/convert with { value, category, from_unit, to_unit }
# ----------------------
@app.route("/api/convert", methods=["POST"])
def api_convert():
    try:
        data = request.get_json(force=True)
        value = float(data.get("value", 0))
        category = (data.get("category") or "length").lower()
        frm = (data.get("from_unit") or "").lower()
        to = (data.get("to_unit") or "").lower()

        # length: base meters
        length = {
            "meter": 1.0, "m": 1.0,
            "kilometer": 1000.0, "km": 1000.0,
            "centimeter": 0.01, "cm": 0.01,
            "millimeter": 0.001, "mm": 0.001,
            "mile": 1609.34, "yard": 0.9144, "foot": 0.3048, "inch": 0.0254
        }
        # weight: base kg
        weight = {
            "kilogram": 1.0, "kg": 1.0,
            "gram": 0.001, "g": 0.001,
            "milligram": 0.000001, "mg": 0.000001,
            "pound": 0.453592, "lb": 0.453592,
            "ounce": 0.0283495, "oz": 0.0283495
        }

        if category == "length":
            if frm not in length or to not in length:
                return json_err("Unsupported length units", 400)
            meters = value * length[frm]
            result = meters / length[to]

        elif category == "weight":
            if frm not in weight or to not in weight:
                return json_err("Unsupported weight units", 400)
            kgs = value * weight[frm]
            result = kgs / weight[to]

        elif category == "temperature":
            # handle temperature conversions
            v = value
            if frm == to:
                result = v
            else:
                # convert from -> celsius -> to
                def to_celsius(x, u):
                    if u in ("celsius", "c"):
                        return x
                    if u in ("fahrenheit", "f"):
                        return (x - 32) * 5.0/9.0
                    if u in ("kelvin", "k"):
                        return x - 273.15
                    raise ValueError("unknown temp unit")

                def from_celsius(x, u):
                    if u in ("celsius", "c"):
                        return x
                    if u in ("fahrenheit", "f"):
                        return (x * 9.0/5.0) + 32
                    if u in ("kelvin", "k"):
                        return x + 273.15
                    raise ValueError("unknown temp unit")

                c = to_celsius(v, frm)
                result = from_celsius(c, to)
        else:
            return json_err("Invalid category", 400)

        return jsonify({"result": result})
    except Exception as e:
        app.logger.exception("Convert API error")
        return json_err(str(e), 500)


# ----------------------
# API: JSON Formatter
# Template posts to /api/format-json with { json_string, indent }
# Returns { formatted }
# ----------------------
@app.route("/api/format-json", methods=["POST"])
def api_format_json():
    try:
        data = request.get_json(force=True)
        json_string = data.get("json_string", "")
        indent = int(data.get("indent", 2))
        parsed = json.loads(json_string)
        pretty = json.dumps(parsed, indent=indent, ensure_ascii=False)
        return jsonify({"formatted": pretty})
    except json.JSONDecodeError as e:
        app.logger.exception("JSON parse error")
        return json_err(f"JSON parse error: {str(e)}", 400)
    except Exception as e:
        app.logger.exception("JSON formatter error")
        return json_err(str(e), 500)


# ----------------------
# API: Text Tools
# Template posts to /api/text-process with { text, operation }
# For 'count' operation we return stats as well
# ----------------------
@app.route("/api/text-process", methods=["POST"])
def api_text_process():
    try:
        data = request.get_json(force=True)
        text = data.get("text", "") or ""
        op = (data.get("operation") or "").lower()

        if op == "uppercase":
            return jsonify({"result": text.upper()})
        if op == "lowercase":
            return jsonify({"result": text.lower()})
        if op == "titlecase":
            return jsonify({"result": text.title()})
        if op == "reverse":
            return jsonify({"result": text[::-1]})
        if op == "trim":
            return jsonify({"result": text.strip()})
        if op == "remove_extra_spaces":
            import re
            res = re.sub(r'\s+', ' ', text).strip()
            return jsonify({"result": res})
        if op == "count":
            words = len([w for w in text.split() if w])
            chars = len(text)
            chars_no_space = len(text.replace(" ", ""))
            lines = text.count("\n") + 1 if text else 0
            stats = {
                "words": words,
                "characters": chars,
                "characters_no_space": chars_no_space,
                "lines": lines
            }
            return jsonify({"result": text, "stats": stats})

        return json_err("Invalid operation", 400)

    except Exception as e:
        app.logger.exception("Text tools error")
        return json_err(str(e), 500)


# ----------------------
# Error pages (for browser clients)
# ----------------------
@app.errorhandler(404)
def page_not_found(e):
    # if api path, return JSON
    if request.path.startswith("/api/"):
        return json_err("Not found", 404)
    return render_template("404.html"), 404


@app.errorhandler(500)
def server_error(e):
    app.logger.exception("Unhandled server error")
    if request.path.startswith("/api/"):
        return json_err("Internal server error", 500)
    return render_template("500.html"), 500


# ----------------------
# Run
# ----------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=81, debug=True)
