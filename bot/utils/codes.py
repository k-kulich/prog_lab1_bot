import secrets
import string

ALPHABET = string.ascii_uppercase + string.digits
CODE_LENGTH = 6


def generate_tutor_code(length: int = CODE_LENGTH) -> str:
    """Код для привязки ученика к репетитору."""
    return "".join(secrets.choice(ALPHABET) for _ in range(length))