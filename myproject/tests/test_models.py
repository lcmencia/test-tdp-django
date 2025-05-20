from django.contrib.auth import get_user_model

def test_password_hashing():
    """
    Comprobamos que el método set_password genera un hash válido
    sin guardar nada en la BD.
    """
    User = get_user_model()
    user = User(username="testuser")  # 💡 no hace .save()
    user.set_password("testpassword")

    assert user.check_password("testpassword")
    assert not user.check_password("otra-cosa")

def test_default_flags():
    """
    Un usuario recién instanciado (sin persistir) debe tener los
    flags de staff/superuser en False.
    """
    User = get_user_model()
    user = User(username="foo")

    assert user.is_staff is False
    assert user.is_superuser is False
