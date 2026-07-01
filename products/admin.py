from django.contrib import admin
from .models import  Product


#@admin.register(Category)
#class CategoryAdmin(admin.ModelAdmin):
    #list_display = ('id', 'name')
    #search_fields = ('name',)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'price', 'stock', 'available')
    list_filter = ('available', 'category')
    search_fields = ('name',)
    list_editable = ('price', 'stock', 'available')
    prepopulated_fields = {'slug': ('name',)}