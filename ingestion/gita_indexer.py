from ingestion.pdf_loader import PdfLoader
from vector_store.pinecone_store import PineconeStore


class GitaIndexer:
    TOTAL_CHAPTERS = 18

    def __init__(
        self,
        loader: PdfLoader | None = None,
        store: PineconeStore | None = None,
        pdf_filename: str = "Bhagavad-gita-As-It-Is.pdf",
    ) -> None:
        self._loader = loader or PdfLoader()
        self._store = store or PineconeStore()
        self._pdf_filename = pdf_filename

    def index_chapter(self, chapter: int) -> int:
        """Load one chapter, embed verses, upsert to Pinecone. Returns verse count."""
        self._validate_chapter(chapter)
        verses = self._loader.read_pdf(
            filename=self._pdf_filename,
            chapter=chapter,
        )
        if not verses:
            raise ValueError(f"No verses found for chapter {chapter}")
        return self._store.upsert_verses(verses)

    def index_all_chapters(
        self,
        *,
        start: int = 1,
        end: int = 18,
    ) -> dict[int, int]:
        """Index chapters start..end. Returns {chapter: verse_count}."""
        self._validate_chapter_range(start, end)
        self._store.ensure_index()

        results: dict[int, int] = {}
        for chapter in range(start, end + 1):
            results[chapter] = self.index_chapter(chapter)
        return results

    def index_chapters(self, chapters: list[int]) -> dict[int, int]:
        """Index a specific list of chapters."""
        if not chapters:
            raise ValueError("Chapters must be a non-empty list")

        for chapter in chapters:
            self._validate_chapter(chapter)

        self._store.ensure_index()

        results: dict[int, int] = {}
        for chapter in chapters:
            results[chapter] = self.index_chapter(chapter)
        return results

    def _validate_chapter(self, chapter: int) -> None:
        if chapter < 1 or chapter > self.TOTAL_CHAPTERS:
            raise ValueError(
                f"Chapter must be between 1 and {self.TOTAL_CHAPTERS}, got {chapter}"
            )

    def _validate_chapter_range(self, start: int, end: int) -> None:
        self._validate_chapter(start)
        self._validate_chapter(end)
        if start > end:
            raise ValueError(f"Start chapter ({start}) must be <= end chapter ({end})")
