from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Order,OrderItem



class OrderItemInline(
    admin.TabularInline
):

    model=OrderItem



@admin.register(Order)

class OrderAdmin(admin.ModelAdmin):


    list_display=(

        "id",

        "name",

        "phone",

        "total",

        "status",

        "created_at"

    )


    list_filter=(

        "status",

    )


    inlines=[

        OrderItemInline

    ]
