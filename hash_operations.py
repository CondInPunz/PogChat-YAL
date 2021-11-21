import bcrypt


def create_password(password):
    salt = bcrypt.gensalt()
    password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return password, salt


def encode_password(password, salt):
    password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return password
