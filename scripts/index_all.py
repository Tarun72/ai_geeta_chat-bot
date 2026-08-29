import argparse

from ingestion.gita_indexer import GitaIndexer


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Index Bhagavad Gita verses into Pinecone"
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--chapters",
        type=int,
        nargs="+",
        help="Specific chapter numbers to index (e.g. --chapters 1 2 18)",
    )
    parser.add_argument(
        "--start",
        type=int,
        default=1,
        help="First chapter to index (default: 1)",
    )
    parser.add_argument(
        "--end",
        type=int,
        default=GitaIndexer.TOTAL_CHAPTERS,
        help=f"Last chapter to index (default: {GitaIndexer.TOTAL_CHAPTERS})",
    )
    args = parser.parse_args()

    indexer = GitaIndexer()

    if args.chapters:
        results = indexer.index_chapters(args.chapters)
    else:
        results = indexer.index_all_chapters(start=args.start, end=args.end)

    index_name = indexer._store._index_name
    for chapter, count in sorted(results.items()):
        print(f"Indexed {count} verses from chapter {chapter}")

    total = sum(results.values())
    print(
        f"\nDone: indexed {total} verses across {len(results)} chapters "
        f"into '{index_name}'"
    )


if __name__ == "__main__":
    main()
