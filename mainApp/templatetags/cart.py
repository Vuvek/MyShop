from django import template
from mainApp.models import Product
from mainApp.views import product
register = template.Library()

@register.filter('cartQuantity')
def cartQuantity(request,id):
    cart = request.session.get('cart',None)
    for key,value in cart.items():
        if key == str(id):
            return value


@register.filter('cartFinal')
def cartFinal(request,id):
    cart = request.session.get('cart',None)
    for key,value in cart.items():
        if key == str(id):
            p = Product.objects.get(id = id)
            return value*p.finalPrice



@register.filter('paymentStatus')
def paymentStatus(request,num):
    if num == 1:
        return "Pending"
    
    else:
        return "Done"


@register.filter('orderStatus')
def paymentStatus(request,num):
    if num == 1:
        return "Not Packed"
    elif num == 1:
        return "Packed"
    elif num == 1:
        return "Out For Delivery"
    
    else:
        return "Delivered"



@register.filter("products")
def products(items):
    
    item = items.split(",")
    object = []
    for i in item[:-1]:
        item_id = int(i.split(":")[0])
        object.append(Product.objects.get(id = item_id))
    return object



@register.filter('paymentmode')
def paymentmode(mode):
    if mode == 1:
        return "COD"
    else:
        return "Net Banking" 




@register.filter('checkoutdelete')
def checkoutdelete(mode):
    if mode == 1:
        return True
    else:
        return False 



