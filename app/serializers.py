from django.contrib.auth import authenticate
from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework.exceptions import APIException

from app.exc import AppException
from app.models import User, Product, Order


class LoginSerializer(AuthTokenSerializer):
    email = serializers.CharField(
        write_only=True
    )
    username = None

    def validate(self, attrs):
        username = attrs.get('email')
        password = attrs.get('password')

        if username and password:
            user = authenticate(request=self.context.get('request'),
                                username=username, password=password)
            if not user:
                raise AppException('Authentication failed', 401)
        else:
            msg = _('Must include "username" and "password".')
            raise serializers.ValidationError(msg, code='authorization')

        attrs['user'] = user
        return attrs


class RegisterSerializer(serializers.Serializer):
    fio = serializers.CharField(max_length=100)
    email = serializers.EmailField(max_length=100)
    password = serializers.CharField(max_length=100)

    def validate(self, values):
        if User.objects.filter(email=values['email']).exists():
            raise AppException('email must be unique', 400)

        user = User.objects.create_user(
            values['email'],
            values['email'],
            values['password']
        )
        user.fio = values['fio']
        user.save()

        values['user'] = user

        return user


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'price']


class OrderSerializer(serializers.ModelSerializer):
    products = ProductSerializer(many=True) # НЕ ТАК ДЛЯ WS

    class Meta:
        model = Order
        fields = '__all__'
