from functools import total_ordering
import imp
from math import prod
import pstats
from unicodedata import name
from black import main
from click import password_option
from django.shortcuts import render,HttpResponseRedirect
from django.contrib.auth.models import User
from django.contrib import auth , messages
from matplotlib.style import use
from . models import *
from django.contrib.auth.decorators import login_required
from MyShop.settings import RAZORPAY_API_KEY,RAZORPAY_API_SECRET_KEY
import razorpay
from django.conf import settings
from django.core.mail import send_mail
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
import random

# Create your views here.

def home(request):
    data = Product.objects.all()
    data = data[::-1]
    return render(request,'index.html',{"Data":data})


def shop(request,mc,sc,br):
    if mc == 'all' and sc == 'all' and br == 'all':
        data = Product.objects.all()
    elif mc != 'all' and sc == 'all' and br == 'all':
        data = Product.objects.filter(maincat = MainCategory.objects.get(name=mc))
    elif mc == 'all' and sc != 'all' and br == 'all':
        data = Product.objects.filter(subcat = SubCategory.objects.get(name=sc))
    elif mc == 'all' and sc == 'all' and br != 'all':
        data = Product.objects.filter(brand = Brand.objects.get(name=br))
    elif mc != 'all' and sc != 'all' and br == 'all':
        data = Product.objects.filter(maincat = MainCategory.objects.get(name=mc),brand = Brand.objects.get(name=br))
    elif mc != 'all' and sc == 'all' and br != 'all':
        data = Product.objects.filter(maincat = MainCategory.objects.get(name=mc))
    elif mc == 'all' and sc != 'all' and br != 'all':
        data = Product.objects.filter(subcat = SubCategory.objects.get(name=sc),
        brand = Brand.objects.get(name = br))
    elif mc != 'all' and sc != 'all' and br != 'all':
        data = Product.objects.filter(maincat = MainCategory.objects.get(name=mc),subcat = SubCategory.objects.get(name=sc),brand = Brand.objects.get(name=br))
    
    maincat = MainCategory.objects.all()
    subcat = SubCategory.objects.all()
    brand = Brand.objects.all()

    return render(request,"shop.html",{"Data":data,
                                            "Maincat":maincat,
                                            "Subcat":subcat,
                                            'Brand':brand,
                                            "MC":mc,
                                            "SC":sc,
                                            "BR":br})


def product(request,id):
    product = Product.objects.get(id = id)
    if request.method == "POST":
        try:
            buyer = Buyer.objects.get(username = request.user)
        except:
            return HttpResponseRedirect("/profile/")

        cart = request.session.get('cart',None)
        q = int(request.POST.get('q'))
        if cart:
            if str(id) in cart.keys():
                cart[str(id)]+=int(q)
            else:
                cart.setdefault(str(id),int(q))
        else:
            cart = {str(product.id):q}
        print(cart)
        request.session['cart'] = cart
        request.session.set_expiry(60*60*24*30)
        print("Aaya2 -----------------------------")
        return HttpResponseRedirect('/cartPage/')

    return render(request,"product.html",{"product":product})





@login_required(login_url='/login/')
def cartPage(request):

    # request.session.flush()
    try:
        buyer = Buyer.objects.get(username = request.user)
    except:
        return HttpResponseRedirect('/profile/')


    flushcart = request.session.get('flushcart',None)
    print(flushcart)
    if flushcart == True:
        print(f"{flushcart}2")
        request.session['cart'] = {}
        request.session['flushcart'] = False
        
    
    cart = request.session.get('cart',None)
    products = []
    total = 0 
    shipping = 0
    final = 0
    if cart:
        for key,value in cart.items():
            p =Product.objects.get(id = int(key))
            products.append(p)
            total += p.finalPrice * value
        if total < 1000:
            shipping = 150
        else:
            shipping = 0
        
        final = total + shipping

    if request.method == "POST":
        id = request.POST.get("id")
        q = int(request.POST.get('q'))
        cart[id] = q
        request.session['cart'] = cart
        request.session.set_expiry(60*60*24*30)
        return HttpResponseRedirect("/cartPage/")

    return render(request,'cart.html',{"Products":products,
                                       "Total":total,
                                       "Shipping":shipping,
                                       "Final":final
                                        })





@login_required(login_url='/login/')
def deleteCart(request,id):
    cart = request.session.get('cart',None)
    if cart:
        cart.pop(str(id))
        request.session['cart'] = cart
    return HttpResponseRedirect('/cartPage/')



