from django.db import models

# Create your models here.


class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return f' topic: {self.name}'


class Book(models.Model):
    title = models.CharField(max_length=100)
    author = models.CharField(max_length=100)
    category = models.ForeignKey(to=Category, on_delete=models.PROTECT, related_name='books', null=True)

    def __str__(self):
        return self.title + " - " + self.author + " - " + self.category.name

