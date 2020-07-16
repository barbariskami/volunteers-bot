import json
from enumerates import KeyboardTypes


class Keyboard:
    def __init__(self, buttons=None, board_type=None, language=None, state=None, json_set=None):
        if buttons and board_type and language:
            self.buttons = buttons
            self.type = board_type
        elif state or json_set:
            if state:
                json_set = self.__class__.load_keyboard(state.name)
            self.buttons = list()
            for line in json_set['buttons']:
                self.buttons.append(list())
                for button in line:
                    self.buttons[-1].append(
                        KeyboardButton(text=button.get(language.name, button['RU']), following_state=button['state']))
            self.type = KeyboardTypes[json_set['type']]
        else:
            raise ValueError

    def get_buttons(self):
        res = list()
        for button in self.buttons:
            res.append(button.text)
        return res

    @staticmethod
    def load_keyboard(state_name):
        FILE_PATH = 'possible_keyboards.json'
        file = open(FILE_PATH, mode='r')
        data = json.load(file)
        file.close()
        keyboard = data['keyboards'][state_name]
        return keyboard


class KeyboardButton:
    def __init__(self, text, following_state):
        self.text = text
        self.following_state = following_state
