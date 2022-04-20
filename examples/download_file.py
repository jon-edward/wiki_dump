import re

from wiki_data_dump import WikiDump

if __name__ == '__main__':
    wiki = WikiDump()

    file = wiki["enwiki", "sitestable", re.compile(r"sites\.sql\.gz$")]

    def download_completion_hook(exc_type, exc_val, exc_tb):
        print("completed sites table download")

    def decompress_completion_hook(exc_type, exc_val, exc_tb):
        print("completed sites table decompression")

    #  Completion hooks follow the same signature as __exit__

    download_thread = wiki.download(file, destination="sitestable.sql",
                                    download_completion_hook=download_completion_hook,
                                    decompress_completion_hook=decompress_completion_hook)
    download_thread.join()
