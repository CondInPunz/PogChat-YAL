import socket
import db_operations

host = socket.gethostbyname(socket.gethostname())
port = 9090
db_name = 'userdata.sqlite'
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('', port))
LOG_IN = 0
SEND = 1
LOG_OUT = 2
SELECT_ALL_MESS = 3

server_socket.listen(1)
print('server started!')
conn, addr = server_socket.accept()

print('connected:', addr)
shutdown_server = False
is_logged_in = False

while not shutdown_server:
    try:
        data = conn.recv(1024)
        data = data.decode('utf-8')
        query = int(data.split()[0])
        client_login = data.split()[1]
        extra_data = ' '.join(data.split()[2:])
        # print(extra_data)

        if query == SEND:
            # print('all is ok')
            if is_logged_in:
                message = extra_data
                if db_operations.find_user(db_name, client_login):
                    db_operations.send_message(db_name, client_login, message)
                    conn.send(client_login.encode('utf-8').upper())
                else:
                    conn.send('send failed : user not found'.encode('utf-8'))
            else:
                conn.send('not logged in'.encode('utf-8'))

        if query == LOG_IN:
            # print('all is ok')
            password = extra_data
            if db_operations.find_user(db_name, client_login):
                # print('all is ok')
                if db_operations.check_password(db_name, client_login, password):
                    conn.send('u joined chat'.encode('utf-8'))
                    is_logged_in = True
                    db_operations.send_message(db_name, '[SERVER]', f'{client_login} joined chat!')
                else:
                    conn.send('u r not the father'.encode('utf-8'))
                    # print('error sent')
                db_operations.set_status(db_name, client_login, True)
            else:
                conn.send('new_challenger_appears'.encode('utf-8'))
                print('new_user appeared')

        if query == LOG_OUT:
            db_operations.set_status(db_name, client_login, False)
            is_logged_in = False
            db_operations.send_message(db_name, '[SERVER]', f'[{client_login} joined chat!]')
            conn.send('u left chat'.encode('utf-8'))
        if query == SELECT_ALL_MESS:
            pass
    except:
        shutdown_server = True

print('server stopped')
server_socket.close()
