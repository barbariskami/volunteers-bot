class DataBaseException(Exception):
    pass


class UserNotFound(DataBaseException):
    message = 'User is not found'


class RegistrationException(Exception):
    pass


class AlreadyRegistered(RegistrationException):
    pass
