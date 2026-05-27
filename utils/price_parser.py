def parse_price(text: str) -> float:
    if not text:
        raise ValueError("empty price text")
    cleaned = "".join(c for c in text if c.isdigit() or c == ".")
    if not cleaned:
        raise ValueError(f"no numeric content in: {text!r}")
    return float(cleaned)
