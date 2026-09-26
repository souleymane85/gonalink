from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Sum, Count, Q

from .models import Product
from .forms import ProductForm
from orders.models import Order
from accounts.models import User


# ============================================================
# TEST ADMIN / VENDEUR
# ============================================================

def is_admin(user):
    """
    Autorise :
    - superuser
    - ADMIN
    - VENDEUR
    """

    return (
        user.is_authenticated
        and (
            user.is_superuser
            or user.role in ["ADMIN", "VENDEUR"]
        )
    )


# ============================================================
# TABLEAU DE BORD
# ============================================================

@login_required
def dashboard(request):

    if not (
        request.user.is_superuser
        or request.user.role in ["ADMIN", "VENDEUR"]
    ):
        return redirect("home")

    # ADMIN / SUPERUSER
    is_admin = (
        request.user.is_superuser
        or request.user.role == "ADMIN"
    )

    # ==========================================================
    # PRODUITS ET COMMANDES
    # ==========================================================

    if is_admin:

        products = Product.objects.all()

        orders = (
            Order.objects
            .all()
            .prefetch_related("items__product")
        )

    else:

        products = Product.objects.filter(
            seller=request.user
        )

        orders = (
            Order.objects
            .filter(
                items__seller=request.user
            )
            .distinct()
            .prefetch_related("items__product")
        )

    # ==========================================================
    # STATISTIQUES
    # ==========================================================

    total_products = products.count()

    low_stock = products.filter(
        stock__lte=10,
        stock__gt=0
    ).count()

    out_of_stock = products.filter(
        stock=0
    ).count()

    total_orders = orders.count()

    revenue = (
        orders
        .filter(status="delivered")
        .aggregate(
            total=Sum("total")
        )["total"]
        or 0
    )

    pending_orders = orders.filter(
        status="pending"
    ).count()

    delivered_orders = orders.filter(
        status="delivered"
    ).count()

    # ==========================================================
    # PRODUITS RÉCENTS
    # ==========================================================

    recent_products = (
        products
        .select_related("seller")
        .order_by("-created_at")[:5]
    )

    # ==========================================================
    # COMMANDES RÉCENTES
    #
    # items__product permet au template d'afficher :
    # {{ item.product.name }}
    # ==========================================================

    recent_orders = (
        orders
        .prefetch_related("items__product")
        .order_by("-created_at")[:5]
    )

    # ==========================================================
    # CONTEXTE
    # ==========================================================

    context = {
        "products": products,

        "total_products": total_products,
        "low_stock": low_stock,
        "out_of_stock": out_of_stock,

        "total_orders": total_orders,
        "revenue": revenue,

        "pending_orders": pending_orders,
        "delivered_orders": delivered_orders,

        "recent_products": recent_products,
        "recent_orders": recent_orders,

        "is_admin": is_admin,
    }

    # ==========================================================
    # STATISTIQUES VENDEURS POUR ADMIN
    # ==========================================================

    if is_admin:

        vendors = (
            User.objects
            .filter(role="VENDEUR")
            .annotate(
                nb_products=Count(
                    "products",
                    distinct=True
                ),

                nb_orders=Count(
                    "sales",
                    distinct=True
                ),
            )
        )

        context["vendors"] = vendors

    # ==========================================================
    # AFFICHAGE
    # ==========================================================

    return render(
        request,
        "dashboard.html",
        context
    )


# ============================================================
# PAGE D'ACCUEIL E-COMMERCE
# ============================================================

def home(request):

    category = request.GET.get("category")

    search = request.GET.get(
        "q",
        ""
    ).strip()

    # --------------------------------------------------------
    # PRODUITS DISPONIBLES
    # --------------------------------------------------------

    products = (
        Product.objects
        .filter(available=True)
        .select_related("seller")
    )

    # --------------------------------------------------------
    # RECHERCHE
    # --------------------------------------------------------

    if search:

        products = products.filter(
            Q(name__icontains=search)
            |
            Q(category__icontains=search)
        )

    # --------------------------------------------------------
    # CATÉGORIE
    # --------------------------------------------------------

    if category:

        products = products.filter(
            category=category
        )

    # --------------------------------------------------------
    # CONTEXT
    # --------------------------------------------------------

    return render(
        request,
        "home.html",
        {
            "products": products,
            "categories": Product.CATEGORY,
            "selected_category": category,
            "search_query": search,
        }
    )


