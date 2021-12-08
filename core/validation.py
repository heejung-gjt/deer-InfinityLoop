import re

from users.models    import Role


def phone_number_validator(phone_number):
    return re.compile("\d{3}-\d{3,4}-\d{4}").match(phone_number)


def email_validator(email):
    return re.compile("^[a-zA-Z0-9+-_.]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$").match(email)


def code_validator(first, code):
    return re.compile(f"{first}"+"-\S{1}-\d{1}").match(code)


def check_admin(user_id):
    if user_id != Role.Type.ADMIN.value:
        return {"error": True}
    
    return {"error": False}
