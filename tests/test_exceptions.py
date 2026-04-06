from prismeai._exceptions import (
    PrismeAIError,
    AuthenticationError,
    PermissionDeniedError,
    NotFoundError,
    ConflictError,
    ValidationError,
    RateLimitError,
    InternalServerError,
    error_from_status,
)


def test_base_error():
    err = PrismeAIError("test error", status_code=400)
    assert str(err) == "test error"
    assert err.status_code == 400
    assert err.body is None


def test_authentication_error():
    err = AuthenticationError("unauthorized")
    assert err.status_code == 401


def test_error_from_status_401():
    err = error_from_status(401, "unauthorized")
    assert isinstance(err, AuthenticationError)


def test_error_from_status_403():
    err = error_from_status(403, "forbidden")
    assert isinstance(err, PermissionDeniedError)


def test_error_from_status_404():
    err = error_from_status(404, "not found")
    assert isinstance(err, NotFoundError)


def test_error_from_status_409():
    err = error_from_status(409, "conflict")
    assert isinstance(err, ConflictError)


def test_error_from_status_422():
    err = error_from_status(422, "invalid")
    assert isinstance(err, ValidationError)


def test_error_from_status_429():
    err = error_from_status(429, "rate limited", headers={"retry-after": "5"})
    assert isinstance(err, RateLimitError)
    assert err.retry_after == 5.0


def test_error_from_status_500():
    err = error_from_status(500, "server error")
    assert isinstance(err, InternalServerError)


def test_error_from_status_502():
    err = error_from_status(502, "bad gateway")
    assert isinstance(err, InternalServerError)


def test_error_from_status_unknown():
    err = error_from_status(418, "teapot")
    assert err.status_code == 418
