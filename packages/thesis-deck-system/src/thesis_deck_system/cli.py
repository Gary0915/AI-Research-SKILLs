from .build import build


def main() -> int:
    result = build()
    print(f"built {result['revised']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
