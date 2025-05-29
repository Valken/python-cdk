from datetime import datetime
from ..post_routes import get_year_month_range


def test_get_year_month_range():
    # Define test input
    from_date = datetime(2025, 6, 1)
    to_date = datetime(2025, 1, 1)

    # Call the function
    result = list(get_year_month_range(from_date, to_date))

    # Define expected output
    expected = ["2025-06", "2025-05", "2025-04", "2025-03", "2025-02", "2025-01"]

    # Assert the result matches the expected output
    assert result == expected
