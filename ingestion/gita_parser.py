import re

CHAPTER_WORDS = {
    "ONE": 1,
    "TWO": 2,
    "THREE": 3,
    "FOUR": 4,
    "FIVE": 5,
    "SIX": 6,
    "SEVEN": 7,
    "EIGHT": 8,
    "NINE": 9,
    "TEN": 10,
    "ELEVEN": 11,
    "TWELVE": 12,
    "THIRTEEN": 13,
    "FOURTEEN": 14,
    "FIFTEEN": 15,
    "SIXTEEN": 16,
    "SEVENTEEN": 17,
    "EIGHTEEN": 18,
}

MARKER_PATTERN = re.compile(r"CHAPTER\s+(\w+)|\bTEXT\s+(\d+)\b")


def _parse_verse_block(block: str) -> tuple[str, str] | None:
    # Each verse block should contain a TRANSLATION section
    if "TRANSLATION" not in block:
        return None

    _, after_translation = block.split("TRANSLATION", 1)

    if "PURPORT" in after_translation:
        translation, commentary = after_translation.split("PURPORT", 1)
    else:
        translation = after_translation
        commentary = ""

    translation = translation.strip()
    commentary = commentary.strip()

    if not translation:
        return None

    return translation, commentary


def _build_text(translation: str, commentary: str) -> str:
    if commentary:
        return f"{translation}\n\n{commentary}"
    return translation


def parse_verses(
    full_text: str,
    source: str,
    chapter: int | None = None,
) -> list[dict[str, str | int]]:
    # Walk the document and collect chapter headers and verse markers
    verse_markers: list[tuple[int | None, int, int, int]] = []
    active_chapter: int | None = None

    for match in MARKER_PATTERN.finditer(full_text):
        if match.group(1):
            chapter_word = match.group(1).upper()
            if chapter_word in CHAPTER_WORDS:
                active_chapter = CHAPTER_WORDS[chapter_word]
        elif match.group(2):
            verse_number = int(match.group(2))
            verse_markers.append((
                active_chapter,
                verse_number,
                match.end(),
                match.start(),
            ))

    verses: list[dict[str, str | int]] = []

    for index, (ch, verse_number, content_start, _) in enumerate(verse_markers):
        if ch is None:
            continue
        if chapter is not None and ch != chapter:
            continue

        if index + 1 < len(verse_markers):
            content_end = verse_markers[index + 1][3]
        else:
            content_end = len(full_text)

        block = full_text[content_start:content_end]
        parsed = _parse_verse_block(block)
        if parsed is None:
            continue

        translation, commentary = parsed

        verses.append({
            "id": f"ch{ch}-v{verse_number}",
            "chapter": ch,
            "verse_number": verse_number,
            "source": source,
            "text": _build_text(translation, commentary),
            "sanskrit": "",
            "transliteration": "",
            "translation": translation,
            "commentary": commentary,
        })

    return verses
