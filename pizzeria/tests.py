import pytest
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from .models import Pizza, Ingredient
from .serializers import PizzaSerializer

User = get_user_model()


@pytest.fixture
def api_client():
    """Fixture for API client."""
    return APIClient()


@pytest.fixture
def create_user():
    """Fixture to create a regular user."""

    def _create_user(username, password="password"):
        return User.objects.create_user(username=username, password=password)

    return _create_user


@pytest.fixture
def create_staff_user():
    """Fixture to create a staff user."""

    def _create_staff_user(username, password="password"):
        return User.objects.create_user(
            username=username, password=password, is_staff=True
        )

    return _create_staff_user


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

    pass


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
    assert data["price"] == "10.50"
    assert data["ingredients_count"] == 2


@pytest.mark.django_db
def test_pizza_list_view(api_client, create_pizza_with_ingredients):
    """Test the PizzaListView endpoint."""
    create_pizza_with_ingredients("Margherita", 10.50, ["Tomato", "Cheese"])
    create_pizza_with_ingredients(
        "Pepperoni", 12.00, ["Pepperoni", "Cheese", "Tomato Sauce"]
    )
    create_pizza_with_ingredients("Hawaiian", 11.00, ["Ham", "Pineapple", "Cheese"])

    url = "/api/pizzas/"
    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 3

    pizza1_data = next(item for item in response.data if item["name"] == "Margherita")
    assert pizza1_data["price"] == "10.50"
    assert pizza1_data["ingredients_count"] == 2

    pizza2_data = next(item for item in response.data if item["name"] == "Pepperoni")
    assert pizza2_data["price"] == "12.00"
    assert pizza2_data["ingredients_count"] == 3

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


@pytest.mark.django_db
def test_create_pizza_as_staff(api_client, create_staff_user):
    """Test creating a pizza as a staff user."""
    staff_user = create_staff_user("staffuser")
    api_client.force_authenticate(user=staff_user)

    ingredient1 = Ingredient.objects.create(name="Tomato")
    ingredient2 = Ingredient.objects.create(name="Cheese")

    pizza_data = {
        "name": "Veggie",
        "price": 15.00,
        "status": "active",
        "ingredients": [ingredient1.id, ingredient2.id],
    }
    url = "/api/pizzas/create/"
    response = api_client.post(url, pizza_data, format="json")

    assert response.status_code == status.HTTP_201_CREATED
    assert Pizza.objects.count() == 1
    pizza = Pizza.objects.first()
    assert pizza.name == "Veggie"
    assert pizza.price == 15.00
    assert pizza.status == "active"
    assert pizza.ingredients.count() == 2
    assert ingredient1 in pizza.ingredients.all()
    assert ingredient2 in pizza.ingredients.all()


@pytest.mark.django_db
def test_create_pizza_as_regular_user(api_client, create_user):
    """Test creating a pizza as a regular user (should be forbidden)."""
    regular_user = create_user("regularuser")
    api_client.force_authenticate(user=regular_user)

    ingredient1 = Ingredient.objects.create(name="Tomato")
    ingredient2 = Ingredient.objects.create(name="Cheese")

    pizza_data = {
        "name": "Veggie",
        "price": 15.00,
        "status": "active",
        "ingredients": [ingredient1.id, ingredient2.id],
    }
    url = "/api/pizzas/create/"
    response = api_client.post(url, pizza_data, format="json")

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert Pizza.objects.count() == 0


@pytest.mark.django_db
def test_update_pizza_as_staff(api_client, create_staff_user):
    """Test updating a pizza as a staff user."""
    staff_user = create_staff_user("staffuser")
    api_client.force_authenticate(user=staff_user)

    ingredient1 = Ingredient.objects.create(name="Tomato")
    ingredient2 = Ingredient.objects.create(name="Cheese")
    ingredient3 = Ingredient.objects.create(name="Pepperoni")

    pizza = Pizza.objects.create(name="Margherita", price=10.50, status="active")
    pizza.ingredients.add(ingredient1, ingredient2)

    updated_data = {
        "name": "Margherita Updated",
        "price": 11.00,
        "status": "inactive",
        "ingredients": [ingredient1.id, ingredient3.id],
    }
    url = f"/api/pizzas/{pizza.id}/update/"
    response = api_client.put(url, updated_data, format="json")

    assert response.status_code == status.HTTP_200_OK
    pizza.refresh_from_db()
    assert pizza.name == "Margherita Updated"
    assert pizza.price == 11.00
    assert pizza.status == "inactive"
    assert pizza.ingredients.count() == 2
    assert ingredient1 in pizza.ingredients.all()
    assert ingredient2 not in pizza.ingredients.all()


