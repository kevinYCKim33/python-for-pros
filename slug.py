def slugify(name: str) -> str:
    cleaned = name.strip()
    if not cleaned:
        raise ValueError("name cannot be empty")
    return cleaned.lower().replace(" ", "-")
