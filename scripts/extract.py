"""Script for page-by-page text extraction from raw PDF (docs/data-spec.md Section 4).

Extraction rules from docs/data-spec.md Section 2 and Section 4:
- Scope: pages 14 to 98, plus the accreditation table on page 11.
- Section separators: skip pages 13, 26, and 99 during extraction.
- Two-column regulation pages (e.g. page 17): do not use pdftotext -layout.
  Extract without -layout or crop page into left and right halves.
- Accreditation table (page 11): extract via pdftotext -layout or manual CSV input.
- Curriculum pages: visual verification required for course code mapping due to inconsistent positions.
- Page numbering reference: strictly follow PDF page numbers.
- Output raw extracted text per page into data/raw/.
"""


def main() -> None:
    """Execute text extraction pipeline skeleton."""
    # TODO: Implement PDF page extraction adhering to layout and page scope rules
    print("Extract script skeleton - awaiting PDF extraction implementation.")


if __name__ == "__main__":
    main()
