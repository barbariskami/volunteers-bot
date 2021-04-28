import json
import os
from enumerates import KeyboardTypes, States, ButtonActions, DateType, Languages


class Keyboard:
    def __init__(self, language=Languages.RU, buttons=None, board_type=None, state=None, text_label=None, json_set=None,
                 delete_keyboard=False):
        self.DELETE = delete_keyboard
        if self.DELETE:
            return
        if buttons and board_type:
            self.buttons = buttons
            self.type = board_type
        elif state or text_label or json_set:
            if state:
                json_set = self.__class__.load_keyboard(state.name)
            elif text_label:
                json_set = self.__class__.load_keyboard(text_label.name)
            self.type = KeyboardTypes[json_set['type']]
            self.buttons = list()
            for line in json_set['buttons']:
                self.buttons.append(list())
                for button in line:
                    if self.type == KeyboardTypes.INLINE:
                        callback_data = button['info']['callback_data']
                    else:
                        callback_data = None
                    self.buttons[-1].append(
                        KeyboardButton(text=button.get(language.name, button['RU']),
                                       following_state=States[button['state']],
                                       info=button.get('info', dict()),
                                       callback_data=callback_data))
        else:
            raise ValueError

    def get_buttons(self):
        res = list()
        for line in self.buttons:
            for button in line:
                res.append(button.text)
        return res

    def get_button(self, text):
        res_button = None
        for line in self.buttons:
            for button in line:
                if button.text == text:
                    res_button = button
                    break
        return res_button

    @staticmethod
    def load_keyboard(state_name):
        cwd = os.getcwd().split('/')
        if cwd[-1] == 'telegram_bot':
            os.chdir('/'.join(cwd[:-1]))
        FILE_PATH = 'possible_keyboards.json'
        file = open(FILE_PATH, mode='r')
        data = json.load(file)
        file.close()
        keyboard = data['keyboards'][state_name]
        return keyboard


class KeyboardButton:
    def __init__(self, text, following_state, info, callback_data=None):
        self.text = text
        self.following_state = following_state
        self.info = info
        self.callback_data = callback_data
        self.actions = info.get('actions', list())
        for i in range(len(self.actions)):
            self.actions[i] = ButtonActions[self.actions[i]]
        if not self.info.get('ignore_standard_action', False):
            self.actions.append(ButtonActions.LOAD_STATE)
        if 'date_type' in self.info.keys():
            self.info['date_type'] = DateType[self.info['date_type']]
