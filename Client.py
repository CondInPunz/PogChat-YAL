import sys
import socket

from db_operations import select_all_messages, select_last_message
from PyQt5 import uic
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QMainWindow

LOG_IN = 0
SEND = 1
LOG_OUT = 2
SELECT_ALL_MESS = 3
SELECT_LAST_MESS = 4


class Client(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('client.ui', self)
        self.initUI()

    def initUI(self):
        if not self.establish_connection():
            raise ServerConnectionError('Сервер недоступен.')
        self.users_tab_name = 'userdata.sqlite'
        self.login = ''
        self.password = ''
        self.second_form = None
        self.wrong_answer_label.hide()
        self.wrong_answer_label.setText('Введённые данные неверны.')
        self.enter_button.clicked.connect(self.enter)
        self.password_enter.textChanged.connect(self.hide_password)

    def establish_connection(self):
        try:
            server = ('localhost', 9090)

            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect(server)
            return True
        except ServerConnectionError:
            print('В данный момент сервер находится на техническом обслуживании.')
            return False

    def enter(self):
        self.login = self.login_enter.text()
        self.login_enter.setText('')
        self.password_enter.setText('')

        self.client_socket.send(f'{LOG_IN} {self.login} {self.password}'.encode('utf-8'))
        answer = self.client_socket.recv(1024).decode('utf-8')
        print(answer)
        if answer == 'u r not the father':
            self.wrong_answer_label.show()
            self.password = ''
            self.login = ''
        else:
            self.open_second_form()

    def open_second_form(self):
        self.second_form = ClientChat(self.login, self.client_socket)
        self.second_form.show()
        self.hide()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Enter:
            self.enter()

    def hide_password(self):
        if self.password_enter.text() != '*' * len(self.password_enter.text()):
            self.password += self.password_enter.text()[-1]
            self.password_enter.setText('*' * len(self.password))
        if len(self.password) != len(self.password_enter.text()) and len(self.password_enter.text()) != 0:
            self.password = self.password[:-1]


class ClientChat(QMainWindow):
    def __init__(self, login, client_socket):
        super().__init__()
        uic.loadUi('chat_client.ui', self)
        self.initUI(login, client_socket)

    def initUI(self, login, client_socket):
        self.user_login = login
        self.users_tab_name = 'userdata.sqlite'
        self.send_button.clicked.connect(self.send)
        self.fulfil_chat()
        self.first_form = None
        self.client_socket = client_socket

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Enter:
            self.send(self.user_login)

    def fulfil_chat(self):
        messages = select_all_messages(self.users_tab_name)
        for message in messages:
            message = list(map(str, message))
            date = message[3]
            time = message[4][:8]
            user = message[2]
            text = message[1]
            self.chat_window.append(f'[{date}] [{time}] {user}: {text}')

    def show_new_message(self, message):
        message = message.decode('utf-8')
        date = message[3]
        time = message[4][:8]
        user = message[2]
        text = message[1]
        self.chat_window.append(f'[{date}] [{time}] {user}: {text}')

    def send(self, login):
        message = self.message_enter.text()
        print(message)
        self.message_enter.setText('')
        self.client_socket.send(f'{SEND} {login} {message}'.encode('utf-8'))
        new_message = self.client_socket.recv(1024)
        print(new_message)
        self.show_new_message(new_message)

    def quit_the_chat(self):
        self.client_socket.close()


class ServerConnectionError(ConnectionError):
    pass


class QueryWindow(QMainWindow):
    def __init__(self, query):
        super().__init__()
        uic.loadUi('chat_client.ui', self)
        self.initUI(query)

    def initUI(self, query):
        self.confirm_button.clicked.connect(self.confirm())
        self.cancel_button.clicked.connect(self.cancel())
        self.query = query

    def confirm(self):
        pass

    def cancel(self):
        pass


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Client()
    ex.show()
    sys.exit(app.exec_())