client = razorpay.Client(auth = (RAZORPAY_API_KEY,RAZORPAY_API_SECRET_KEY))
@login_required(login_url='/login/')
def checkout(request):

    try:
        buyer = Buyer.objects.get(username = request.user)
    except:
        return HttpResponseRedirect('/profile/')

    if request.method == "POST":
        cart = request.session.get('cart',None)
        if cart is None:
            return HttpResponseRedirect("/cartPage/")
        else:
            check = Checkout()
            check.buyer = buyer
            check.products = ""
            check.total = 0
            check.shipping = 0
            check.finalAmount = 0   
            for key,value in cart.items():
                check.products = check.products+key+":"+str(value)+","
                p = Product.objects.get(id = key)
                check.total = p.finalPrice * value
            if check.total<1000:
                check.shipping = 150
            check.finalAmount = check.total + check.shipping
            check.save()
            mode = request.POST.get("mode")
            if mode == "cod":
                check.save()
                request.session['flushcart'] = True
                return HttpResponseRedirect("/confirm/")
            else:
                orderAmount = check.finalAmount*100
                orderCurrency = "INR"
                paymentOrder = client.order.create(dict(amount = orderAmount,currency = orderCurrency,payment_capture = 1))
                paymentId = paymentOrder['id']
                # check.order_id = paymentId
                check.mode = 2
                check.save()
                return render(request,"pay.html",{
                                                  "amount":orderAmount,
                                                  "api_key":RAZORPAY_API_KEY,
                                                  "order_id":paymentId,
                                                  "User":buyer
                })

    else:
        cart = request.session.get('cart',None)
        products = []
        total = 0 
        shipping = 0
        final = 0
        if cart:
            for key,value in cart.items():
                p =Product.objects.get(id = int(key))
                products.append(p)
                total += p.finalPrice * value
            if total < 1000:
                shipping = 150
            else:
                shipping = 0
            
            final = total + shipping

   


    return render(request,'checkout.html',{"Products":products,
                                       "Total":total,
                                       "Shipping":shipping,
                                       "Final":final,
                                       "User":buyer
                                        })





@login_required(login_url='/login/')
def paymentSuccesss(request,rppid,rpoid,rpsid):
    buyer = Buyer.objects.get(username=request.user)
    check = Checkout.objects.filter(buyer=buyer)
    check=check[::-1]
    check=check[0]
    check.paymentId=rppid
    check.orderId=rpoid
    check.paymentsignature=rpsid
    check.paymentStatus=2
    check.save()
    request.session['flushcart'] = True
    return HttpResponseRedirect('/confirm/')





@login_required(login_url='/login/')
def confirmPage(request):
    return render(request,"confirmation.html")


def login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = auth.authenticate(username = username,password= password)
        if user is not None:
            auth.login(request,user)
            if user.is_superuser:
                return HttpResponseRedirect("/admin/")
            else:
                return HttpResponseRedirect('/profile/')
        else:
            messages.error(request,"Username or Password is Incorrect")
    return render(request,'login.html')


def signup(request):
    if request.method == "POST":
      
        actype = request.POST.get("actype")
        
        if actype == "seller":
            s = Seller()
            s.name = request.POST.get('name')
            s.username = request.POST.get("username")
            s.phone = request.POST.get("phone")
            s.email = request.POST.get('email')
            s.password = request.POST.get('password')
            try:
                user = User.objects.create_user(username = s.username,password = s.password)
                user.save()
                s.save()
                return HttpResponseRedirect('/login/')
            except :
                messages.error(request,"Username Is Already Takend!!")

        elif actype == "buyer":
            b = Buyer()
            b.name = request.POST.get('name')
            b.username = request.POST.get("username")
            b.phone = request.POST.get("phone")
            b.email = request.POST.get('email')
            b.password = request.POST.get('password')
            try:
                user = User.objects.create_user(username = b.username,password = b.password)
                user.save()
                b.save()
                return HttpResponseRedirect('/login/')
            except :
                messages.error(request,"Username Is Already Takend!!")

    return render(request, 'signup.html')




@login_required(login_url='/login/')
def logout(request):
    auth.logout(request)
    return HttpResponseRedirect("/login/")


@login_required(login_url='/login/')
def profile(request):
    
    user = User.objects.get(username = request.user)

    if user.is_superuser:
        return HttpResponseRedirect("/admin/")
    else:
        try:
            seller = Seller.objects.get(username = request.user)
            return HttpResponseRedirect("/sellerProfile/")
        except:
            return HttpResponseRedirect("/buyerProfile/")


@login_required(login_url='/login/')
def sellerProfile(request):
    seller = Seller.objects.get(username = request.user)
    products = Product.objects.filter(seller = seller)
    print(products)
    print("products"+"---------------------------------------------")
    return render(request,"sellerProfile.html",{'User':seller,"Products":products})



