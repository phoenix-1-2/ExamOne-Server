from rest_framework.exceptions import APIException


class ServiceUnavailableException(APIException):
    status_code = 503
    message = "Service temporarily unavailable, try again later."


class EmailNotVerfiedException(APIException):
    status_code = 401
    message = "Teacher Not Verfied. Please check your mail"


class AlreadyExistsException(APIException):
    status_code = 409
    message = "Resource Already exists"


class UnauthorizedException(APIException):
    status_code = 401
    message = "Unauthorized User"


class BadRequestException(APIException):
    status_code = 404
    message = "Bad Request"


class NotFoundException(APIException):
    status_code = 404
    default_detail = "Not Found"
    default_code = "not_found"
