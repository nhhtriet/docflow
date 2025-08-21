"""Placeholder for an ML-based classifier."""

def classify(text: str) -> str:
    """Return a dummy ML-based classification."""
    return "ml-invoice" if "total" in text.lower() else "ml-other"
