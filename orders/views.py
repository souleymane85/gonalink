from django.shortcuts import redirect, render, get_object_or_404
from django.db import transaction
from django.http import FileResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required

from .models import Order, OrderItem
from products.models import Product
from .utils import generate_invoice_pdf

import urllib.parse

# CHECKOUT CLIENT
# ==========================

@transaction.atomic
def checkout(request):
    cart = request.session.get("cart",{})

    if not cart:

        return redirect("cart_detail")
    # ======================
    # CREER COMMANDE
    # ======================
    if request.method == "POST":
        order = Order.objects.create(name=request.POST.get("name"), phone=request.POST.get( "phone"),address=request.POST.get( "address"),status="PENDING")
        total = 0
        products = Product.objects.filter(id__in=cart.keys())

        for product in products:
            quantity = int(cart[str(product.id)])
            # vérifier stock
            if product.stock < quantity:
                return render(request,"orders/error.html",{"message":f"Stock insuffisant : {product.name}"})

            subtotal = (product.price *quantity)
            total += subtotal
            # diminuer stock
            product.stock -= quantity

            product.save()

            OrderItem.objects.create(order=order,product=product,seller=product.seller,price=product.price,quantity=quantity)

        order.total = total

        order.save()

        # vider panier
        request.session["cart"] = {}
        # ======================
        # WHATSAPP CLIENT
        # ======================

        phone = order.phone.strip()

        phone = phone.replace(
            " ",
            ""
        )
        # Niger

        if phone.startswith("0"):

            phone = "227" + phone[1:]

        message = f"""

Bonjour {order.name},

Votre commande #{order.id}

a été enregistrée.
Montant :

{order.total} FCFA

Statut :

{order.status}

Merci pour votre achat.

"""
        whatsapp_url = (

            "https://wa.me/"

            + phone

            + "?text="

            + urllib.parse.quote(message)

        )
        return render(request,"orders/order_success.html",{"order":order, "whatsapp_url":whatsapp_url})
    # formulaire checkout

    return render(request,"orders/checkout.html")
# ==========================
# CONFIRMATION VENDEUR
# ==========================
@login_required
def confirm_order(request,id):
    order = get_object_or_404(

        Order,

        id=id

    )

    order.status = "CONFIRMED"

    order.invoice_number = (

        f"FAC-{order.id}"

    )

    order.save()

    message = f"""

Bonjour {order.name},


Votre commande #{order.id}

est confirmée.

Montant :

{order.total} FCFA


Facture :

{order.invoice_number}

Merci.

"""
    phone = order.phone.strip()
    phone = phone.replace(
        " ",
        ""
    )
    if phone.startswith("0"):

        phone = "227" + phone[1:]

    whatsapp = (

        "https://wa.me/"

        + phone

        + "?text="

        + urllib.parse.quote(message)

    )
    return HttpResponseRedirect(whatsapp)
# ==========================
# FACTURE PDF
# ==========================
def download_invoice(request, order_id):

    order = get_object_or_404(

        Order,

        id=order_id

    )

    if not order.invoice_number:

        order.invoice_number = (

            f"FAC-{order.id}"

        )
        order.save()

    pdf = generate_invoice_pdf(

        order

    )
    return FileResponse(pdf,as_attachment=True,filename=(f"FACTURE_{order.invoice_number}.pdf"))
# ==========================
# ESPACE VENDEUR
# ==========================

@login_required
def seller_orders(request):


    orders = Order.objects.filter(

        items__seller=request.user

    ).distinct().order_by(

        "-created_at"

    )


    return render(

        request,

        "orders/seller_orders.html",

        {

        "orders":orders

        }

    )
from django.shortcuts import render, get_object_or_404

from .models import Order



def order_detail(request,id):


    order = get_object_or_404(

        Order,

        id=id

    )


    return render(

        request,

        "orders/order_detail.html",

        {

        "order":order

        }

    )
    
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import Order


@login_required
def order_list(request):

    orders = Order.objects.all().order_by("-created_at")

    return render(
        request,
        "orders/order_list.html",
        {
            "orders": orders
        }
    )