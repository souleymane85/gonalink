from django.shortcuts import redirect, render, get_object_or_404
from django.db import transaction
from django.http import FileResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required

from .models import Order, OrderItem
from products.models import Product
from .utils import generate_invoice_pdf

import urllib.parse

# ==========================
# CHECKOUT CLIENT
# ==========================
@transaction.atomic
def checkout(request):

    cart = request.session.get("cart", {})

    if not cart:
        return redirect("cart_detail")


    # ==========================
    # PRODUITS DU PANIER
    # ==========================

    products = Product.objects.filter(
        id__in=cart.keys()
    )


    # Préparer les lignes du panier
    cart_items = []

    total_panier = 0


    for product in products:

        quantity = int(
            cart.get(str(product.id), 0)
        )

        subtotal = product.price * quantity

        total_panier += subtotal


        cart_items.append({
            "product": product,
            "quantity": quantity,
            "price": product.price,
            "subtotal": subtotal,
        })


    # ==========================
    # CREER COMMANDE
    # ==========================

    if request.method == "POST":

        order = Order.objects.create(
            name=request.POST.get("name"),
            phone=request.POST.get("phone"),
            address=request.POST.get("address"),
            status="PENDING"
        )


        total = 0


        for product in products:

            quantity = int(
                cart.get(str(product.id), 0)
            )


            # Vérifier le stock

            if product.stock < quantity:

                return render(
                    request,
                    "orders/error.html",
                    {
                        "message":
                        f"Stock insuffisant : {product.name}"
                    }
                )


            subtotal = (
                product.price * quantity
            )

            total += subtotal


            # Diminuer le stock

            product.stock -= quantity

            product.save()


            # Créer la ligne de commande

            OrderItem.objects.create(
                order=order,
                product=product,
                seller=product.seller,
                price=product.price,
                quantity=quantity
            )


        # ==========================
        # TOTAL
        # ==========================

        order.total = total

        order.save()


        # ==========================
        # PRODUITS POUR WHATSAPP
        # ==========================

        produits_message = ""

        for item in order.items.select_related("product"):

            produits_message += (
                f"- {item.product.name} "
                f"x {item.quantity} "
                f"({item.price} FCFA)\n"
            )


        # ==========================
        # DATE / HEURE
        # ==========================

        date_commande = order.created_at.strftime(
            "%d/%m/%Y à %H:%M"
        )


        # ==========================
        # VIDER PANIER
        # ==========================

        request.session["cart"] = {}

        request.session.modified = True


        # ==========================
        # WHATSAPP
        # ==========================

        phone = order.phone.strip()

        phone = phone.replace(" ", "")


        if phone.startswith("0"):

            phone = "227" + phone[1:]


        message = f"""
Bonjour {order.name},

Votre commande #{order.id} a été enregistrée.

Date :
{date_commande}

Produits :
{produits_message}

Montant :
{order.total} FCFA

Statut :
{order.get_status_display()}

Merci pour votre achat.
"""


        whatsapp_url = (
            "https://wa.me/"
            + phone
            + "?text="
            + urllib.parse.quote(message)
        )


        return render(
            request,
            "orders/order_success.html",
            {
                "order": order,
                "whatsapp_url": whatsapp_url
            }
        )


    # ==========================
    # FORMULAIRE CHECKOUT
    # ==========================

    return render(
        request,
        "orders/checkout.html",
        {
            "cart_items": cart_items,
            "total_panier": total_panier,
        }
    )




@login_required
def confirm_order(request, id):

    order = get_object_or_404(
        Order,
        id=id
    )


    order.status = "CONFIRMED"

    order.invoice_number = (
        f"FAC-{order.id}"
    )

    order.save()


    # ==========================
    # PRODUITS
    # ==========================

    produits_message = ""

    for item in order.items.select_related("product"):

        produits_message += (
            f"- {item.product.name} "
            f"x {item.quantity} "
            f"({item.price} FCFA)\n"
        )


    # ==========================
    # DATE / HEURE
    # ==========================

    date_commande = order.created_at.strftime(
        "%d/%m/%Y à %H:%M"
    )


    # ==========================
    # WHATSAPP
    # ==========================

    message = f"""
Bonjour {order.name},

Votre commande #{order.id} est confirmée.

Date :
{date_commande}

Produits :
{produits_message}

Montant :
{order.total} FCFA

Facture :
{order.invoice_number}

Merci pour votre achat.
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


    return HttpResponseRedirect(
        whatsapp
    )



# ==========================
# FACTURE PDF
# ==========================

def download_invoice(request, order_id):

    order = get_object_or_404(
        Order.objects.prefetch_related(
            "items__product"
        ),
        id=order_id
    )


    # Numéro de facture

    if not order.invoice_number:

        order.invoice_number = (
            f"FAC-{order.id}"
        )

        order.save()


    # Génération PDF

    pdf = generate_invoice_pdf(
        order
    )


    return FileResponse(
        pdf,
        as_attachment=True,
        filename=(
            f"FACTURE_{order.invoice_number}.pdf"
        )
    )


# ==========================
# ESPACE VENDEUR
# ==========================


# ==========================
# ESPACE VENDEUR
# ==========================

@login_required
def seller_orders(request):

    orders = (
        Order.objects
        .filter(items__seller=request.user)
        .prefetch_related(
            "items__product",
            "items__seller"
        )
        .distinct()
        .order_by("-created_at")
    )

    return render(
        request,
        "orders/seller_orders.html",
        {
            "orders": orders
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