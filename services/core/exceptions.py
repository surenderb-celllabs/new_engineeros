class AuthError(Exception):
    """Raised when authentication fails."""


class UserExistsError(Exception):
    """Raised when trying to create a user that already exists."""


class UserNotFoundError(Exception):
    """Raised when user lookup fails."""


class ResourceNotFoundError(Exception):
    """Raised when a resource does not exist."""


class PermissionDeniedError(Exception):
    """Raised when a user does not have permission to access a resource."""
