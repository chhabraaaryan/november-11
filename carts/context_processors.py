# Making cart icon dynamic

from .models import Cart, CartItem
from .views import _cart_id


def counter(request):
    cart_count = 0   # initialize cart count to function
    if 'admin' in request.path: 
        return {} #return empty dictionaryy here
    else:
        try:
             # this cart id contains session key
            cart = Cart.objects.filter(cart_id=_cart_id(request))
        
            # bring correspondiing cart items
            if request.user.is_authenticated:
                # filter it by the cart _>only need one result 
                # want to get cart items
                cart_items = CartItem.objects.all().filter(user=request.user)
                
            else:
                cart_items = CartItem.objects.all().filter(cart=cart[:1])
            for cart_item in cart_items:
                cart_count += cart_item.quantity
                
        except Cart.DoesNotExist:
            cart_count = 0
            # get number of cart items
            
        # in settings.py add cart counter
    return dict(cart_count=cart_count)
