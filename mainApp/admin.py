from re import M
from django.contrib import admin
from . models import *
# Register your models here.

admin.site.register((MainCategory,SubCategory,Brand,Product,Seller,Buyer,WishList,Checkout,Subscribe,Contact))
