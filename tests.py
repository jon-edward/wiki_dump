"""wiki-data-dump tests."""

from unittest import TestCase
from unittest.mock import patch, MagicMock
import re

from wiki_data_dump import WikiDump


class IterContentWrapper:
    """Used to mock requests.Response"""

    @staticmethod
    def iter_content(chunk_size: int):
        """Mocks requests.Response.iter_content"""
        #  Returns an iterator for test_cache, which only contains 'enwiki' branch of index.
        with open("test_data/test_cache.json", "rb") as f_buffer:
            while chunk := f_buffer.read(chunk_size):
                yield chunk

    @staticmethod
    def raise_for_status():
        """Noop for mocking requests.Response.raise_for_status"""


@patch("requests.Session.get", autospec=True)
def new_wiki_dump(mock_get: MagicMock) -> WikiDump:
    """Get new WikiDump without caching."""
    mock_get.return_value = IterContentWrapper()
    #  Not using cache, and not writing to cache.
    return WikiDump(use_cache=False, cache_index=False, clear_expired_caches=False)


class TestWikiDumpWrapper(TestCase):
    """Tests API operations in WikiDump wrapper class."""

    wiki: WikiDump

    def setUp(self) -> None:
        """Create WikiDump without caching enabled."""
        #  pylint: disable=no-value-for-parameter
        #  Due to wrapper, new_wiki_dump does not take parameter.
        self.wiki = new_wiki_dump()
        #  pylint: enable=no-value-for-parameter

    def test_wiki_dump_creation(self):
        """Tests simple WikiDump creation."""
        self.assertTrue(self.wiki)

    def test_successful_get_wiki(self):
        """Tests a successful result from getting a Wiki by name."""
        self.assertTrue(self.wiki.get_wiki("enwiki"))

    def test_unsuccessful_get_wiki(self):
        """Tests an unsuccessful result from getting a Wiki by name."""
        self.assertRaises(KeyError, lambda: self.wiki.get_wiki("[invalid wiki name]"))

    def test_successful_get_job(self):
        """Tests a successful result from getting a Job by name."""
        self.assertTrue(self.wiki.get_job("enwiki", "wbcentityusagetable"))

    def test_unsuccessful_get_job(self):
        """Tests an unsuccessful result from getting a Job by name."""
        self.assertRaises(
            KeyError, lambda: self.wiki.get_job("enwiki", "[invalid job name]")
        )

    def test_successful_get_file_absolute(self):
        """Tests a successful result from getting a File by absolute name."""
        self.assertTrue(
            self.wiki.get_file(
                "enwiki",
                "wbcentityusagetable",
                "enwiki-20220420-wbc_entity_usage.sql.gz",
            )
        )

    def test_unsuccessful_get_file_absolute(self):
        """Tests an unsuccessful result from getting a File by absolute name."""
        self.assertRaises(
            KeyError,
            lambda: self.wiki.get_file(
                "enwiki", "wbcentityusagetable", "[invalid file]"
            ),
        )

    def test_successful_get_file_pattern(self):
        """Tests a successful result from getting a File by regex pattern, matching
        first successful case."""
        self.assertTrue(
            self.wiki.get_file(
                "enwiki",
                "wbcentityusagetable",
                re.compile(r"wbc_entity_usage\.sql\.gz$"),
            )
        )

    def test_unsuccessful_get_file_pattern(self):
        """Tests an unsuccessful result from getting a File by regex patterm."""
        self.assertRaises(
            KeyError,
            lambda: self.wiki.get_file(
                "enwiki",
                "wbcentityusagetable",
                re.compile("this is an invalid file pattern"),
            ),
        )

    def test_iter_files(self):
        """Tests iterating over all files in a data dump, using known file count to verify."""
        file_count = 31  # In this particular index file, there are 31 files.
        self.assertEqual(len(list(self.wiki.iter_files())), file_count)

    def test_get_wiki_by_getitem(self):
        """Test getting a Wiki by means of __getitem__."""
        self.assertTrue(self.wiki["enwiki"])

    def test_get_job_by_getitem(self):
        """Test getting a Job by means of __getitem__."""
        self.assertTrue(self.wiki["enwiki", "xmlstubsdumprecombine"])

    def test_get_file_by_getitem_absolute(self):
        """Test getting a File by means of __getitem__, using absolute path."""
        self.assertTrue(
            self.wiki[
                "enwiki",
                "wbcentityusagetable",
                "enwiki-20220420-wbc_entity_usage.sql.gz",
            ]
        )

    def test_get_file_by_getitem_pattern(self):
        """Test getting a Wiki by means of __getitem__, using regex pattern."""
        self.assertTrue(
            self.wiki[
                "enwiki",
                "wbcentityusagetable",
                re.compile(r"wbc_entity_usage\.sql\.gz$"),
            ]
        )

    def test_get_files_some(self):
        """Tests a non-empty result for getting all matching occurrences of a file by regex."""
        self.assertTrue(
            self.wiki.get_job("enwiki", "wbcentityusagetable").get_files(
                re.compile(r"\.gz$")
            )
        )

    def test_get_files_none(self):
        """Tests an empty result for getting all matching occurrences of a file by regex."""
        self.assertFalse(
            self.wiki.get_job("enwiki", "wbcentityusagetable").get_files(
                re.compile(r"invalid file$")
            )
        )

    def test_wiki(self):
        """Test getting all wiki names, test index only contains enwiki."""
        #  Only contains 'enwiki' wiki
        self.assertEqual(self.wiki.wikis, ["enwiki"])
