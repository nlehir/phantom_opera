import re


def valid_email(email):
    return bool(re.fullmatch(r"^[\w\.\+\-]+\@[\w]+\.[a-z]{2,3}$", email))
