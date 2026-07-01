from django.urls import path
from . import views

urlpatterns = [
    path('checkout/', views.checkout, name='checkout'),
    path('invoice/<int:order_id>/', views.download_invoice, name='invoice'),
    path("confirm/<int:id>/",views.confirm_order,name="confirm_order"),
    path("seller/orders/",views.seller_orders,name="seller_orders"),
    path("orders/<int:id>/",views.order_detail,name="order_detail"),
    path("orders/",views.order_list,name="order_list"),

   
]