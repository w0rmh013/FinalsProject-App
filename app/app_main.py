from handler import Handler

import threading

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk


class AppMain:
    def __init__(self, builder, user):
        self._builder = builder
        self._user = user
        self._handler = Handler(self._builder, self._user)
        self._builder.connect_signals(self._handler)

        self._user_run_thread = threading.Thread(target=self._user.run)
        self._user_run_thread.start()

        self._handler.handle_exec('ls', self._handler.__class__.update_treeview_file_explorer)
        self._handler.handle_exec('space', self._handler.__class__.update_space)

        # set dnd
        treeview_file_explorer = self._builder.get_object('treeview_file_explorer')
        treeview_file_explorer.enable_model_drag_source(Gdk.ModifierType.BUTTON1_MASK, list(), Gdk.DragAction.COPY)
        treeview_file_explorer.drag_dest_set(Gtk.DestDefaults.ALL, list(), Gdk.DragAction.COPY)
        treeview_file_explorer.drag_dest_add_text_targets()
        treeview_file_explorer.drag_source_add_text_targets()

        self._main_window = self._builder.get_object('applicationwindow_main')
        self._main_window.set_default_size(600, 450)
        self._main_window.set_title('Locker- {}'.format(self._user.username))
        self._main_window.connect('destroy', Gtk.main_quit)
        self._main_window.show_all()
        Gtk.main()

        self._user.logged_in = False
