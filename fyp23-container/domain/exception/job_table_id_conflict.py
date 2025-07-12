class JobTableIDConflict(Exception):
    """
    Exception raised when there is an issue with job ID conflicts in the job table.
    """

    message: str

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message
