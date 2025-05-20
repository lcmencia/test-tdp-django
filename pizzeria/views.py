from rest_framework import generics
from .models import Pizza
from .serializers import PizzaSerializer


class PizzaListView(generics.ListAPIView):
    serializer_class = PizzaSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated and (user.is_staff or user.is_superuser):
            return Pizza.objects.all()
        else:
            return Pizza.objects.filter(status="active")
