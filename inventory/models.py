from PIL import Image
from django.db import models
from django.urls import reverse

# Create your models here.


class Category(models.Model):
    name = models.CharField(max_length=50, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(default='product.png', upload_to='category_pics')

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("category_detail", kwargs={"pk": self.pk})

    def save(self, *args, **kwargs):
        super(Category, self).save(*args, **kwargs)

        img = Image.open(self.image.path)

        if img.height > 600 or img.width > 500:
            output_size = (300, 300)
            img.thumbnail(output_size)
            img.save(self.image.path)