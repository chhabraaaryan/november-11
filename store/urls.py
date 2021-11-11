from django.urls import path
from . import views

urlpatterns = [
    path('', views.store, name='store'),
    # seperate filters by category so that it is easy to navigate
    # creating product slugs
    path('category/<slug:category_slug>/', views.store, name='products_by_category'),
    path('category/<slug:category_slug>/<slug:product_slug>/', views.product_detail, name='product_detail'),
    # HARSHIT 7
    # another path for views.search for search algorithm
    path('search/', views.search, name='search'),
    path('submit_review/<int:product_id>/', views.submit_review, name='submit_review'),
]
