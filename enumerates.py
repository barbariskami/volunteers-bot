import enum


class Media(enum.Enum):
    TELEGRAM = 1


class TextLabels(enum.Enum):
    MAIN_MENU = 1
    MAIN_MENU_GREETING = 2
    MAIN_MENU_GREETING_NEW = 3
    REGISTRATION = 4
    WRONG_PASSWORD = 5
    ALREADY_REGISTERED = 6


class States(enum.Enum):
    MAIN_MENU = 1


class MessageMarks(enum.Enum):
    UNREGISTERED = 1


class KeyboardTypes(enum.Enum):
    INLINE = 1
    REPLY = 2
