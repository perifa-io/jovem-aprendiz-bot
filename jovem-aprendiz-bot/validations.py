import re


def is_auth_verifier(auth_verifier):
    return bool(re.match(r"\d{7}$", auth_verifier))
