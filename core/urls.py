from django.urls import path
from .views import SignUpView, SignInView, AddProductView, UpdateProductView, DeleteProductView, GetAllProductsView, AddProductToCartView, GetCartView, PlaceOrderView, GetOrdersView

urlpatterns = [
    path('signup', SignUpView.as_view(), name='signup'),
    path('signin', SignInView.as_view(), name='signin'),
    path('addproduct', AddProductView.as_view(), name='addproduct'),
    path('updateproduct/<int:product_id>', UpdateProductView.as_view(), name='updateproduct'),
    path('deleteproduct/<int:product_id>', DeleteProductView.as_view(), name='deleteproduct'),
    path('products', GetAllProductsView.as_view(), name='get_all_products'),
    path('cart/add', AddProductToCartView.as_view(), name='add_to_cart'),
    path('cart', GetCartView.as_view(), name='get_cart'),
    path('placeorder', PlaceOrderView.as_view(), name='place_order'),
    path('getorders', GetOrdersView.as_view(), name='get_orders'),
]
