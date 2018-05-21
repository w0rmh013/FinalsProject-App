import json
import socket
import subprocess
import paramiko


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

    def login(self, username, password):
        self._ssh_conn = paramiko.SSHClient()
        self._ssh_conn.set_missing_host_key_policy(paramiko.AutoAddPolicy)

        try:
            self._ssh_conn.connect(self._ip, username, password)

        except paramiko.AuthenticationException:
            return False

        self._shell_channel = self._ssh_conn.invoke_shell()

        return True

    def run(self):
