from functools import wraps
from zExceptions import BadRequest
from zExceptions import Forbidden
from zExceptions import InternalError
from zExceptions import MethodNotAllowed
from zExceptions import NotFound
from zExceptions import Unauthorized
from zope.component.hooks import getSite
import json
import sys
import transaction


class JSONRequestError(Exception):

    def __init__(self, error, status_code=500):
        self.error = error
        self.status_code = status_code


def json_response(request, data=None, **kwargs):
    request.response.setHeader('Content-Type', 'application/json')
    request.response.setHeader('X-Theme-Disabled', 'True')
    return json.dumps(data or kwargs)


def json_error_responses(func):
    def exception_response(status_code, error):
        request = getSite().REQUEST
        getSite().error_log.raising(sys.exc_info())
        transaction.doom()
        request.response.setStatus(status_code)
        return json_response(request, error=error, proceed=False)

    @wraps(func)
    def wrapper(self, REQUEST):
        try:
            return func(self, REQUEST)
        except BadRequest, exc:
            return exception_response(400, str(exc))
        except Unauthorized, exc:
            return exception_response(401, str(exc))
        except Forbidden, exc:
            return exception_response(403, str(exc))
        except NotFound, exc:
            return exception_response(404, str(exc))
        except MethodNotAllowed, exc:
            return exception_response(405, str(exc))
        except (InternalError, Exception), exc:
            return exception_response(500, repr(exc))

    return wrapper
