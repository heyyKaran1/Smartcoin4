import re
from flask import jsonify

class Validator:
    @staticmethod
    def validate_address(address):
        if not address or not isinstance(address, str):
            return False, "Address must be a non-empty string"

        if len(address) != 40:
            return False, "Address must be 40 characters"

        if not re.match(r'^[a-f0-9]{40}$', address):
            return False, "Address must contain only hexadecimal characters"

        return True, None

    @staticmethod
    def validate_amount(amount):
        if amount is None:
            return False, "Amount is required"

        try:
            amount = float(amount)
        except (ValueError, TypeError):
            return False, "Amount must be a number"

        if amount <= 0:
            return False, "Amount must be greater than 0"

        if amount > 1000000000:
            return False, "Amount exceeds maximum limit"

        return True, None

    @staticmethod
    def validate_email(email):
        if not email or not isinstance(email, str):
            return False, "Email must be a non-empty string"

        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, email):
            return False, "Invalid email format"

        return True, None

    @staticmethod
    def validate_password(password):
        if not password or not isinstance(password, str):
            return False, "Password must be a non-empty string"

        if len(password) < 6:
            return False, "Password must be at least 6 characters"

        return True, None

    @staticmethod
    def sanitize_string(s, max_length=255):
        if not s:
            return ""

        s = str(s).strip()

        s = re.sub(r'[<>"\']', '', s)

        return s[:max_length]

    @staticmethod
    def validate_transaction_data(data):
        errors = []

        if 'from_address' in data:
            valid, error = Validator.validate_address(data['from_address'])
            if not valid:
                errors.append(f"from_address: {error}")

        if 'to_address' in data:
            valid, error = Validator.validate_address(data['to_address'])
            if not valid:
                errors.append(f"to_address: {error}")

        if 'amount' in data:
            valid, error = Validator.validate_amount(data['amount'])
            if not valid:
                errors.append(f"amount: {error}")

        if 'fee' in data:
            valid, error = Validator.validate_amount(data['fee'])
            if not valid:
                errors.append(f"fee: {error}")

        return len(errors) == 0, errors

    @staticmethod
    def validate_merchant_payment(data):
        required_fields = ['from_address', 'to_address', 'amount', 'merchant_name']

        errors = []

        for field in required_fields:
            if field not in data:
                errors.append(f"{field} is required")

        if not errors:
            valid, trans_errors = Validator.validate_transaction_data(data)
            if not valid:
                errors.extend(trans_errors)

        if 'merchant_name' in data:
            if not data['merchant_name'] or len(data['merchant_name']) > 100:
                errors.append("merchant_name must be 1-100 characters")

        return len(errors) == 0, errors

validator = Validator()
