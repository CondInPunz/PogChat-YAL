import sys
import socket
import time

from PyQt5 import uic
from PyQt5.QtCore import Qt, QThread, QTimer, QSize
from PyQt5.QtGui import QPixmap, QMovie
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QSplashScreen, QDialog

LOG_IN = 0
SEND = 1
LOG_OUT = 2
SELECT_ALL_MESS = 3
SELECT_LAST_MESS = 4
REG = 5
SERVER = ("192.168.1.4", 9091)


class RegWindow(QWidget):
    def __init__(self, socket=None):
        super().__init__()
        uic.loadUi('reg_form.ui', self)
        self.initUI(socket)

    def initUI(self, socket):
        self.client_socket = socket

        self.password = ''
        self.password2 = ''
        self.pw_enter_cursor_pos = None
        self.password_enter.cursorPositionChanged.connect(self.find_cursor)
        self.password_enter_2.cursorPositionChanged.connect(self.find_cursor)
        self.reg_button.clicked.connect(self.enter)
        self.password_enter.textChanged.connect(self.hide_password)
        self.password_enter_2.textChanged.connect(self.hide_password_2)

    def enter(self):
        self.login = self.login_enter.text()
        if self.password == self.password2:
            self.reg()
        else:
            self.wrong_answer_confirmation = QueryWindow('Введённые данные неверны.')
            self.wrong_answer_confirmation.show()

    def reg(self):
        self.client_socket.sendto(f'{REG} {self.login} {self.password}'.encode("utf-8"), SERVER)
        self.close()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Enter:
            self.enter()

    def hide_password(self):
        if self.password_enter.text() != '*' * len(self.password_enter.text()):
            self.password += self.password_enter.text()[-1]
            self.password_enter.setText('*' * len(self.password))
        if len(self.password) != len(self.password_enter.text()):
            self.password = self.password[:self.pw_enter_cursor_pos - 1] + self.password[self.pw_enter_cursor_pos:]
        elif len(self.password_enter.text()) == 0:
            self.password = ''
        print(self.password)

    def hide_password_2(self):
        if self.password_enter_2.text() != '*' * len(self.password_enter_2.text()):
            self.password2 += self.password_enter_2.text()[-1]
            self.password_enter_2.setText('*' * len(self.password2))
        if len(self.password2) != len(self.password_enter_2.text()):
            self.password2 = self.password2[:self.pw_enter_cursor_pos - 1] + self.password2[self.pw_enter_cursor_pos:]
        elif len(self.password_enter_2.text()) == 0:
            self.password2 = ''
        print(self.password2)

    def find_cursor(self):
        self.pw_enter_cursor_pos = self.password_enter.cursorRect()
        self.pw_enter_cursor_pos = (self.pw_enter_cursor_pos.topLeft().x() + 2) // 6


class Client(QMainWindow):
    def __init__(self, login='', socket=None):
        super().__init__()
        uic.loadUi('client.ui', self)
        self.initUI(login, socket)

    def initUI(self, login, socket):
        logo_image_name = 'logo.png'
        self.logo_pixmap = QPixmap(logo_image_name)
        self.logo_label.setPixmap(self.logo_pixmap)
        self.client_socket = socket
        self.info_file = None

        if not self.establish_connection():
            self.server_connection_error = QueryWindow('В данный момент сервер недоступен.')
            self.server_connection_error.show()
            self.close()

        self.set_theme()
        self.users_tab_name = 'userdata.sqlite'
        self.login = login
        self.password = ''
        self.second_form = None
        self.pw_enter_cursor_pos = None
        self.password_enter.cursorPositionChanged.connect(self.find_cursor)
        self.enter_button.clicked.connect(self.enter)
        self.reg_button.clicked.connect(self.create_account)
        self.password_enter.textChanged.connect(self.hide_password)

    def set_theme(self):
        try:
            self.info_file = open('info.txt', 'r')
        except:
            self.info_file = open('info.txt', 'w')
            self.info_file.write('Light')
        self.theme = self.info_file.read()
        print(self.theme)

    def establish_connection(self):
        try:
            host = socket.gethostbyname(socket.gethostname())
            port = 0

            self.client_socket.bind((host, port))
            print('connection succeeded!')
            return True
        except:
            print('В данный момент сервер находится на техническом обслуживании.')
            return False

    def create_account(self):
        self.reg_window = RegWindow(self.client_socket)
        self.reg_window.show()

    def enter(self):
        self.login = self.login_enter.text()
        self.client_socket.sendto(f'{LOG_IN} {self.login} {self.password}'.encode("utf-8"), SERVER)
        self.password_enter.setText('')
        self.login_enter.setText('')

        answer, address = self.client_socket.recvfrom(2048)
        answer = answer.decode('utf-8')
        if answer == 'u r not the father':
            self.wrong_answer_confirmation = QueryWindow('Введённые данные неверны.')
            self.wrong_answer_confirmation.show()
            self.password = ''
            self.login = ''
        elif answer == 'who r u':
            self.wrong_answer_confirmation = QueryWindow('Такой учётной записи не существует.')
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
        if len(self.password) != len(self.password_enter.text()):
            self.password = self.password[:self.pw_enter_cursor_pos - 1] + self.password[self.pw_enter_cursor_pos:]
        elif len(self.password_enter.text()) == 0:
            self.password = ''
        print(self.password)

    def find_cursor(self):
        self.pw_enter_cursor_pos = self.password_enter.cursorRect()
        self.pw_enter_cursor_pos = (self.pw_enter_cursor_pos.topLeft().x() + 2) // 6


