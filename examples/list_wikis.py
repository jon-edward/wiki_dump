from wiki_data_dump import WikiDump

if __name__ == '__main__':
    wiki_dump = WikiDump()

    for wiki_name in wiki_dump.wikis:
        print(wiki_name)
