from rest_framework.exceptions import APIException


class APIBadRequest(APIException):
    status_code = 400
