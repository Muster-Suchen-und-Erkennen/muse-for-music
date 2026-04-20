from http import HTTPStatus
from typing import NoReturn

from flask import abort as _flask_abort
from werkzeug.exceptions import HTTPException


# reimplementation of flask_restx.abort with proper type signature for pylance
def abort(
    code: HTTPStatus = HTTPStatus.INTERNAL_SERVER_ERROR, message=None, **kwargs
) -> NoReturn:
    """
    Properly abort the current request.

    Raise a `HTTPException` for the given status `code`.
    Attach any keyword arguments to the exception for later processing.

    :param int code: The associated HTTP status code
    :param str message: An optional details message
    :param kwargs: Any additional data to pass to the error payload
    :raise HTTPException:
    """
    try:
        _flask_abort(code)
    except HTTPException as e:
        if message:
            kwargs["message"] = str(message)
        if kwargs:
            e.data = kwargs  # type: ignore
        raise e
