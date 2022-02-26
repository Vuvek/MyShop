from django.contrib import admin
from django.urls import path
from mainApp import views
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    path('admin/', admin.site.urls),
    path('',views.home),
    path('shop/<str:mc>/<str:sc>/<str:br>/',views.shop),
    path('product/<int:id>/',views.product),
    path('login/',views.login),
    path('signup/',views.signup),
    path('logout/',views.logout),
    path('profile/',views.profile),
    path('sellerProfile/',views.sellerProfile),
    path('buyerProfile/',views.buyerProfile),
    path('updateProfile/',views.updateProfile),
    path('addProduct/',views.addProduct),
    path('editProduct/<int:id>/',views.editProduct),
    path('deleteProduct/<int:id>/',views.deleteProduct),
    path('wishlistPage/<int:id>/',views.wishlistPage),
    path('deleteWishlist/<int:id>/',views.deleteWishlist),
    path('cartPage/',views.cartPage),
    path('deleteCart/<int:id>/',views.deleteCart),
    path('checkout/',views.checkout),
    path('confirm/',views.confirmPage),
    path('paymentSucesss/<str:rppid>/<str:rpoid>/<str:rpsid>/',views.paymentSuccesss),
    path('subscirbe/',views.subscribe),
    path('contactus/',views.contactus),
    path('forgotPassword/',views.forgotPassword),
    path('confirmOTP/<str:username>/',views.confirmOTP),
    path('enterPassword/<str:username>/',views.enterPassword),
    path('checkoutDelete/<str:id>/',views.checkoutDelete),
    path('paynow/<str:id>/',views.paynow),
    
]+static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT) 
