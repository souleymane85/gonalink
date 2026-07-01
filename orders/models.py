from django.db import models
from products.models import Product
from django.conf import settings



class Order(models.Model):


    STATUS = [

        ('pending', 'En attente'),

        ('confirmed', 'Confirmée'),

        ('shipped', 'Expédiée'),

        ('delivered', 'Livrée'),

        ('cancelled', 'Annulée'),

    ]


    invoice_number = models.CharField(

        max_length=20,

        unique=True,

        blank=True,

        null=True

    )



    # CLIENT ANONYME

    name = models.CharField(

        max_length=150

    )


    phone = models.CharField(

        max_length=30

    )


    address = models.CharField(

        max_length=255

    )



    total = models.DecimalField(

        max_digits=10,

        decimal_places=2,

        default=0

    )



    status = models.CharField(

        max_length=20,

        choices=STATUS,

        default='pending'

    )



    created_at = models.DateTimeField(

        auto_now_add=True

    )





    def save(self,*args,**kwargs):


        if not self.invoice_number:


            last = Order.objects.count()+1


            self.invoice_number = (

                f"INV-{last:05d}"

            )



        super().save(*args,**kwargs)





    def __str__(self):

        return f"Commande #{self.id} - {self.name}"









class OrderItem(models.Model):


    order = models.ForeignKey(Order,

        on_delete=models.CASCADE,

        related_name="items"

    )



    product = models.ForeignKey(Product,on_delete=models.PROTECT)
# vendeur du produit
    seller = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name="sales", null=True,blank=True)
    price = models.DecimalField(max_digits=10,decimal_places=2)

    quantity = models.PositiveIntegerField()

    def subtotal(self):

        return self.price * self.quantity