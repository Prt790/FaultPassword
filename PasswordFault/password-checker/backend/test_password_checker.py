import os
import sys
import unittest

# Ensure the backend directory is in sys.path regardless of execution working directory
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

from password_checker import check_password_strength
from app import app


class TestPasswordCheckerLogic(unittest.TestCase):
    """Tests the password_checker module logic directly."""

    def test_empty_password(self):
        result = check_password_strength("")
        self.assertEqual(result["password_length"], 0)
        self.assertEqual(result["satisfied_count"], 0)
        self.assertEqual(result["strength"], "Weak")
        self.assertEqual(len(result["missing_requirements"]), 5)
        for req in result["requirements"]:
            self.assertFalse(req["met"])

    def test_prompt_example_hello123(self):
        # "hello123" has length 8, lowercase, numbers, but no uppercase and no special
        result = check_password_strength("hello123")
        req_map = {r["id"]: r["met"] for r in result["requirements"]}

        self.assertTrue(req_map["min_length"], "Minimum length should be satisfied (8 chars)")
        self.assertTrue(req_map["lowercase"], "Lowercase should be satisfied")
        self.assertFalse(req_map["uppercase"], "Uppercase should be missing")
        self.assertTrue(req_map["digit"], "Digit should be satisfied")
        self.assertFalse(req_map["special_char"], "Special symbol should be missing")

        self.assertEqual(result["satisfied_count"], 3)
        self.assertEqual(result["strength"], "Medium")
        self.assertIn("At least one uppercase letter (A–Z)", result["missing_requirements"])
        self.assertIn("At least one special character (!@#$%...)", result["missing_requirements"])

    def test_length_boundary(self):
        # 7 chars vs 8 chars
        res_7 = check_password_strength("Abc!123")
        self.assertFalse(any(r["met"] for r in res_7["requirements"] if r["id"] == "min_length"))

        res_8 = check_password_strength("Abc!1234")
        self.assertTrue(any(r["met"] for r in res_8["requirements"] if r["id"] == "min_length"))

    def test_weak_classifications(self):
        # 0 satisfied: empty
        self.assertEqual(check_password_strength("")["strength"], "Weak")
        # 1 satisfied: only lowercase
        self.assertEqual(check_password_strength("abc")["strength"], "Weak")
        # 2 satisfied: lowercase + digit (length < 8)
        self.assertEqual(check_password_strength("abc1")["strength"], "Weak")

    def test_medium_classifications(self):
        # 3 satisfied: length >= 8 + lower + digit
        self.assertEqual(check_password_strength("short123")["strength"], "Medium")
        # 4 satisfied: length >= 8 + lower + upper + digit (no special)
        self.assertEqual(check_password_strength("Short123")["strength"], "Medium")

    def test_strong_classification(self):
        # All 5 satisfied: length >= 8, lower, upper, digit, special
        result = check_password_strength("P@ssw0rd123!")
        self.assertEqual(result["satisfied_count"], 5)
        self.assertEqual(result["strength"], "Strong")
        self.assertEqual(len(result["missing_requirements"]), 0)
        for req in result["requirements"]:
            self.assertTrue(req["met"])

    def test_various_special_characters(self):
        specials = ["@", "#", "$", "%", "!", "^", "&", "*", "(", ")", "_", "+", "-", "=", "[", "]"]
        for symbol in specials:
            pwd = f"Testing1{symbol}"
            result = check_password_strength(pwd)
            req_map = {r["id"]: r["met"] for r in result["requirements"]}
            self.assertTrue(req_map["special_char"], f"Special character '{symbol}' should be detected")


class TestFlaskEndpoints(unittest.TestCase):
    """Tests the Flask REST API endpoints."""

    def setUp(self):
        self.client = app.test_client()

    def test_index_health_endpoint(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data["status"], "online")

    def test_check_password_success(self):
        response = self.client.post(
            "/check-password",
            json={"password": "SecurePassword#99"}
        )
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn("requirements", data)
        self.assertIn("satisfied_count", data)
        self.assertIn("strength", data)
        self.assertIn("missing_requirements", data)
        self.assertEqual(data["strength"], "Strong")
        self.assertEqual(data["satisfied_count"], 5)

    def test_non_json_request(self):
        response = self.client.post(
            "/check-password",
            data="plain text",
            content_type="text/plain"
        )
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertIn("error", data)

    def test_missing_password_field(self):
        response = self.client.post(
            "/check-password",
            json={"wrong_key": "some_value"}
        )
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertIn("error", data)

    def test_invalid_password_data_type(self):
        response = self.client.post(
            "/check-password",
            json={"password": 12345}
        )
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertIn("error", data)


if __name__ == "__main__":
    unittest.main()
