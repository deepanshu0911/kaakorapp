from django.db import models
import uuid
import os


def product_image(instance, filename):
    ext = filename.split('.')[-1]
    filename = "%s.%s" % (uuid.uuid4(), ext)
    return os.path.join('uploads/products', filename)


def invoice_file(instance, filename):
    ext = filename.split('.')[-1]
    filename = "%s.%s" % (uuid.uuid4(), ext)
    return os.path.join('uploads/invoices', filename)


def printable_file(instance, filename):
    ext = filename.split('.')[-1]
    filename = "%s.%s" % (uuid.uuid4(), ext)
    return os.path.join('uploads/printable', filename)


class Product(models.Model):
    product_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    description = models.TextField(null=True, blank=True)
    colors = models.TextField(null=True, blank=True)
    sku = models.CharField(max_length=100, null=True, blank=True)
    stock = models.IntegerField(default=0)
    sold = models.IntegerField(default=0)
    active = models.BooleanField(default=False)
    printable = models.BooleanField(default=False)

    photo1 = models.FileField(upload_to=product_image, null=True, blank=True)
    photo2 = models.FileField(upload_to=product_image, null=True, blank=True)
    photo3 = models.FileField(upload_to=product_image, null=True, blank=True)
    photo4 = models.FileField(upload_to=product_image, null=True, blank=True)
    photo5 = models.FileField(upload_to=product_image, null=True, blank=True)
    photo6 = models.FileField(upload_to=product_image, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    objects = models.Manager()

    def __str__(self):
        return str(self.product_id) + ' ' + self.title + ' ' + str(self.created_at)

    def delete(self, *args, **kwargs):
        self.photo1.delete(save=False)
        self.photo2.delete(save=False)
        self.photo3.delete(save=False)
        self.photo4.delete(save=False)
        self.photo5.delete(save=False)
        self.photo6.delete(save=False)
        super(Product, self).delete(*args, **kwargs)

    def save(self, force_insert=False, force_update=False, using=None, *args, **kwargs):
        if self.photo1:
            image = self.photo1
            if image.size > 1*1024*1024:  # if size greater than 1mb then it will send to compress image function
                self.photo1 = compress_image(image)
        if self.photo2:
            image = self.photo2
            if image.size > 1*1024*1024: #if size greater than 1mb then it will send to compress image function
                self.photo2 = compress_image(image)
        if self.photo3:
            image = self.photo3
            if image.size > 1*1024*1024: #if size greater than 1mb then it will send to compress image function
                self.photo3 = compress_image(image)
        if self.photo4:
            image = self.photo4
            if image.size > 1*1024*1024: #if size greater than 1mb then it will send to compress image function
                self.photo4 = compress_image(image)
        if self.photo5:
            image = self.photo5
            if image.size > 1*1024*1024: #if size greater than 1mb then it will send to compress image function
                self.photo5 = compress_image(image)
        if self.photo6:
            image = self.photo6
            if image.size > 1*1024*1024: #if size greater than 1mb then it will send to compress image function
                self.photo6 = compress_image(image)            
        super(Product, self).save(*args, **kwargs)    

from django.core.files import File
from io import BytesIO
from PIL import Image

def compress_image(image):
    im = Image.open(image)
    if im.mode != 'RGB':
        im = im.convert('RGB')
    im_io = BytesIO()
    im.save(im_io, 'jpeg', quality=70,optimize=True)
    new_image = File(im_io, name=image.name)
    return new_image

class Order(models.Model):
    order_id = models.AutoField(primary_key=True)
    products = models.TextField()

    user_id = models.CharField(max_length=50, null=True, blank=True)
    customer_name = models.CharField(max_length=200)
    email = models.CharField(max_length=200, null=True, blank=True)
    mobile = models.CharField(max_length=50, null=True, blank=True)
    address = models.TextField()
    landmark = models.CharField(max_length=100, null=True, blank=True)
    city = models.CharField(max_length=200)
    pincode = models.CharField(max_length=20, null=True, blank=True)
    state = models.CharField(max_length=200)
    country = models.CharField(max_length=100, default="India")

    paid_amount = models.DecimalField(max_digits=20, decimal_places=2)
    purchase_id = models.CharField(max_length=200, null=True, blank=True)
    order_status = models.CharField(max_length=100, default="Unpaid")
    order_tracking = models.TextField(null=True, blank=True)
    
    track_id = models.CharField(max_length=100, null=True, blank=True)
    invoice = models.FileField(upload_to=invoice_file, null=True, blank=True)
    printableFile = models.FileField(upload_to=printable_file, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    objects = models.Manager()   

    def __str__(self):
       return str(self.order_id) + ' ' + self.customer_name + ' ' + str(self.created_at) 
    
    def delete(self, *args, **kwargs):
        self.invoice.delete(save=False)
        super(Order, self).delete(*args, **kwargs)


    





