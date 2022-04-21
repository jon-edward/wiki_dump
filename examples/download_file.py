import re

from wiki_data_dump import WikiDump

# pylint: disable=C0103
if __name__ == '__main__':
    wiki = WikiDump()

    file = wiki["enwiki", "sitestable", re.compile(r"sites\.sql\.gz$")]

    def download_completion_hook(_exc_type, _exc_val, _exc_tb):
        """Called after file has finished downloading but not decompressing, mirrors __exit__ calls."""
        print("completed sites table download")

    def decompress_completion_hook(_exc_type, _exc_val, _exc_tb):
        """Called after file has finished decompressing, mirrors __exit__ calls."""
        print("completed sites table decompression")

    #  Completion hooks follow the same signature as __exit__

    download_thread = wiki.download(file, destination="sitestable.sql",
                                    download_completion_hook=download_completion_hook,
                                    decompress_completion_hook=decompress_completion_hook)
    download_thread.join()
# pylint: enable=C0103
