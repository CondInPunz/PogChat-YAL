import sqlite3
import datetime
from hash_operations import encode_password, create_password


def add_user(name, login, password):
    connect = sqlite3.connect(name)
    cursor = connect.cursor()
    password, salt = create_password(password)

    query = f"""INSERT INTO users(login, password, status, salt) 
    VALUES('{login}', '{password.decode('utf-8')}', {True}, '{salt.decode('utf-8')}')"""

    cursor.execute(query).fetchall()
    connect.commit()
    connect.close()


def delete_user(name, login):
    connect = sqlite3.connect(name)
    cursor = connect.cursor()

    query = f"""DELETE from users
            where login LIKE '{login}'"""

    cursor.execute(query).fetchall()
    connect.commit()
    connect.close()


def update_password(name, login, new_password):
    connect = sqlite3.connect(name)
    cursor = connect.cursor()
    new_password, salt = create_password(new_password)

    query = f"""UPDATE users
            SET password = '{new_password.decode('utf-8')}'
            WHERE login = '{login}'"""

    cursor.execute(query).fetchall()

    query = f"""UPDATE users
                SET salt = '{salt.decode('utf-8')}'
                WHERE login = '{login}'"""

    cursor.execute(query).fetchall()
    connect.commit()
    connect.close()


def set_status(name, login, status=True):
    connect = sqlite3.connect(name)
    cursor = connect.cursor()

    query = f"""UPDATE users
                SET status = {status}
                WHERE login = '{login}'"""

    cursor.execute(query).fetchall()
    connect.commit()
    connect.close()


def find_user(name, login):
    connect = sqlite3.connect(name)
    cursor = connect.cursor()

    query = f"""SELECT id from users 
            WHERE login = '{login}'"""
    result = cursor.execute(query).fetchall()
    connect.commit()
    connect.close()
    if result:
        id = result[0][0]
        return id
    else:
        return False


def check_password(name, login, not_checked_pw):
    connect = sqlite3.connect(name)
    cursor = connect.cursor()

    query = f"""SELECT password, salt from users 
                WHERE login = '{login}'"""

    password = cursor.execute(query).fetchall()[0][0]
    salt = cursor.execute(query).fetchall()[0][1]
    salt = salt.encode('utf-8')
    password = password.encode('utf-8')
    not_checked_pw = encode_password(not_checked_pw, salt)

    connect.commit()
    connect.close()
    return password == not_checked_pw


def send_message(name, login, text):
    connect = sqlite3.connect(name)
    cursor = connect.cursor()

    query = f"""INSERT INTO messages(text, sender, date, time) 
    VALUES('{text}', '{login}', '{datetime.datetime.now().date()}', '{datetime.datetime.now().time()}')"""

    cursor.execute(query).fetchall()

    connect.commit()
    connect.close()


def select_all_messages(name):
    connect = sqlite3.connect(name)
    cursor = connect.cursor()

    query = f"""SELECT * from messages"""

    data = cursor.execute(query).fetchall()
    connect.commit()
    connect.close()
    return data


def select_last_message(name):
    connect = sqlite3.connect(name)
    cursor = connect.cursor()

    query = f"""SELECT id from messages"""

    data = cursor.execute(query).fetchall()
    last_id = data[-1][0] - 1

    query = f"""SELECT * from messages where id = {last_id}"""
    data = cursor.execute(query).fetchall()

    connect.commit()
    connect.close()
    return data
