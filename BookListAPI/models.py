from django.db import models
from django.contrib.auth.models import User
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


class Rating(models.Model):
    rating = models.SmallIntegerField(null=False, )
    book = models.ForeignKey(to=Book, on_delete=models.CASCADE, related_name='ratings')
    user = models.ForeignKey(to=User, on_delete=models.CASCADE, related_name='ratings')

    def __str__(self):
        return f'user = {self.user.username} - book = {self.book.title} - rating = {self.rating}'

    class Meta:
        unique_together = ['user', 'book']

