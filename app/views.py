from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import APIException
from rest_framework.response import Response
from rest_framework.views import APIView

from app.models import Product, Cart, Order
from app.serializers import LoginSerializer, RegisterSerializer, ProductSerializer, OrderSerializer


class Login(ObtainAuthToken):
    serializer_class = LoginSerializer
    format_kwarg = None

    def post(self, request, *args, **kwargs):
        data = request.data
        data['username'] = data.pop('email')

        response = super().post(request, *args, **kwargs)
        response.data = {
            'data': {
                'user_token': response.data['token']
            }
        }

        return response


class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        view = Login()
        view.request = request
        return view.post(request)


class Products(APIView):
    def get(self, request):
        serializer = ProductSerializer(Product.objects.all(), many=True)
        return Response({
            'body': serializer.data
        })


from rest_framework.permissions import IsAuthenticated


@api_view(['POST', 'DELETE'])
@permission_classes([IsAuthenticated])
def add_to_cart(request, product_id):
    if request.method == 'POST':
        product = Product.objects.filter(pk=product_id)
        if not product.exists():
            err = APIException('Product not found')
            err.status_code = 404

            raise err
        cart = Cart.objects.create(
            user=request.user,
            item=product[0]
        )
        return Response({
            'body': {
                'message': 'Product add to card'
            }
        }, 201)
    if request.method == 'DELETE':
        product_cart = Cart.objects.get(pk=product_id)
        if product_cart.user != request.user:
            err = APIException('Forbidden for you')
            err.status_code = 403
            raise err
        product_cart.delete()
        return Response({
            'data': {
                'message': 'Item removed from cart'
            }
        })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def cart_view(request):
    cart = Cart.objects.filter(user=request.user)
    for i in cart:
        i.item.id = i.id
    products = [i.item for i in cart]
    return Response({
        'body': ProductSerializer(products, many=True).data
    })


@api_view(['POST', 'GET'])
@permission_classes([IsAuthenticated])
def order_view(request):
    if request.method == 'POST':
        cart_products = Cart.objects.filter(user=request.user)
        if not cart_products.exists():
            err = APIException('Cart is empty')
            err.status_code = 422
            raise err
        products = [i.item for i in cart_products]
        total_price = sum([i.price for i in products])
        order = Order.objects.create(
            user=request.user,
            order_price=total_price
        )
        for i in products:
            order.products.add(i)
        cart_products.delete()
        return Response({
            'body': {
                'order_id': order.id,
                'message': 'Order is processed'
            }
        }, 201)
    elif request.method == 'GET':
        orders = Order.objects.filter(user=request.user)
        return Response({
            'body': OrderSerializer(orders, many=True).data
        })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def logout(request):
    Token.objects.get(user=request.user).delete()

    return Response({
        'body': {
            'message': 'logout'
        }
    })


from rest_framework.permissions import IsAdminUser


@api_view(['POST'])
@permission_classes([IsAdminUser])
def product_admin(request):
    serializer = ProductSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    product = serializer.save()

    return Response({
        'body': {
            'id': product.id,
            'message': 'Product added'
        }
    }, 201)


@api_view(['DELETE', 'PATCH'])
@permission_classes([IsAdminUser])
def product_detail_admin(request, product_id):
    product = Product.objects.get(pk=product_id)
    if request.method == 'DELETE':
        product.delete()
        return Response({
            'body': {
                'message': 'Product removed'
            }
        })
    elif request.method == 'PATCH':
        serializer = ProductSerializer(product, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({
            'body': serializer.data
        })
