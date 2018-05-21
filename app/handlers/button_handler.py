import gi
gi.require_version('Gtk', '3.0')


class ButtonHandler:
    _builder = None
    _user = None

    def on_button_login_clicked(self, login_window):
        if self._builder is None or self._user is None:
            return

        entry_username = self._builder.get_object('entry_username')
        entry_password = self._builder.get_object('entry_password')
        print(entry_username.get_text(), entry_password.get_text())
