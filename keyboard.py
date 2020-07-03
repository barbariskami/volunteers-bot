class Keyboard:
    def __init__(self, buttons, board_type):
        self.buttons = buttons
        self.type = board_type


class KeyboardButton:
    def __init__(self, text, following_state):
        self.text = text
        self.following_state = following_state


class InlineKeyboardButton:
    def __init__(self, text, following_state, url=None):
        self.text = text
        self.following_state = following_state