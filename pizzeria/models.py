from django.db import models


class Pizza(models.Model):
    STATUS_CHOICES = [
        ("active", "Active"),
        ("inactive", "Inactive"),
    ]

    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=5, decimal_places=2)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="active")
    ingredients = models.ManyToManyField("Ingredient", related_name="pizzas")

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    CATEGORY_CHOICES = [
        ("basic", "Basic"),
        ("premium", "Premium"),
    ]

    name = models.CharField(max_length=100)
    category = models.CharField(
        max_length=10, choices=CATEGORY_CHOICES, default="basic"
    )

    def __str__(self):
        return self.name
