from rest_framework import serializers
from .models import Pizza


class PizzaSerializer(serializers.ModelSerializer):
    ingredients_count = serializers.SerializerMethodField()

    class Meta:
        model = Pizza
        fields = ["name", "price", "ingredients_count", "status"]

    def get_ingredients_count(self, obj):
        return obj.ingredients.count()
