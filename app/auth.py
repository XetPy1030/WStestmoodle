from rest_framework.authentication import TokenAuthentication


class Auth(TokenAuthentication):
    keyword = 'Bearer'
