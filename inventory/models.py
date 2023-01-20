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


MARKET_CATEGORY = (
    ('Local', 'Local'),
    ('Foreign', 'Foreign'),
)


class Customers(models.Model):
    name = models.CharField(max_length=50, blank=True, null=True)
    location = models.CharField(max_length=50, blank=True, null=True)
    contact_no = models.CharField(max_length=50, blank=True, null=True)
    category = models.CharField(max_length=50, choices=MARKET_CATEGORY, blank=True, null=True)
    country = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("customer_detail", kwargs={"pk": self.pk})


Invoice_Choice = (
    ('Credit', 'Credit'),
    ('Full Payment', 'Full Payment'),
    ('Part Payment', 'Part Payment'),
    ('Take Balance', 'Take Balance'),
)


class Stock(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, blank=True)
    item_name = models.CharField(max_length=50, blank=True, null=True)
    image = models.ImageField(default='product.png', upload_to='category_pics')
    receipt_no = models.CharField(max_length=50, blank=True, null=True)
    item_description = models.TextField(blank=True, null=True)
    quantity = models.IntegerField(default='0', blank=True, null=True)
    returned_quantity = models.IntegerField(default='0', blank=True, null=True)
    returned_by = models.ForeignKey(Customers, on_delete=models.DO_NOTHING, blank=True)
    unit_returned_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    total_returned_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    sale_quantity = models.IntegerField(default='0', blank=True, null=True)
    delivery_quantity = models.IntegerField(default='0', blank=True, null=True)
    yet_to_deliver = models.IntegerField(default='0', blank=True, null=True)
    waybill_number = models.CharField(max_length=50, blank=True, null=True)
    sale_by = models.CharField(max_length=50, blank=True, null=True)
    sale_to = models.ForeignKey(Customers, on_delete=models.DO_NOTHING, blank=True, related_name='sale_to')
    unit_sale_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    total_sale_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    payment_status = models.CharField(max_length=50, choices=Invoice_Choice, blank=True, null=True)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    phone_number = models.CharField(max_length=50, blank=True, null=True)
    created_on = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.item_name

    def get_absolute_url(self):
        return reverse("stock_detail", kwargs={"pk": self.pk})