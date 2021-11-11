# ===============================================================================================================

# IMPORTS

from django.shortcuts import render, redirect, get_object_or_404
from .forms import RegistrationForm, UserForm, UserProfileForm
from django.contrib import messages, auth
from django.utils.encoding import force_bytes # Verification email
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from .models import Account, UserProfile  #save details on db
from orders.models import Order, OrderProduct
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage
from carts.views import _cart_id
from carts.models import Cart, CartItem
import requests
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode

# ===============================================================================================================

# HARSHIT B
# the same way can be used for different registter portal
# create new folder in accounts
def register(request):
    # Create a register of html 
    
    if request.method == 'POST':
        form = RegistrationForm(request.POST) #bring from .forms import 
        # contrain all form values in post 
        
        # Fetch all fields from form post
        # to Create a profile
        if form.is_valid():
            first_name = form.cleaned_data['first_name'] #For django have to use clelaned_data to fetch
            last_name = form.cleaned_data['last_name']
            phone_number = form.cleaned_data['phone_number']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            # username here will be created from the first part of user's email id, 
            username = email.split("@")[0]
            
            # pass all the fields to create user account using django module
            user = Account.objects.create_user(first_name=first_name, last_name=last_name, email=email, username=username, password=password)
            user.phone_number = phone_number
            user.save()

            # user profile
            profile = UserProfile()
            profile.user_id = user.id
            profile.profile_picture = 'default/default-user.png'
            profile.save()

            # user account activation -> token based activation
            current_site = get_current_site(request) #get current site apart from local host
            mail_subject = 'Kindly activate your account'
            message = render_to_string('accounts/account_verification_email.html', {
                'user': user, #Need primary key of user
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)), #user primary key
                #URLsafe -> encoding user id with url safe
                # so nobody can see primary key
                # when activated account -> decode 
                'token': default_token_generator.make_token(user), #defaul token generator from library -> create token 
                # of the particular user
    
            })
            
            # Send email confirmation 
            to_email = email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()
            # using accountt verification html
            # messages.success(request, 'Registration Successful!') # (since it will disappear)
            return redirect('/accounts/login/?command=verification&email='+email)
    
    else:
    # registration form should render
        form = RegistrationForm()
        
        # form variable available at register.html
    context = {
        'form': form,
    }
    return render(request, 'accounts/register.html', context) 





# ===============================================================================================================

# Function for login

def login(request):
    if request.method == 'POST':
        email = request.POST['email']
        # input fields
        password = request.POST['password']

        user = auth.authenticate(email=email, password=password)
        # return user object

        if user is not None:
            # redirect to dashboard
            try:
                cart = Cart.objects.get(cart_id=_cart_id(request))
                is_cart_item_exists = CartItem.objects.filter(cart=cart).exists()
                if is_cart_item_exists:
                    cart_item = CartItem.objects.filter(cart=cart)

                    # PRODUCT VARIATION AS PEER CART ID
                    product_variation = []
                    for item in cart_item:
                        variation = item.variations.all()
                        product_variation.append(list(variation))

                    cart_item = CartItem.objects.filter(user=user)
                    ex_var_list = []
                    id = []
                    for item in cart_item:
                        existing_variation = item.variations.all()
                        ex_var_list.append(list(existing_variation))
                        id.append(item.id)

                    for pr in product_variation:
                        if pr in ex_var_list:
                            index = ex_var_list.index(pr)
                            item_id = id[index]
                            item = CartItem.objects.get(id=item_id)
                            item.quantity += 1
                            item.user = user
                            item.save()
                        else:
                            cart_item = CartItem.objects.filter(cart=cart)
                            for item in cart_item:
                                item.user = user
                                item.save()
            except:
                pass
            auth.login(request, user)
            messages.success(request, 'You are now logged in.')
            url = request.META.get('HTTP_REFERER')
            try:
                query = requests.utils.urlparse(url).query
                # next=/cart/checkout/
                params = dict(x.split('=') for x in query.split('&'))
                if 'next' in params:
                    nextPage = params['next']

                    return redirect(nextPage)
            except:
                # when logged in go direct to dashboard 
                return redirect('dashboard')
        else:
            
            # wrong password
            messages.error(request, 'Invalid login credentials')
            return redirect('login')
    return render(request, 'accounts/login.html')


# logout user

# bring import login requirement decor. from django
@login_required(login_url = 'login') #only log out when logged in
def logout(request):
    auth.logout(request)
    messages.success(request, 'Logged Out.')
    return redirect('login')



