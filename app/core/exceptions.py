class TripMateException(Exception):
    """Base exception for TripMate."""

    def __init__(
        self,
        message: str,
        error_code: str = "TRIPMATE_ERROR"
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code


class LLMException(TripMateException):
    pass


class MCPException(TripMateException):
    pass


class DatabaseException(TripMateException):
    pass


class AgentException(TripMateException):
    pass


class WorkflowException(TripMateException):
    pass