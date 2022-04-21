"""Example showing how to list all available files."""
from wiki_data_dump import WikiDump


def main():
    """Top-level main function."""
    wiki_dump = WikiDump()

    for wiki_name, job_name, file_name in wiki_dump.iter_files():
        print(file_name)


if __name__ == "__main__":
    main()
