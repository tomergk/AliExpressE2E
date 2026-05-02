def parse_price(text: str) -> float:
    cleaned = "".join(c for c in text if c.isdigit() or c == ".")
    try:
        return float(cleaned) if cleaned else 0.0
    except ValueError:
        return 0.0
