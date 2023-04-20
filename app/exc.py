from django.core.exceptions import ObjectDoesNotExist
from rest_framework.exceptions import ValidationError, APIException
from rest_framework.views import exception_handler


class AppException(APIException):
    def __init__(self, detail, status_code):
        super().__init__(detail)
        self.status_code = status_code


def handler(exc, context):
    if isinstance(exc, ObjectDoesNotExist):
        exc = AppException(f'Объект не найден', 404)
    if isinstance(exc, ValidationError):
        exc.detail = {
            'error': {
                'code': 422,
                'message': 'Нарушение правил валидации',
                'errors': exc.detail
            }
        }
        exc.status_code = 422
    elif hasattr(exc, 'status_code'):
        exc.detail = {
            'error': {
                'code': exc.status_code,
                'message': exc.detail
            }
        }
    return exception_handler(exc, context)
