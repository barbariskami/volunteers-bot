import enum


class Media(enum.Enum):
    """Enumerates all media and platforms this bot works with"""
    TELEGRAM = 1


class TextLabels(enum.Enum):
    """Enumerates all the Texts that can be sent to a user by the bot. They are used for specifying pieces of text
    that must be loaded from a file and sent to a user."""
    MAIN_MENU = 1
    MAIN_MENU_GREETING = 2
    MAIN_MENU_GREETING_NEW = 3
    REGISTRATION = 4
    WRONG_PASSWORD = 5
    ALREADY_REGISTERED = 6


class States(enum.Enum):
    """This enumerator lists all the states the user can has. These states are a kind of spots on the tree of a dialog,
    for example main_menu or choosing_task_draft"""
    MAIN_MENU = 1
    SETTINGS = 2
    HELP = 3


class MessageMarks(enum.Enum):
    """This is a list of all markers that can be applied to a message for giving an external program some special
    information about it."""
    UNREGISTERED = 1
    SUCCESSFUL_REGISTRATION = 2
    KEYBOARD = 3


class KeyboardTypes(enum.Enum):
    """Here are two types of a keyboard. They are taken from Telegram api and the info about it can be found in
    python-telegram-bot library docs"""
    INLINE = 1  # appears inside a message
    REPLY = 2  # is not connected with a message


class Languages(enum.Enum):
    """All the languages that are available in the bot"""
    RU = 1
    EN = 2
