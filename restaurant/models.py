from django.db import models
from django.utils.text import slugify
from django.contrib.auth.models import User

from decimal import Decimal
# Create your models here.


class Category(models.Model):
    slug = models.SlugField(null=False)
    title = models.CharField(max_length=255)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        self.slug = slugify(self.title)
        if update_fields is not None and 'title' in update_fields:
            update_fields = {'slug'}.union(update_fields)

        super().save(force_insert, force_update, using, update_fields)

    def get_absolute_url(self):
        # TODO return url
        pass


class MenuItem(models.Model):
    title = models.CharField(max_length=255, db_index=True)
    slug = models.SlugField(null=False)
    price = models.DecimalField(decimal_places=2, max_digits=10, db_index=True)
    featured = models.BooleanField(default=False, db_index=True)
    category = models.ForeignKey(to=Category, on_delete=models.PROTECT, related_name='menu_items')

    def get_absolute_url(self):
        # TODO return absolute url
        pass

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        self.slug = slugify(self.title)
        if update_fields is not None and 'title' in update_fields:
            update_fields = {'slug'}.union(update_fields)

        super().save(force_insert, force_update, using, update_fields)


class Cart(models.Model):
    user = models.ForeignKey(to=User, on_delete=models.CASCADE)
    menu_item = models.ForeignKey(to=MenuItem, on_delete=models.CASCADE)
    quantity = models.SmallIntegerField(default=1)

    class Meta:
        unique_together = ('user', 'menu_item')

    @classmethod
    def get_total_price_for(cls, user: User):
        """
        :return: total price of all purchased items of user
        """
        return sum((cart.price for cart in cls.objects.filter(user=user)))
        pass

    @property
    def price(self) -> Decimal:
        return self.menu_item.price * self.quantity

    @property
    def unit_price(self) -> Decimal:
        return self.menu_item.price


class Order(models.Model):
    user = models.ForeignKey(to=User, on_delete=models.CASCADE, related_name='orders')
    status = models.BooleanField(default=False, help_text='is delivered or not')
    total_price = models.DecimalField(decimal_places=2, max_digits=10)
    delivery_crew = models.ForeignKey(to=User, on_delete=models.PROTECT, related_name='assigned_orders', null=True)
    date_time = models.DateTimeField(db_index=True, auto_now_add=True)


class OrderItem(models.Model):
    menu_item = models.ForeignKey(to=MenuItem, on_delete=models.CASCADE)
    quantity = models.SmallIntegerField(default=1)
    unit_price = models.DecimalField(decimal_places=2, max_digits=10)
    order = models.ForeignKey(to=Order, on_delete=models.CASCADE, related_name='order_items', db_index=True)

    class Meta:
        unique_together = ('order', 'menu_item')
