# main.py
from flask import Flask, render_template, request, jsonify, send_from_directory, flash, redirect, url_for
import os
import json
import qrcode
import base64
from io import BytesIO
from datetime import datetime
import logging

# --------------------------------------------------
# Create Flask App FIRST (IMPORTANT)
# --------------------------------------------------
app = Flask(__name__)
app.secret_key = "supersecretkey"  # Required for flash()
logging.basicConfig(level=logging.DEBUG)

# --------------------------------------------------
# Inject current year globally
# --------------------------------------------------
@app.context_processor
def inject_year():
    return {"current_year": datetime.now().year}


# --------------------------------------------------
# CONTACT FORM STORAGE
# --------------------------------------------------
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
os.makedirs(DATA_DIR, exist_ok=True)
CONTACTS_FILE = os.path.join(DATA_DIR, "contacts.json")


def save_contact_record(record):
    try:
        if os.path.exists(CONTACTS_FILE):
            with open(CONTACTS_FILE, "r", encoding="utf-8") as f:
                items = json.load(f)
        else:
            items = []
    except:
        items = []

    items.append(record)
    with open(CONTACTS_FILE, "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)


# --------------------------------------------------
# STATIC PAGES
# --------------------------------------------------
@app.route("/about")
def about_page():
    return render_template("about.html")


@app.route("/contact", methods=["GET", "POST"])
def contact_page():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        subject = request.form.get("subject", "").strip()
        message = request.form.get("message", "").strip()

        if not name or not email or not message:
            flash("Please fill all required fields.")
            return redirect(url_for("contact_page"))

        record = {
            "name": name,
            "email": email,
            "subject": subject,
            "message": message,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }

        save_contact_record(record)
        flash("Thank you — your message was received!")
        return redirect(url_for("contact_page"))

    return render_template("contact.html")


@app.route("/privacy")
def privacy_page():
    return render_template("privacy.html")


# --------------------------------------------------
# BASIC ROUTES
# --------------------------------------------------
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
            height_m = height_cm / 100
            if height_m > 0:
                bmi_result = round(weight / (height_m**2), 2)
        except:
            bmi_result = None
    return render_template("bmi.html", bmi=bmi_result)


@app.route("/password")
def password_page():
    return render_template("password.html")


@app.route("/qr", methods=["GET", "POST"])
def qr_page():
    qr_image = None
    if request.method == "POST":
        text = request.form.get("data")
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
        except:
            result = None

    return render_template("age.html", age=result)


# --------------------------------------------------
# FAVICON
# --------------------------------------------------
@app.route('/favicon.ico')
def favicon():
    return send_from_directory('static', 'favicon.ico')


# --------------------------------------------------
# SITEMAP + ROBOTS
# --------------------------------------------------
@app.route('/sitemap.xml')
def sitemap():
    return send_from_directory('.', 'sitemap.xml')


@app.route('/robots.txt')
def robots():
    return send_from_directory('.', 'robots.txt')


# --------------------------------------------------
# API ENDPOINTS (Calculator, Converter, JSON, Text)
# --------------------------------------------------
@app.route("/api/calculate", methods=["POST"])
def api_calculate():
    try:
        data = request.get_json(force=True)

        num1 = float(data.get("num1"))
        num2 = float(data.get("num2"))
        op = data.get("operation", "").lower()

        if op in ("add", "+"):
            result = num1 + num2
        elif op in ("subtract", "-"):
            result = num1 - num2
        elif op in ("multiply", "*"):
            result = num1 * num2
        elif op in ("divide", "/"):
            if num2 == 0:
                return json_err("Division by zero not allowed")
            result = num1 / num2
        else:
            return json_err("Invalid operation")

        return json_ok(result)

    except:
        return json_err("Invalid input", 400)


# JSON OK + Error Helpers
def json_ok(result):
    return jsonify({"ok": True, "result": result})


def json_err(msg, status=400):
    return jsonify({"ok": False, "error": msg}), status


# --------------------------------------------------
# Error Pages
# --------------------------------------------------
@app.errorhandler(404)
def page_not_found(e):
    if request.path.startswith("/api"):
        return json_err("Not found", 404)
    return render_template("404.html"), 404


@app.errorhandler(500)
def server_error(e):
    if request.path.startswith("/api"):
        return json_err("Server error", 500)
    return render_template("500.html"), 500


# --------------------------------------------------
# RUN APP
# --------------------------------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=81, debug=True)
