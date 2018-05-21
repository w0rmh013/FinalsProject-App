from handlers.button_handler import ButtonHandler
from handlers.imagemenuitem_handler import ImageMenuItemHandler
from handlers.menuitem_handler import MenuItemHandler
from handlers.treeview_handler import TreeViewHandler


class Handler(ButtonHandler, ImageMenuItemHandler, MenuItemHandler, TreeViewHandler):
    def __init__(self, builder, user):
        self._builder = builder
        self._user = user
