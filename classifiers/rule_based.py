"""Simple rule-based classifier."""

def classify(text: str) -> str:
    """Classify text using keyword rules."""
    return "invoice" if "invoice" in text.lower() else "other"
