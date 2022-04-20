from wiki_data_dump import WikiDump

if __name__ == '__main__':
    wiki_dump = WikiDump()

    for wiki_name, job_name, file_name in wiki_dump.iter_files():
        print(file_name)
