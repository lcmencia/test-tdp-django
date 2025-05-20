from django.urls import path
from .views import (
    PizzaListView,
    PizzaDetailView,
    PizzaCreateView,
    PizzaUpdateView,
    PizzaAddIngredientView,
    PizzaRemoveIngredientView,
)

urlpatterns = [
    path("pizzas/", PizzaListView.as_view(), name="pizza-list"),
    path("pizzas/create/", PizzaCreateView.as_view(), name="pizza-create"),
    path("pizzas/<int:pk>/", PizzaDetailView.as_view(), name="pizza-detail"),
    path("pizzas/<int:pk>/update/", PizzaUpdateView.as_view(), name="pizza-update"),
    path(
        "pizzas/<int:pk>/add_ingredient/<int:ingredient_pk>/",
        PizzaAddIngredientView.as_view(),
        name="pizza-add-ingredient",
    ),
    path(
        "pizzas/<int:pk>/remove_ingredient/<int:ingredient_pk>/",
        PizzaRemoveIngredientView.as_view(),
        name="pizza-remove-ingredient",
    ),
]
