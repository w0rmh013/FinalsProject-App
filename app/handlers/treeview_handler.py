import json

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk


class TreeViewHandler:
    _builder = None
    _user = None
    last_location = ''

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

    def update_treeview_file_explorer(self, data):
        data_dict = json.loads(data)
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

