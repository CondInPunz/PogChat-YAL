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
        print(data)
        data = data.decode('utf-8')
        print(data)
        query = int(data.split()[0])
        client_login = data.split()[1]
        extra_data = ' '.join(data.split()[2:])
        print(extra_data)

        if query == SEND:
            print('all is ok')
            message = extra_data
            print(message)
            db_operations.send_message(db_name, client_login, message)
            server_socket.sendto(client_login.encode('utf-8').upper(), client_address)
            print('cool')

        if query == LOG_IN:
            print('all is ok')
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
            print('all messages sent to client successfully.')

        if query == REG:
            password = extra_data
            print(client_login, password)
            db_operations.add_user(db_name, client_login, password)
            print('new user created.')
    except:
        shutdown_server = True

print('server stopped')
server_socket.close()
