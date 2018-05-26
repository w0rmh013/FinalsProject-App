import json

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk


class Handler:
    def __init__(self, builder, user):
        self._builder = builder
        self._user = user
        self.logged_in = False

        self.root_dir = ''
        self.location_history = list()

        self._icon_folder = Gtk.IconTheme.get_default().load_icon('folder-symbolic', 16, 0)
        self._icon_file = Gtk.IconTheme.get_default().load_icon('folder-documents-symbolic', 16, 0)
        self._icon_unknown = Gtk.IconTheme.get_default().load_icon('window-close-symbolic', 16, 0)

    def _format_perm(self, x):
        if x.startswith('rwx'):
            return 'View, Modify'
        if x.startswith('r'):
            return 'View'
        return '---'

    def _format_size(self, x):
        x = str(x)
        if x == '':
            return x
        seps = len(x) // 3
        seps_dict = {0: 'B', 1: 'KB', 2: 'MB', 3: 'GB', 4: 'TB'}
        return x[:-3*seps]+'.'+x[-3*seps:-3*seps+2]+seps_dict[seps]

    def _append_to_location_history(self, location):
        self.location_history = reduce(lambda lst, x: lst.append(x) or lst if x not in lst else lst,
                                       self.location_history, [location])

    def _do_nothing(self, data):
        pass

    def handle_exec(self, command, handler_class_func):
        self._user.exec_command(command)
        if command.lower().strip() == 'logout':
            self._user.logged_in = False
        else:
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
            if type(data_dict) is int:
                self.update_statusbar('statusbar_action_feedback', 'feedback', 'ERROR ' + data, Gtk.StateFlags.NORMAL,
                                      Gdk.RGBA(1.0, 0.0, 0.0, 1.0))
            return
        liststore_file_explorer = self._builder.get_object('liststore_file_explorer')
        liststore_file_explorer.clear()

        # when we update treeview, we want to update the location bar as well
        entry_location = self._builder.get_object('entry_location')
        entry_location.set_text(data_dict['Path'])

        liststore_file_explorer.append([self._icon_folder, '.', '', '', '', ''])
        liststore_file_explorer.append([self._icon_folder, '..', '', '', '', ''])

        for d, info in data_dict['Directories'].items():
            liststore_file_explorer.append([self._icon_folder, d, info.get('Owner', ''), info.get('Created', ''),
                                            info.get('Last Modified', ''), self._format_size(info.get('Size', ''))])

        for f, info in data_dict['Files'].items():
            liststore_file_explorer.append([self._icon_file, f, info.get('Owner', ''), info.get('Created', ''),
                                            info.get('Last Modified', ''), self._format_size(info.get('Size', ''))])

        for u, info in data_dict['Unknown Types'].items():
            liststore_file_explorer.append([self._icon_unknown, u, info.get('Owner', ''), info.get('Created', ''),
                                            info.get('Last Modified', ''), self._format_size(info.get('Size', ''))])

    def update_treeview_shared_file_explorer(self, data):
        data_dict = json.loads(data)

        liststore_shared_file_explorer = self._builder.get_object('liststore_shared_file_explorer')
        liststore_shared_file_explorer.clear()

        for d, info in data_dict['Directories'].items():
            perms = info.get('My Permissions', '---')
            liststore_shared_file_explorer.append([self._icon_folder, d, info.get('Owner', ''), self._format_perm(perms)
                                                   ])

        for f, info in data_dict['Files'].items():
            perms = info.get('My Permissions', '---')
            liststore_shared_file_explorer.append([self._icon_file, f, info.get('Owner', ''), self._format_perm(perms)])

        for u, info in data_dict['Unknown Types'].items():
            liststore_shared_file_explorer.append([self._icon_unknown, u, info.get('Owner', ''),
                                                   info.get('My Permissions', '---')])

    def update_treeview_edit_permissions(self, data):
        data_dict = json.loads(data)

        liststore_edit_permissions = self._builder.get_object('liststore_edit_permissions')
        liststore_edit_permissions.clear()

        label_edit_permissions_file = self._builder.get_object('label_edit_permissions_file')
        label_edit_permissions_file.set_text(data_dict['Path'])

        for u, p in data_dict['Permissions'].items():
            liststore_edit_permissions.append([u, self._format_perm(p)])

    def update_location(self, data):
        entry_location = self._builder.get_object('entry_location')
        if data == '0':
            self._append_to_location_history(entry_location.get_text())
            self.update_statusbar('statusbar_action_feedback', 'feedback', 'OK', Gtk.StateFlags.NORMAL,
                                  Gdk.RGBA(0.2, 0.9, 0.2, 1.0))
        else:
            entry_location.set_text(self.location_history[0])
            self.update_statusbar('statusbar_action_feedback', 'feedback', 'ERROR ' + data, Gtk.StateFlags.NORMAL,
                                  Gdk.RGBA(1.0, 0.0, 0.0, 1.0))

    def update_feedback(self, data):
        if data == '0':
            self.update_statusbar('statusbar_action_feedback', 'feedback', 'OK', Gtk.StateFlags.NORMAL,
                                  Gdk.RGBA(0.2, 0.9, 0.2, 1.0))
        else:
            self.update_statusbar('statusbar_action_feedback', 'feedback', 'ERROR ' + data, Gtk.StateFlags.NORMAL,
                                  Gdk.RGBA(1.0, 0.0, 0.0, 1.0))

    def update_space(self, data):
        data_dict = json.loads(data)
        label_space_used_percentage = self._builder.get_object('label_space_used_percentage')
        label_space_used_percentage.set_text(data_dict['Use%'])

    def update_help_detailed(self, data):
        textview_help_detailed = self._builder.get_object('textview_help_detailed')
        textbuffer = textview_help_detailed.get_buffer()
        textbuffer.set_text(data)

    def update_help_functions(self, data):
        textview_help = self._builder.get_object('textview_help')
        textbuffer = textview_help.get_buffer()
        textbuffer.set_text(data)

    def on_applicationwindow_main_destroy(self, applicationwindow_main):
        self.handle_exec('logout', self._do_nothing)
        applicationwindow_main.destroy()
        return True

    def on_dialog_destroy(self, dialog, event):
        dialog.hide()
        return True

    def on_treeview_file_explorer_button_press_event(self, treeview_file_explorer, event):
        if event.type == Gdk.EventType.DOUBLE_BUTTON_PRESS:
            tree_selection = treeview_file_explorer.get_selection()
            path = treeview_file_explorer.get_path_at_pos(event.x, event.y)
            if path is None:
                return False

            tree_selection.select_path(path[0])
            model, tree_iter = tree_selection.get_selected()
            value = model[tree_iter][:]

            # if user double-clicked a directory, we want to cd into it
            if value[0] == self._icon_folder:
                entry_location = self._builder.get_object('entry_location')
                new_location = '/'.join([entry_location.get_text(), value[1]])
                entry_location.set_text(new_location)

                self.handle_exec('cd\0{}'.format(new_location), Handler.update_location)
                self.handle_exec('ls', Handler.update_treeview_file_explorer)
                self.handle_exec('space', Handler.update_space)

    def on_treeview_file_explorer_button_release_event(self, treeview_file_explorer, event):
        if event.type == Gdk.EventType.BUTTON_RELEASE and event.button == 3:
            tree_selection = treeview_file_explorer.get_selection()
            model, tree_iter = tree_selection.get_selected()
            value = model[tree_iter][:]
            if value[1] == '..' or value[1] == '.':
                return
            if value[0] == self._icon_folder:
                menu = self._builder.get_object('menu_drive_dir')
            elif value[0] == self._icon_file:
                menu = self._builder.get_object('menu_drive_file')
            else:
                return
            if menu.get_attach_widget() is None:
                menu.attach_to_widget(treeview_file_explorer)
            menu.show_all()
            menu.popup(None, None, None, None, event.button, event.time)

    def on_treeview_shared_file_explorer_button_press_event(self, treeview_shared_file_explorer, event):
        if event.type == Gdk.EventType.DOUBLE_BUTTON_PRESS:
            tree_selection = treeview_shared_file_explorer.get_selection()
            path = treeview_shared_file_explorer.get_path_at_pos(event.x, event.y)
            if path is None:
                return False

            tree_selection.select_path(path[0])
            model, tree_iter = tree_selection.get_selected()
            value = model[tree_iter][:]

            # if user double-clicked a directory, we want to cd into it
            if value[0] == self._icon_folder:
                entry_location = self._builder.get_object('entry_location')
                new_location = value[1]
                entry_location.set_text(new_location)

                notebook_main = self._builder.get_object('notebook_main')
                notebook_main.set_current_page(0)

                self.handle_exec('cd\0{}'.format(new_location), Handler.update_location)
                self.handle_exec('ls', Handler.update_treeview_file_explorer)

    def on_treeview_shared_file_explorer_button_release_event(self, treeview_shared_file_explorer, event):
        if event.type == Gdk.EventType.BUTTON_RELEASE and event.button == 3:
            tree_selection = treeview_shared_file_explorer.get_selection()
            model, tree_iter = tree_selection.get_selected()
            value = model[tree_iter][:]
            if value[0] == self._icon_file:
                menu = self._builder.get_object('menu_shared_file')
            else:
                return
            if menu.get_attach_widget() is None:
                menu.attach_to_widget(treeview_shared_file_explorer)
            menu.show_all()
            menu.popup(None, None, None, None, event.button, event.time)

    def on_treeview_edit_permissions_button_release_event(self, treeview_edit_permissions, event):
        if event.type == Gdk.EventType.BUTTON_RELEASE and event.button == 3:
            menu = self._builder.get_object('menu_edit_permissions')
            if menu.get_attach_widget() is None:
                menu.attach_to_widget(treeview_edit_permissions)
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

        self.root_dir = '{}@/'.format(self._user.username)
        self._append_to_location_history(self.root_dir)
        return True

    def on_button_go_clicked(self, entry_location):
        location = entry_location.get_text()

        self.handle_exec('cd\0{}'.format(location), Handler.update_location)
        self.handle_exec('ls', Handler.update_treeview_file_explorer)
        self.handle_exec('space', Handler.update_space)

    def on_button_back_clicked(self, entry_location):
        self.location_history = self.location_history[1:]
        if len(self.location_history) == 0:
            self._append_to_location_history(self.root_dir)

        entry_location.set_text(self.location_history[0])

        self.handle_exec('cd\0{}'.format(self.location_history[0]), Handler.update_location)
        self.handle_exec('ls', Handler.update_treeview_file_explorer)
        self.handle_exec('space', Handler.update_space)

    def on_button_home_clicked(self, entry_location):
        entry_location.set_text(self.root_dir)

        self.handle_exec('cd\0{}'.format(self.root_dir), Handler.update_location)
        self.handle_exec('ls', Handler.update_treeview_file_explorer)
        self.handle_exec('space', Handler.update_space)

    def on_button_create_dir_clicked(self, dialog_create_dir):
        response = dialog_create_dir.run()
        dialog_create_dir.hide()
        entry_create_dir = self._builder.get_object('entry_create_dir')
        if response == Gtk.ResponseType.OK:
            self.handle_exec('create\0{}'.format(entry_create_dir.get_text()), Handler.update_feedback)
            self.handle_exec('ls', Handler.update_treeview_file_explorer)

        self.handle_exec('space', Handler.update_space)

        entry_create_dir.set_text('')

    def on_button_upload_clicked(self, filechooserdialog_transfer):
        filechooserdialog_transfer.set_action(Gtk.FileChooserAction.OPEN)
        filechooserdialog_transfer.set_title('Select a File to Upload')
        response = filechooserdialog_transfer.run()
        filechooserdialog_transfer.hide()

        if response == Gtk.ResponseType.OK:
            dialog_enter_password = self._builder.get_object('dialog_enter_password')
            label_enter_password = self._builder.get_object('label_enter_password')
            label_enter_password.set_text('Enter your password')
            password_dialog_response = dialog_enter_password.run()
            dialog_enter_password.hide()

            entry_enter_password = self._builder.get_object('entry_enter_password')
            if password_dialog_response == Gtk.ResponseType.OK:
                selected_filename = filechooserdialog_transfer.get_filename()

                password = entry_enter_password.get_text()
                self.handle_exec('upload\0{}\0.\0{}'.format(selected_filename, password), Handler.update_feedback)
                self.handle_exec('ls', Handler.update_treeview_file_explorer)

            entry_enter_password.set_text('')

        self.handle_exec('space', Handler.update_space)

    def on_button_confirm_changes_clicked(self, button):
        entry_current_password = self._builder.get_object('entry_current_password')
        entry_new_password = self._builder.get_object('entry_new_password')
        entry_confirm_password = self._builder.get_object('entry_confirm_password')

        self.handle_exec('passwd\0{}\0{}\0{}'.format(entry_current_password.get_text(),
                                                     entry_new_password.get_text(),
                                                     entry_confirm_password.get_text()), Handler.update_feedback)

        entry_current_password.set_text('')
        entry_new_password.set_text('')
        entry_confirm_password.set_text('')

    def on_button_help_detailed_clicked(self, entry_help_function):
        self.handle_exec('help\0{}'.format(entry_help_function.get_text()), Handler.update_help_detailed)

    def on_notebook_main_switch_page(self, notebook_main, switched_page, switched_page_num):
        # drive tab
        if switched_page_num == 0:
            self.handle_exec('ls', Handler.update_treeview_file_explorer)

        # shared with me tab
        elif switched_page_num == 1:
            self.handle_exec('shared', Handler.update_treeview_shared_file_explorer)

        elif switched_page_num == 2:
            entry_current_password = self._builder.get_object('entry_current_password')
            entry_new_password = self._builder.get_object('entry_new_password')
            entry_confirm_password = self._builder.get_object('entry_confirm_password')
            entry_current_password.set_text('')
            entry_new_password.set_text('')
            entry_confirm_password.set_text('')


    def on_imagemenuitem_logout_activate(self, applicationwindow_main):
        self.on_applicationwindow_main_destroy(applicationwindow_main)

    def on_imagemenuitem_help_activate(self, dialog_help):
        dialog_help.set_default_size(320, 240)
        dialog_help.run()
        dialog_help.hide()

    def on_menuitem_permit_activate(self, treeview_selection_file_explorer):
        dialog_edit_permissions = self._builder.get_object('dialog_edit_permissions')
        dialog_edit_permissions.set_default_size(300, 225)

        model, tree_iter = treeview_selection_file_explorer.get_selected()
        value = model[tree_iter][:]

        self.handle_exec('info\0{}'.format(value[1]), Handler.update_treeview_edit_permissions)
        dialog_edit_permissions.run()
        dialog_edit_permissions.hide()

    def on_menuitem_delete_activate(self, treeview_selection_file_explorer):
        model, tree_iter = treeview_selection_file_explorer.get_selected()
        value = model[tree_iter][:]

        self.handle_exec('delete\0{}'.format(value[1]), Handler.update_feedback)
        self.handle_exec('ls', Handler.update_treeview_file_explorer)
        self.handle_exec('space', Handler.update_space)

    def on_menuitem_file_download_activate(self, treeview_selection):
        filechooserdialog_transfer = self._builder.get_object('filechooserdialog_transfer')
        filechooserdialog_transfer.set_action(Gtk.FileChooserAction.SAVE)
        filechooserdialog_transfer.set_title('Select Download Destination')
        response = filechooserdialog_transfer.run()
        filechooserdialog_transfer.hide()

        model, tree_iter = treeview_selection.get_selected()
        value = model[tree_iter][:]
        src = value[1]

        if response == Gtk.ResponseType.OK:
            dialog_enter_password = self._builder.get_object('dialog_enter_password')
            label_enter_password = self._builder.get_object('label_enter_password')
            label_enter_password.set_text('Enter your password')
            password_dialog_response = dialog_enter_password.run()
            dialog_enter_password.hide()

            entry_enter_password = self._builder.get_object('entry_enter_password')
            if password_dialog_response == Gtk.ResponseType.OK:
                dst = filechooserdialog_transfer.get_filename()

                password = entry_enter_password.get_text()
                self.handle_exec('download\0{}\0{}\0{}'.format(src, dst, password), Handler.update_feedback)
                self.handle_exec('ls', Handler.update_treeview_file_explorer)

            entry_enter_password.set_text('')

        self.handle_exec('space', Handler.update_space)

    def on_menuitem_file_lock_activate(self, treeview_selection_file_explorer):
        dialog_enter_password = self._builder.get_object('dialog_enter_password')
        label_enter_password = self._builder.get_object('label_enter_password')
        label_enter_password.set_text('Enter lock password')
        response = dialog_enter_password.run()
        dialog_enter_password.hide()

        entry_enter_password = self._builder.get_object('entry_enter_password')
        if response == Gtk.ResponseType.OK:
            model, tree_iter = treeview_selection_file_explorer.get_selected()
            value = model[tree_iter][:]

            name = value[1]
            password = entry_enter_password.get_text()
            self.handle_exec('lock\0{}\0{}'.format(name, password), Handler.update_feedback)
            self.handle_exec('ls', Handler.update_treeview_file_explorer)

        self.handle_exec('space', Handler.update_space)
        entry_enter_password.set_text('')

    def on_menuitem_file_unlock_activate(self, treeview_selection_file_explorer):
        dialog_enter_password = self._builder.get_object('dialog_enter_password')
        label_enter_password = self._builder.get_object('label_enter_password')
        label_enter_password.set_text('Enter unlock password')
        response = dialog_enter_password.run()
        dialog_enter_password.hide()

        entry_enter_password = self._builder.get_object('entry_enter_password')
        if response == Gtk.ResponseType.OK:
            model, tree_iter = treeview_selection_file_explorer.get_selected()
            value = model[tree_iter][:]

            name = value[1]
            password = entry_enter_password.get_text()
            self.handle_exec('unlock\0{}\0{}'.format(name, password), Handler.update_feedback)
            self.handle_exec('ls', Handler.update_treeview_file_explorer)

        self.handle_exec('space', Handler.update_space)
        entry_enter_password.set_text('')

    def on_menuitem_add_activate(self, dialog_give_permission):
        label_edit_permissions_file = self._builder.get_object('label_edit_permissions_file')
        name = label_edit_permissions_file.get_text()
        dialog_give_permission.set_title('Edit Permissions for: {}'.format(name))

        response = dialog_give_permission.run()
        dialog_give_permission.hide()

        entry_perm_username = self._builder.get_object('entry_perm_username')
        radiobutton_view = self._builder.get_object('radiobutton_view')
        radiobutton_view_and_modify = self._builder.get_object('radiobutton_view_and_modify')

        if response == Gtk.ResponseType.OK:
            if radiobutton_view.get_active():
                self.handle_exec('permit\0{}:rx\0{}'.format(entry_perm_username.get_text(), name), Handler._do_nothing)

            elif radiobutton_view_and_modify.get_active():
                self.handle_exec('permit\0{}:rwx\0{}'.format(entry_perm_username.get_text(), name), Handler._do_nothing)

            self.handle_exec('info\0{}'.format(name), Handler.update_treeview_edit_permissions)

        entry_perm_username.set_text('')

    def on_menuitem_remove_activate(self, treeview_selection_edit_permissions):
        model, tree_iter = treeview_selection_edit_permissions.get_selected()
        if tree_iter is None:
            return

        label_edit_permissions_file = self._builder.get_object('label_edit_permissions_file')
        name = label_edit_permissions_file.get_text()

        value = model[tree_iter][:]
        self.handle_exec('permit\0{}:---\0{}'.format(value[0], name), Handler._do_nothing)
        self.handle_exec('info\0{}'.format(name), Handler.update_treeview_edit_permissions)

    def on_entry_activate(self, ok_button):
        ok_button.clicked()
