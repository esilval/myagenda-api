from __future__ import annotations

import argparse
import json
import random
import sys

# Permite ejecución tanto dentro como fuera del paquete
try:
    from src.utils.nit import compute_check_digit  # type: ignore
except Exception:  # pragma: no cover
    # fallback cuando se ejecuta como script directo sin PYTHONPATH
    import os
    sys.path.append(os.path.dirname(os.path.dirname(__file__)))
    from src.utils.nit import compute_check_digit  # type: ignore


def generate_base_9_digits(rng: random.Random) -> str:
    # Evitar base que comience con 0 (más realista) y usar 9 dígitos
    first = str(rng.randint(1, 9))
    rest = "".join(str(rng.randint(0, 9)) for _ in range(8))
    return first + rest


def format_nit(base9: str, dv: int, with_dash: bool) -> str:
    return f"{base9}-{dv}" if with_dash else f"{base9}{dv}"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generador de NITs válidos aleatorios (Colombia)")
    parser.add_argument("-n", "--count", type=int, default=1, help="Cantidad de NITs a generar (default: 1)")
    parser.add_argument("--seed", type=int, default=None, help="Semilla para aleatoriedad (opcional)")
    parser.add_argument("--dash", action="store_true", help="Incluir guion entre base y DV (base-DV)")
    parser.add_argument("--json", action="store_true", help="Salida en JSON con campos base,dv,canonical,nit")

    args = parser.parse_args(argv)

    if args.count < 1:
        print("--count debe ser >= 1", file=sys.stderr)
        return 2

    rng = random.Random(args.seed)

    items: list[dict[str, str | int]] = []
    for _ in range(args.count):
        base9 = generate_base_9_digits(rng)
        dv = compute_check_digit(base9)
        nit = format_nit(base9, dv, with_dash=args.dash)
        items.append({
            "base": base9,
            "dv": dv,
            "canonical": f"{base9}{dv}",
            "nit": nit,
        })

    if args.json:
        print(json.dumps(items if args.count > 1 else items[0], ensure_ascii=False))
    else:
        for it in items:
            print(it["nit"])  # type: ignore[index]

    return 0


if __name__ == "__main__":
    raise SystemExit(main())