@login_required(login_url='/login/')
def buyerProfile(request):
    buyer = Buyer.objects.get(username = request.user)
    wishlist = WishList.objects.filter(buyer = buyer)
    check = Checkout.objects.filter(buyer = buyer)
    return render(request,"buyerProfile.html",{'User':buyer,
                                               "Wishlist":wishlist,
                                               "Checkout":check
                                                })




@login_required(login_url='/login/')
def updateProfile(request):
    user = User.objects.get(username = request.user)
    if user.is_superuser:
        return HttpResponseRedirect("/admin/")
    try:
        seller = Seller.objects.get(username = request.user)
        flag = seller
    except:
        buyer = Buyer.objects.get(username = request.user)
        flag = buyer
    
    if request.method == "POST":
        flag.name = request.POST.get('name')
        flag.email = request.POST.get('email')
        flag.phone = request.POST.get('phone')
        flag.addressline1 = request.POST.get('name')
        flag.addressline2 = request.POST.get('addressline2')
        flag.addressline3 = request.POST.get('addressline3')
        flag.pin = request.POST.get('pin')
        flag.city = request.POST.get('city')
        flag.state = request.POST.get('state')
        if request.FILES.get('pic'):
            flag.pic = request.FILES.get('pic')
        flag.save()
        return HttpResponseRedirect('/profile/')
        
    return render(request,"updateProfile.html",{'User':flag})




@login_required(login_url='/login/')
def addProduct(request):
    mainCat = MainCategory.objects.all()
    subCat = SubCategory.objects.all()
    brand = Brand.objects.all()
    seller = Seller.objects.get(username = request.user)
    if request.method == "POST":
        p = Product()
        p.seller = seller
        p.name = request.POST.get('name')
        p.maincat = MainCategory.objects.get(name = request.POST.get('maincategory')) 
        p.subcat = SubCategory.objects.get(name = request.POST.get('subcategory'))
        p.brand =  Brand.objects.get(name = request.POST.get('brand'))
        p.baseprice = int(request.POST.get('baseprice'))
        p.discount = int(request.POST.get('discount'))
        p.finalPrice = p.baseprice - p.baseprice*p.discount//100
        p.color = request.POST.get('color')
        p.size = request.POST.get('size')
        p.description = request.POST.get('description')
        p.stock = request.POST.get('stock')
        if request.FILES.get("pic1"):
            p.pic1 = request.FILES.get('pic1')
        if request.FILES.get("pic2"):
            p.pic2 = request.FILES.get('pic2')
        if request.FILES.get("pic3"):
            p.pic3 = request.FILES.get('pic3')
        if request.FILES.get("pic4"):
            p.pic4 = request.FILES.get('pic4')
        p.save()
        return HttpResponseRedirect('/sellerProfile/')
       
    return render(request,'addproduct.html',{"Maincat":mainCat,
                                             "Subcat":subCat,
                                             "Brand":brand})



@login_required(login_url='/login/')
def deleteProduct(request,id):
    try:
        product = Product.objects.get(id = id)
        seller = Seller.objects.get(username = request.user)
        if seller == product.seller:
            product.delete()
    except:
        pass
    return HttpResponseRedirect('/sellerProfile/')



@login_required(login_url='/login/')
def editProduct(request,id):

    mainCat = MainCategory.objects.all()
    subCat = SubCategory.objects.all()
    brand = Brand.objects.all()
    seller = Seller.objects.get(username = request.user)
    p = Product.objects.get(id = id)
    if request.method == "POST":
        p.seller = seller
        p.name = request.POST.get('name')
        p.maincat = MainCategory.objects.get(name = request.POST.get('maincategory')) 
        p.subcat = SubCategory.objects.get(name = request.POST.get('subcategory'))
        p.brand =  Brand.objects.get(name = request.POST.get('brand'))
        p.baseprice = int(request.POST.get('baseprice'))
        p.discount = int(request.POST.get('discount'))
        p.finalPrice = p.baseprice - p.baseprice*p.discount//100
        p.color = request.POST.get('color')
        p.size = request.POST.get('size')
        p.description = request.POST.get('description')
        p.stock = request.POST.get('stock')
        if request.FILES.get("pic1"):
            p.pic1 = request.FILES.get('pic1')
        if request.FILES.get("pic2"):
            p.pic2 = request.FILES.get('pic2')
        if request.FILES.get("pic3"):
            p.pic3 = request.FILES.get('pic3')
        if request.FILES.get("pic4"):
            p.pic4 = request.FILES.get('pic4')
        p.save()
        return HttpResponseRedirect('/sellerProfile/')
       
    return render(request,'editProduct.html',{"Maincat":mainCat,
                                             "Subcat":subCat,
                                             "Brand":brand,
                                             "Product":p})



