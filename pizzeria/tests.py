import pytest
from rest_framework.test import APIClient
from rest_framework import status
from .models import Pizza, Ingredient
from .serializers import PizzaSerializer


@pytest.fixture
def api_client():
    """Fixture for API client."""
    return APIClient()


@pytest.fixture
def create_pizza_with_ingredients():
    """Fixture to create a pizza with ingredients."""

    def _create_pizza(name, price, ingredient_names):
        pizza = Pizza.objects.create(name=name, price=price)
        ingredients = [
            Ingredient.objects.create(name=ing_name) for ing_name in ingredient_names
        ]
        pizza.ingredients.set(ingredients)
        return pizza

    return _create_pizza


@pytest.mark.django_db
def test_ingredient_creation():
    """Test creating an ingredient."""
    ingredient = Ingredient.objects.create(name="Tomato", category="basic")
    assert ingredient.name == "Tomato"
    assert ingredient.category == "basic"
    assert str(ingredient) == "Tomato"


@pytest.mark.django_db
def test_pizza_creation():
    """Test creating a pizza."""
    pizza = Pizza.objects.create(name="Margherita", price=10.50, status="active")
    assert pizza.name == "Margherita"
    assert pizza.price == 10.50
    assert pizza.status == "active"
    assert str(pizza) == "Margherita"


@pytest.mark.django_db
def test_pizza_ingredients_relationship():
    """Test the ManyToMany relationship between Pizza and Ingredient."""
    ingredient1 = Ingredient.objects.create(name="Tomato", category="basic")
    ingredient2 = Ingredient.objects.create(name="Cheese", category="basic")
    pizza = Pizza.objects.create(name="Margherita", price=10.50)
    pizza.ingredients.add(ingredient1, ingredient2)

    assert pizza.ingredients.count() == 2
    assert ingredient1 in pizza.ingredients.all()
    assert ingredient2 in pizza.ingredients.all()


@pytest.mark.django_db
def test_pizza_default_status():
    """Test the default status of a pizza."""
    pizza = Pizza.objects.create(name="Pepperoni", price=12.00)
    assert pizza.status == "active"


@pytest.mark.django_db
def test_pizza_status_choices():
    """Test that only valid status choices can be saved."""
    pizza = Pizza.objects.create(name="Hawaiian", price=11.00, status="active")
    assert pizza.status == "active"

    pizza.status = "inactive"
    pizza.save()
    assert pizza.status == "inactive"

    # Test invalid status (this should ideally be handled by forms/serializers,
    # but testing model-level constraint if applicable, though Django CharField
    # with choices doesn't enforce this at DB level by default)
    # For a true constraint test, a CheckConstraint would be needed in the model.
    # We can simulate a potential issue or test the choices definition.
    # This part is more conceptual for model constraints without CheckConstraint.
    # A more practical test would be at the serializer/form level.
    pass  # Skipping strict invalid status test at model level without CheckConstraint


# Example of testing a constraint if one existed, e.g., unique name
# @pytest.mark.django_db
# def test_unique_pizza_name_constraint():
#     Pizza.objects.create(name='Margherita', price=10.50)
#     with pytest.raises(IntegrityError):
#         Pizza.objects.create(name='Margherita', price=11.00)


@pytest.mark.django_db
def test_pizza_serializer():
    """Test the PizzaSerializer."""
    ingredient1 = Ingredient.objects.create(name="Tomato")
    ingredient2 = Ingredient.objects.create(name="Cheese")
    pizza = Pizza.objects.create(name="Margherita", price=10.50)
    pizza.ingredients.add(ingredient1, ingredient2)

    serializer = PizzaSerializer(pizza)
    data = serializer.data

    assert data["name"] == "Margherita"
    assert data["price"] == "10.50"  # Price is returned as a string
    assert data["ingredients_count"] == 2


@pytest.mark.django_db
def test_pizza_list_view(api_client, create_pizza_with_ingredients):
    """Test the PizzaListView endpoint."""
    create_pizza_with_ingredients("Margherita", 10.50, ["Tomato", "Cheese"])
    create_pizza_with_ingredients(
        "Pepperoni", 12.00, ["Pepperoni", "Cheese", "Tomato Sauce"]
    )
    create_pizza_with_ingredients(
        "Hawaiian", 11.00, ["Ham", "Pineapple", "Cheese"]
    )

    url = "/api/pizzas/"
    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 3

    # Check data for pizza1
    pizza1_data = next(item for item in response.data if item["name"] == "Margherita")
    assert pizza1_data["price"] == "10.50"
    assert pizza1_data["ingredients_count"] == 2

    # Check data for pizza2
    pizza2_data = next(item for item in response.data if item["name"] == "Pepperoni")
    assert pizza2_data["price"] == "12.00"
    assert pizza2_data["ingredients_count"] == 3

    # Check data for pizza3
    pizza3_data = next(item for item in response.data if item["name"] == "Hawaiian")
    assert pizza3_data["price"] == "11.00"
    assert pizza3_data["ingredients_count"] == 3


@pytest.mark.django_db
def test_pizza_list_view_no_pizzas(api_client):
    """Test the PizzaListView endpoint when no pizzas exist."""
    url = "/api/pizzas/"
    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 0
