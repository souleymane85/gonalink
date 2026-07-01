from django.db import models
from django.db import models
from django.utils.text import slugify
from accounts.models import User
#class Category(models.Model):
    #name = models.CharField(max_length=100)

    #def __str__(self):
        #return self.name


class Product(models.Model):
    UNIT = [
        ('kg', 'Kg'),
        ('sac', 'Sac'),
        ('piece', 'Pièce'),
    ]
    CATEGORY = [
        ('legume', 'Légumes'),
        ('fruit', 'Fruits'),
        ('cereale', 'Céréales'),
        ('tubercule', 'Tubercules'),
    ]
    seller = models.ForeignKey(User,on_delete=models.CASCADE,null=True,blank=True)

    category = models.CharField(max_length=20, choices=CATEGORY)
    
    
    #category = models.ForeignKey(Category, on_delete=models.CASCADE)
    
    name = models.CharField(max_length=200)
    slug = models.SlugField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField(default=0)
    unit = models.CharField(max_length=10, choices=UNIT, default='kg')
    image = models.ImageField(upload_to='products/')
    available = models.BooleanField(default=True)
    description = models.TextField(blank=True)
    origin = models.CharField(max_length=100,blank=True,verbose_name="Provenance")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1

            while Product.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            self.slug = slug

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name