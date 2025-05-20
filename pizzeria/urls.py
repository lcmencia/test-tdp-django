from django.urls import path
from .views import PizzaListView, PizzaDetailView

urlpatterns = [
    path("pizzas/", PizzaListView.as_view(), name="pizza-list"),
    path("pizzas/<int:pk>/", PizzaDetailView.as_view(), name="pizza-detail"),
]
