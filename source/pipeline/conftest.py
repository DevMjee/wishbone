import pytest
from unittest.mock import patch


@pytest.mark.parametrize("value,rate,expected", [
    ("£12.99", 1.0, 1299),
    ("£0.00", 1.0, 0),
    ("Free", 1.0, 0),
    ("$19.99", 0.8, int(1999 * 0.8)),
])
