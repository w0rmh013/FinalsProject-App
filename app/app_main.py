from handler import Handler

import threading

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk


class AppMain:
    def __init__(self, builder, user):
        self._builder = builder
        self._user = user
        self._handler = Handler(self._builder, self._user)
        self._builder.connect_signals(self._handler)

        self._user_run_thread = threading.Thread(target=self._user.run)
        self._user_run_thread.start()

        self._user_output_thread = threading.Thread(target=self._user.handle_output)
        self._user_output_thread.start()

        self._user.exec_command('ls')
        self._user.exec_command('space')
        self._user.exec_command('info')
        self._user.exec_command('create dir1')
        self._user.exec_command('cd dir1')
        self._user.exec_command('info')
        self._user.exec_command('ls user1@/')

        self._main_window = self._builder.get_object('applicationwindow_main')
        self._main_window.set_default_size(600, 450)
        self._main_window.set_title('Locker- {}'.format(self._user.username))
        self._main_window.connect('destroy', Gtk.main_quit)
        self._main_window.show_all()
        Gtk.main()

        self._user.logged_in = False
