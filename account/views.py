from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from django.db.models import Q
from django.contrib.auth.hashers import make_password, check_password
from account.models import CustomerDetails
from products.models import *
from account.serializers import CustomerDetailsSerializer, UserSerializer

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.backends import TokenBackend


from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout

from django.conf import settings
from django.core.mail import send_mail
from django.contrib.sites.shortcuts import get_current_site



def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

class CreateUser(APIView):
      
    def post(self, request):
        data = JSONParser().parse(request)
        if User.objects.filter(email=data['email']).exists():
           return Response({"status": False, "message": "User email already exists"})
        if not User.objects.filter(email=data['email']).exists():
           if User.objects.filter(username=data['username']).exists():
                return Response({"status": False, "message": "Username already exists"})
           else:      
              user = User.objects.create(username=data['username'],first_name=data['firstName'], 
              email=data['email'])
              user.set_password(data['password'])
              user.is_active = False
              userData = UserSerializer(user)
              refresh = get_tokens_for_user(user)
              print(refresh)
            #   Yes, I am storing token in last_name
              user.last_name = str(user.id)+'||'+refresh['access'][0:50]
              user.save()
              
              subject = 'Kaakor Account Activation'
              domain = get_current_site(request).domain
              link = '/account/verify-user/'+ user.last_name
              activate_url = 'http://'+domain+link

              message = f'Hi {user.username}, thank you for registering on Kaakor. \nUse this link to verify your account {activate_url}'
              email_from = settings.EMAIL_HOST_USER
              recipient_list = [user.email]
              send_mail( subject, message, email_from, recipient_list )
              print(user.id)
              if not CustomerDetails.objects.filter(user_id=user.id).exists():
                customerDetails = CustomerDetails.objects.create(user_id=user.id, username=user.username, name=user.first_name,
                                     email=user.email)
              return Response({"status": True, "message": "Verification mail send",})   
        return Response({"status": False, "message": "Request failed"})

class UserVerification(APIView):
   def get(self, request,token):
      # token = request.GET.get('token')
      print(token)
      user = User.objects.get(last_name=token)
      if user:
         user.is_active = True
         user.last_name = ''
         user.save()
         # return Response({"status": True, "message": "Account verified successfully"})
         return render(request,'verified.html')
      else:
         return Response({"status": "Account cannot be verified"})    

class UserLogin(APIView):
   
    def post(self, request):
        data = JSONParser().parse(request)
        username = data['username']
        password = data['password']
        user = authenticate(request, username=username, password=password)
        if user is None:
            return Response({"status": False, "message": "User not found"})
        elif user.is_authenticated:
           login(request, user)
           userData = UserSerializer(user)
           if not user.is_superuser:
             try:    
               customer = CustomerDetails.objects.get(user_id=user.id)
               customerData = CustomerDetailsSerializer(customer)
               refresh = get_tokens_for_user(user)
               return Response({"status": True, "message": "User logged in",
                   "user": userData.data, "details": customerData.data, "tokens": refresh})
             except:
               logout(request)
               return Response({"status": False, "message": "User details not found"})  
           refresh = get_tokens_for_user(user)
           return Response({"status": True, "message": "User logged in",
                   "user": userData.data, "tokens": refresh})   
        else:
           return Response({"status": False, "message": "An error occured"})   

class UserAPI(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
       print(request.user)
       token = request.META.get('HTTP_AUTHORIZATION', " ").split(' ')[1]
       data = {'token': token}
       valid_data = TokenBackend(algorithm='HS256').decode(token, None)
       user = User.objects.get(id=valid_data['user_id'])
       userData = UserSerializer(user)
       if not user.is_superuser:
         try:    
            customer = CustomerDetails.objects.get(user_id=user.id)
            customerData = CustomerDetailsSerializer(customer)
            return Response({"status": True, "message": "User logged in",
                   "user": userData.data, "details": customerData.data})
         except:
            return Response({"status": False, "message": "User details not found"})  
       return Response({"status": True, "message": "User logged in", "user": userData.data}) 
    
    def put(self, request):
      data = JSONParser().parse(request)
      if User.objects.filter(id=data['id']).exists():    
        if CustomerDetails.objects.filter(user_id=data['id']).exists():
           # Not updating email and username due to security reasons 
           user = User.objects.filter(id=data['id']).update(first_name=data['name'])
           customer = CustomerDetails.objects.filter(user_id=data['user_id']).update(mobile=data['mobile'], 
                     addrLine1=data['addrLine1'], addrLine2=data['addrLine2'], city=data['city'], 
                     country=data['country'], pincode=data['pincode'], state=data['state'])
           return Response({"status": True, "message": "Profile updated successfully"})           
        else:
          return Response({"status": False, "message": "This account is not eligible for update"})   
      else:
        return Response({"status": False, "message": "No user found"})       

class UserLogout(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
       logout(request)
       request.session.flush()
       return Response({"status": True, "message": "User logged out"})

class UsersManageAPI(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
       users = CustomerDetails.objects.all()
       usersData = CustomerDetailsSerializer(users, many=True)
       return Response({"status": True, "users": usersData.data})

class DashboardAPI(APIView):
     authentication_classes = [JWTAuthentication]
     permission_classes = [IsAuthenticated]

     def get(self, request):
        users = CustomerDetails.objects.all().count()
        orders = Order.objects.all().count()
        newOrders = Order.objects.filter(order_status='Ordered').count()
        products = Product.objects.all().count()
        outOfStock = Product.objects.filter(stock__lt=5).count()
        ActiveProducts = Product.objects.filter(active=True).count()
        overview = {
           "totalUsers": users,
           "totalOrders": orders,
           "totalProducts": products,
           "newOrders": newOrders,
           "outOfStock": outOfStock,
           "activeProducts": ActiveProducts
        }
        return Response({"status": True, "overview": overview})




   


