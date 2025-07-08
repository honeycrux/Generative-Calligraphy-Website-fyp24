class JobQueueAccessException(Exception):
    """
    Exception raised when there is an issue storing or retrieving a job in the job table.
    """

    message: str

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message
