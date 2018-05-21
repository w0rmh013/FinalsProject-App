import json
import socket
import subprocess
import sys
import paramiko


LOGGED_IN = False
USERNAME = 'user1'
PASSWORD = 'user111'


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
    except socket.error:
        # socket closed
        LOGGED_IN = False


def main():
    global LOGGED_IN
    with open('locker_server_params.json', 'r') as f:
        params = json.load(f)

    try:
        p = subprocess.Popen(['python3', 'user_locker_service.py', params['ServerIP'], str(params['LockerServicePort']),
                              params['Curve'], params['ServerVerifyingKey']])
    except KeyError:
        sys.exit(0)

    try:
        ssh_conn = paramiko.SSHClient()
        ssh_conn.set_missing_host_key_policy(paramiko.AutoAddPolicy)
        ssh_conn.connect(params['ServerIP'], port=params['LockerAppSSHPort'], username=USERNAME, password=PASSWORD)
        LOGGED_IN = True

    except paramiko.AuthenticationException:
        LOGGED_IN = False

    else:
        chan = ssh_conn.invoke_shell()
        windows_shell(chan)
        ssh_conn.close()

    p.kill()
    sys.exit(0)


if __name__ == '__main__':
    main()
