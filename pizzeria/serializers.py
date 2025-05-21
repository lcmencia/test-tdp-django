from rest_framework import serializers
from .models import Pizza, Ingredient


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ["id", "name", "category"]


class PizzaSerializer(serializers.ModelSerializer):
    ingredients_count = serializers.SerializerMethodField()

    class Meta:
        model = Pizza
        fields = ["name", "price", "ingredients_count"]

    def get_ingredients_count(self, obj):
        return obj.ingredients.count()


class PizzaDetailSerializer(serializers.ModelSerializer):
    ingredients = IngredientSerializer(many=True, read_only=True)

    class Meta:
        model = Pizza
        fields = ["name", "price", "status", "ingredients"]


class PizzaCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pizza
        fields = ["name", "price", "status", "ingredients"]
