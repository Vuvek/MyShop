from distutils.command.upload import upload
from email.policy import default
from pyexpat import model
from unittest.util import _MAX_LENGTH
import black
from django.db import models
from sqlalchemy import null

# Create your models here.

class MainCategory(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)

    def __str__(self) :
        return self.name


class SubCategory(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)

    def __str__(self) :
        return self.name



class Brand(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)

    def __str__(self) :
        return self.name



class Seller(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    username = models.CharField(max_length=50,unique=True)
    email = models.EmailField(max_length=50,unique = True)
    phone = models.CharField(max_length=15)
    addressline1 = models.CharField(max_length=100 , default=None,blank=True,null=True)
    addressline2 = models.CharField(max_length=100, default=None,blank=True,null=True)
    addressline3 = models.CharField(max_length=100, default=None,blank=True,null=True)
    pin = models.CharField(max_length=10, default=None,blank=True,null=True)
    city = models.CharField(max_length=20, default=None,blank=True,null=True)
    state = models.CharField(max_length=20, default=None,blank=True,null=True)
    pic = models.ImageField(upload_to="images/",default=None,blank=True,null=True)

    def __str__(self):
        return f"{self.id} {self.username}"



class Product(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    maincat = models.ForeignKey(MainCategory,on_delete=models.CASCADE,default=1)
    subcat = models.ForeignKey(SubCategory,on_delete=models.CASCADE,default=1)
    brand = models.ForeignKey(Brand,on_delete=models.CASCADE,default=1)
    seller = models.ForeignKey(Seller,on_delete = models.CASCADE,default=1)
    baseprice = models.IntegerField()
    discount = models.IntegerField(default = 0)
    finalPrice = models.IntegerField()
    color = models.CharField(max_length=50)
    size = models.CharField(max_length=20)
    description = models.TextField()
    stock = models.BooleanField(default = True)
    time = models.DateTimeField(auto_now=True)
    pic1 = models.ImageField(upload_to="Images/")
    pic2 = models.ImageField(upload_to="Images/")
    pic3 = models.ImageField(upload_to="Images/")
    pic4 = models.ImageField(upload_to="Images/")


    def __str__(self):
        return f"{self.id}  {self.name} "






class UpdateProfile(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    username = models.CharField(max_length=50,unique=True)
    email = models.EmailField(max_length=50,unique = True)
    phone = models.CharField(max_length=15)
    otp = models.IntegerField(default = 0)
    addressline1 = models.CharField(max_length=100 , default=None,blank=True,null=True)
    addressline2 = models.CharField(max_length=100, default=None,blank=True,null=True)
    addressline3 = models.CharField(max_length=100, default=None,blank=True,null=True)
    pin = models.CharField(max_length=10, default=None,blank=True,null=True)
    city = models.CharField(max_length=20, default=None,blank=True,null=True)
    state = models.CharField(max_length=20, default=None,blank=True,null=True)
    pic = models.ImageField(upload_to="images/",default=None,blank=True,null=True)

    def __str__(self):
        return f"{self.id} {self.username}"



class Buyer(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    username = models.CharField(max_length=50,unique=True)
    email = models.EmailField(max_length=50,unique = True)
    phone = models.CharField(max_length=15)
    otp = models.IntegerField(default = 0)
    addressline1 = models.CharField(max_length=100 , default=None,blank=True,null=True)
    addressline2 = models.CharField(max_length=100, default=None,blank=True,null=True)
    addressline3 = models.CharField(max_length=100, default=None,blank=True,null=True)
    pin = models.CharField(max_length=10, default=None,blank=True,null=True)
    city = models.CharField(max_length=20, default=None,blank=True,null=True)
    state = models.CharField(max_length=20, default=None,blank=True,null=True)
    pic = models.ImageField(upload_to="images/",default=None,blank=True,null=True)

    def __str__(self):
        return f"{self.id} {self.username}"


class WishList(models.Model):
    id = models.AutoField(primary_key=True)
    buyer = models.ForeignKey(Buyer,on_delete=models.CASCADE)
    product = models.ForeignKey(Product,on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.id} {self.buyer.username}"



choice = ((1,"Not Packed"),(2,"Packed"),(3,"Out For Delivery"),(4,"Delivered"))
paymentChoice = ((1,"Pending"),(2,"Done"))
mode = ((1,"COD"),(2,"Net Banking"))
class Checkout(models.Model):
    id = models.AutoField(primary_key=True)
    buyer = models.ForeignKey(Buyer,on_delete=models.CASCADE)
    products = models.CharField(max_length = 20)
    total = models.IntegerField()
    shipping = models.IntegerField(default = 0)
    finalAmount = models.IntegerField()
    active = models.BooleanField(default=True)
    time = models.DateTimeField(auto_now=True)
    status = models.IntegerField(choices = choice,default = 1)
    paymentStatus = models.IntegerField(choices = paymentChoice,default = 1)
    mode = models.IntegerField(choices = mode,default = 1)
    orderId = models.CharField(max_length=50,default=None,blank=True,null=True)
    paymentId = models.CharField(max_length=50,default=None,blank=True,null=True)
    paymentsignature = models.CharField(max_length=50,default=None,blank=True,null=True)

    def __str__(self):
        return f"{self.id} {self.buyer.username} {self.active}"

        

     




class Subscribe(models.Model):
    id = models.AutoField(primary_key = True)
    email = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.id} {self.email}"





class Contact(models.Model):
    id = models.AutoField(primary_key = True)
    name = models.CharField(max_length=50)
    email = models.CharField(max_length=50)
    phone = models.CharField(max_length=15,default = None)
    subject = models.CharField(max_length = 50)
    message = models.TextField()
    active = models.BooleanField(default = True)

    def __str__(self):
        return f"{self.id} {self.active} {self.name} {self.subject}"