from django.urls import path
from . import views

urlpatterns = [
    path('', views.cart_detail, name='cart_detail'),
    
    path('add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('remove/<int:product_id>/', views.remove_one, name='remove_one'),
    path('delete/<int:product_id>/', views.delete_item, name='delete_item'),
    path('clear/', views.clear_cart, name='clear_cart'),
    path('cart/', views.cart, name='cart'),
]