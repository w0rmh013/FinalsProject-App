from app.app_login import AppLogin
from app.app_main import AppMain
from logical_app import User

import json

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk


def main():
    builder = Gtk.Builder()
    builder.add_from_file('app_design_new.glade')

    with open('locker_server_params.json', 'r') as f:
        params = json.load(f)
    user = User(params['ServerIP'], str(params['LockerServicePort']), params['Curve'], params['ServerVerifyingKey'],
                params['LockerAppSSHPort'])

    app_login = AppLogin(builder, user)
    if app_login.logged_in:
        AppMain(builder, user)


if __name__ == '__main__':
    main()
