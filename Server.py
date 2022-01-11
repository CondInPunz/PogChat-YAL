import socket
import db_operations

LOG_IN = 0
SEND = 1
LOG_OUT = 2
SELECT_ALL_MESS = 3
SELECT_LAST_MESS = 4
REG = 5
db_name = 'userdata.sqlite'

host = socket.gethostbyname(socket.gethostname())
print(host)
port = 9091

server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind((host, port))

print('server started!')

shutdown_server = False

while not shutdown_server:
    try:
        data, client_address = server_socket.recvfrom(2048)
        data = data.decode('utf-8')
        query = int(data.split()[0])
        client_login = data.split()[1]
        if len(data) > 2:
            extra_data = ' '.join(data.split()[2:])

        if query == SEND:
            message = extra_data
            print(message)
            db_operations.send_message(db_name, client_login, message)
            last_message = db_operations.select_last_message(db_name)
            last_message = db_operations.select_last_message(db_name)
            last_message = list(last_message[0])
            last_message = list(map(str, last_message))
            server_socket.sendto('%'.join(last_message).encode('utf-8'), client_address)
            print(last_message)
            print('message sent successfully!')

        if query == LOG_IN:
            password = extra_data
            if db_operations.find_user(db_name, client_login):
                if db_operations.check_password(db_name, client_login, password):
                    server_socket.sendto('u joined chat'.encode('utf-8'), client_address)
                    print('user joined chat')
                    is_logged_in = True
                    db_operations.send_message(db_name, '[SERVER]', f'{client_login} joined chat!')
                else:
                    server_socket.sendto('u r not the father'.encode('utf-8'), client_address)
                    print('error sent')
                db_operations.set_status(db_name, client_login, True)
            else:
                server_socket.sendto('who r u'.encode('utf-8'), client_address)

        if query == LOG_OUT:
            db_operations.set_status(db_name, client_login, False)
            is_logged_in = False
            db_operations.send_message(db_name, '[SERVER]', f'[{client_login} joined chat!]')

        if query == SELECT_ALL_MESS:
            data = db_operations.select_all_messages(db_name)
            full_text = ''
            for message in data:
                message = list(map(str, list(message)))
                full_text += '%'.join(message) + '$'
            server_socket.sendto(full_text.encode('utf-8'), client_address)
            print('all messages sent to client successfully.')

        if query == REG:
            password = extra_data
            db_operations.add_user(db_name, client_login, password)
            print('new user created.')
    except:
        shutdown_server = True

print('server stopped')
server_socket.close()