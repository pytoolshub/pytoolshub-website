from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import json
import os

app = Flask(__name__)
app.secret_key = os.environ.get('SESSION_SECRET', 'dev-secret-key')
CORS(app)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/calculator')
def calculator():
    return render_template('calculator.html')

@app.route('/api/calculate', methods=['POST'])
def calculate():
    try:
        data = request.get_json()
        num1 = float(data.get('num1', 0))
        num2 = float(data.get('num2', 0))
        operation = data.get('operation')
        
        result = None
        if operation == 'add':
            result = num1 + num2
        elif operation == 'subtract':
            result = num1 - num2
        elif operation == 'multiply':
            result = num1 * num2
        elif operation == 'divide':
            if num2 == 0:
                return jsonify({'error': 'Cannot divide by zero'}), 400
            result = num1 / num2
        else:
            return jsonify({'error': 'Invalid operation'}), 400
            
        return jsonify({'result': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/converter')
def converter():
    return render_template('converter.html')

@app.route('/api/convert', methods=['POST'])
def convert():
    try:
        data = request.get_json()
        value = float(data.get('value', 0))
        from_unit = data.get('from_unit')
        to_unit = data.get('to_unit')
        category = data.get('category')
        
        conversions = {
            'length': {
                'meter': 1,
                'kilometer': 1000,
                'centimeter': 0.01,
                'millimeter': 0.001,
                'mile': 1609.34,
                'yard': 0.9144,
                'foot': 0.3048,
                'inch': 0.0254
            },
            'weight': {
                'kilogram': 1,
                'gram': 0.001,
                'milligram': 0.000001,
                'pound': 0.453592,
                'ounce': 0.0283495
            },
            'temperature': {
                'celsius': lambda v, to: v if to == 'celsius' else (v * 9/5 + 32 if to == 'fahrenheit' else v + 273.15),
                'fahrenheit': lambda v, to: (v - 32) * 5/9 if to == 'celsius' else (v if to == 'fahrenheit' else (v - 32) * 5/9 + 273.15),
                'kelvin': lambda v, to: v - 273.15 if to == 'celsius' else ((v - 273.15) * 9/5 + 32 if to == 'fahrenheit' else v)
            }
        }
        
        if category == 'temperature':
            result = conversions[category][from_unit](value, to_unit)
        else:
            base_value = value * conversions[category][from_unit]
            result = base_value / conversions[category][to_unit]
            
        return jsonify({'result': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/json-formatter')
def json_formatter():
    return render_template('json_formatter.html')

@app.route('/api/format-json', methods=['POST'])
def format_json():
    try:
        data = request.get_json()
        json_string = data.get('json_string', '')
        indent = int(data.get('indent', 2))
        
        parsed = json.loads(json_string)
        formatted = json.dumps(parsed, indent=indent, sort_keys=False)
        
        return jsonify({
            'formatted': formatted,
            'valid': True
        })
    except json.JSONDecodeError as e:
        return jsonify({
            'error': f'Invalid JSON: {str(e)}',
            'valid': False
        }), 400
    except Exception as e:
        return jsonify({
            'error': str(e),
            'valid': False
        }), 400

@app.route('/text-tools')
def text_tools():
    return render_template('text_tools.html')

@app.route('/api/text-process', methods=['POST'])
def text_process():
    try:
        data = request.get_json()
        text = data.get('text', '')
        operation = data.get('operation')
        
        result = ''
        stats = {}
        
        if operation == 'count':
            words = len(text.split())
            chars = len(text)
            chars_no_space = len(text.replace(' ', ''))
            lines = len(text.splitlines())
            stats = {
                'words': words,
                'characters': chars,
                'characters_no_space': chars_no_space,
                'lines': lines
            }
            result = text
        elif operation == 'uppercase':
            result = text.upper()
        elif operation == 'lowercase':
            result = text.lower()
        elif operation == 'titlecase':
            result = text.title()
        elif operation == 'reverse':
            result = text[::-1]
        elif operation == 'trim':
            result = text.strip()
        elif operation == 'remove_extra_spaces':
            result = ' '.join(text.split())
        else:
            return jsonify({'error': 'Invalid operation'}), 400
            
        return jsonify({
            'result': result,
            'stats': stats
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
