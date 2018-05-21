from handler import Handler

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk


class AppLogin:
    def __init__(self, builder, user):
        self._builder = builder
        self._user = user
        self._handler = Handler(self._builder, self._user)
        self._builder.connect_signals(self._handler)

        self.logged_in = False

        self._login_window = self._builder.get_object('applicationwindow_login')
        self._login_window.set_default_size(300, 225)
        self._login_window.set_title('Locker Login')
        self._login_window.connect('destroy', Gtk.main_quit)
        self._login_window.show_all()
        Gtk.main()

        self.logged_in = True
