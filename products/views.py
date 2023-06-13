from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from django.db.models import Q
from products.models import Product, Order
from products.serializers import ProductSerializer, OrderSerializer

from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.views import APIView
from rest_framework.response import Response

import json

from django.conf import settings
from django.core.mail import send_mail
from django.contrib.sites.shortcuts import get_current_site
from django.db.models import Q


class ProductAPI(APIView):

    def get(self, request):
        if request.GET.get('prod_id'):
            try:
                product = Product.objects.filter(
                    product_id=request.GET.get('prod_id'), active=True)
                product = ProductSerializer(product, many=True)
                return Response({"status": True, "product": product.data})
            except:
                return Response({"status": False, "message": "Product not found by product id"})
        else:
            try:
                products = Product.objects.filter(active=True)
                products = ProductSerializer(products, many=True)
                return Response({"status": True, "products": products.data})
            except:
                return Response({"status": False, "message": "Products not found"})


class AuthProductsAPI(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.GET.get('prod_id'):
            try:
                product = Product.objects.filter(
                    product_id=request.GET.get('prod_id'))
                product = ProductSerializer(product)
                return Response({"status": True, "product": product.data})
            except:
                return Response({"status": False, "message": "Product not found by product id"})
        else:
            try:
                products = Product.objects.all()
                products = ProductSerializer(products, many=True)
                return Response({"status": True, "products": products.data})
            except:
                return Response({"status": False, "message": "Products not found"})

    def post(self, request):
        data = JSONParser().parse(request)
        product = Product.objects.create(title=data['title'], description=data['description'],
                                         price=data['price'], stock=data['stock'], active=data['active'],
                                         printable=data['printable'])
        product.save()
        print(product.product_id)
        return Response({"status": True, "message": "Product added", "prod_id": product.product_id})

    def put(self, request):
        data = JSONParser().parse(request)
        Product.objects.filter(product_id=data['product_id']).update(title=data['title'],
                                                                     price=data['price'], description=data['description'], stock=data['stock'],
                                                                     sold=data['sold'], active=data['active'], printable=data['printable'], sku=data['sku'])
        return Response({"status": True, "message": "Product updated successfully"})


class ProductImageAPI(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        prod_id = request.POST.get('prod_id')
        if Product.objects.filter(product_id=prod_id).exists():
            product = Product.objects.get(product_id=prod_id)
            product.photo1 = request.FILES.get('photo1')
            if request.FILES.get('photo2'):
                product.photo2.delete()
                product.photo2 = request.FILES.get('photo2')
            if request.FILES.get('photo3'):
                product.photo3.delete()
                product.photo3 = request.FILES.get('photo3')
            if request.FILES.get('photo4'):
                product.photo4.delete()
                product.photo4 = request.FILES.get('photo4')
            if request.FILES.get('photo5'):
                product.photo5.delete()
                product.photo5 = request.FILES.get('photo5')
            if request.FILES.get('photo6'):
                product.photo6.delete()
                product.photo6 = request.FILES.get('photo6')
            product.save()
            return Response({"status": True, "message": "Product images added", "prod_id": product.product_id})
        else:
            return Response({"status": False, "message": "Product not found"})


class SetProductStatusAPI(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def put(self, request):
        data = JSONParser().parse(request)
        if Product.objects.filter(product_id=data['product_id']).exists():
            product = Product.objects.get(product_id=data['product_id'])
            product.active = data['status']
            product.save()
            return Response({"status": True, "message": "Product status changed"})
        else:
            return Response({"status": False, "message": "Product not found"})


class SearchProductsAPI(APIView):

    def get(self, request):
        query = request.GET.get('query')
        products = Product.objects.filter(
            Q(title__icontains=query)).order_by('-created_at')
        productsData = ProductSerializer(products, many=True)
        return Response({"status": True, "products": productsData.data})


class OrderAPI(APIView):
    def get(self, request):
        if request.GET.get('order_id'):
            try:
                order = Order.objects.filter(
                    order_id=request.GET.get('order_id'))
                order = OrderSerializer(order, many=True)
                return Response({"status": True, "order": order.data})
            except:
                return Response({"status": False, "message": "Order not found by order id"})
        else:
            try:
                orders = Order.objects.all().order_by('-created_at')
                orders = OrderSerializer(orders, many=True)
                return Response({"status": True, "orders": orders.data})
            except:
                return Response({"status": False, "message": "Orders not found"})

    def post(self, request):
        data = JSONParser().parse(request)
        order = Order.objects.create(products=data['products'], customer_name=data['name'],
                                     email=data['email'], mobile=data['mobile'], address=data['address'], city=data['city'],
                                     pincode=data['pincode'], state=data['state'], country=data['country'], paid_amount=0)

        products = json.loads(data['products'])

        for product in products:
            getProduct = Product.objects.get(product_id=product['product_id'])
            getProduct.stock = getProduct.stock - int(product['qty'])
            getProduct.sold = getProduct.sold + int(product['qty'])
            getProduct.save()

        try:
            if data['user_id']:
                order.user_id = data['user_id']
                order.save()
        except:
            pass

        return Response({"status": True, "message": "Order created", "order_id": order.order_id})

    def put(self, request):
        data = JSONParser().parse(request)
        if Order.objects.filter(order_id=data['order_id']).exists():
            order = Order.objects.get(order_id=data['order_id'])
            order.purchase_id = data['purchase_id']
            order.paid_amount = data['grand_total']
            order.order_status = 'Ordered'
            order.save()

            subject = 'Kaakor Order Confirmation'
            domain = settings.MAIN_SITE_URL
            link = '/track?order_id=' + str(order.order_id)
            url = domain+link
            message = f'Dear {data["name"]},\n Thank you for ordering from Kaakor. Your order ID is {order.order_id}. \nUse the below link to track your order \n{url}'
            email_from = settings.EMAIL_HOST_USER
            recipient_list = [data['email']]
            send_mail(subject, message, email_from, recipient_list)
            return Response({"status": True, "message": "Order successful", "order_id": order.order_id})
        else:
            return Response({"status": False, "message": "Order failed"})



class OrderPrintableAPI(APIView):
    def post(self, request):
        order_id = request.POST.get('order_id')
        if Order.objects.filter(order_id=order_id).exists():
            order = Order.objects.get(order_id=order_id)
            order.printableFile = request.FILES.get('printable')
            order.save()
            return Response({"status": True, "message": "Printable image uploaded"})
        else:
            return ({"status": False, "message": "Cannot find order to upload file"})


class TrackOrderAPI(APIView):

    def post(self, request):
        data = JSONParser().parse(request)
        if Order.objects.filter(order_id=data['order_id']).exists():
            order = Order.objects.get(order_id=data['order_id'])
            orderData = OrderSerializer(order)
            if order.mobile == data['mobile']:
                return Response({"status": True, "order": orderData.data})
            elif order.mobile == '+91'+data['mobile']:
                return Response({"status": True, "order": orderData.data})
            else:
                return Response({"status": False, "message": "Could not verify mobile"})

        else:
            return Response({"status": False, "message": 'Could not found order'})


class UserOrderAPI(APIView):
  #  authentication_classes = [JWTAuthentication]
  #  permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.GET.get('user_id'):
            orders = Order.objects.filter(user_id=request.GET.get(
                'user_id')).order_by('-created_at')[:10]
            ordersData = OrderSerializer(orders, many=True)
            return Response({"status": False, "orders": ordersData.data})


class AuthOrdersAPI(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def put(self, request):
        data = JSONParser().parse(request)

        if Order.objects.filter(order_id=data['order_id']).exists():
            try:
                Order.objects.filter(order_id=data['order_id']).update(order_status=data['order_status'],
                                                                       order_tracking=data['order_tracking'], track_id=data['track_id'])
                return Response({"status": True, "message": "Order updated successfully"})
            except:
                return Response({"status": False, "message": "Order update failed"})
        else:
            return Response({"status": False, "message": "Order not found"})


class UpdateInvoiceAPI(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        order_id = request.POST.get('order_id')
        if Order.objects.filter(order_id=order_id).exists():
            order = Order.objects.get(order_id=order_id)
            if request.FILES.get('invoice'):
                order.invoice.delete()
                order.invoice = request.FILES.get('invoice')
                order.save()
                return Response({"status": True, "message": "Invoice added"})
            else:
                return Response({"status": False, "message": "Failed to update invoice"})
        else:
            return Response({"status": False, "message": "Failed to update invoice"})
