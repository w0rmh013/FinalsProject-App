import json
import threading

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk


class Handler:
    def __init__(self, builder, user):
        self._builder = builder
        self._user = user
        self.logged_in = False
        self.last_location = ''

        self._updating_lock = threading.Lock()

    def handle_exec(self, command, handler_class_func):
        self._user.exec_command(command)
        output = self._user.get_output()
        handler_class_func(self, output)

    def update_statusbar(self, statusbar_name, context_name, status, flag=None, color=None):
        statusbar = self._builder.get_object(statusbar_name)
        context = statusbar.get_context_id(context_name)
        statusbar.pop(context)
        if color is not None and flag is not None:
            statusbar.override_color(flag, color)
        statusbar.push(context, status)

    def update_treeview_file_explorer(self, data):
        data_dict = json.loads(data)
        if type(data_dict) is not dict:
            pass
        liststore_file_explorer = self._builder.get_object('liststore_file_explorer')
        liststore_file_explorer.clear()

        # when we update treeview, we want to update the location bar as well
        entry_location = self._builder.get_object('entry_location')
        if self.last_location != data_dict['Path']:
            entry_location.set_text(data_dict['Path'])

        for d, info in data_dict['Directories'].items():
            liststore_file_explorer.append([d, info.get('Owner', '-'), info.get('Created', '-'),
                                            info.get('Last Modified', '-'), info.get('Size', 0), 'Directory'])

        for f, info in data_dict['Files'].items():
            liststore_file_explorer.append([f, info.get('Owner', '-'), info.get('Created', '-'),
                                            info.get('Last Modified', '-'), info.get('Size', 0), 'File'])

        for u, info in data_dict['Unknown Types'].items():
            liststore_file_explorer.append([u, info.get('Owner', '-'), info.get('Created', '-'),
                                            info.get('Last Modified', '-'), info.get('Size', 0), 'Unknown'])

    def update_location(self, data):
        entry_location = self._builder.get_object('entry_location')
        if data == '0':
            self.last_location = entry_location.get_text()
            self.update_statusbar('statusbar_action_feedback', 'feedback', 'OK', Gtk.StateFlags.NORMAL,
                                  Gdk.RGBA(0.2, 0.9, 0.2, 1.0))
        else:
            entry_location.set_text(self.last_location)
            self.update_statusbar('statusbar_action_feedback', 'feedback', 'ERROR ' + data, Gtk.StateFlags.NORMAL,
                                  Gdk.RGBA(1.0, 0.0, 0.0, 1.0))

    def on_treeview_file_explorer_button_press_event(self, treeview_file_explorer, event):
        if event.type == Gdk.EventType.BUTTON_PRESS:
            tree_selection = treeview_file_explorer.get_selection()
            path = treeview_file_explorer.get_path_at_pos(event.x, event.y)
            if path is None:
                return False
            tree_selection.select_path(path[0])

    def on_treeview_file_explorer_button_release_event(self, treeview_file_explorer, event):
        if event.type == Gdk.EventType.BUTTON_RELEASE and event.button == 3:
            tree_selection = treeview_file_explorer.get_selection()
            model, tree_iter = tree_selection.get_selected()
            value = model[tree_iter][:]
            if value[-1] == 'Directory':
                menu = self._builder.get_object('menu_drive_dir_right_click')
            elif value[-1] == 'File:':
                menu = self._builder.get_object('menu_drive_file_right_click')
            else:
                return
            menu.attach_to_widget(treeview_file_explorer)
            menu.show_all()
            menu.popup(None, None, None, None, event.button, event.time)

    def on_button_login_clicked(self, login_window):
        if self._builder is None or self._user is None:
            return

        entry_username = self._builder.get_object('entry_username')
        entry_password = self._builder.get_object('entry_password')
        self.logged_in = self._user.login(entry_username.get_text(), entry_password.get_text())

        if self.logged_in:
            login_window.destroy()
        else:
            if self.logged_in is None:
                context_name = 'server error'
                status = 'Could not connect to server'

            else:
                context_name = 'incorrect credentials'
                status = 'Username or password are incorrect'
                entry_password.set_text('')

            self.update_statusbar('statusbar_login', context_name, status, Gtk.StateFlags.NORMAL,
                                  Gdk.RGBA(1.0, 0.0, 0.0, 1.0))

        return True

    def on_button_go_clicked(self, entry_location):
        location = entry_location.get_text()
        print('LOCATION', location)
        self.handle_exec('cd \"{}\"'.format(location), Handler.update_location)
        self.handle_exec('ls', Handler.update_treeview_file_explorer)
