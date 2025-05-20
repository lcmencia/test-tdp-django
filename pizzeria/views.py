from django.shortcuts import get_object_or_404

from rest_framework import generics, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Ingredient, Pizza
from .serializers import (
    PizzaSerializer,
    PizzaDetailSerializer,
    PizzaCreateUpdateSerializer,
)


class PizzaListView(generics.ListAPIView):
    serializer_class = PizzaSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated and (user.is_staff or user.is_superuser):
            return Pizza.objects.all()
        else:
            return Pizza.objects.filter(status="active")


class PizzaDetailView(generics.RetrieveAPIView):
    queryset = Pizza.objects.all()
    serializer_class = PizzaDetailSerializer


class PizzaCreateView(generics.CreateAPIView):
    queryset = Pizza.objects.all()
    serializer_class = PizzaCreateUpdateSerializer
    permission_classes = [IsAdminUser]


class PizzaUpdateView(generics.RetrieveUpdateAPIView):
    queryset = Pizza.objects.all()
    serializer_class = PizzaCreateUpdateSerializer
    permission_classes = [IsAdminUser]

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        user = request.user

        if instance.status == "inactive" and not (
            user.is_authenticated and (user.is_staff or user.is_superuser)
        ):
            raise PermissionDenied(
                "You do not have permission to view inactive pizzas."
            )

        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class PizzaAddIngredientView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, pk, ingredient_pk):
        pizza = get_object_or_404(Pizza, pk=pk)
        ingredient = get_object_or_404(Ingredient, pk=ingredient_pk)

        pizza.ingredients.add(ingredient)
        return Response({"status": "ingredient added"}, status=status.HTTP_200_OK)


class PizzaRemoveIngredientView(APIView):
    permission_classes = [IsAdminUser]

    def delete(self, request, pk, ingredient_pk):
        pizza = get_object_or_404(Pizza, pk=pk)
        ingredient = get_object_or_404(Ingredient, pk=ingredient_pk)

        pizza.ingredients.remove(ingredient)
        return Response({"status": "ingredient removed"}, status=status.HTTP_200_OK)
