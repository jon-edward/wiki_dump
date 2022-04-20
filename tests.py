from unittest import TestCase
from unittest.mock import patch, MagicMock

from wiki_data_dump import WikiDump


class IterContentWrapper:
    @staticmethod
    def iter_content(chunk_size: int):
        #  Returns an iterator for test_cache, which only contains 'enwiki' branch of index.
        with open("test_data/test_cache.json", 'rb') as f:
            while chunk := f.read(chunk_size):
                yield chunk

    @staticmethod
    def raise_for_status():
        pass


@patch("requests.Session.get", autospec=True)
def new_wiki_dump(mock_get: MagicMock) -> WikiDump:
    mock_get.return_value = IterContentWrapper()
    #  Not using cache, and not writing to cache.
    return WikiDump(use_cache=False, cache_index=False)


class TestWikiDumpWrapper(TestCase):
    wiki: WikiDump

    def setUp(self) -> None:
        self.wiki = new_wiki_dump()

    def test_wiki_dump_creation(self):
        self.assertTrue(self.wiki)

    def test_successful_get_wiki(self):
        self.assertTrue(self.wiki.get_wiki("enwiki"))

    def test_unsuccessful_get_wiki(self):
        self.assertRaises(KeyError, lambda: self.wiki.get_wiki("[invalid wiki name]"))

    def test_successful_get_job(self):
        self.assertTrue(self.wiki.get_job("enwiki", "wbcentityusagetable"))

    def test_unsuccessful_get_job(self):
        self.assertRaises(KeyError, lambda: self.wiki.get_job("enwiki", "[invalid job name]"))

    def test_successful_get_file_absolute(self):
        self.assertTrue(self.wiki.get_file("enwiki", "wbcentityusagetable", "enwiki-20220420-wbc_entity_usage.sql.gz"))

    def test_unsuccessful_get_file_absolute(self):
        self.assertRaises(KeyError, lambda: self.wiki.get_file("enwiki", "wbcentityusagetable", "[invalid file]"))

    def test_successful_get_file_pattern(self):
        import re

        self.assertTrue(self.wiki.get_file("enwiki", "wbcentityusagetable", re.compile(r"wbc_entity_usage\.sql\.gz$")))

    def test_unsuccessful_get_file_pattern(self):
        import re

        self.assertRaises(KeyError, lambda: self.wiki.get_file("enwiki", "wbcentityusagetable",
                                                               re.compile("this is an invalid file pattern")))

    def test_iter_files(self):
        file_count = 31  # In this particular index file, there are 31 files.
        self.assertEqual(len(list(self.wiki.iter_files())), file_count)

    def test_get_wiki_by_getitem(self):
        self.assertTrue(self.wiki["enwiki"])

    def test_get_job_by_getitem(self):
        self.assertTrue(self.wiki["enwiki", "xmlstubsdumprecombine"])

    def test_get_file_by_getitem_absolute(self):
        self.assertTrue(self.wiki["enwiki", "wbcentityusagetable", "enwiki-20220420-wbc_entity_usage.sql.gz"])

    def test_get_file_by_getitem_pattern(self):
        import re

        self.assertTrue(self.wiki["enwiki", "wbcentityusagetable", re.compile(r"wbc_entity_usage\.sql\.gz$")])

    def test_get_files_some(self):
        import re

        self.assertTrue(self.wiki.get_job("enwiki", "wbcentityusagetable").get_files(re.compile(r"\.gz$")))

    def test_get_files_none(self):
        import re

        self.assertFalse(self.wiki.get_job("enwiki", "wbcentityusagetable").get_files(re.compile(r"invalid file$")))

    def test_wiki(self):
        #  Only contains 'enwiki' wiki
        self.assertEqual(self.wiki.wikis, ["enwiki"])