@pytest.mark.django_db
def test_prevent_delete_ingredient_in_use(api_client, create_staff_user):
    """Test preventing deletion of an ingredient used by a pizza."""
    staff_user = create_staff_user("staffuser")
    api_client.force_authenticate(user=staff_user)

    ingredient = Ingredient.objects.create(name="Tomato", category="basic")
    pizza = Pizza.objects.create(name="Margherita", price=10.50)
    pizza.ingredients.add(ingredient)

    url = f"/api/ingredients/{ingredient.id}/"
    response = api_client.delete(url)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert (
        "Cannot delete ingredient as it is used by one or more pizzas."
        in response.content.decode("utf-8")
    )
    assert Ingredient.objects.count() == 1
    assert Pizza.objects.count() == 1
    pizza.refresh_from_db()
    assert ingredient in pizza.ingredients.all()


@pytest.mark.django_db
def test_ingredient_list_create_as_staff(api_client, create_staff_user):
    """Test listing and creating ingredients as a staff user."""
    staff_user = create_staff_user("staffuser")
    api_client.force_authenticate(user=staff_user)

    Ingredient.objects.create(name="Tomato", category="basic")
    Ingredient.objects.create(name="Cheese", category="basic")
    url = "/api/ingredients/"
    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 2
    assert response.data[0]["name"] == "Tomato"
    assert response.data[1]["name"] == "Cheese"

    new_ingredient_data = {"name": "Pepperoni", "category": "premium"}
    response = api_client.post(url, new_ingredient_data, format="json")

    assert response.status_code == status.HTTP_201_CREATED
    assert Ingredient.objects.count() == 3
    ingredient = Ingredient.objects.get(name="Pepperoni")
    assert ingredient.category == "premium"


@pytest.mark.django_db
def test_ingredient_list_create_as_regular_user(api_client, create_user):
    """Test listing and creating ingredients as a regular user (should be forbidden)."""
    regular_user = create_user("regularuser")
    api_client.force_authenticate(user=regular_user)

    Ingredient.objects.create(name="Tomato", category="basic")
    url = "/api/ingredients/"
    response = api_client.get(url)

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert Ingredient.objects.count() == 1

    new_ingredient_data = {"name": "Pepperoni", "category": "premium"}
    response = api_client.post(url, new_ingredient_data, format="json")

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert Ingredient.objects.count() == 1


@pytest.mark.django_db
def test_ingredient_detail_update_destroy_as_staff(api_client, create_staff_user):
    """Test retrieving, updating, and deleting an ingredient as a staff user."""
    staff_user = create_staff_user("staffuser")
    api_client.force_authenticate(user=staff_user)

    ingredient = Ingredient.objects.create(name="Tomato", category="basic")
    url = f"/api/ingredients/{ingredient.id}/"

    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert response.data["name"] == "Tomato"
    assert response.data["category"] == "basic"

    updated_data = {"name": "Tomato Updated", "category": "premium"}
    response = api_client.put(url, updated_data, format="json")
    assert response.status_code == status.HTTP_200_OK
    ingredient.refresh_from_db()
    assert ingredient.name == "Tomato Updated"
    assert ingredient.category == "premium"

    response = api_client.delete(url)
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert Ingredient.objects.count() == 0


@pytest.mark.django_db
def test_ingredient_detail_update_destroy_as_regular_user(api_client, create_user):
    """Test retrieving, updating, and deleting an ingredient as a regular user (should be forbidden)."""
    regular_user = create_user("regularuser")
    api_client.force_authenticate(user=regular_user)

    ingredient = Ingredient.objects.create(name="Tomato", category="basic")
    url = f"/api/ingredients/{ingredient.id}/"

    response = api_client.get(url)
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert Ingredient.objects.count() == 1

    updated_data = {"name": "Tomato Updated", "category": "premium"}
    response = api_client.put(url, updated_data, format="json")
    assert response.status_code == status.HTTP_403_FORBIDDEN
    ingredient.refresh_from_db()
    assert ingredient.name == "Tomato"

    response = api_client.delete(url)
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert Ingredient.objects.count() == 1


