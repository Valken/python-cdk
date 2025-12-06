from unittest.mock import patch

from ..schemas import Model
from ..thing_routes import get_threedos, post_pets


def test_get_threedos() -> None:
    """Test get_threedos endpoint with mocked SSM parameter."""
    with patch("api.thing_routes.get_ssm_parameter") as mock_get:
        mock_get.return_value = "something"
        result = get_threedos()
        assert result == {"hello": "something"}
        mock_get.assert_called_once_with("/hello-world/something")


def test_post_pets() -> None:
    """Test post_pets endpoint with a cat model."""
    model = Model(pet={"pet_type": "cat", "meows": 3}, n=5)
    result = post_pets(model)
    assert result == {"message": model}
