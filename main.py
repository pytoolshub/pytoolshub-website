# main.py
from flask import Flask, render_template, request, jsonify, send_from_directory
import random
import qrcode
import base64
from io import BytesIO
from datetime import datetime
import json
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)


# ---------- Helper utilities ----------
def json_response(ok: bool, result=None, error: str = None, status: int = 200):
    payload = {"ok": ok}
    if ok:
        payload["result"] = result
    else:
        payload["error"] = error
    return jsonify(payload), status


def safe_get_json():
    """
    Return parsed JSON from request, whether request.json or body JSON string.
    Returns: dict or None
    """
    data = None
    if request.is_json:
        data = request.get_json(silent=True)
    else:
        # maybe the client sent application/x-www-form-urlencoded or text/json
        try:
            raw = request.get_data(as_text=True)
            if raw:
                data = json.loads(raw)
        except Exception:
            data = None
    return data or {}


# ---------- Frontend pages ----------
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


@app.route("/bmi")
def bmi_page():
    return render_template("bmi.html")


@app.route("/password")
def password_page():
    return render_template("password.html")


@app.route("/qr")
def qr_page():
    return render_template("qr.html")


@app.route("/age")
def age_page():
    return render_template("age.html")


# ---------- Utility assets (favicon if any) ----------
@app.route('/favicon.ico')
def favicon():
    return send_from_directory('static', 'favicon.ico')


# ---------- API endpoints ----------

# Calculator API: expects JSON { "a": <num>, "b": <num>, "op": "+|-|*|/" }
@app.route("/api/calc", methods=["POST"])
def api_calc():
    try:
        data = safe_get_json()
        a = float(data.get("a", 0))
        b = float(data.get("b", 0))
        op = data.get("op", "+")
    except Exception as e:
        return json_response(False, error=f"Invalid input: {str(e)}", status=400)

    try:
        if op == "+":
            result = a + b
        elif op == "-":
            result = a - b
        elif op == "*":
            result = a * b
        elif op == "/":
            if b == 0:
                return json_response(False, error="Division by zero", status=400)
            result = a / b
        else:
            return json_response(False, error="Invalid operation", status=400)

        # return numeric result (float or int)
        return json_response(True, result=result)
    except Exception as e:
        logging.exception("Calculator error")
        return json_response(False, error=str(e), status=500)


# Converter API: supports length units (meter, kilometer, centimeter, millimeter)
@app.route("/api/convert", methods=["POST"])
def api_convert():
    try:
        data = safe_get_json()
        value = float(data.get("value", 0))
        from_unit = (data.get("from") or "").lower()
        to_unit = (data.get("to") or "").lower()
    except Exception as e:
        return json_response(False, error=f"Invalid input: {str(e)}", status=400)

    length_units = {
        "meter": 1.0,
        "m": 1.0,
        "kilometer": 1000.0,
        "km": 1000.0,
        "centimeter": 0.01,
        "cm": 0.01,
        "millimeter": 0.001,
        "mm": 0.001,
    }

    try:
        if from_unit in length_units and to_unit in length_units:
            # convert value to meters then to target
            meters = value * length_units[from_unit]
            result = meters / length_units[to_unit]
            return json_response(True, result=result)
        else:
            return json_response(False, error="Unsupported units", status=400)
    except Exception as e:
        logging.exception("Converter error")
        return json_response(False, error=str(e), status=500)


# JSON Formatter API: expects { "data": "<json string>" } or raw JSON in body
@app.route("/api/format_json", methods=["POST"])
def api_format_json():
    try:
        data = safe_get_json()
        # Accept either {"data": "<string>"} or direct body JSON to be prettified
        raw = data.get("data")
        if raw is None:
            # maybe the client posted text directly; try raw body
            raw = request.get_data(as_text=True) or ""
        parsed = json.loads(raw)
        pretty = json.dumps(parsed, indent=4, ensure_ascii=False)
        return json_response(True, result=pretty)
    except json.JSONDecodeError as e:
        return json_response(False, error=f"JSON parse error: {str(e)}", status=400)
    except Exception as e:
        logging.exception("JSON formatter error")
        return json_response(False, error=str(e), status=500)


# Text Tools API: expects { "text": "...", "action": "upper|lower|title|trim" }
@app.route("/api/text", methods=["POST"])
def api_text_tools():
    try:
        data = safe_get_json()
        text = data.get("text", "")
        action = (data.get("action") or "").lower()
    except Exception as e:
        return json_response(False, error=f"Invalid input: {str(e)}", status=400)

    try:
        if action == "upper":
            return json_response(True, result=text.upper())
        elif action == "lower":
            return json_response(True, result=text.lower())
        elif action == "title":
            return json_response(True, result=text.title())
        elif action == "trim":
            return json_response(True, result=text.strip())
        else:
            return json_response(False, error="Invalid action", status=400)
    except Exception as e:
        logging.exception("Text tools error")
        return json_response(False, error=str(e), status=500)


# QR generator (page above) — keep server-side PNG -> base64 if used via POST form
@app.route("/api/qr", methods=["POST"])
def api_qr():
    try:
        data = safe_get_json()
        text = data.get("data") or data.get("text") or ""
        if not text:
            return json_response(False, error="No input text provided", status=400)

        img = qrcode.make(text)
        buf = BytesIO()
        img.save(buf, format="PNG")
        buf.seek(0)
        b64 = base64.b64encode(buf.getvalue()).decode()
        return json_response(True, result=b64)
    except Exception as e:
        logging.exception("QR error")
        return json_response(False, error=str(e), status=500)


# Age calculator endpoint (optionally used via API)
@app.route("/api/age", methods=["POST"])
def api_age():
    try:
        data = safe_get_json()
        dob = data.get("dob")
        if not dob:
            return json_response(False, error="dob required (YYYY-MM-DD)", status=400)
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
        return json_response(True, result={"years": years, "months": months, "days": days})
    except Exception as e:
        logging.exception("Age calc error")
        return json_response(False, error=str(e), status=500)


# ---------- Error handlers ----------
@app.errorhandler(404)
def not_found(e):
    # If an API route was requested, return JSON; otherwise show HTML 404 page
    if request.path.startswith("/api/"):
        return json_response(False, error="Not found", status=404)
    return render_template("404.html"), 404


@app.errorhandler(500)
def internal_error(e):
    logging.exception("Internal server error")
    if request.path.startswith("/api/"):
        return json_response(False, error="Internal server error", status=500)
    return render_template("500.html"), 500


# ---------- Run ----------
if __name__ == "__main__":
    # debug=True while developing; turn off in production
    app.run(host="0.0.0.0", port=81, debug=True)
