from wiki_data_dump import WikiDump, Wiki


def jobs_for_wiki(wiki_object: Wiki):
    """Gets jobs for a given Wiki."""
    return wiki_object.jobs.keys()


# pylint: disable=C0103
if __name__ == "__main__":
    wiki_dump = WikiDump()

    for wiki in wiki_dump.wikis:
        print(wiki)
        for job in jobs_for_wiki(wiki_dump[wiki]):
            print(f" - {job}")
# pylint: enable=C0103
