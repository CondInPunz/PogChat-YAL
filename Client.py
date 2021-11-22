import sys
import socket
import time

from db_operations import select_all_messages
from PyQt5 import uic
from PyQt5.QtCore import Qt, pyqtSignal, QThread, QObject, QTimer, QSize
from PyQt5.QtGui import QPixmap, QMovie
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QWidget, QSplashScreen

LOG_IN = 0
SEND = 1
LOG_OUT = 2
SELECT_ALL_MESS = 3
SELECT_LAST_MESS = 4
REG = 5
SERVER = ("192.168.1.2", 9091)


class Client(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('client.ui', self)
        self.initUI()

    def initUI(self):
        logo_image_name = 'logo.png'
        self.logo_pixmap = QPixmap(logo_image_name)
        self.logo_label.setPixmap(self.logo_pixmap)

        if not self.establish_connection():
            raise ServerConnectionError('Сервер недоступен.')

        self.users_tab_name = 'userdata.sqlite'
        self.login = ''
        self.password = ''
        self.second_form = None
        self.enter_button.clicked.connect(self.enter)
        self.reg_button.clicked.connect(self.create_account)
        self.password_enter.textChanged.connect(self.hide_password)

    def establish_connection(self):
        try:
            host = socket.gethostbyname(socket.gethostname())
            port = 0

            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.client_socket.bind((host, port))
            print('connection succeeded!')
            return True
        except ServerConnectionError:
            print('В данный момент сервер находится на техническом обслуживании.')
            return False

    def create_account(self):
        self.reg_window = RegWindow(self.client_socket)
        self.reg_window.show()

    def enter(self):
        self.login = self.login_enter.text()
        self.login_enter.setText('')
        self.password_enter.setText('')
        self.client_socket.sendto(f'{LOG_IN} {self.login} {self.password}'.encode("utf-8"), SERVER)

        answer, address = self.client_socket.recvfrom(2048)
        print(answer)
        answer = answer.decode('utf-8')
        if answer == 'u r not the father':
            self.wrong_answer_confirmation = QueryWindow('Введённые данные неверны.')
            self.wrong_answer_confirmation.show()
            self.password = ''
            self.login = ''
        elif answer == 'who r u':
            self.wrong_answer_confirmation = QueryWindow('Такой учётной записи не существует. Пожалуйста, создайте её.')
            self.wrong_answer_confirmation.show()
            self.password = ''
            self.login = ''
        else:
            self.open_second_form()

    def open_second_form(self):
        self.second_form = ClientChat(self.login, self.client_socket)
        self.second_form.show()
        self.close()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Enter:
            self.enter()

    def hide_password(self):
        if self.password_enter.text() != '*' * len(self.password_enter.text()):
            self.password += self.password_enter.text()[-1]
            self.password_enter.setText('*' * len(self.password))
        if len(self.password) != len(self.password_enter.text()) and len(self.password_enter.text()) != 0:
            self.password = self.password[:-1]


class RegWindow(QWidget):
    def __init__(self, socket, parent=None):
        super().__init__(parent, Qt.Window)
        uic.loadUi('reg_form.ui', self)
        self.initUI(socket)

    def initUI(self, socket):
        self.client_socket = socket
        self.password_enter.textChanged.connect(self.hide_password)
        self.password_enter_2.textChanged.connect(self.hide_2nd_password)
        self.reg_button.clicked.connect(self.reg)
        self.password = ''
        self.conf_password = ''

    def reg(self):
        self.login = self.login_enter.text()
        if self.password == self.conf_password:
            self.client_socket.sendto(f'{REG} {self.login} {self.password}'.encode("utf-8"), SERVER)
            self.close()
        else:
            self.incorrect_password_conf = QueryWindow('Введённые данные неверны.')
            self.incorrect_password_conf.show()

    def hide_password(self):
        if self.sender().text() != '*' * len(self.sender().text()):
            self.password += self.sender().text()[-1]
            self.sender().setText('*' * len(self.password))
        if len(self.password) != len(self.sender().text()) and len(self.sender().text()) != 0:
            self.password = self.password[:-1]

    def hide_2nd_password(self):
        if self.sender().text() != '*' * len(self.sender().text()):
            self.conf_password += self.sender().text()[-1]
            self.sender().setText('*' * len(self.conf_password))
        if len(self.conf_password) != len(self.sender().text()) and len(self.sender().text()) != 0:
            self.password = self.conf_password[:-1]


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

    def receive_message(self):
        while True:
            time.sleep(5)
            data, addr = self.client_socket.recvfrom(1024)
            data = data.decode('utf-8')
            print(data)

    def quit_the_chat(self):
        self.client_socket.close()


class ServerConnectionError(ConnectionError):
    pass


class QueryWindow(QWidget):
    def __init__(self, query):
        super().__init__()
        uic.loadUi('confirm.ui', self)
        self.initUI(query)

    def initUI(self, query):
        image_name = 'warning_icon.png'
        self.icon_pixmap = QPixmap(image_name)

        self.warning_icon.setPixmap(self.icon_pixmap)

        self.extra_button.hide()
        self.warning_icon.show()
        self.confirm_button.clicked.connect(self.confirm)
        self.cancel_button.clicked.connect(self.cancel)
        self.query_label.setText(query)
        self.cancel_button.setText('Отмена')

    def confirm(self):
        self.close()

    def cancel(self):
        self.close()


class LoadingScreen(QSplashScreen):
    def __init__(self, *args, **kwargs):
        super(LoadingScreen, self).__init__(*args, **kwargs)
        self.loading_movie = QMovie('loading_gif.gif')
        self.loading_movie.setScaledSize(QSize(150, 50))
        self.loading_movie.frameChanged.connect(self.onFrameChanged)
        self.loading_movie.start()

    def onFrameChanged(self, _):
        self.setPixmap(self.loading_movie.currentPixmap())

    def finish(self, widget):
        self.loading_movie.stop()
        super(LoadingScreen, self).finish(widget)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Client()
    splash = LoadingScreen()
    splash.show()

    def createWindow():
        app.w = Client()
        QTimer.singleShot(500, lambda: (app.w.show(), splash.finish(app.w)))

    QTimer.singleShot(500, createWindow)
    sys.exit(app.exec_())
