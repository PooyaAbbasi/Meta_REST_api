from django.db import models

# Create your models here.


class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return f' topic: {self.name}'


class Book(models.Model):
    title = models.CharField(max_length=100)
    author = models.CharField(max_length=100)
    category = models.ForeignKey(to=Category, on_delete=models.PROTECT, related_name='books')
    price = models.DecimalField(max_digits=10, decimal_places=2, default=20)

    def __str__(self):
        return self.title + " - " + self.author + " - " + self.category.name

