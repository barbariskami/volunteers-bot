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
    UNREGISTERED = 19
    MAIN_REQUEST = 20
    ENOUGH_EXECUTORS_NOTIFICATION = 21
    NEW_EXECUTOR_NOTIFICATION = 22
    TAKING_CONFIRMATION_FOR_EXECUTOR = 23
    REQUESTS_I_TOOK = 24
    REQUEST_INFO = 25,
    REQUESTS_I_TOOK_PENDING = 26
    REQUESTS_I_TOOK_FULFILLED = 27

    CREATION_MAIN_MENU = 101
    CREATION_MAIN_MENU_GREETING = 102
    CREATION_MAIN_MENU_GREETING_NEW = 103
    CREATION_UNREGISTERED = 104
    CREATION_NEW_REQUEST = 105
    CREATION_TYPE_TEXT = 106
    CREATION_MY_REQUESTS = 107
    CREATION_DRAFT_DELETED_SUCCESSFULLY = 108
    CREATION_CHOSE_DATE_TYPE = 109
    CREATION_SET_DATE = 110
    CREATION_SET_DATE_EARLY_DATE = 111
    CREATION_SET_DATE_FORMAT_ERROR = 112
    CREATION_SET_DATE_WRONG_DATE_ORDER = 113
    CREATION_SET_PEOPLE_NUMBER = 114
    CREATION_SET_PEOPLE_NUMBER_VALUE_ERROR = 115
    CREATION_SET_TAGS = 116
    CREATION_TAG_ADDED_TO_DRAFT = 117
    CREATION_TAG_DELETED_FROM_DRAFT = 118
    CREATION_SAVING_CONFIRMATION = 119
    CREATION_SUBMIT_OR_EDIT = 120
    CREATION_ASK_ABOUT_MODERATION = 121
    CREATION_SHOW_REQUEST_TEXT = 122
    CREATION_SUBMIT_REQUEST = 123
    CREATION_PUBLICATION_NOTIFICATION = 124
    CREATION_REQUEST_DISMISSED_NOTIFICATION = 125
    CREATION_DRAFTS_LIST = 126
    CREATION_REQUESTS_ON_MODERATION_LIST = 127
    CREATION_REQUESTS_WAITING_TO_BE_DONE_LIST = 128
    CREATION_FINISHED_REQUESTS_LIST = 129
    CREATION_EDIT_OR_SEND_SAVED_DRAFT = 130
    CREATION_REQUESTS_LIST_IS_EMPTY = 131
    CREATION_REQUEST_DRAFT = 132
    CREATION_CHOSE_FIELD_TO_EDIT = 133
    CREATION_CONFIRM_DRAFT_SUBMISSION = 134
    CREATION_CONFIRM_EDITED_DRAFT_DELETION = 135
    CREATION_EDIT_FIELD_NAME = 136
    CREATION_EDIT_FIELD_TEXT = 137
    CREATION_EDIT_FIELD_DATE_TYPE = 138
    CREATION_EDIT_FIELD_DATE = 139
    CREATION_EDIT_FIELD_PEOPLE_NUMBER = 140
    CREATION_EDIT_FIELD_TAGS = 141
    CREATION_REQUEST_AFTER_EDITING = 142
    CREATION_HELP = 143
    CREATION_SET_DATE_ONE_DATE_MISSING = 144

    MODERATION_UNREGISTERED = 201
    MODERATION_GREETING = 202
    MODERATION_ACCESS_DENIED = 203
    MODERATION_SEND_DRAFT = 204


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
    MAIN_REQUEST = 10
    REQUESTS_I_TOOK = 11
    REQUESTS_I_TOOK_PENDING = 12
    REQUESTS_I_TOOK_FULFILLED = 13
    HELP_HOW_TO_USE = 14

    CREATION_MAIN_MENU = 101
    CREATION_NEW_REQUEST = 102
    CREATION_MY_REQUESTS = 103
    CREATION_UNREGISTERED = 104
    CREATION_TYPE_TEXT = 105
    CREATION_CHOSE_DATE_TYPE = 106
    CREATION_SET_DATE = 107
    CREATION_SET_PEOPLE_NUMBER = 108
    CREATION_SET_TAGS = 109
    CREATION_SUBMIT_OR_EDIT = 110
    CREATION_ASK_ABOUT_MODERATION = 111
    CREATION_EDIT_DRAFT = 112
    CREATION_HELP = 113
    CREATION_DRAFTS_LIST = 114
    CREATION_REQUESTS_ON_MODERATION_LIST = 115
    CREATION_REQUESTS_WAITING_TO_BE_DONE_LIST = 116
    CREATION_FINISHED_REQUESTS_LIST = 117
    CREATION_EDIT_OR_SEND_SAVED_DRAFT = 118
    CREATION_CONFIRM_DRAFT_SUBMISSION = 119
    CREATION_CHOSE_FIELD_TO_EDIT = 120
    CREATION_CONFIRM_EDITED_DRAFT_DELETION = 121
    CREATION_EDIT_FIELD_NAME = 122
    CREATION_EDIT_FIELD_TEXT = 123
    CREATION_EDIT_FIELD_DATE_TYPE = 124
    CREATION_EDIT_FIELD_DATE = 125
    CREATION_EDIT_FIELD_PEOPLE_NUMBER = 126
    CREATION_EDIT_FIELD_TAGS = 127
    CREATION_HELP_REQUEST = 128
    CREATION_HELP_RULES = 129

    MODERATION_MAIN_MENU = 201


class MessageMarks(enum.Enum):
    """This is a list of all markers that can be applied to a message for giving an external program some special
    information about it."""
    UNREGISTERED = 1
    SUCCESSFUL_REGISTRATION = 2
    NO_ACCESS = 3


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
    DELETE_CURRENT_EDITED_DRAFT = 6
    SET_DATE_TYPE = 7
    ADD_TAG_TO_DRAFT = 8
    DELETE_TAG_FROM_DRAFT = 9
    PREVIOUS_PAGE = 10
    NEXT_PAGE = 11
    CREATION_SHOW_REQUEST_TEXT = 12
    CREATION_SEND_SAVING_CONFIRMATION = 13
    CREATION_SUBMIT_REQUEST = 14
    MODERATION_APPROVE_REQUEST = 15
    MODERATION_DISMISS_REQUEST = 16
    TAKE_REQUEST = 17
    DECLINE_REQUEST = 18
    CREATION_SET_EDITED_DRAFT = 19
    CREATION_SHOW_REQUEST_AFTER_EDITING = 20


class HashTags(enum.Enum):
    """A list of hash tags that requests can have"""
    IT = 1
    DESIGN = 2
    PUBLIC_PERFORMANCE = 3
    TRANSLATION = 4
    TEXT = 5
    PHOTO_VIDEO = 6
    MUSIC = 7
    VIDEO_EDITING = 8


class DateType(enum.Enum):
    DATE = 1
    DEADLINE = 2
    PERIOD = 3


class Bots(enum.Enum):
    MAIN = 1
    CREATION = 2
    MODERATION = 3
