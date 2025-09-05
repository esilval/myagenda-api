from __future__ import annotations

import re


# DIAN weighting factors for NIT DV calculation (right-to-left)
_WEIGHTS = [3, 7, 13, 17, 19, 23, 29, 37, 41, 43, 47, 53, 59, 67, 71]


def _compute_dv(base_digits: str) -> int:
    total = 0
    # align weights from rightmost digit
    for i, digit_char in enumerate(reversed(base_digits)):
        weight = _WEIGHTS[i]
        total += int(digit_char) * weight
    remainder = total % 11
    if remainder in (0, 1):
        return remainder
    return 11 - remainder


def compute_check_digit(base_digits: str) -> int:
    """Calcula el dígito de verificación (DV) para un NIT base de 9 dígitos.

    - base_digits: cadena numérica de exactamente 9 dígitos.
    - Retorna un entero entre 0 y 9.
    - Lanza ValueError si la entrada no es válida.
    """
    if not isinstance(base_digits, str) or not base_digits.isdigit() or len(base_digits) != 9:
        raise ValueError("Base del NIT debe ser una cadena de 9 dígitos")
    return _compute_dv(base_digits)


def validate_and_normalize_nit(nit: str) -> str:
    """Validate Colombian NIT format and DV, return canonical 9-digit base.

    Accepted inputs (with optional separators ".- "):
    - 9 base digits + DV (total 10 digits), e.g. "XXXXXXXXX-D" or "XXXXXXXXXD".

    Returns the 9-digit base (without DV), numeric string without separators.
    Raises ValueError if invalid.
    """
    if nit is None:
        raise ValueError("NIT is required")

    candidate = nit.strip()
    if not candidate:
        raise ValueError("NIT cannot be empty")

    # Only digits, spaces, dots and hyphen are allowed in input
    if not re.fullmatch(r"[0-9.\-\s]+", candidate):
        raise ValueError("NIT must contain only digits and optional separators (.-)")

    digits = re.sub(r"\D", "", candidate)
    if len(digits) == 10:
        base, dv_char = digits[:-1], digits[-1]
        dv_expected = _compute_dv(base)
        if int(dv_char) != dv_expected:
            raise ValueError("Invalid NIT check digit (DV)")
        return base

    # If exactly 9 digits provided, treat as invalid input (base only is ambiguous)
    if len(digits) == 9:
        raise ValueError("NIT must include check digit (provide 9 base digits plus DV)")

    raise ValueError("NIT must be 9 base digits plus 1 check digit (total 10 digits)")


