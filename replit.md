# PyToolsHub.in

## Overview
PyToolsHub.in is a Python Flask-based web application that provides a collection of useful utility tools. The application features a clean, responsive design and multiple tools for everyday tasks.

## Project Structure
```
.
├── app.py                 # Main Flask application with routes and API endpoints
├── templates/             # HTML templates
│   ├── base.html         # Base template with navigation and footer
│   ├── home.html         # Landing page with tool showcase
│   ├── calculator.html   # Calculator tool page
│   ├── converter.html    # Unit converter tool page
│   ├── json_formatter.html # JSON formatter tool page
│   └── text_tools.html   # Text tools page
├── static/
│   └── css/
│       └── style.css     # Custom styling
└── .gitignore            # Git ignore file
```

## Features Implemented
1. **Calculator** - Basic arithmetic operations (add, subtract, multiply, divide)
2. **Unit Converter** - Convert between units of length, weight, and temperature
3. **JSON Formatter** - Format, validate, and beautify JSON with syntax highlighting
4. **Text Tools** - Word counter, case converter, text reversal, and whitespace tools

## Technology Stack
- Backend: Python 3.11, Flask, Flask-CORS
- Frontend: Bootstrap 5, Bootstrap Icons, Vanilla JavaScript
- Responsive design with mobile support

## Architecture
- Flask serves HTML templates and provides REST API endpoints
- All processing happens server-side with JSON responses
- Client-side JavaScript handles form submissions and displays results
- Bootstrap 5 provides responsive UI components

## Recent Changes
- Initial project setup (November 17, 2024)
- Created Flask application with 4 main tools
- Implemented responsive design with Bootstrap 5
- Added API endpoints for all tool operations