class ClientChat(QMainWindow):
    def __init__(self, login, client_socket):
        super().__init__()
        uic.loadUi('chat_client.ui', self)
        self.initUI(login, client_socket)

    def initUI(self, login, client_socket):
        self.client_socket = client_socket
        self.user_login = login
        self.send_button.clicked.connect(self.send)
        self.fulfil_chat()
        self.first_form = None
        logo_image_name = 'logo.png'
        self.logo_pixmap = QPixmap(logo_image_name)
        self.logo_label.setPixmap(self.logo_pixmap)
        self.nick_name_label.setText(self.user_login)

        self.updatingChatWindowThread = UpdatingChatWindowThread(self)
        self.launch_updating_chat_window()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Enter:
            self.send()

    def fulfil_chat(self):
        self.client_socket.sendto(f"{SELECT_ALL_MESS} {self.user_login} extra_data".encode('utf-8'), SERVER)
        received_data, address = self.client_socket.recvfrom(10240)
        messages = received_data.decode('utf-8').split('$')
        for message in messages:
            if message:
                message = message.split('%')
                send_date = message[3]
                send_time = message[4][:8]
                user = message[2]
                text = message[1]
                self.chat_window.append(f'[{send_date}] [{send_time}] {user}: {text}')

    def launch_updating_chat_window(self):
        self.updatingChatWindowThread.start()

    def send(self):
        message = self.message_enter.text()
        self.message_enter.setText('')
        self.client_socket.sendto(f'{SEND} {self.user_login} {message}'.encode('utf-8'), SERVER)

    def quit_the_chat(self):
        self.client_socket.close()

    def closeEvent(self, event):
        self.client_socket.sendto(f'{LOG_OUT} {self.user_login} left chat.'.encode('utf-8'), SERVER)
        self.hide()
        time.sleep(3)
        self.close()

    def open_first_form(self):
        self.first_form = ClientChat(self.login, self.client_socket)
        self.first_form.show()
        self.close()


class UpdatingChatWindowThread(QThread):
    def __init__(self, main_window):
        super(UpdatingChatWindowThread, self).__init__()
        self.initUI(main_window)

    def initUI(self, main_window):
        self.value = 0
        self.main_window = main_window

    def run(self):
        while True:
            last_message, address = self.main_window.client_socket.recvfrom(2048)
            last_message = last_message.decode('utf-8')
            last_message = last_message.split('%')
            send_date = last_message[3]
            send_time = last_message[4][:8]
            user = last_message[2]
            text = last_message[1]
            self.main_window.chat_window.append(f'[{send_date}] [{send_time}] {user}: {text}')
            time.sleep(0.3)


class QueryWindow(QDialog):
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
        self.loading_movie.frameChanged.connect(self.change_frame)
        self.loading_movie.start()

    def change_frame(self, _):
        self.setPixmap(self.loading_movie.currentPixmap())

    def finish(self, widget):
        self.loading_movie.stop()
        super(LoadingScreen, self).finish(widget)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    cl_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    splash = LoadingScreen()
    splash.show()

    def createWindow():
        app.w = Client('', cl_socket)
        QTimer.singleShot(500, lambda: (app.w.show(), splash.finish(app.w)))

    QTimer.singleShot(500, createWindow)
    sys.exit(app.exec_())
