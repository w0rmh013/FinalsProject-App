from Queue import Queue
import paramiko
import socket
import subprocess
import threading


class User:
    def __init__(self, server_ip, local_scp_port, curve, server_verifying_key, server_ssh_port):
        self._ip = server_ip
        self._local_port = local_scp_port
        self._curve = curve
        self._server_verifying_key = server_verifying_key
        self._port = server_ssh_port

        self._locker_service_proc = subprocess.Popen(['python3', 'user_locker_service.py', self._ip, self._local_port,
                                                      self._curve, self._server_verifying_key])

        self._ssh_conn = None
        self._shell_channel = None
        self.logged_in = False
        self.username = ''

        self._input = ''
        self._output = ''

        self.input_queue = Queue()
        self.output_queue = Queue()
        self.output_lock = threading.Lock()

    def login(self, username, password):
        self._ssh_conn = paramiko.SSHClient()
        self._ssh_conn.set_missing_host_key_policy(paramiko.AutoAddPolicy)

        try:
            self._ssh_conn.connect(self._ip, port=self._port, username=username, password=password, timeout=15)

        except paramiko.AuthenticationException:
            self.logged_in = False
            return False

        except socket.error:
            self.logged_in = None
            return None

        self._shell_channel = self._ssh_conn.invoke_shell()
        self.logged_in = True
        self.username = username

        return True

    def run(self):
        # get login message
        # use instead of blocking acquire, because if we logout we want the program to end
        while not self.output_lock.acquire():
            if not self.logged_in:
                break
        temp = self._shell_channel.recv(4096).decode()
        while not temp.endswith('\0'):
            temp += self._shell_channel.recv(4096).decode()
        self.output_lock.release()

        while True:
            # use instead of plain empty check, because if we logout we want the program to end
            while self.input_queue.empty():
                if not self.logged_in:
                    break
            if not self.logged_in:
                break

            self._input = self.input_queue.get()
            self._shell_channel.send(self._input[0] + '\n')

            # use instead of blocking acquire, because if we logout we want the program to end
            while not self.output_lock.acquire():
                if not self.logged_in:
                    break
            if not self.logged_in:
                break
            self._output = self._shell_channel.recv(4096).decode()
            while not self._output.endswith('\0'):
                self._output += self._shell_channel.recv(4096).decode()

            self.output_lock.release()
            # the last character of the output is always '\0', we trim it
            self.output_queue.put((self._input[1], self._output[:-1].strip()))

        self.close()

    def exec_command(self, command, func):
        # add command to input queue, func will be used with the output
        self.input_queue.put((command, func))

    def handle_output(self):
        while self.logged_in:
            while not self.output_queue.empty():
                func, data = self.output_queue.get()
                func(data)

    def close(self):
        self._locker_service_proc.kill()
        self._ssh_conn.close()
