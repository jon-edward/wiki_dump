from wiki_data_dump import WikiDump

# pylint: disable=C0103
if __name__ == "__main__":
    wiki_dump = WikiDump()

    for wiki_name, job_name, file_name in wiki_dump.iter_files():
        print(file_name)
# pylint: enable=C0103
