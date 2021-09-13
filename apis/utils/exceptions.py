from rest_framework.exceptions import APIException


class ServiceUnavailableException(APIException):
    status_code = 503
    default_detail = "Service temporarily unavailable, try again later."
    default_code = "service_unavailable"


class UnauthorizedException(APIException):
    status_code = 401
    default_detail = "Unauthorized User"
    default_code = "unauthorized_user"
