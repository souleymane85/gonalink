
from django.shortcuts import render, get_object_or_404,redirect
from .models import Product #, Category
from .forms import ProductForm
from django.contrib.auth.decorators import user_passes_test


from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Sum

from .models import Product
from orders.models import Order, OrderItem


from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Sum

from .models import Product
from orders.models import Order



@login_required
def dashboard(request):


    # ADMIN Django ou vendeur

    if not (
        request.user.is_superuser
        or request.user.role in ["ADMIN","VENDEUR"]
    ):

        return redirect("home")



    # produits

    if request.user.is_superuser or request.user.role=="ADMIN":


        products = Product.objects.all()


        orders = Order.objects.all()


    else:


        products = Product.objects.filter(

            seller=request.user

        )


        orders = Order.objects.filter(

            items__seller=request.user

        ).distinct()





    total_products = products.count()



    low_stock = products.filter(

        stock__lte=10,

        stock__gt=0

    ).count()



    out_of_stock = products.filter(

        stock=0

    ).count()



    total_orders = orders.count()



    revenue = orders.filter(

        status="delivered"

    ).aggregate(

        total=Sum("total")

    )["total"] or 0



    return render(
    request,
    "dashboard.html",
    {
        "products": products,
        "total_products": total_products,
        "low_stock": low_stock,
        "out_of_stock": out_of_stock,
        "total_orders": total_orders,
        "revenue": revenue,
    }
)

def home(request):
    products = Product.objects.filter(available=True)
    return render(request, 'home.html', {'products': products})

def is_admin(user):
    
    return (
        user.is_superuser
        or user.role in ["ADMIN","VENDEUR"]
    )

def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    return render(request, 'products/detail.html', {'product': product})

# Ajouter un produit
#@user_passes_test(is_admin)
def product_create(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
    
            product = form.save(commit=False)
            product.seller = request.user
            product.save()

            return redirect('product_list')
    else:
        form = ProductForm()

    return render(request, 'products/form.html', {
        'form': form
    })
    
    
def product_list(request):
    products = Product.objects.all()
    return render(request, 'products/product_list.html', {
        'products': products
    })

# Modifier un produit
@user_passes_test(is_admin)
def product_update(request, pk):
    product = get_object_or_404(Product, pk=pk)

    if request.method == 'POST':
        form = ProductForm(
            request.POST,
            request.FILES,
            instance=product
        )

        if form.is_valid():
            form.save()
            return redirect('product_list')
    else:
        form = ProductForm(instance=product)

    return render(request, 'products/form.html', {
    'form': form
})

# Supprimer un produit
@user_passes_test(is_admin)
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)

    if request.method == 'POST':
        product.delete()
        return redirect('product_list')

    return render(request, 'delete.html', {
        'product': product
    })