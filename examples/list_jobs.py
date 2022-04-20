from wiki_data_dump import WikiDump, Wiki


def jobs_for_wiki(wiki_object: Wiki):
    return wiki_object.jobs.keys()


if __name__ == '__main__':
    wiki_dump = WikiDump()

    for wiki in wiki_dump.wikis:
        print(wiki)
        for job in jobs_for_wiki(wiki_dump[wiki]):
            print(f" - {job}")
