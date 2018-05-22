import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk


class ButtonHandler:
    _builder = None
    _user = None
    logged_in = False
    _last_location = ''

    def on_button_login_clicked(self, login_window):
        if self._builder is None or self._user is None:
            return

        entry_username = self._builder.get_object('entry_username')
        entry_password = self._builder.get_object('entry_password')
        self.logged_in = self._user.login(entry_username.get_text(), entry_password.get_text())

        if self.logged_in:
            login_window.destroy()
        else:
            statusbar_login = self._builder.get_object('statusbar_login')
            statusbar_login.override_color(Gtk.StateFlags.NORMAL, Gdk.RGBA(1.0, 0.0, 0.0, 1.0))

            if self.logged_in is None:
                context_name = 'server error'
                status = 'Could not connect to server'

            else:
                context_name = 'incorrect credentials'
                status = 'Username or password are incorrect'

            context_id = statusbar_login.get_context_id(context_name)
            statusbar_login.pop(context_id)
            statusbar_login.push(context_id, status)
            entry_password.set_text('')

        return True

    def on_button_go_clicked(self, entry_location):
        location = entry_location.get_text()
        self._user.exec_command('cd \"{}\"'.format(location), self.update_location)

    def update_location(self, data):
        entry_location = self._builder.get_object('entry_location')
        statusbar_action_feedback = self._builder.get_object('statusbar_action_feedback')
        context_id = statusbar_action_feedback.get_context_id('feedback')
        statusbar_action_feedback.pop(context_id)

        if data == '0':
            self.last_location = entry_location.get_text()
            statusbar_action_feedback.override_color(Gtk.StateFlags.NORMAL, Gdk.RGBA(0.2, 0.9, 0.2, 1.0))
            self._user.exec_command('ls \"{}\"'.format(self.last_location), self.update_treeview_file_explorer)
            statusbar_action_feedback.push(context_id, 'OK')
        else:
            entry_location.set_text(self.last_location)
            statusbar_action_feedback.override_color(Gtk.StateFlags.NORMAL, Gdk.RGBA(1.0, 0.0, 0.0, 1.0))
            statusbar_action_feedback.push(context_id, 'ERROR ' + data)
