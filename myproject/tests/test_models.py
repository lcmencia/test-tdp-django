from django.contrib.auth import get_user_model

def test_password_hashing():
    User = get_user_model()
    user = User(username="testuser")
    user.set_password("testpassword")

    assert user.check_password("testpassword")
    assert not user.check_password("otra-cosa")

def test_default_flags():

    User = get_user_model()
    user = User(username="foo")

    assert user.is_staff is False
    assert user.is_superuser is False
