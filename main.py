# main.py

import os
from flask import Flask, render_template, request, jsonify, send_from_directory, flash, redirect, url_for
import json
import qrcode
import base64
from io import BytesIO
from datetime import datetime
import logging

app = Flask(__name__)

@app.route('/static/<path:filename>')
def staticfiles(filename):
    return send_from_directory('static', filename)



app.secret_key = "supersecret"  # required for flash messages
logging.basicConfig(level=logging.DEBUG)

# ----------------------
# Helper year function
# ----------------------
def year():
    return datetime.now().year

# ----------------------
# Data Directory for Contact Form
# ----------------------
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
    except Exception:
        items = []

    items.append(record)
    with open(CONTACTS_FILE, "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)

# ----------------------
# Routes
# ----------------------

@app.route("/")
def home():
    return render_template("index.html", current_year=year())

@app.route("/calculator")
def calculator():
    return render_template("calculator.html", current_year=year())

@app.route("/converter")
def converter():
    return render_template("converter.html", current_year=year())

@app.route("/json-formatter")
def json_formatter():
    return render_template("json_formatter.html", current_year=year())

@app.route("/text-tools")
def text_tools():
    return render_template("text_tools.html", current_year=year())

@app.route("/bmi-calculator")
def bmi_calc():
    return render_template("bmi.html", current_year=year())

@app.route("/qr-code")
def qr_code():
    return render_template("qr.html", current_year=year())

@app.route("/base64")
def base64_page():
    return render_template("base64.html", current_year=year())

@app.route("/age-calculator")
def age_calculator():
    return render_template("age.html", current_year=year())

# ----------------------
# About Page
# ----------------------
@app.route("/about")
def about_page():
    return render_template("about.html", current_year=year())

# ----------------------
# Privacy Page
# ----------------------
@app.route("/privacy")
def privacy_page():
    return render_template("privacy.html", current_year=year())

# ----------------------
# Contact Page (GET + POST)
# ----------------------
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

    return render_template("contact.html", current_year=year())

# ----------------------
# Sitemap
# ----------------------
@app.route("/sitemap.xml")
def sitemap():
    return send_from_directory(".", "sitemap.xml")

# ----------------------
# QR Generator API
# ----------------------
@app.route("/api/qr", methods=["POST"])
def api_qr():
    text = request.json.get("text", "")
    if not text:
        return jsonify({"ok": False, "error": "No text"}), 400

    img = qrcode.make(text)
    buf = BytesIO()
    img.save(buf, format="PNG")
    b64 = base64.b64encode(buf.getvalue()).decode("utf-8")

    return jsonify({"ok": True, "image": "data:image/png;base64," + b64})

# ----------------------
# Run App
# ----------------------
if __name__ == "__main__":
    app.run(debug=True)
