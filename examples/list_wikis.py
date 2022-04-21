"""Example showing how to list all available wikis."""
from wiki_data_dump import WikiDump

# pylint: disable=C0103
if __name__ == "__main__":
    wiki_dump = WikiDump()

    for wiki_name in wiki_dump.wikis:
        print(wiki_name)
# pylint: enable=C0103
