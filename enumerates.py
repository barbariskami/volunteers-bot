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
    HELP = 7
    SETTINGS = 8
    CHOSE_LANGUAGE = 9
    LANGUAGE_SWITCHED_SUCCESSFULLY = 10
    IGNORE_SETTINGS = 11
    EMPTY_LIST = 12
    CHOSE_TAG_ADDING = 13
    CHOSE_TAG_DELETION = 14
    TAG_DELETED_FROM_IGNORE = 15
    TAG_ADDED_INTO_IGNORE = 16
    HELP_FAQ = 17
    HELP_ABOUT_REQUEST = 18


class States(enum.Enum):
    """This enumerator lists all the states the user can has. These states are a kind of spots on the tree of a dialog,
    for example main_menu or choosing_task_draft"""
    MAIN_MENU = 1
    SETTINGS = 2
    HELP = 3
    CHOSE_LANGUAGE = 4
    IGNORE_SETTINGS = 5
    CHOSE_TAG_ADDING = 6
    CHOSE_TAG_DELETION = 7
    HELP_FAQ = 8
    HELP_ABOUT_REQUEST = 9


class MessageMarks(enum.Enum):
    """This is a list of all markers that can be applied to a message for giving an external program some special
    information about it."""
    UNREGISTERED = 1
    SUCCESSFUL_REGISTRATION = 2


class KeyboardTypes(enum.Enum):
    """Here are two types of a keyboard. They are taken from Telegram api and the info about it can be found in
    python-telegram-bot library docs"""
    INLINE = 1  # appears inside a message
    REPLY = 2  # is not connected with a message


class Languages(enum.Enum):
    """All the languages that are available in the bot"""
    RU = 1
    EN = 2


class ButtonActions(enum.Enum):
    LOAD_STATE = 1  # For all simple buttons that just change the state of a user
    SWITCH_LANGUAGE = 2
    FORM_MESSAGE = 3
    ADD_TAG = 4
    DELETE_TAG = 5


class HashTags(enum.Enum):
    """A list of hash tags that requests can have"""
    OUTSIDE = 1
    LIBRARY = 2
    THEATRE = 3
    DRAWING = 4
    BOARDING = 5
    SCHOOL_OPEN_DAY = 6
    SELF_GOVERNANCE = 7
