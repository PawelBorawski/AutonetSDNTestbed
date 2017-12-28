class XMLValidationError(Exception):
    def __init__(self):
        self.message = 'XML is not well-formed.'

    def __str__(self):
        return repr(self.message)


class MininetIsBusyError(Exception):
    def __init__(self):
        self.message = 'Mininet is busy. Wait until test ends up.'

    def __str__(self):
        return repr(self.message)