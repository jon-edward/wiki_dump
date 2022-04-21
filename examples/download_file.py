"""Example explaining how to download a file."""
import re

from wiki_data_dump import WikiDump


def download_completion_hook(_exc_type, _exc_val, _exc_tb):
    """Called after file has finished downloading but not decompressing,
    mirrors __exit__ calls."""
    print("completed sites table download")


def decompress_completion_hook(_exc_type, _exc_val, _exc_tb):
    """Called after file has finished decompressing, mirrors __exit__ calls."""
    #  Completion hooks follow the same function signature as object.__exit__
    print("completed sites table decompression")


def main():
    """Top-level main function."""

    wiki = WikiDump()

    file = wiki["enwiki", "sitestable", re.compile(r"sites\.sql\.gz$")]

    download_thread = wiki.download(
        file,
        destination="sitestable.sql",
        download_completion_hook=download_completion_hook,
        decompress_completion_hook=decompress_completion_hook,
    )
    download_thread.join()


if __name__ == "__main__":
    main()
