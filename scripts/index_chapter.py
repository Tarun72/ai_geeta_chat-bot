import argparse

from ingestion.gita_indexer import GitaIndexer


def main() -> None:
    parser = argparse.ArgumentParser(description="Index Bhagavad Gita verses into Pinecone")
    parser.add_argument(
        "--chapter",
        type=int,
        required=True,
        help="Chapter number to index (1-18)",
    )
    args = parser.parse_args()

    indexer = GitaIndexer()
    indexer._store.ensure_index()
    count = indexer.index_chapter(args.chapter)
    print(
        f"Indexed {count} verses from chapter {args.chapter} "
        f"into '{indexer._store._index_name}'"
    )


if __name__ == "__main__":
    main()
