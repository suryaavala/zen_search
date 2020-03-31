class PrimaryKeyNotFoundError(Exception):
    def __init__(self, *args):
        if args:
            self.message = args[0]
        else:
            self.message = None
        self.default_message = "Cannot find primary key in the data point. Every data point should at least have primary key"

    def __str__(self):
        if self.message:
            return f"{self.message}"
        else:
            return self.default_message


class DuplicatePrimaryKeyError(PrimaryKeyNotFoundError):
    def __init__(self, *args):
        super().__init__(*args)
        self.default_message = "Duplicate primary key value found in the data point. It's been assumed that every entity should have a unique set of primary keys"

    def __str__(self):
        return super().__str__()
