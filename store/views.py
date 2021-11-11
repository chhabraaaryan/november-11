from django.shortcuts import render, get_object_or_404, redirect
from .models import Product, ReviewRating, ProductGallery
from category.models import Category
# default for cart_item to check if it exists -> true or false
from carts.models import CartItem
from django.db.models import Q

from carts.views import _cart_id
#  Harshit3

# modules for paginator
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.http import HttpResponse #for search algorithm.
from .forms import ReviewForm
from django.contrib import messages
from orders.models import OrderProduct

# ====================================================================================================


# Getting all products here
def store(request, category_slug=None):
    categories = None
    products = None

    # products by categories
    if category_slug != None:
        categories = get_object_or_404(Category, slug=category_slug)
        products = Product.objects.filter(category=categories, is_available=True)
        paginator = Paginator(products, 1)
        page = request.GET.get('page')
        paged_products = paginator.get_page(page)
        product_count = products.count()
    
    # all products
    else:
        # Have all the products here
        products = Product.objects.all().filter(is_available=True).order_by('id') #order_by(id) removes warning
        # from imported paginator, decide how many products to be shown in one page
        paginator = Paginator(products, 3)
        page = request.GET.get('page') #Capture URL that comes with the page number
        paged_products = paginator.get_page(page) #the 3 products will get stored here
        product_count = products.count()

    context = {
        'products': paged_products, #copied from above, this contains the 3 products now
        'product_count': product_count, 
    }
    return render(request, 'store/store.html', context)



# ====================================================================================================



def product_detail(request, category_slug, product_slug):
    try:
        single_product = Product.objects.get(category__slug=category_slug, slug=product_slug)
        # check cart item
        # filter items: check if cart model. cart is foreign key of item
        # access cart first 
        in_cart = CartItem.objects.filter(cart__cart_id=_cart_id(request), product=single_product).exists()
        # if this query returns anything then it will return true -> show add to cart button
        # cart_id imported 
    except Exception as e:
        
        raise e
# otherwise false and does not show add to cart button
    if request.user.is_authenticated:
        try:
            orderproduct = OrderProduct.objects.filter(user=request.user, product_id=single_product.id).exists()
        except OrderProduct.DoesNotExist:
            orderproduct = None
    else:
        orderproduct = None

    # Get the reviews
    reviews = ReviewRating.objects.filter(product_id=single_product.id, status=True)

    # Get the product gallery
    product_gallery = ProductGallery.objects.filter(product_id=single_product.id)

    context = {
        'single_product': single_product,
        'in_cart'       : in_cart, #pass item to dictionary
        'orderproduct': orderproduct,
        'reviews': reviews,
        'product_gallery': product_gallery,
    }
    return render(request, 'store/product_detail.html', context)



# ====================================================================================================


# HARSHIT 8
# SEARCH algorithm as path made in urls
def search(request):
    #  make different page and bring data
    # get from templates>includes>navbar
    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
        # first taking if get request has keyword or not
        if keyword:
            # check if keyword is not blank
            products = Product.objects.order_by('-created_date').filter(Q(description__icontains=keyword) | Q(product_name__icontains=keyword))
            # even if one of above conditions work it will run
            # Q is imported from django.db.models which will get OR function -> complex queries
            # filter will check for description if it equals keyword-> finding relatetd stuff to search result page
            product_count = products.count()
            # storing that value inside the keyword, which will use in future to fetch details
            # from database
    context = {
        # 
        'products': products,
        'product_count': product_count, #pass product count to bring all products
    }
    return render(request, 'store/store.html', context)


# ====================================================================================================





def submit_review(request, product_id):
    url = request.META.get('HTTP_REFERER')
    if request.method == 'POST':
        try:
            reviews = ReviewRating.objects.get(user__id=request.user.id, product__id=product_id)
            form = ReviewForm(request.POST, instance=reviews)
            form.save()
            messages.success(request, 'Thank you! Your review has been updated.')
            return redirect(url)
        except ReviewRating.DoesNotExist:
            form = ReviewForm(request.POST)
            if form.is_valid():
                data = ReviewRating()
                data.subject = form.cleaned_data['subject']
                data.rating = form.cleaned_data['rating']
                data.review = form.cleaned_data['review']
                data.ip = request.META.get('REMOTE_ADDR')
                data.product_id = product_id
                data.user_id = request.user.id
                data.save()
                messages.success(request, 'Thank you! Your review has been submitted.')
                return redirect(url)
