"""
Password Checker Module
=======================
Provides reusable password analysis logic for the Password Fault Detector.
Evaluates passwords against five standard security rules independently
and computes a beginner-friendly strength classification.
"""

import string
from typing import Any, Dict, List

# Standard set of special punctuation characters commonly used in passwords
SPECIAL_CHARACTERS: set[str] = set(string.punctuation)


def check_password_strength(password: str) -> Dict[str, Any]:
    """
    Analyzes a password against five core validation requirements.

    Requirements evaluated:
    1. Minimum length: at least 8 characters.
    2. Lowercase letter: at least one [a-z].
    3. Uppercase letter: at least one [A-Z].
    4. Digit: at least one [0-9].
    5. Special character: at least one symbol from string.punctuation.

    Strength Classification:
    - Weak:   0 to 2 requirements satisfied
    - Medium: 3 to 4 requirements satisfied
    - Strong: All 5 requirements satisfied

    Args:
        password: The password string to evaluate.

    Returns:
        A dictionary containing:
        - requirements: list of requirement status objects
        - satisfied_count: integer count of satisfied requirements (0-5)
        - total_requirements: total count of requirements (5)
        - strength: "Weak", "Medium", or "Strong"
        - missing_requirements: list of labels of unsatisfied requirements
        - password_length: length of the input password
    """
    if not isinstance(password, str):
        password = str(password or "")

    # 1. Independent checks for each rule
    has_min_length = len(password) >= 8
    has_lowercase = any(char.islower() for char in password)
    has_uppercase = any(char.isupper() for char in password)
    has_digit = any(char.isdigit() for char in password)
    has_special = any(char in SPECIAL_CHARACTERS for char in password)

    requirements: List[Dict[str, Any]] = [
        {
            "id": "min_length",
            "label": "Minimum 8 characters",
            "met": has_min_length,
            "description": "Must be at least 8 characters in length",
        },
        {
            "id": "lowercase",
            "label": "At least one lowercase letter (a–z)",
            "met": has_lowercase,
            "description": "Must contain at least one lowercase letter",
        },
        {
            "id": "uppercase",
            "label": "At least one uppercase letter (A–Z)",
            "met": has_uppercase,
            "description": "Must contain at least one uppercase letter",
        },
        {
            "id": "digit",
            "label": "At least one number (0–9)",
            "met": has_digit,
            "description": "Must contain at least one numerical digit",
        },
        {
            "id": "special_char",
            "label": "At least one special character (!@#$%...)",
            "met": has_special,
            "description": "Must contain at least one special symbol (e.g., @, #, $, %, !)",
        },
    ]

    # 2. Total requirements satisfied
    satisfied_count = sum(1 for req in requirements if req["met"])
    total_requirements = len(requirements)

    # 3. Simple strength classification:
    #    - Weak: 0-2
    #    - Medium: 3-4
    #    - Strong: 5
    if satisfied_count <= 2:
        strength = "Weak"
    elif satisfied_count <= 4:
        strength = "Medium"
    else:
        strength = "Strong"

    # 4. List of missing requirements for user guidance
    missing_requirements = [req["label"] for req in requirements if not req["met"]]

    return {
        "password_length": len(password),
        "requirements": requirements,
        "satisfied_count": satisfied_count,
        "total_requirements": total_requirements,
        "strength": strength,
        "missing_requirements": missing_requirements,
    }
