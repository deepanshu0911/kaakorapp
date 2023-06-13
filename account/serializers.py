from rest_framework import serializers
from account.models import CustomerDetails, OTP
from django.contrib.auth.models import User

class CustomerDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerDetails
        fields = '__all__'

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields =  ('id', 'email', 'first_name', 'is_active', 'username', 'is_superuser', 
        'last_login')

class OTPSerializer(serializers.ModelSerializer):
    class Meta:
        model = OTP
        fields = '__all__'