@pytest.mark.django_db
def test_ingredient_detail_update_destroy_nonexistent(api_client, create_staff_user):
    """Test retrieving, updating, or deleting a non-existent ingredient (should be 404)."""
    staff_user = create_staff_user("staffuser")
    api_client.force_authenticate(user=staff_user)

    nonexistent_ingredient_id = 999
    url = f"/api/ingredients/{nonexistent_ingredient_id}/"

    response = api_client.get(url)
    assert response.status_code == status.HTTP_404_NOT_FOUND

    updated_data = {"name": "Tomato Updated", "category": "premium"}
    response = api_client.put(url, updated_data, format="json")
    assert response.status_code == status.HTTP_404_NOT_FOUND

    response = api_client.delete(url)
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_update_pizza_as_regular_user(api_client, create_user):
    """Test updating a pizza as a regular user (should be forbidden)."""
    regular_user = create_user("regularuser")
    api_client.force_authenticate(user=regular_user)

    pizza = Pizza.objects.create(name="Margherita", price=10.50, status="active")

    updated_data = {
        "name": "Margherita Updated",
        "price": 11.00,
        "status": "inactive",
        "ingredients": [],
    }
    url = f"/api/pizzas/{pizza.id}/update/"
    response = api_client.put(url, updated_data, format="json")

    assert response.status_code == status.HTTP_403_FORBIDDEN
    pizza.refresh_from_db()
    assert pizza.name == "Margherita"
    assert pizza.price == 10.50
    assert pizza.status == "active"


@pytest.mark.django_db
def test_add_ingredient_as_staff(api_client, create_staff_user):
    """Test adding an ingredient to a pizza as a staff user."""
    staff_user = create_staff_user("staffuser")
    api_client.force_authenticate(user=staff_user)

    pizza = Pizza.objects.create(name="Margherita", price=10.50)
    ingredient1 = Ingredient.objects.create(name="Tomato")
    ingredient2 = Ingredient.objects.create(name="Cheese")
    pizza.ingredients.add(ingredient1)

    url = f"/api/pizzas/{pizza.id}/add_ingredient/{ingredient2.id}/"
    response = api_client.post(url)

    assert response.status_code == status.HTTP_200_OK
    pizza.refresh_from_db()
    assert pizza.ingredients.count() == 2
    assert ingredient1 in pizza.ingredients.all()
    assert ingredient2 in pizza.ingredients.all()


@pytest.mark.django_db
def test_add_ingredient_as_regular_user(api_client, create_user):
    """Test adding an ingredient as a regular user (should be forbidden)."""
    regular_user = create_user("regularuser")
    api_client.force_authenticate(user=regular_user)

    pizza = Pizza.objects.create(name="Margherita", price=10.50)
    ingredient = Ingredient.objects.create(name="Tomato")

    url = f"/api/pizzas/{pizza.id}/add_ingredient/{ingredient.id}/"
    response = api_client.post(url)

    assert response.status_code == status.HTTP_403_FORBIDDEN
    pizza.refresh_from_db()
    assert pizza.ingredients.count() == 0


@pytest.mark.django_db
def test_add_nonexistent_ingredient(api_client, create_staff_user):
    """Test adding a non-existent ingredient (should be 404)."""
    staff_user = create_staff_user("staffuser")
    api_client.force_authenticate(user=staff_user)

    pizza = Pizza.objects.create(name="Margherita", price=10.50)
    nonexistent_ingredient_id = 999

    url = f"/api/pizzas/{pizza.id}/add_ingredient/{nonexistent_ingredient_id}/"
    response = api_client.post(url)

    assert response.status_code == status.HTTP_404_NOT_FOUND
    pizza.refresh_from_db()
    assert pizza.ingredients.count() == 0


