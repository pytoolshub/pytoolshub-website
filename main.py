# main.py
from flask import Flask, render_template, request, jsonify, send_from_directory
import os
import json
import qrcode
import base64
from io import BytesIO
from datetime import datetime
import logging
from flask import flash, redirect, url_for

# ensure data dir exists (run-once at startup)
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
os.makedirs(DATA_DIR, exist_ok=True)
CONTACTS_FILE = os.path.join(DATA_DIR, "contacts.json")

# helper to append contact
def save_contact_record(record):
    try:
        # read existing
        if os.path.exists(CONTACTS_FILE):
            with open(CONTACTS_FILE, "r", encoding="utf-8") as f:
                items = json.load(f)
        else:
            items = []
    except Exception:
        items = []

    items.append(record)
    with open(CONTACTS_FILE, "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)

# About page route
@app.route("/about")
def about_page():
    # pass current_year if base.html uses it
    return render_template("about.html", current_year=datetime.now().year)

# Contact page route (GET + POST)
@app.route("/contact", methods=["GET", "POST"])
def contact_page():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        subject = request.form.get("subject", "").strip()
        message = request.form.get("message", "").strip()

        if not name or not email or not message:
            # minimal validation
            flash("Please fill all required fields.")
            return redirect(url_for("contact_page"))

        record = {
            "name": name,
            "email": email,
            "subject": subject,
            "message": message,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }

        # Save locally
        save_contact_record(record)

        # Optional: send email here (commented) - configure SMTP/env in production
        # try:
        #     send_email_to_admin(subject, f"{name} <{email}>: {message}")
        # except Exception:
        #     app.logger.exception("Failed to send email")

        flash("Thank you — your message was received. We'll get back to you soon.")
        return redirect(url_for("contact_page"))

    # GET
    return render_template("contact.html")


@app.route("/privacy")
def privacy_page():
    return render_template("privacy.html")

app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG)


# ----------------------
# Helper responders
# ----------------------
def json_ok(result):
    return jsonify({"ok": True, "result": result})


def json_err(msg, status=400):
    return jsonify({"ok": False, "error": msg}), status


@app.route("/base64")
def base64_tool():
    return render_template("base64.html")


@app.route('/sitemap.xml')
def sitemap():
    return send_from_directory('.', 'sitemap.xml')


@app.route('/robots.txt')
def robots():
    return send_from_directory('.', 'robots.txt')


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


@app.route("/api/calculate", methods=["POST"])
def api_calculate():
    try:
        data = request.get_json(force=True) or {}

        # Validate num1
        try:
            num1 = float(data.get("num1", 0))
        except (TypeError, ValueError):
            return json_err("Invalid input for num1", 400)

        # Validate num2
        try:
            num2 = float(data.get("num2", 0))
        except (TypeError, ValueError):
            return json_err("Invalid input for num2", 400)

        # Validate operation
        op = (data.get("operation") or "").strip().lower()
        if not op:
            return json_err("Operation not specified", 400)

        # Perform calculation
        if op in ("add", "+"):
            result = num1 + num2
        elif op in ("subtract", "-"):
            result = num1 - num2
        elif op in ("multiply", "*", "times"):
            result = num1 * num2
        elif op in ("divide", "/"):
            if num2 == 0:
                return json_err("Division by zero is not allowed", 400)
            result = num1 / num2
        else:
            return json_err(f"Invalid operation: {op}", 400)

        # Return success JSON
        return jsonify({"ok": True, "result": result})

    except Exception as e:
        app.logger.exception("Calculator API unexpected error")
        return json_err("Internal server error", 500)

# ----------------------
#API: CONVERTER
# ----------------------
@app.route("/api/convert", methods=["POST"])
def api_convert():
    try:
        data = request.get_json(force=True) or {}

        # Helper to accept multiple possible keys from frontend
        def pick(*keys):
            for k in keys:
                if k in data and data[k] is not None:
                    return data[k]
            return None

        # Get value
        raw_value = pick("value", "val", "amount")
        try:
            value = float(raw_value)
        except (TypeError, ValueError):
            return json_err("Invalid or missing 'value' (must be a number)", 400)

        # Accept many forms for unit keys
        frm_raw = pick("from_unit", "fromUnit", "from", "frm")
        to_raw = pick("to_unit", "toUnit", "to", "t")
        category_raw = pick("category", "cat", None)

        frm = (frm_raw or "").strip().lower()
        to = (to_raw or "").strip().lower()
        category = (category_raw or "").strip().lower()

        if not frm or not to:
            return json_err("Missing 'from' or 'to' unit", 400)

        # Unit tables
        length = {
            "meter": 1.0, "m": 1.0,
            "kilometer": 1000.0, "km": 1000.0,
            "centimeter": 0.01, "cm": 0.01,
            "millimeter": 0.001, "mm": 0.001,
            "mile": 1609.34, "mi": 1609.34,
            "yard": 0.9144, "yd": 0.9144,
            "foot": 0.3048, "ft": 0.3048,
            "inch": 0.0254, "in": 0.0254
        }

        weight = {
            "kilogram": 1.0, "kg": 1.0,
            "gram": 0.001, "g": 0.001,
            "milligram": 0.000001, "mg": 0.000001,
            "pound": 0.45359237, "lb": 0.45359237,
            "ounce": 0.028349523125, "oz": 0.028349523125
        }

        temp_units = {"celsius", "c", "fahrenheit", "f", "kelvin", "k"}

        # Try to infer category if not provided
        def infer_category(frm_u, to_u):
            if frm_u in length or to_u in length:
                return "length"
            if frm_u in weight or to_u in weight:
                return "weight"
            if frm_u in temp_units or to_u in temp_units:
                return "temperature"
            return None

        if not category:
            category = infer_category(frm, to)
            if not category:
                return json_err("Could not infer category. Provide 'category' or use supported units.", 400)

        # Conversion logic
        if category == "length":
            if frm not in length or to not in length:
                return json_err("Unsupported length units", 400)
            meters = value * length[frm]
            result = meters / length[to]
            return jsonify({"ok": True, "result": result})

        elif category == "weight":
            if frm not in weight or to not in weight:
                return json_err("Unsupported weight units", 400)
            kgs = value * weight[frm]
            result = kgs / weight[to]
            return jsonify({"ok": True, "result": result})

        elif category == "temperature":
            # normalize names
            def norm(u):
                u = u.lower()
                if u in ("c", "celsius"): return "c"
                if u in ("f", "fahrenheit"): return "f"
                if u in ("k", "kelvin"): return "k"
                return u

            f = norm(frm)
            t = norm(to)

            def to_celsius(x, u):
                if u == "c": return x
                if u == "f": return (x - 32) * 5.0/9.0
                if u == "k": return x - 273.15
                raise ValueError("unknown temp unit")

            def from_celsius(x, u):
                if u == "c": return x
                if u == "f": return (x * 9.0/5.0) + 32
                if u == "k": return x + 273.15
                raise ValueError("unknown temp unit")

            if f not in ("c","f","k") or t not in ("c","f","k"):
                return json_err("Unsupported temperature units", 400)

            c = to_celsius(value, f)
            result = from_celsius(c, t)
            return jsonify({"ok": True, "result": result})

        else:
            return json_err("Invalid category", 400)

    except Exception as e:
        app.logger.exception("Unit Converter API unexpected error")
        return json_err("Internal server error", 500)



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
