from pathlib import Path

from pypdf import PdfReader

from ingestion.gita_parser import parse_verses


class PdfLoader:
    # Stores the folder path where PDF files are kept
    def __init__(self, data_dir: Path | None = None) -> None:
        if data_dir is None:
            # Go up two levels from this file to reach project root
            project_root = Path(__file__).resolve().parent.parent
            # Default PDF location is project_root/data/
            data_dir = project_root / "data"
        self._data_dir = data_dir

    # Reads the PDF and returns structured verse records
    def read_pdf(
        self,
        filename: str = "Bhagavad-gita-As-It-Is.pdf",
        chapter: int | None = None,
    ) -> list[dict[str, str | int]]:
        pages = self._extract_pages(filename)
        # Join all pages so verses split across pages are parsed correctly
        full_text = "\n".join(page["text"] for page in pages)
        return parse_verses(full_text, filename, chapter=chapter)

    def _extract_pages(
        self, filename: str
    ) -> list[dict[str, str | int]]:
        # Build full path: data/Bhagavad-gita-As-It-Is.pdf
        pdf_path = self._data_dir / filename

        # Stop early if the file does not exist
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF not found: {pdf_path}")

        # Open the PDF file and extract text page by page
        reader = PdfReader(pdf_path)
        pages: list[dict[str, str | int]] = []

        for index, page in enumerate(reader.pages):
            pages.append({
                "page": index + 1,
                "text": page.extract_text() or "",
            })

        return pages
