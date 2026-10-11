from email_validator import EmailNotValidError, validate_email
from pydantic_core import PydanticCustomError

TYPO_DOMAINS = {
    "gmal.com": "gmail.com",
    "gmial.com": "gmail.com",
    "gamil.com": "gmail.com",
    "gmail.co": "gmail.com",
    "gmaill.com": "gmail.com",
    "gmai.com": "gmail.com",
    "hotmial.com": "hotmail.com",
    "hotmal.com": "hotmail.com",
    "hotnail.com": "hotmail.com",
    "outlok.com": "outlook.com",
    "outloook.com": "outlook.com",
    "yaho.com": "yahoo.com",
    "yahooo.com": "yahoo.com",
}


def check_email(value):
    if value is None:
        return None
    email = str(value).strip()
    try:
        validate_email(email, check_deliverability=False)
    except EmailNotValidError:
        raise PydanticCustomError("email", "Enter a valid email address")
    local, domain = email.rsplit("@", 1)
    fixed = TYPO_DOMAINS.get(domain.lower())
    if fixed:
        raise PydanticCustomError("email_typo", "Did you mean {suggestion}?", {"suggestion": f"{local}@{fixed}"})
    return email
