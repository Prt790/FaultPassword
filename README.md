# Password Fault Detector — Password Strength Checker

A full-stack, beginner-friendly web application that analyzes passwords in real-time and pinpoints **exactly which requirements are missing**. Rather than failing silently, the application provides clear visual feedback to help users understand how to construct stronger passwords.

---

## 📸 Example Behavior

When a user types `hello123`:
* ✅ **Minimum length requirement satisfied** (8 characters)
* ✅ **Lowercase letter present** (`h`, `e`, `l`, `o`)
* ❌ **Uppercase letter missing**
* ✅ **Number present** (`1`, `2`, `3`)
* ❌ **Special symbol missing**

**Classification**: `Medium` (3 of 5 rules satisfied).

---

## 🗂️ Project Structure

```text
password-checker/
├── frontend/
│   ├── index.html            # Clean, accessible user interface
│   ├── style.css             # Modern responsive styling & animations
│   └── script.js             # Vanilla JS: debounced API client & state manager
├── backend/
│   ├── app.py                # Flask REST API server with CORS
│   ├── password_checker.py   # Reusable independent validation logic
│   ├── requirements.txt      # Python dependencies
│   └── test_password_checker.py # Automated unit and endpoint test suite
├── .gitignore                # Git exclusions
└── README.md                 # Complete documentation
```

---

## ⚙️ Technology Stack

* **Frontend**: HTML5, CSS3, Vanilla JavaScript (zero external UI frameworks).
* **Backend**: Python 3.8+, Flask, Flask-CORS.
* **Testing**: Python `unittest`.

---

## 🔒 Password Validation Rules

The backend evaluates **all 5 requirements independently** and returns complete results rather than short-circuiting at the first failure:

| # | Requirement | Rule |
|---|-------------|------|
| 1 | **Minimum Length** | At least 8 characters in length |
| 2 | **Lowercase Letter** | At least one lowercase letter (`a–z`) |
| 3 | **Uppercase Letter** | At least one uppercase letter (`A–Z`) |
| 4 | **Numerical Digit** | At least one digit (`0–9`) |
| 5 | **Special Symbol** | At least one symbol (`@`, `#`, `$`, `%`, `!`, `&`, `*`, etc.) |

### Strength Classification

* **Weak**: 0–2 requirements satisfied
* **Medium**: 3–4 requirements satisfied
* **Strong**: All 5 requirements satisfied

> [!NOTE]
> **Educational Disclaimer**: This application calculates a basic structural strength indicator based on character sets and length. It is designed for educational purposes and does not represent a complete security assessment. Production password security must also evaluate dictionary word resistance, common password lists, breach database checks (e.g., HaveIBeenPwned), and true Shannon entropy.

> [!IMPORTANT]
> **Privacy & Zero-Logging Policy**: The backend will **never** print, log, or persist user passwords to the terminal or log files.

---

## 🚀 Getting Started

### 1. Prerequisites
* **Python 3.8+** installed ([python.org](https://www.python.org/))
* A modern web browser (Chrome, Firefox, Safari, Edge)

### 2. Backend Setup
1. Open a terminal in the project directory:
   ```bash
   cd backend
   ```
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Start the Flask development server:
   ```bash
   python app.py
   ```
   The backend server will start on `http://127.0.0.1:5000`.

### 3. Frontend Setup
You can run the frontend in any of the following ways:
* **Option A (Direct)**: Double-click or open `frontend/index.html` directly in your browser.
* **Option B (VS Code Live Server)**: Right-click `frontend/index.html` in VS Code and click *Open with Live Server*.
* **Option C (Local HTTP Server)**:
  ```bash
  cd frontend
  python -m http.server 3000
  ```
  Then navigate to `http://127.0.0.1:3000` in your web browser.

---

## 📡 API Reference

### `POST /check-password`
Analyzes a submitted password and returns the evaluation of all five rules.

#### Request Headers
```http
Content-Type: application/json
```

#### Request Body
```json
{
  "password": "hello123"
}
```

#### Response (`200 OK`)
```json
{
  "password_length": 8,
  "satisfied_count": 3,
  "total_requirements": 5,
  "strength": "Medium",
  "missing_requirements": [
    "At least one uppercase letter (A–Z)",
    "At least one special character (!@#$%...)"
  ],
  "requirements": [
    {
      "id": "min_length",
      "label": "Minimum 8 characters",
      "description": "Must be at least 8 characters in length",
      "met": true
    },
    {
      "id": "lowercase",
      "label": "At least one lowercase letter (a–z)",
      "description": "Must contain at least one lowercase letter",
      "met": true
    },
    {
      "id": "uppercase",
      "label": "At least one uppercase letter (A–Z)",
      "description": "Must contain at least one uppercase letter",
      "met": false
    },
    {
      "id": "digit",
      "label": "At least one number (0–9)",
      "description": "Must contain at least one numerical digit",
      "met": true
    },
    {
      "id": "special_char",
      "label": "At least one special character (!@#$%...)",
      "description": "Must contain at least one special symbol (e.g., @, #, $, %, !)",
      "met": false
    }
  ]
}
```

#### Error Handling (`400 Bad Request`)
If the request is not JSON or does not provide a string for `password`:
```json
{
  "error": "Missing 'password' field in JSON request."
}
```

---

## 🧪 Running Automated Tests

Run the test suite using Python's built-in `unittest` runner:

```bash
python -m unittest discover -s backend
```

Or run the test file directly:
```bash
python backend/test_password_checker.py
```

The test suite covers:
- Boundary checks (7 vs 8 characters)
- Individual character classes (lowercase, uppercase, digit, special characters)
- Score thresholds (Weak, Medium, Strong)
- Missing requirements output accuracy
- Flask endpoint status codes and error validation

---

## 💡 Frontend Features

* **Real-Time Dynamic Analysis**: Evaluates requirements seamlessly as the user types.
* **Show/Hide Password Button**: Toggle plain text visibility with accessible SVG icons.
* **Segmented Strength Meter**: Smoothly animates and shifts color (Red $\rightarrow$ Amber $\rightarrow$ Green).
* **Live Fault Checklist**: Each item displays an active status icon (`✓` or `✕`) and changes background and border color.
* **Resilient Offline Fallback**: If the Flask server is stopped, the interface automatically detects the disconnection, displays a helpful banner, and uses an internal client fallback so the user experience is never blocked.