# ============================================================
# DÉTAIL PRODUIT
# ============================================================

def product_detail(request, slug):

    product = get_object_or_404(
        Product.objects.select_related("seller"),
        slug=slug
    )

    return render(
        request,
        "products/detail.html",
        {
            "product": product
        }
    )


# ============================================================
# LISTE DES PRODUITS
# ============================================================

#@login_required
def product_list(request):

    # --------------------------------------------------------
    # ADMIN : tous les produits
    # VENDEUR : uniquement ses produits
    # --------------------------------------------------------

    if (
        request.user.is_superuser
        or request.user.role == "ADMIN"
    ):

        products = (
            Product.objects
            .select_related("seller")
            .all()
            .order_by("-created_at")
        )

    elif request.user.role == "VENDEUR":

        products = (
            Product.objects
            .filter(
                seller=request.user
            )
            .select_related("seller")
            .order_by("-created_at")
        )

    else:

        return redirect("home")

    return render(
        request,
        "products/product_list.html",
        {
            "products": products
        }
    )


# ============================================================
@user_passes_test(is_admin)
def product_create(request):

    if request.method == "POST":

        print("========== CREATE PRODUCT ==========")
        print("FILES :", request.FILES)
        print("POST :", request.POST)

        try:

            form = ProductForm(
                request.POST,
                request.FILES
            )

            print("FORM CREATED")
            print("FORM VALID :", form.is_valid())
            print("FORM ERRORS :", form.errors)

            if form.is_valid():

                print("FORM IS VALID")

                product = form.save(
                    commit=False
                )

                print("PRODUCT CREATED :", product)
                print("IMAGE :", product.image)

                product.seller = request.user

                print("SELLER :", product.seller)

                product.save()

                print("PRODUCT SAVED")
                print("IMAGE URL :", product.image.url)

                return redirect(
                    "product_list"
                )

        except Exception as e:

            import traceback

            print("========== ERREUR CREATE PRODUCT ==========")
            print("TYPE :", type(e).__name__)
            print("ERROR :", str(e))
            traceback.print_exc()
            print("===========================================")

            raise

    else:

        form = ProductForm()

    return render(
        request,
        "products/form.html",
        {
            "form": form
        }
    )

# ============================================================
# MODIFIER UN PRODUIT
# ============================================================

@user_passes_test(is_admin)
def product_update(request, pk):

    product = get_object_or_404(
        Product,
        pk=pk
    )

    # --------------------------------------------------------
    # Un vendeur ne peut modifier que ses produits
    # --------------------------------------------------------

    if (
        not request.user.is_superuser
        and request.user.role == "VENDEUR"
        and product.seller != request.user
    ):
        return redirect("product_list")

    # --------------------------------------------------------
    # FORMULAIRE
    # --------------------------------------------------------

    if request.method == "POST":

        form = ProductForm(
            request.POST,
            request.FILES,
            instance=product
        )

        if form.is_valid():

            form.save()

            return redirect(
                "product_list"
            )

    else:

        form = ProductForm(
            instance=product
        )

    return render(
        request,
        "products/form.html",
        {
            "form": form,
            "product": product,
        }
    )


# ============================================================
# SUPPRIMER UN PRODUIT
# ============================================================

@user_passes_test(is_admin)
def product_delete(request, pk):

    product = get_object_or_404(
        Product,
        pk=pk
    )

    # --------------------------------------------------------
    # Sécurité vendeur
    # --------------------------------------------------------

    if (
        not request.user.is_superuser
        and request.user.role == "VENDEUR"
        and product.seller != request.user
    ):
        return redirect(
            "product_list"
        )

    # --------------------------------------------------------
    # SUPPRESSION
    # --------------------------------------------------------

    if request.method == "POST":

        product.delete()

        return redirect(
            "product_list"
        )

    return render(
        request,
        "delete.html",
        {
            "product": product
        }
    )