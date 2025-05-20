from django.urls import path
from .views import PizzaListView

urlpatterns = [
    path("pizzas/", PizzaListView.as_view(), name="pizza-list"),
]
