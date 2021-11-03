import uuid


def get_default_uid():
    return uuid.uuid4().hex[:6].upper()