# ===============================================================================================================

# Method for activating account

def activate(request, uidb64, token):
    try:
        # use base decide
        # decode uibd and store it there
        # give primary key of user
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
        # turn user object
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist): #handle errors
        user = None
        
        # check token
        # if there is no error then .check_token
    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        
        # send message 
        messages.success(request, 'Yipee! Your account is activated!')
        return redirect('login')
    else:
        messages.error(request, 'Invalid activation link')
        return redirect('register')
    
                    
# ===============================================================================================================

# create dashboard

@login_required(login_url = 'login') #can only view it logged in 
def dashboard(request):
    orders = Order.objects.order_by('-created_at').filter(user_id=request.user.id, is_ordered=True)
    orders_count = orders.count()

    userprofile = UserProfile.objects.get(user_id=request.user.id)
    context = {
        'orders_count': orders_count,
        'userprofile': userprofile,
    }
    return render(request, 'accounts/dashboard.html', context)



# ===============================================================================================================


# forgot password method

def forgotPassword(request):
    # check if request post or not
    if request.method == 'POST':
        email = request.POST['email']
        # check if account exist or not
        if Account.objects.filter(email=email).exists():
            user = Account.objects.get(email__exact=email)
            
            
            # resetting password via email
            current_site = get_current_site(request) #current site same copied from before
            mail_subject = 'Password Reset'
            message = render_to_string('accounts/reset_password_email.html', {
                'user': user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            to_email = email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()

            # once email is sent:
            messages.success(request, 'Password reset email has been sent to your email address.')
            return redirect('login') #otherwise it will give error
        
        # account does not exist
        else:
            messages.error(request, 'Account does not exist!')
            return redirect('forgotPassword')
    return render(request, 'accounts/forgotPassword.html')




# ================================================


# Forgot > Reset Passward 

def resetpassword_validate(request, uidb64, token):
    try:
        # token is to know if it is a secure request or not
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        
        request.session['uid'] = uid
        messages.success(request, 'Kindly reset your password')
        return redirect('resetPassword')
    else:
        
        messages.error(request, 'Link Expired!')
        return redirect('login')




# ===============================================



def resetPassword(request):
    # check if request post or not
    if request.method == 'POST':
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password == confirm_password:
            uid = request.session.get('uid')
            user = Account.objects.get(pk=uid)
            user.set_password(password)
            user.save()
            messages.success(request, 'Password reset successful')
            return redirect('login')
        else:
            messages.error(request, 'Password do not match!')
            return redirect('resetPassword')
    else:
        return render(request, 'accounts/resetPassword.html')



# ===============================================================================================================
# ===============================================================================================================
# ===============================================================================================================

@login_required(login_url='login') #Dec.
def my_orders(request):
    orders = Order.objects.filter(user=request.user, is_ordered=True).order_by('-created_at')
    context = {
        'orders': orders,
    }
    return render(request, 'accounts/my_orders.html', context)


@login_required(login_url='login')
def edit_profile(request):
    userprofile = get_object_or_404(UserProfile, user=request.user)
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=userprofile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile has been updated.')
            return redirect('edit_profile')
    else:
        user_form = UserForm(instance=request.user)
        profile_form = UserProfileForm(instance=userprofile)
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'userprofile': userprofile,
    }
    return render(request, 'accounts/edit_profile.html', context)


@login_required(login_url='login')
def change_password(request):
    if request.method == 'POST':
        current_password = request.POST['current_password']
        new_password = request.POST['new_password']
        confirm_password = request.POST['confirm_password']

        user = Account.objects.get(username__exact=request.user.username)

        if new_password == confirm_password:
            success = user.check_password(current_password)
            if success:
                user.set_password(new_password)
                user.save()
                # auth.logout(request)
                messages.success(request, 'Password updated successfully.')
                return redirect('change_password')
            else:
                messages.error(request, 'Please enter valid current password')
                return redirect('change_password')
        else:
            messages.error(request, 'Password does not match!')
            return redirect('change_password')
    return render(request, 'accounts/change_password.html')


@login_required(login_url='login')
def order_detail(request, order_id):
    order_detail = OrderProduct.objects.filter(order__order_number=order_id)
    order = Order.objects.get(order_number=order_id)
    subtotal = 0
    for i in order_detail:
        subtotal += i.product_price * i.quantity

    context = {
        'order_detail': order_detail,
        'order': order,
        'subtotal': subtotal,
    }
    return render(request, 'accounts/order_detail.html', context)
