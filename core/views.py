from rest_framework import status, permissions, views
from rest_framework.response import Response
from .models import CustomUser, Product, Cart, CartItem, Order
from .serializers import UserSerializer, ProductSerializer, CartSerializer, OrderSerializer
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from django.shortcuts import get_object_or_404
from rest_framework.permissions import AllowAny, IsAuthenticated
from datetime import timedelta

# Sign Up
class SignUpView(views.APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({'message': 'User created successfully', 'user_id': user.id}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Sign In
class SignInView(views.APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        try:
            user = CustomUser.objects.get(email=email)
            if user.check_password(password):
                # Create a refresh token
                refresh = RefreshToken.for_user(user)

                # Set the access token expiration time to 45 minutes
                access_token = refresh.access_token
                access_token.set_exp(lifetime=timedelta(minutes=45))  # Set expiry time here

                return Response({
                    "access_token": str(access_token),
                    "refresh_token": str(refresh),
                }, status=status.HTTP_200_OK)
            return Response({"error": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST)
        except CustomUser.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)


# Add Product
class AddProductView(views.APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            product = serializer.save()
            return Response({'message': 'Product added successfully', 'product_id': product.id}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Update Product
class UpdateProductView(views.APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, product_id):
        product = get_object_or_404(Product, id=product_id)
        serializer = ProductSerializer(product, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Product updated successfully'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Delete Product
class DeleteProductView(views.APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, product_id):
        product = get_object_or_404(Product, id=product_id)
        product.delete()
        return Response({'message': 'Product deleted successfully'}, status=status.HTTP_204_NO_CONTENT)

# Get All Products
class GetAllProductsView(views.APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        products = Product.objects.all()
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

# Add Product to Cart
class AddProductToCartView(views.APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        product_id = request.data.get('product_id')

        product = get_object_or_404(Product, id=product_id)

        if product.stock <= 0:
            return Response({'message': 'Product is out of stock'}, status=status.HTTP_400_BAD_REQUEST)

        # Ensure user has a cart, create one if not
        cart, created = Cart.objects.get_or_create(user=user)

        # Ensure product is not already in the cart
        if CartItem.objects.filter(cart=cart, product=product).exists():
            return Response({'message': 'Product already in cart'}, status=status.HTTP_400_BAD_REQUEST)

        # Add product to the cart
        CartItem.objects.create(cart=cart, product=product, quantity=1)

        # Update product stock
        product.stock -= 1
        product.save()

        return Response({'message': 'Product added to cart'}, status=status.HTTP_201_CREATED)

# Get Cart
class GetCartView(views.APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        try:
            cart = Cart.objects.get(user=user)
            serializer = CartSerializer(cart, context={'request': request})
            return Response(serializer.data)
        except Cart.DoesNotExist:
            return Response({"message": "Cart is empty."}, status=status.HTTP_404_NOT_FOUND)

# Place Order
class PlaceOrderView(views.APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        try:
            cart = user.cart
        except Cart.DoesNotExist:
            return Response({'message': 'No cart found'}, status=status.HTTP_404_NOT_FOUND)

        if cart.items.count() == 0:
            return Response({'message': 'Cart is empty'}, status=status.HTTP_400_BAD_REQUEST)

        total_amount = sum(item.product.price * item.quantity for item in cart.items.all())
        order = Order.objects.create(user=user, total_amount=total_amount, shipping_address=request.data.get('shipping_address'))
        order.items.set(cart.items.all())
        order.save()

        cart.items.all().delete()
        return Response({'message': 'Order placed successfully', 'order_id': order.id}, status=status.HTTP_201_CREATED)

# Get Orders
class GetOrdersView(views.APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        orders = Order.objects.filter(user=user)
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
