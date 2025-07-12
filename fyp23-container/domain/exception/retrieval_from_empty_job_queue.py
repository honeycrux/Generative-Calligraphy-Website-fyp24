class RetrievalFromEmptyJobQueue(Exception):
    """
    Exception raised when there is an issue retrieving a job from an empty job queue.
    """

    message: str

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message
