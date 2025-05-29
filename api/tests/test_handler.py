from ..handler import get_todos
from ..routes import get_threedos, post_pets
from ..schemas import Model


def test_get_todos():
    result = get_todos()
    assert result == {"message": "Hello World"}


def test_get_threedos():
    from unittest.mock import patch

    with patch("api.routes.ssm_provider.get") as mock_get:
        mock_get.return_value = "something"
        result = get_threedos()
        assert result == {"hello": "something"}


def test_post_pets():
    model = Model(pet={"pet_type": "cat", "meows": 3}, n=5)
    result = post_pets(model)
    assert result == {"message": model}
