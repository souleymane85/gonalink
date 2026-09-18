
from django.db import models
from django.utils.text import slugify
from accounts.models import User


class Product(models.Model):

    # ============================================================
    # UNITÉS
    # ============================================================

    UNIT = [
        ("kg", "Kg"),
        ("sac", "Sac"),
        ("piece", "Pièce"),
    ]

    # ============================================================
    # CATÉGORIES
    # ============================================================

    CATEGORY = [
        ("legume", "Légumes"),
        ("fruit", "Fruits"),
        ("cereale", "Céréales"),
        ("forestiers", "Produits forestiers"),
    ]

    # ============================================================
    # VENDEUR
    # ============================================================

    seller = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="products",
    )

    # ============================================================
    # INFORMATIONS PRODUIT
    # ============================================================

    category = models.CharField(
        max_length=20,
        choices=CATEGORY,
    )

    name = models.CharField(
        max_length=200,
    )

    slug = models.SlugField(
        max_length=220,
        unique=True,
        blank=True,
    )

    description = models.TextField(
        blank=True,
    )

    origin = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Provenance",
    )

    # ============================================================
    # PRIX / STOCK
    # ============================================================

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    stock = models.PositiveIntegerField(
        default=0,
    )

    unit = models.CharField(
        max_length=10,
        choices=UNIT,
        default="kg",
    )

    # ============================================================
    # IMAGE
    # ============================================================

    image = models.ImageField(
        upload_to="products/",
    )

    # ============================================================
    # DISPONIBILITÉ
    # ============================================================

    available = models.BooleanField(
        default=True,
    )

    # ============================================================
    # DATES
    # ============================================================

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    # ============================================================
    # SAUVEGARDE
    # ============================================================

    def save(self, *args, **kwargs):

        if not self.slug:

            base_slug = slugify(self.name)

            # Sécurité si le nom contient uniquement des
            # caractères que slugify ne peut pas convertir.
            if not base_slug:
                base_slug = "produit"

            slug = base_slug
            counter = 1

            while Product.objects.filter(
                slug=slug
            ).exclude(pk=self.pk).exists():

                slug = f"{base_slug}-{counter}"
                counter += 1

            self.slug = slug

        super().save(*args, **kwargs)

    # ============================================================
    # AFFICHAGE
    # ============================================================

    def __str__(self):
        return self.name

    # ============================================================
    # PROPRIÉTÉS UTILITAIRES
    # ============================================================

    @property
    def is_in_stock(self):
        return self.stock > 0 and self.available

    @property
    def is_low_stock(self):
        return 0 < self.stock <= 10

    @property
    def is_out_of_stock(self):
        return self.stock <= 0