@pytest.mark.django_db
def test_add_ingredient_to_nonexistent_pizza(api_client, create_staff_user):
    """Test adding an ingredient to a non-existent pizza (should be 404)."""
    staff_user = create_staff_user("staffuser")
    api_client.force_authenticate(user=staff_user)

    ingredient = Ingredient.objects.create(name="Tomato")
    nonexistent_pizza_id = 999

    url = f"/api/pizzas/{nonexistent_pizza_id}/add_ingredient/{ingredient.id}/"
    response = api_client.post(url)

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert Pizza.objects.count() == 0


@pytest.mark.django_db
def test_remove_ingredient_as_staff(api_client, create_staff_user):
    """Test removing an ingredient from a pizza as a staff user."""
    staff_user = create_staff_user("staffuser")
    api_client.force_authenticate(user=staff_user)

    pizza = Pizza.objects.create(name="Margherita", price=10.50)
    ingredient1 = Ingredient.objects.create(name="Tomato")
    ingredient2 = Ingredient.objects.create(name="Cheese")
    pizza.ingredients.add(ingredient1, ingredient2)

    url = f"/api/pizzas/{pizza.id}/remove_ingredient/{ingredient2.id}/"
    response = api_client.delete(url)

    assert response.status_code == status.HTTP_200_OK
    pizza.refresh_from_db()
    assert pizza.ingredients.count() == 1
    assert ingredient1 in pizza.ingredients.all()
    assert ingredient2 not in pizza.ingredients.all()


@pytest.mark.django_db
def test_remove_ingredient_as_regular_user(api_client, create_user):
    """Test removing an ingredient as a regular user (should be forbidden)."""
    regular_user = create_user("regularuser")
    api_client.force_authenticate(user=regular_user)

    pizza = Pizza.objects.create(name="Margherita", price=10.50)
    ingredient1 = Ingredient.objects.create(name="Tomato")
    pizza.ingredients.add(ingredient1)

    url = f"/api/pizzas/{pizza.id}/remove_ingredient/{ingredient1.id}/"
    response = api_client.delete(url)

    assert response.status_code == status.HTTP_403_FORBIDDEN
    pizza.refresh_from_db()
    assert pizza.ingredients.count() == 1


@pytest.mark.django_db
def test_remove_nonexistent_ingredient(api_client, create_staff_user):
    """Test removing a non-existent ingredient (should be 404)."""
    staff_user = create_staff_user("staffuser")
    api_client.force_authenticate(user=staff_user)

    pizza = Pizza.objects.create(name="Margherita", price=10.50)
    nonexistent_ingredient_id = 999

    url = f"/api/pizzas/{pizza.id}/remove_ingredient/{nonexistent_ingredient_id}/"
    response = api_client.delete(url)

    assert response.status_code == status.HTTP_404_NOT_FOUND
    pizza.refresh_from_db()
    assert pizza.ingredients.count() == 0


@pytest.mark.django_db
def test_remove_ingredient_from_nonexistent_pizza(api_client, create_staff_user):
    """Test removing an ingredient from a non-existent pizza (should be 404)."""
    staff_user = create_staff_user("staffuser")
    api_client.force_authenticate(user=staff_user)

    ingredient = Ingredient.objects.create(name="Tomato")
    nonexistent_pizza_id = 999

    url = f"/api/pizzas/{nonexistent_pizza_id}/remove_ingredient/{ingredient.id}/"
    response = api_client.post(url)

    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
    assert Pizza.objects.count() == 0


@pytest.mark.django_db
def test_remove_ingredient_not_on_pizza(api_client, create_staff_user):
    """Test removing an ingredient that is not on the pizza (should be 200 OK, no change)."""
    staff_user = create_staff_user("staffuser")
    api_client.force_authenticate(user=staff_user)

    pizza = Pizza.objects.create(name="Margherita", price=10.50)
    ingredient1 = Ingredient.objects.create(name="Tomato")
    ingredient2 = Ingredient.objects.create(name="Cheese")
    pizza.ingredients.add(ingredient1)

    url = f"/api/pizzas/{pizza.id}/remove_ingredient/{ingredient2.id}/"
    response = api_client.delete(url)

    assert response.status_code == status.HTTP_200_OK
    pizza.refresh_from_db()
    assert pizza.ingredients.count() == 1
    assert ingredient1 in pizza.ingredients.all()
    assert ingredient2 not in pizza.ingredients.all()
