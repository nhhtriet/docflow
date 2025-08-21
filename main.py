"""Entry point for the PDF classification tool."""

from extract_text import extract_text
from classifiers.rule_based import classify as rule_classify

def main(path: str) -> str:
    """Extract text from a file and classify it."""
    text = extract_text(path)
    return rule_classify(text)

if __name__ == "__main__":  # pragma: no cover
    import sys
    if len(sys.argv) > 1:
        print(main(sys.argv[1]))
