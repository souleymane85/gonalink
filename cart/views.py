from django.shortcuts import render, redirect
from products.models import Product


from django.shortcuts import redirect
from products.models import Product

def add_to_cart(request, product_id):
    cart = request.session.get('cart', {})
    product_id = str(product_id)

    product = Product.objects.get(id=product_id)

    # STOCK PROTECTION
    current_qty = cart.get(product_id, 0)

    if product.stock <= current_qty:
        return redirect('cart_detail')

    if product.stock <= 0:
        return redirect('cart_detail')

    cart[product_id] = current_qty + 1

    request.session['cart'] = cart
    request.session.modified = True

    return redirect('cart_detail')


def cart_detail(request):
    cart = request.session.get('cart', {})

    products = Product.objects.filter(id__in=cart.keys())

    total = 0
    items = []

    for p in products:
        qty = cart.get(str(p.id), 0)

        subtotal = p.price * qty
        total += subtotal

        items.append({
            'product': p,
            'qty': qty,
            'subtotal': subtotal
        })

    return render(request, 'cart/detail.html', {
        'items': items,
        'total': total
    })


def remove_one(request, product_id):
    cart = request.session.get('cart', {})
    product_id = str(product_id)

    if product_id in cart:
        cart[product_id] -= 1

        if cart[product_id] <= 0:
            del cart[product_id]

    request.session['cart'] = cart
    request.session.modified = True

    return redirect('cart_detail')


def delete_item(request, product_id):
    cart = request.session.get('cart', {})
    product_id = str(product_id)

    if product_id in cart:
        del cart[product_id]

    request.session['cart'] = cart
    request.session.modified = True

    return redirect('cart_detail')
def clear_cart(request):
    request.session['cart'] = {}
    request.session.modified = True
    return redirect('cart_detail')
def cart(request):
    return render(request, 'cart.html')