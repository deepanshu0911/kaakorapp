from django.db import models
import uuid
import os

class CustomerDetails(models.Model):
    customer_id = models.AutoField(primary_key=True)
    user_id = models.CharField(max_length=100)
    name = models.CharField(max_length=100, null=True, blank=True)
    username = models.CharField(max_length=200)
    email = models.CharField(max_length=200, null=True, blank=True)
    mobile = models.CharField(max_length=50, null=True, blank=True)
    addrLine1 = models.CharField(max_length=200, null=True, blank=True)
    addrLine2 = models.CharField(max_length=200, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    pincode = models.CharField(max_length=50, null=True, blank=True)
    state = models.CharField(max_length=100, null=True, blank=True)
    country = models.CharField(max_length=100, default="India")
    created_at = models.DateTimeField(auto_now_add=True)
    objects = models.Manager()

    def __str__(self):
        return self.username + ' ' + str(self.created_at)
    
class OTP(models.Model):
    otp_id = models.AutoField(primary_key=True)
    user_id = models.CharField(max_length=100)
    otp = models.CharField(max_length=10)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.used_id + ' ' + str(self.created_at)

