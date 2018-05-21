import socket
import sys
import paramiko


LOGGED_IN = False
HOST = '10.0.0.21'
PORT = 2280
USERNAME = 'user'
PASSWORD = 'pass'


# this code is a snippet from paramiko/demos/interactive.py
def windows_shell(chan):
    import threading
    global LOGGED_IN

    # sys.stdout.write("Line-buffered terminal emulation. Press F6 or ^Z to send EOF.\r\n\r\n")

    def writeall(sock):
        while True:
            data = sock.recv(256).decode()
            if not data:
                sys.stdout.write('\r\n*** EOF ***\r\n\r\n')
                sys.stdout.flush()
                break
            sys.stdout.write(data)
            sys.stdout.flush()

    writer = threading.Thread(target=writeall, args=(chan,))
    writer.start()

    try:
        while True:
            d = sys.stdin.read(1)
            if not d:
                break
            chan.send(d)
    except EOFError:
        # user hit ^Z or F6
        pass
    except OSError:
        # socket closed
        LOGGED_IN = False
        pass


def main():
    global LOGGED_IN

    try:
        ssh_conn = paramiko.SSHClient()
        ssh_conn.set_missing_host_key_policy(paramiko.AutoAddPolicy)
        # ssh_conn.connect(HOST, port=PORT, username=USERNAME, password=PASSWORD)
        ssh_conn.connect(HOST, port=PORT, username=USERNAME, password=PASSWORD)
        LOGGED_IN = True

    except paramiko.AuthenticationException:
        LOGGED_IN = False

    else:
        chan = ssh_conn.invoke_shell()
        windows_shell(chan)
        # b'b\x00\x00\x00\x00\x00\x00\x00\x04exec\x01\x00\x00\x00\x02ls'
        # stdin, stdout, stderr = ssh_conn.exec_command('ls')
        # print(stdout.read())
        ssh_conn.close()


if __name__ == '__main__':
    main()
