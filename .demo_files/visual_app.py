import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk


builder = Gtk.Builder()
builder.add_from_file('app_design_new.glade')

LOGGED_IN = False


# Button signal handlers
def on_button_login_activate(applicationwindow_login):
    global LOGGED_IN
    entry_username = builder.get_object('entry_username')
    entry_password = builder.get_object('entry_password')
    print(entry_username.get_text(), entry_password.get_text())
    LOGGED_IN = True
    if LOGGED_IN:
        applicationwindow_login.destroy()


def on_button_home_activate():
    pass


def on_button_back_activate():
    pass


def on_button_upload_activate():
    pass


def on_button_create_dir_activate():
    pass


def on_button_confirm_changes_activate():
    pass

# End of Button signal handlers


# Image Menu Item signal handlers
def on_imagemenuitem_logout_activate():
    pass


def on_imagemenuitem_help_activate():
    pass

# End of Image Menu Item signal handlers


# Menu Item signal handlers
def on_menuitem_permit_activate():
    pass


def on_menuitem_show_info_activate():
    pass


def on_menuitem_dir_delete_activate():
    pass


def on_menuitem_file_delete_activate():
    pass


def on_menuitem_file_download_activate():
    pass


def on_menuitem_file_lock_activate():
    pass


def on_menuitem_file_unlock_activate():
    pass

# End of Menu Item signal handlers


# Treeview signal handlers
def on_treeview_file_explorer_button_press_event(treeview, event):
    if event.type == Gdk.EventType.BUTTON_PRESS:
        tree_selection = treeview.get_selection()
        path = treeview.get_path_at_pos(event.x, event.y)
        if path is None:
            return False
        tree_selection.select_path(path[0])

        # right mouse button was clicked
        if event.button == 3:
            model, tree_iter = tree_selection.get_selected()
            value = model[tree_iter][:]
            print(value)


def on_treeview_file_explorer_button_release_event(treeview, event):
    if event.type == Gdk.EventType.BUTTON_RELEASE and event.button == 3:
        menu = builder.get_object('menu_drive_dir_right_click')
        menu.attach_to_widget(treeview)
        menu.show_all()
        menu.popup(None, None, None, None, event.button, event.time)

# End of Treeview signal handlers


def main():
    handlers = {
        'on_button_login_activate': on_button_login_activate,
        'on_button_upload_activate': on_button_upload_activate,
        'on_button_home_activate': on_button_home_activate,
        'on_button_back_activate': on_button_back_activate,
        'on_button_create_dir_activate': on_button_create_dir_activate,
        'on_button_confirm_changes_activate': on_button_confirm_changes_activate,
        'on_imagemenuitem_logout_activate': on_imagemenuitem_logout_activate,
        'on_imagemenuitem_help_activate': on_imagemenuitem_help_activate,
        'on_menuitem_permit_activate': on_menuitem_permit_activate,
        'on_menuitem_show_info_activate': on_menuitem_show_info_activate,
        'on_menuitem_dir_delete_activate': on_menuitem_dir_delete_activate,
        'on_menuitem_file_delete_activate': on_menuitem_file_delete_activate,
        'on_menuitem_file_download_activate': on_menuitem_file_download_activate,
        'on_menuitem_file_lock_activate': on_menuitem_file_lock_activate,
        'on_menuitem_file_unlock_activate': on_menuitem_file_unlock_activate,
        'on_treeview_file_explorer_button_press_event': on_treeview_file_explorer_button_press_event,
        'on_treeview_file_explorer_button_release_event': on_treeview_file_explorer_button_release_event
    }
    builder.connect_signals(handlers)

    # login window
    window = builder.get_object('applicationwindow_login')
    window.set_default_size(300, 225)
    window.set_title('Locker Login')
    window.connect('destroy', Gtk.main_quit)
    window.show_all()
    Gtk.main()

    # main window
    if LOGGED_IN:
        window = builder.get_object('applicationwindow_main')
        window.set_default_size(600, 450)
        window.connect('destroy', Gtk.main_quit)
        window.show_all()
        Gtk.main()


if __name__ == '__main__':
    main()