@login_required(login_url='/login/')
def wishlistPage(request,id):
    product = Product.objects.get(id = id)
    try:
        buyer = Buyer.objects.get(username = request.user)
    except:
        return HttpResponseRedirect('/profile/')

    try:
        WishList.objects.get(product = product)
    except:
        w = WishList()
        w.product = product
        w.buyer = buyer
        w.save()

    return HttpResponseRedirect('/buyerProfile/')


@login_required(login_url='/login/')
def deleteWishlist(request,id):
    wishlist = WishList.objects.get(id = id)
    try:
        buyer = Buyer.objects.get(username = request.user)
    except:
        return HttpResponseRedirect('/profile/')
    if wishlist.buyer == buyer:
        wishlist.delete()

    return HttpResponseRedirect('/buyerProfile/')




def subscribe(request):

    if request.method == "POST":
        email = request.POST.get('email')
        try:
            Subscribe.objects.get(email = email)
        except:
            subs = Subscribe()
            subs.email = email
            subs.save()

    return HttpResponseRedirect("/")
    

   

def contactus(request):
    if request.method == "POST":
        c = Contact()
        c.name = request.POST.get("name")
        c.email = request.POST.get("email")
        c.phone = request.POST.get("phone")
        c.subject = request.POST.get("subject")
        c.message = request.POST.get("message")
        c.save()
        messages.success(request,"Message Sent!!!")

    return render(request,"contactus.html")






def forgotPassword(request):
    if request.method == "POST":
        try:
            username = request.POST.get('username')
            user = Buyer.objects.get(username = username)
        except:
            try:
                user = Seller.objects.get(username = username )
            except:
                messages.error(request,"Username Not Found")
                return render(request,"forgotPassword.html")
        user.otp = random.randint(1000,9999)
        user.save()
        subject = 'welcome to MyShop.com'
        # message = f'''
        #             <h1>Hello {user.username} How are You!!</h1>

        #             <h2>Team : MyShop.com</h2>
        #             <h3>OTP  : %d</h3>
        #             '''%(user.otp)
        email_from = settings.EMAIL_HOST_USER
        recipient_list = [user.email, ]

         # send_mail( subject, message, email_from, recipient_list )
        # messages.success(request,"OTP is send on your Registered Email Id")

        
        # Below code is my customized code
        html_content = render_to_string('emailMessage.html', {'username':user.username,"Otp":user.otp}) # render with dynamic value
        text_content = strip_tags(html_content) # Strip the html tag. So people can see the pure text at least.

        # create the email, and attach the HTML version as well.
        msg = EmailMultiAlternatives(subject, text_content, email_from, recipient_list)
        msg.attach_alternative(html_content, "text/html")
        msg.send()

        return HttpResponseRedirect('/confirmOTP/'+username+'/')
        # return HttpResponseRedirect('\G:\1.  Rana Laptop\F Drive\1. Web Designing\Django 9 AM batch videos\17.  23-02-2022\MyShop\mainApp\static\images\c.rar')

    return render(request,'forgotPassword.html')




def confirmOTP(request,username):
    if request.method == "POST":
        otp = int(request.POST.get("otp"))
        try:
            user = Buyer.objects.get(username = username)
        except:
            user = Seller.objects.get(username = username )
        if otp == user.otp:
            return HttpResponseRedirect('/enterPassword/'+username+'/')
        else:
            messages.error(request,"OTP is not Valid!!!")

    return render(request,'confirmOTP.html')


def enterPassword(request,username):
    if request.method == "POST":
        password = request.POST.get("password")
        cpassword = request.POST.get("cpassword")
        try:
            user = Buyer.objects.get(username = username)
        except:
            user = Seller.objects.get(username = username )

        if password == cpassword:
            user = User.objects.get(username = username)
            user.set_password(password)
            user.save()
            return HttpResponseRedirect('/login/')
        else:
            messages.error(request,"Password and Confirm Password Does Not Match!!")

    return render(request,"enterPassword.html")



def checkoutDelete(request,id):
    buyer = Buyer.objects.get(username = request.user)
    check = Checkout.objects.get(id = id)
    if check.buyer == buyer:
        check.delete()
    return HttpResponseRedirect("/buyerProfile/")


@login_required(login_url='/login/')
def paynow(request,id):

    buyer = Buyer.objects.get(username = request.user)
    check = Checkout.objects.get(id = id)
    if check.buyer == buyer :
        orderAmount = check.finalAmount*100
        orderCurrency = "INR"
        paymentOrder = client.order.create(dict(amount = orderAmount,currency = orderCurrency,payment_capture = 1))
        paymentId = paymentOrder['id']
        # check.order_id = paymentId
        check.mode = 2
        check.save()
        return render(request,"pay.html",{
                                            "amount":orderAmount,
                                            "api_key":RAZORPAY_API_KEY,
                                            "order_id":paymentId,
                                            "User":buyer
        })









