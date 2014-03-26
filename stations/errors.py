class StationError(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return 'Error: ' + self.message


class AdapterParsingError(StationError):
    def __str__(self):
        return 'Parsing error: ' + self.message


class AdapterFetchingError(StationError):
    def __init__(self, url, message):
        self.url = url
        self.message = message
        
    def __str__(self):
        message = 'Parsing error: ' + self.message
        message += '\nError URL: ' + self.url
        return message