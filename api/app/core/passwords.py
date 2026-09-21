"""Password strength policy, shared by registration and any future password-change flow.

Follows the spirit of NIST 800-63B: length is the primary lever, screen against a
blocklist of common/breached passwords, and reject values trivially derived from the
account's own identifiers. Deliberately avoids draconian composition rules while still
rejecting obviously weak inputs.
"""

MIN_PASSWORD_LENGTH = 10
MAX_PASSWORD_LENGTH = 128

# The most common / breached passwords, normalized to lowercase. Not exhaustive; this is a
# cheap offline guard, not a substitute for live breach screening (see README follow-ups).
COMMON_PASSWORDS = frozenset(
    {
        "password", "password1", "password123", "passw0rd", "passw0rd1",
        "12345678", "123456789", "1234567890", "123123123", "qwertyuiop",
        "qwerty123", "azerty123", "1q2w3e4r", "111111111", "000000000",
        "iloveyou1", "welcome123", "welcome1", "letmein123", "changeme",
        "changeme123", "abc123456", "motdepasse", "administrator", "superman1",
        "trustno1", "fitfolio", "fitfolio123", "adminadmin", "passwordpassword",
    }
)


class PasswordPolicyError(ValueError):
    """Raised when a candidate password fails the strength policy."""


def _character_classes(password: str) -> int:
    has_lower = any(c.islower() for c in password)
    has_upper = any(c.isupper() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_symbol = any(not c.isalnum() for c in password)
    return sum((has_lower, has_upper, has_digit, has_symbol))


def validate_password_strength(
    password: str, *, email: str | None = None, display_name: str | None = None
) -> str:
    """Return the password unchanged if it satisfies the policy, else raise PasswordPolicyError."""
    if len(password) < MIN_PASSWORD_LENGTH:
        raise PasswordPolicyError(
            f"Password must be at least {MIN_PASSWORD_LENGTH} characters long"
        )
    if len(password) > MAX_PASSWORD_LENGTH:
        raise PasswordPolicyError(
            f"Password must be at most {MAX_PASSWORD_LENGTH} characters long"
        )

    if password.strip().lower() in COMMON_PASSWORDS:
        raise PasswordPolicyError("Password is too common; choose a less predictable password")

    if len(set(password)) == 1:
        raise PasswordPolicyError("Password must not be a single repeated character")

    if _character_classes(password) < 2:
        raise PasswordPolicyError(
            "Password must combine at least two of: lowercase, uppercase, digits, symbols"
        )

    # Reject passwords trivially derived from the account's own identifiers.
    lowered = password.lower()
    local_part = email.split("@", 1)[0].lower() if email and "@" in email else None
    for token in (local_part, display_name.lower() if display_name else None):
        if token and len(token) >= 4 and token in lowered:
            raise PasswordPolicyError("Password must not contain your email or display name")

    return password
