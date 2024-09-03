from django.db import models
from django.core.validators import MinValueValidator


class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    slug = models.SlugField(max_length=200, unique=True, blank=True, null=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.slug = self.name.replace(" ", "-")
        super(Category, self).save(*args, **kwargs)


class Product(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(null=True, blank=True)
    is_new = models.BooleanField(default=False)
    stock = models.IntegerField(validators=[MinValueValidator(0)], default=1)
    seller = models.ForeignKey(
        "profile.Seller", related_name="seller", on_delete=models.CASCADE
    )
    category = models.ForeignKey(
        Category, related_name="category", on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class ProductImage(models.Model):
    product = models.ForeignKey(
        Product, related_name="product_images", on_delete=models.CASCADE
    )
    # image = models.URLField()
    image_url = models.URLField(max_length=200)  # Cloudinary image URL

    def __str__(self):
        return self.product.name
