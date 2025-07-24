class LoggedOutError(Exception):
    def __init__(
        self,
        message="Spotify User not logged in",
        error_type="LoggedOutError",
        status_code=401,
    ):
        self.message = message
        self.error_type = error_type
        self.status_code = status_code
        super().__init__(message)


class SpotifyAPIError(Exception):
    def __init__(
        self,
        message="Internal error when fetching from Spotify API",
        error_type="SpotifyAPIError",
        status_code=502,
    ):
        self.message = message
        self.error_type = error_type
        self.status_code = status_code
        super().__init__(message)


class ClientError(Exception):
    def __init__(self, message, error_type="ClientError", status_code=400):
        self.message = message
        self.erorr_type = error_type
        self.status_code = status_code
        super().__init__(message)


class NotFoundError(Exception):
    def __init__(self, message, error_type="NotFoundError", status_code=404):
        self.message = message
        self.erorr_type = error_type
        self.status_code = status_code
        super().__init__(message)
