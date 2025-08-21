import argparse


def classify_pdf(pdf_path: str) -> None:
    """Placeholder function for PDF classification."""
    # TODO: Implement actual classification logic
    print(f"Classifying PDF: {pdf_path}")


def main() -> None:
    parser = argparse.ArgumentParser(description="PDF classification CLI")
    parser.add_argument("pdf", help="Path to the PDF file to classify")
    args = parser.parse_args()
    classify_pdf(args.pdf)


if __name__ == "__main__":
    main()
