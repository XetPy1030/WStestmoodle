from django.urls import path

from . import views
from .views import *

urlpatterns = [
    path('login/', views.Login.as_view()),
    path('signup/', views.RegisterView.as_view()),
    path('products/', views.Products.as_view()),
    path('cart/<int:product_id>/', add_to_cart),
    path('cart/', cart_view),
    path('order/', order_view),
    path('logout/', logout),
    path('product/', product_admin),
    path('product/<int:product_id>/', product_detail_admin)
]
