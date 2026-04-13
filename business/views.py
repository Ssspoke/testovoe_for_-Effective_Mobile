from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import MockProduct, MockOrder
from .serializers import ProductSerializer, OrderSerializer, CreateProductSerializer, CreateOrderSerializer
from access.permissions import HasReadPermission, HasCreatePermission, HasUpdatePermission, HasDeletePermission


class ProductViewMixin:
    element_name = 'products'


class OrderViewMixin:
    element_name = 'orders'


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_products(request):
    """Получение списка продуктов"""
    user = request.user
    
    # Проверяем право на чтение
    from access.permissions import get_permission_level
    permission_level = get_permission_level(user, 'products', 'read_permission', 'read_all_permission')
    
    if permission_level == 'none':
        return Response({
            'error': 'Нет прав на просмотр продуктов'
        }, status=status.HTTP_403_FORBIDDEN)
    
    # Если доступ только к своим - фильтруем
    if permission_level == 'own':
        products = MockProduct.objects.filter(owner=user)
    else:
        products = MockProduct.objects.all()
    
    serializer = ProductSerializer(products, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_product(request):
    """Создание продукта"""
    from access.permissions import check_permission
    
    if not check_permission(request.user, 'products', 'create_permission'):
        return Response({
            'error': 'Нет прав на создание продуктов'
        }, status=status.HTTP_403_FORBIDDEN)
    
    serializer = CreateProductSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    
    product = MockProduct.objects.create(
        name=serializer.validated_data['name'],
        description=serializer.validated_data.get('description', ''),
        price=serializer.validated_data['price'],
        owner=request.user,
    )
    
    product_serializer = ProductSerializer(product)
    return Response(product_serializer.data, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_orders(request):
    """Получение списка заказов"""
    user = request.user
    
    from access.permissions import get_permission_level
    permission_level = get_permission_level(user, 'orders', 'read_permission', 'read_all_permission')
    
    if permission_level == 'none':
        return Response({
            'error': 'Нет прав на просмотр заказов'
        }, status=status.HTTP_403_FORBIDDEN)
    
    # Если доступ только к своим - фильтруем
    if permission_level == 'own':
        orders = MockOrder.objects.filter(user=user)
    else:
        orders = MockOrder.objects.all()
    
    serializer = OrderSerializer(orders, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_order(request):
    """Создание заказа"""
    from access.permissions import check_permission
    
    if not check_permission(request.user, 'orders', 'create_permission'):
        return Response({
            'error': 'Нет прав на создание заказов'
        }, status=status.HTTP_403_FORBIDDEN)
    
    serializer = CreateOrderSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    
    try:
        product = MockProduct.objects.get(id=serializer.validated_data['product_id'])
    except MockProduct.DoesNotExist:
        return Response({
            'error': 'Продукт не найден'
        }, status=status.HTTP_404_NOT_FOUND)
    
    order = MockOrder.objects.create(
        product=product,
        user=request.user,
        quantity=serializer.validated_data.get('quantity', 1),
        status='new',
    )
    
    order_serializer = OrderSerializer(order)
    return Response(order_serializer.data, status=status.HTTP_201_CREATED)
