from uuid import UUID


class AppException(Exception):
    def __init__(
        self,
        message: str = "An unexpected error occurred",
        code: str = "app_error",
        details: dict | None = None,
    ):
        self.message = message
        self.code = code
        self.details = details
        super().__init__(self.message)


class NotFoundException(AppException):
    def __init__(
        self,
        resource: str = "Resource",
        id: UUID | str | None = None,
        details: dict | None = None,
    ):
        message = f"{resource} not found"
        if id is not None:
            message = f"{resource} {id} not found"
        super().__init__(message=message, code="not_found", details=details)


class ForbiddenException(AppException):
    def __init__(
        self,
        action: str | None = None,
        details: dict | None = None,
    ):
        message = "Forbidden"
        if action is not None:
            message = f"Forbidden: {action}"
        super().__init__(message=message, code="forbidden", details=details)


class TenantMismatchException(AppException):
    def __init__(self, details: dict | None = None):
        super().__init__(
            message="Tenant mismatch or missing tenant context",
            code="tenant_mismatch",
            details=details,
        )


class ValidationException(AppException):
    def __init__(
        self,
        message: str = "Validation error",
        details: dict | None = None,
    ):
        super().__init__(message=message, code="validation_error", details=details)


class UnauthorizedException(AppException):
    def __init__(
        self,
        message: str = "Unauthorized",
        details: dict | None = None,
    ):
        super().__init__(message=message, code="unauthorized", details=details)


class RateLimitException(AppException):
    def __init__(
        self,
        message: str = "Too many requests",
        retry_after: int = 60,
        details: dict | None = None,
    ):
        super().__init__(
            message=message, code="rate_limit", details={"retry_after": retry_after, **(details or {})}
        )
