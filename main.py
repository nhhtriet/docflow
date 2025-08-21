import argparse
from utils import extract_text_from_pdf


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Extract text and metadata from a PDF document."
    )
    parser.add_argument("pdf_path", help="Path to the PDF file to process")
    args = parser.parse_args()

    text, metadata = extract_text_from_pdf(args.pdf_path)

    print("Extracted Text:\n")
    print(text)
    print("\nMetadata:")
    print(f"doc_type: {metadata.get('doc_type')}")
    print(f"issuer_unit: {metadata.get('issuer_unit')}")
    print(f"date: {metadata.get('date')}")
    print(f"person_name: {metadata.get('person_name')}")
    print(f"person_signer: {metadata.get('person_signer')}")
    print(f"employee_id: {metadata.get('employee_id')}")


if __name__ == "__main__":
    main()
