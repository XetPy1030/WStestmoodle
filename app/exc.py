from django.core.exceptions import ObjectDoesNotExist
from rest_framework.exceptions import ValidationError
from rest_framework.views import exception_handler


def handler(exc, context):
    if isinstance(exc, ObjectDoesNotExist):
        exc.status_code = 404
        exc.detail = 'Object not found'
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
