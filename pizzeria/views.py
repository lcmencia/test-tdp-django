from rest_framework import generics
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from .models import Pizza
from .serializers import PizzaSerializer, PizzaDetailSerializer


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

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        user = request.user

        if instance.status == 'inactive' and not (user.is_authenticated and (user.is_staff or user.is_superuser)):
            raise PermissionDenied("You do not have permission to view inactive pizzas.")

        serializer = self.get_serializer(instance)
        return Response(serializer.data)
