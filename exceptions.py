class DataBaseException(Exception):
    # Exception that is raised if some problems happen during loading data from a base. Base class for more specific
    # exceptions connected with databases
    pass


class UserNotFound(DataBaseException):
    # A child class inherited from DataBaseException. R if during searching for a user by specific parameters
    # the user wasn't found.
    message = 'User is not found'


class RegistrationException(Exception):
    # A father-class for all exceptions raised during registration process
    pass


class AlreadyRegistered(RegistrationException):
    # A child class of RegistrationException, that is raised if someone has already registered his media-account for
    # a certain record in the system-database.
    pass


class LoadingException(Exception):
    pass


class MessageTextNotFoundInFile(LoadingException):
    pass


class DateError(Exception):
    pass


class DateFormatError(DateError):
    pass


class EarlyDate(DateError):
    pass


class WrongDateOrder(DateError):
    pass


class OneDateMissing(DateError):
    pass


class TagNotFound(DataBaseException):
    pass


class TagCodeValueError(ValueError):
    pass


class TagNotAllLanguages(ValueError):
    pass


class TagDuplicateValue(ValueError):
    pass
