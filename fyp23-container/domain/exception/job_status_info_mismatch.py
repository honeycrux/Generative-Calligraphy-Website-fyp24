class JobStatusInfoMismatch(Exception):
    """
    Exception raised when there is a mismatch in job status information.
    This can occur when the status of a job does not match the expected status.
    """

    message: str

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message
