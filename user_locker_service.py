#!/usr/bin/python3
import base64
from ecdsa.keys import SigningKey, VerifyingKey
from ecdsa import curves, util, ellipticcurve
import os
import paramiko
import re
import scp
import socket
import sys
import threading

from AES_cipher import AESCipher


def _ecdh_key_exchange(sock, curve, str_hex_server_verifying_key):
    # signing key: private key of the user
    # verifying key: public key of the user
    # server verifying key: public key of the server

    # generate key-pair
    signing_key = SigningKey.generate(curve=curve)
    verifying_key = signing_key.get_verifying_key()

    # create ecdsa key objects from strings
    server_verifying_key = VerifyingKey.from_string(bytes.fromhex(str_hex_server_verifying_key))

    # generate ecdh parameters
    g = curve.generator
    dh_rn = util.randrange(curve.order)  # generate random number for ecdh

    # calculate point 1
    g_1 = dh_rn * g

    str_point = '{},{}'.format(g_1.x(), g_1.y())
    message = 'public_key={}#str_point={}'.format(base64.b64encode(verifying_key.to_string()).decode(), str_point)
    signature = signing_key.sign(message.encode())

    server_message = sock.recv(4096).decode()  # receive message from server (it initiates the connection)
    sock.send(message.encode())  # send our message
    b64enc_server_signature = sock.recv(4096).decode()  # receive signature for 'server_message'
    sock.send('signature={}'.format(base64.b64encode(signature).decode()).encode())  # send our signature for 'message'

    # check for correct format of 'server_message'
    m = re.match('str_point=(\d+,\d+)', server_message)
    if m is None:
        return None
    server_str_point = m.group(1)

    m = re.match(r'signature=([0-9a-zA-Z+/=]{64})', b64enc_server_signature)
    if m is None:
        return None
    server_signature = base64.b64decode(m.group(1))

    # verify identity of server
    if not server_verifying_key.verify(server_signature, server_message.encode()):
        return None

    # calculate point 2
    g_2_x, g_2_y = map(int, server_str_point.split(','))
    g_2 = ellipticcurve.Point(curve.curve, g_2_x, g_2_y)

    # generate shared aes key
    aes_point = dh_rn * g_2
    aes_raw_key = '{}{}'.format(aes_point.x(), aes_point.y())
    return AESCipher(base64.b64encode(aes_raw_key.encode()))


def _scp_transfer(server_ip, username, password, func, src, dst):
    # do not upload resources which are not files
    if func == 'upload' and not os.path.isfile(src):
        return 997

    try:
        ssh_conn = paramiko.SSHClient()
        ssh_conn.load_system_host_keys()
        ssh_conn.set_missing_host_key_policy(paramiko.AutoAddPolicy)
        ssh_conn.connect(server_ip, username=username, password=password)

    except paramiko.AuthenticationException:
        return 400

    scp_conn = scp.SCPClient(ssh_conn.get_transport())
    try:
        if func == 'upload':
            try:
                scp_conn.put(src, dst)
            except scp.SCPException:
                return 910

        elif func == 'download':
            try:
                scp_conn.get(src, dst)
            except scp.SCPException:
                os.remove(dst)
                return 920

        else:
            return 998

    finally:
        scp_conn.close()
    return 0


def run(server_ip, locker_service_port, curve, server_verifying_key):
    locker_service_port = int(locker_service_port)

    # helper, one-time function
    def get_curve_by_name(curve_name):
        for c in curves.curves:
            if c.name == curve_name:
                return c
        return None

    # get ecdsa curve object
    curve_obj = get_curve_by_name(curve)
    # given invalid curve name
    if curve_obj is None:
        return False

    # start listener
    listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    listener.bind(('0.0.0.0', locker_service_port))
    listener.listen(2)

    while True:
        sock, addr = listener.accept()
        # auth server
        # check if connected ip is the server's ip
        if addr[0] != server_ip:
            sock.close()
            continue

        # verify server with public key
        aes_key = _ecdh_key_exchange(sock, curve_obj, server_verifying_key)
        if aes_key is None:
            sock.close()
            continue

        # receive parameters for scp transfer
        encrypted_scp_params = sock.recv(4096).decode()
        # e.g. user1\0user1pass\0upload\0C:\\test.txt\0/dir1/up_test.txt
        raw_scp_params = aes_key.decrypt(encrypted_scp_params)

        username, password, func, src, dst = raw_scp_params.split('\0')
        scp_ret = _scp_transfer(addr[0], username, password, func, src, dst)
        sock.send(str(scp_ret).encode())  # send return code of scp
        sock.close()


def main():
    if len(sys.argv) < 5:
        print('Usage:', 'python3', 'user_locker_service.py', '<ServerIP>', '<LockerServicePort>', '<Curve>',
              '<ServerVerifyingKey>')
        sys.exit(1)

    locker_service_thread = threading.Thread(target=run, args=(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]))
    locker_service_thread.run()
    sys.exit(0)


if __name__ == '__main__':
    main()
