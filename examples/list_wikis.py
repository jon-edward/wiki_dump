"""Example showing how to list all available wikis."""
from wiki_data_dump import WikiDump


def main():
    """Top-level main function."""
    wiki_dump = WikiDump()

    for wiki_name in wiki_dump.wikis:
        print(wiki_name)


if __name__ == "__main__":
    main()
