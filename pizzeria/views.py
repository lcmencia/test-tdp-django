from rest_framework import generics
from .models import Pizza
from .serializers import PizzaSerializer


class PizzaListView(generics.ListAPIView):
    queryset = Pizza.objects.all()
    serializer_class = PizzaSerializer
