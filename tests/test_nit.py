import pytest

from src.utils.nit import validate_and_normalize_nit


@pytest.mark.parametrize(
    "raw, expected",
    [
        ("800.197.268-4", "800197268"),
        ("800197268-4", "800197268"),
        ("8001972684", "800197268"),
    ],
)
def test_nit_valid_examples(raw, expected):
    assert validate_and_normalize_nit(raw) == expected


@pytest.mark.parametrize("raw", ["800197268-5", "8001972685", "123456780", "111111111"])
def test_nit_invalid_check_digit(raw):
    with pytest.raises(ValueError):
        validate_and_normalize_nit(raw)


@pytest.mark.parametrize("raw", ["", "abc", "12-34x", "12345678", "1234567890"])
def test_nit_invalid_format_or_length(raw):
    with pytest.raises(ValueError):
        validate_and_normalize_nit(raw)


