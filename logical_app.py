import paramiko
import re


USERNAME = 'user1'
PASSWORD = 'user111'

ssh_conn = paramiko.SSHClient()
ssh_conn.set_missing_host_key_policy(paramiko.AutoAddPolicy)
ssh_conn.connect('10.0.0.21', username=USERNAME, password=PASSWORD)

chan = ssh_conn.invoke_shell()


def run_cmd(cmd):
    buff = b''

    # while re.match(USERNAME+'\|locker:(.+)\$')
    while not buff.endswith(b'$ '):
        resp = chan.recv(4096)
        buff += resp
        print(resp)

    chan.send(cmd+'\n')

    # buff = b''
    # while not buff.endswith(b'Enter password: '):
    #     resp = chan.recv(4096)
    #     buff += resp
    #     print(resp)
    #
    # chan.send(PASSWORD+'\n')

    buff = b''
    while not buff.endswith(b'$ '):
        resp = chan.recv(4096)
        buff += resp
        print(resp)

    ssh_conn.close()


def main():
    run_cmd('upload "C:\\Users\\jonat\\Downloads\\Installs\\Git-2.16.1-64-bit.exe" dir1')


if __name__ == '__main__':
    main()

